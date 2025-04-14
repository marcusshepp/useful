#!/usr/bin/env python3
import os
import sys
import json
import logging
import datetime
from typing import Dict, List, Any, Optional, Tuple, Set
import pyodbc
from dotenv import load_dotenv
# from pprint import pprint

load_dotenv()

# Dictionary keys
KEY_COMMITTEE_REPORTS = "committee_reports"
KEY_COMMITTEE_REPORT_IDS = "committee_report_ids"
KEY_MEMBER_ROLL_CALLS = "member_roll_calls"
KEY_COMMITTEE_REPORT_PUBLISHED_ACTIONS = "committee_report_published_actions"
KEY_PUBLISHED_ITEMS = "published_items"
KEY_COMMITTEE_MEETING_AGENDA_ITEMS = "committee_meeting_agenda_items"
KEY_ACTION_TO_AGENDA_ITEMS = "action_to_agenda_items"

# Count keys
COUNT_COMMITTEE_REPORTS = "committee_reports"
COUNT_AGENDA_ITEMS = "agenda_items"
COUNT_PUBLISHED_AGENDA_ITEMS = "published_agenda_items"
COUNT_ROLL_CALLS = "roll_calls"
COUNT_PUBLISHED_ROLL_CALLS = "published_roll_calls"
COUNT_AGENDA_ITEM_ACTIONS = "agenda_item_actions"
COUNT_PUBLISHED_AGENDA_ITEM_ACTIONS = "published_agenda_item_actions"

"""
I'm thinking I should set up a select data routine first. This will analyze the data
and count everything.

what is all the data that I need to select for the pre-deployment?

- Committee reports
  * need to worry about meeting date / whatever else i'm 'saving' a query on 

- CommitteeReportCommitteeActionToAgendaItems
  * these should have all the custom actions and custom agenda items

- CommitteeMeetinAgendaItems where 
CommitteeReportCommitteeActionToAgendaItems.AgendaItemid = CommitteeMeetingAgendaItems.AgendaItemId

- I believe I can just ignore RemovedAgendaItems all together.

- group all CommitteeReportCommitteeActionToAgendaItems by agenda id 
  * ea group will have a agenda item id and many action ids
  * copy over the sub text

- one difference not accounted for in the document:
    * the custom items previously were tracking both the recommended custom action
    and the reported out custom action, on the CommitteeReportCommitteeActionToAgendaItems table
    in the same row.
    * not the custom actions are tracked the exact same way the legislative item actions
    are tracked, with the CommitteeReportActions table. This allows the user to have as many custom action
    as they want

- NOTE: Might be best to create a CommitteeReportAgendaItem for every CommitteeMeetingAgendaItem
    * for every CommitteeMeetingAgendaItems that have a meeting that has a report.
    * then iterate over all the already created actions. and roll calls. and create the relevant rows
    for those


** don't forget the roll call parameter strings


NOTE: 
    what i've done so far
    * get all committee reports
    * get all committee meeting agenda items that 
    have meetings that are tied to the reports
    * get all committee report published agenda items
    * get all committee report published actions




- Committee reports
- Committee report agenda items 
- Committee report actions
- Committee report roll calls

- Committee report attendance ??? not really


"""

class DateTimeEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, (datetime.datetime, datetime.date)):
            return o.isoformat()
        return super().default(o)

class DatabaseConnector:
    def __init__(self, connection_string: str) -> None:
        self.connection_string: str = connection_string
        self.connection: Optional[pyodbc.Connection] = None
        self.cursor: Optional[pyodbc.Cursor] = None

    def connect(self) -> None:
        try:
            self.connection = pyodbc.connect(self.connection_string)
            self.cursor = self.connection.cursor()
            logging.info("Database connection established")
        except Exception as e:
            logging.error(f"Database connection error: {str(e)}")
            raise

    def close(self) -> None:
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        logging.info("Database connection closed")

    def execute_query(self, query: str, params: Optional[Tuple] = None) -> List[Dict[str, Any]]:
        try:
            if not self.cursor:
                raise Exception("No database cursor available")
                
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
                
            columns = [column[0] for column in self.cursor.description]
            results = []
            
            for row in self.cursor.fetchall():
                results.append(dict(zip(columns, row)))
                
            return results
        except Exception as e:
            logging.error(f"Query execution error: {str(e)}\nQuery: {query}")
            raise

class DataGatherer:
    def __init__(self, eva_connection_string: str, shared_connection_string: str) -> None:
        self.eva_db: DatabaseConnector = DatabaseConnector(eva_connection_string)
        self.shared_db: DatabaseConnector = DatabaseConnector(shared_connection_string)
        self.data: Dict[str, Any] = {
            KEY_COMMITTEE_REPORTS: [],
            KEY_COMMITTEE_REPORT_IDS: [],
            KEY_MEMBER_ROLL_CALLS: [],
            KEY_COMMITTEE_REPORT_PUBLISHED_ACTIONS: [],
            KEY_PUBLISHED_ITEMS: [],
            KEY_COMMITTEE_MEETING_AGENDA_ITEMS: [],
        }
        self.counts: Dict[str, int] = {
            COUNT_COMMITTEE_REPORTS: 0,
            COUNT_AGENDA_ITEMS: 0,
            COUNT_PUBLISHED_AGENDA_ITEMS: 0,
            COUNT_ROLL_CALLS: 0,
            COUNT_PUBLISHED_ROLL_CALLS: 0,
            COUNT_AGENDA_ITEM_ACTIONS: 0,
            COUNT_PUBLISHED_AGENDA_ITEM_ACTIONS: 0
        }

    def connect_databases(self) -> None:
        self.eva_db.connect()
        self.shared_db.connect()

    def close_databases(self) -> None:
        self.eva_db.close()
        self.shared_db.close()

    def gather_committee_reports_and_agenda_items(self) -> None:
        logging.info("Gathering committee reports...")
        committee_reports_query: str = """
SELECT 
    cr.Id,
    cr.SessionId,
    cr.CommitteeId,
    cr.MeetingId,
    cr.IsPublished,
    cr.PublishedDate,
    cr.AddendaDate,
    cr.PublishedBy,
    cr.AttendancePublishedBy,
    cr.IsAttendancePublished,
    cr.PublishedReportDocument,
    cr.PublishedAttendanceReportDocument,
    cr.AttendancePublishedDate,
    cr.CreatedBy,
    cr.Created,
    cr.Modified,
    cr.ModifiedBy
FROM CommitteeReports cr
        """
        committee_reports: List[Dict[str, Any]] = self.eva_db.execute_query(committee_reports_query)
        
        # Process committee reports
        for report in committee_reports:
            if report.get("PublishedReportDocument"):
                report["PublishedReportDocument"] = "BINARY_DATA"
            if report.get("PublishedAttendanceReportDocument"):
                report["PublishedAttendanceReportDocument"] = "BINARY_DATA"
            for key, value in list(report.items()):
                if isinstance(value, datetime.datetime):
                    report[key] = value.isoformat()
        
        # Extract meeting IDs from committee reports
        meeting_ids: List[int] = [
                report["MeetingId"] 
                for report in committee_reports 
                if report["MeetingId"] is not None]
        meeting_ids_string: str = ",".join(
                str(id) for id in meeting_ids) if meeting_ids else "0"
        
        # Store committee reports data
        self.counts[COUNT_COMMITTEE_REPORTS] = len(committee_reports)
        self.data[KEY_COMMITTEE_REPORTS] = committee_reports
        self.data[KEY_COMMITTEE_REPORT_IDS] = [report["Id"] for report in committee_reports]
        
        logging.info(f"Found {len(meeting_ids)} meetings with committee reports")
        
        # Get all agenda items for these meetings
        logging.info("Gathering committee meeting agenda items for these meetings...")
        agenda_items_query: str = f"""
SELECT [CommitteeMeetingAgendaItemID]
      ,[SessionID]
      ,[CommitteeMeetingID]
      ,[LegislationID]
      ,[Description]
      ,[SortOrder]
      ,[IsActive]
      ,[DateAdded]
      ,[LastModified]
      ,[LastModifiedBy]
      ,[IsPublic]
FROM [dbo].[CommitteeMeetingAgendaItem]
WHERE [CommitteeMeetingID] IN ({meeting_ids_string})
        """
        
        agenda_items: List[Dict[str, Any]] = self.shared_db.execute_query(agenda_items_query)
        
        # Store agenda items
        self.counts[COUNT_AGENDA_ITEMS] = len(agenda_items)
        self.data[KEY_COMMITTEE_MEETING_AGENDA_ITEMS] = agenda_items
        
        logging.info(f"Found {len(agenda_items)} agenda items connected to meetings with committee reports")
        
        # Get additional meeting and committee info
        if meeting_ids:
            logging.info("Gathering additional meeting and committee information...")
            meeting_committee_info_query: str = f"""
SELECT m.CommitteeMeetingID, m.MeetingLocation, c.CommitteeID, c.CommitteeName 
FROM Committee c
INNER JOIN CommitteeMeetingCommittee cmc ON cmc.CommitteeID = c.CommitteeID
INNER JOIN CommitteeMeeting m ON m.CommitteeMeetingID = cmc.CommitteeMeetingID
WHERE m.CommitteeMeetingID IN ({meeting_ids_string})
            """
            
            meeting_committee_info: List[Dict[str, Any]] = self.shared_db.execute_query(meeting_committee_info_query)
            
            # Create a mapping of meeting IDs to committee info
            meeting_committee_map: Dict[int, Dict[str, Any]] = {
                info["CommitteeMeetingID"]: info for info in meeting_committee_info
            }
            
            logging.info(f"appending committee info to {len(agenda_items)} agenda items")
            # Enrich agenda items with committee info
            for item in agenda_items:
                meeting_id: int = item["CommitteeMeetingID"]
                if meeting_id in meeting_committee_map:
                    info = meeting_committee_map[meeting_id]
                    item["CommitteeName"] = info["CommitteeName"]
                    item["MeetingLocation"] = info["MeetingLocation"]

    def gather_action_to_agenda_items(self) -> None:
        logging.info("Gathering CommitteeReportCommitteeActionToAgendaItems...")
        query: str = """
SELECT [Id]
    ,[CommitteeReportCommitteeActionId]
    ,[AgendaItemId]
    ,[CustomRecommendedAction]
    ,[CustomReportOutAction]
    ,[MeetingId]
    ,[SortOrder]
    ,[Sub]
FROM [dbo].[CommitteeReportCommitteeActionToAgendaItems]
        """
        results: List[Dict[str, Any]] = self.eva_db.execute_query(query)
        self.counts[COUNT_AGENDA_ITEM_ACTIONS] = len(results)
        self.data[KEY_ACTION_TO_AGENDA_ITEMS] = results
        logging.info(f"Gathered {len(results)} action to agenda items.")

    def gather_published_agenda_items(self) -> None:
        logging.info("Gathering CommitteeReportPublishedItems...")
        query: str = """
SELECT [Id]
    ,[MeetingId]
    ,[AgendaItemId]
    ,[CreatedBy]
    ,[Created]
    ,[Modified]
    ,[ModifiedBy]
FROM [dbo].[CommitteeReportPublishedItems]
        """
        published_items_results_from_query: List[Dict[str, Any]] = self.eva_db.execute_query(query)
        self.counts[COUNT_PUBLISHED_AGENDA_ITEMS] = len(published_items_results_from_query)
        self.data[KEY_PUBLISHED_ITEMS] = published_items_results_from_query
        logging.info(f"Gathered {len(published_items_results_from_query)} CommitteeReportPublishedItems.")


        # Create a mapping of agenda item IDs to the actual agenda items
        agenda_item_map: Dict[int, Dict[str, Any]] = {
            item["CommitteeMeetingAgendaItemID"]: item 
            for item in self.data[KEY_COMMITTEE_MEETING_AGENDA_ITEMS]
        }

        # Initialize all items as not published
        for item in self.data[KEY_COMMITTEE_MEETING_AGENDA_ITEMS]:
            item["IsPublished"] = False

        # get the set of published agenda item IDs
        published_agenda_item_ids: Set[int] = {
            item["AgendaItemId"] for item in published_items_results_from_query
        }
          
        # mark items as published
        for agenda_item_id in published_agenda_item_ids:
            if agenda_item_id in agenda_item_map:
                agenda_item_map[agenda_item_id]["IsPublished"] = True
                
        number_of_published_agenda_items: int = len(published_agenda_item_ids)
        logging.info(f"Marked {number_of_published_agenda_items} published agenda items.")


    def gather_published_actions(self) -> None:
        logging.info("Gathering CommitteeReportPublishedActions...")
        committee_report_published_actions_query: str = f"""
SELECT [Id]
      ,[CommitteeReportCommitteeActionId]
      ,[AgendaItemId]
      ,[CustomRecommendedAction]
      ,[CustomReportOutAction]
      ,[MeetingId]
      ,[SortOrder]
      ,[Sub]
FROM [dbo].[CommitteeReportPublishedActions]
        """
        committee_report_published_actions: List[Dict[str, Any]] = self.eva_db.execute_query(
                committee_report_published_actions_query
        )
        self.counts[COUNT_PUBLISHED_AGENDA_ITEM_ACTIONS] = len(committee_report_published_actions)
        self.data[KEY_COMMITTEE_REPORT_PUBLISHED_ACTIONS] = committee_report_published_actions
        logging.info(f"Gathered {len(committee_report_published_actions)} CommitteeReportPublishedActions.")

    # def gather_member_roll_calls(self) -> None:
    #     logging.info("Gathering member roll calls...")
    #     # TODO: Add query and data processing for member roll calls



    def gather_all_data(self) -> None:
        self.connect_databases()
        try:
            # self.gather_committee_reports()
            self.gather_committee_reports_and_agenda_items()
            self.gather_published_agenda_items()
            self.gather_action_to_agenda_items()
            self.gather_published_actions()
            # self.gather_member_roll_calls()
            # TODO: should I consider these removed agenda items? #
            # self.gather_removed_agenda_items() 
            # self.gather_agenda_items()
            
            logging.info("=== PRE-DEPLOYMENT DATA COUNTS ===")
            for category, count in self.counts.items():
                logging.info(f"{category.upper()}: {count}")
        finally:
            self.close_databases()

    def save_to_json(self, output_path: str) -> None:
        data_with_counts: Dict[str, Any] = {
            **self.data,
            "counts": self.counts
        }
        
        with open(output_path, 'w') as f:
            json.dump(data_with_counts, f, cls=DateTimeEncoder, indent=2)
        logging.info(f"Data saved to {output_path}")

def setup_logging() -> None:
    current_time: str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_format: str = "%(asctime)s - %(levelname)s - %(message)s"
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.FileHandler(f"pre_debug_{current_time}.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )

def main() -> None:
    setup_logging()
    logging.info("Starting pre-deployment data gathering")
    
    eva_connection: str | None = os.getenv("EVA_DB_CONNECTION")
    shared_connection: str | None = os.getenv("SHARED_DB_CONNECTION")
    current_time: str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path: str = os.getenv("OUTPUT_PATH", f"predeployment_{current_time}.json")
    
    if not eva_connection or not shared_connection:
        logging.error("Database connection strings not found in environment variables")
        sys.exit(1)
    
    gatherer: DataGatherer = DataGatherer(eva_connection, shared_connection)
    
    try:
        gatherer.gather_all_data()
        gatherer.save_to_json(output_path)
        logging.info(f"Pre-deployment data gathering completed successfully and saved to {output_path}")
    except Exception as e:
        logging.error(f"Error during data gathering: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
