#!/usr/bin/env python3
import os
import sys
import json
import logging
import datetime
from typing import Dict, List, Any, Optional, Tuple
import pyodbc
from dotenv import load_dotenv

load_dotenv()

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


** don't forget the roll call parameter strings





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
            "committee_reports": [],
            "committee_report_ids": [],
            "member_roll_calls": [],
            "committee_report_published_actions": [],
            "published_items": [],
            "agenda_items": [],
            "committee_meeting_agenda_items": [],
        }
        self.counts: Dict[str, int] = {
            "committee_reports": 0,
            "agenda_items": 0,
            "published_agenda_items": 0,
            "roll_calls": 0,
            "published_roll_calls": 0,
            "agenda_item_actions": 0,
            "published_agenda_item_actions": 0
        }

    def connect_databases(self) -> None:
        self.eva_db.connect()
        self.shared_db.connect()

    def close_databases(self) -> None:
        self.eva_db.close()
        self.shared_db.close()

    def gather_committee_reports(self) -> None:
        logging.info("Gathering committee reports...")
        query: str = """
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

        results: List[Dict[str, Any]] = self.eva_db.execute_query(query)
        for report in results:
            if report.get("PublishedReportDocument"):
                report["PublishedReportDocument"] = "BINARY_DATA"
            if report.get("PublishedAttendanceReportDocument"):
                report["PublishedAttendanceReportDocument"] = "BINARY_DATA"
            for key, value in list(report.items()):
                if isinstance(value, datetime.datetime):
                    report[key] = value.isoformat()

        ids: List[int] = [report["Id"] for report in results]
        self.data["committee_reports"] = results
        self.data["committee_report_ids"] = ids
        logging.info(f"Gathered {len(results)} committee reports.")

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
        self.data["action_to_agenda_items"] = results

        ids: List[int] = list(set([item["AgendaItemId"] for item in results]))
        agenda_item_id_string: str = ",".join(map(str, ids))

        print(f"Gathered {len(results)} action to agenda items.")
        print(f"agenda_item_id_string {agenda_item_id_string}")

        committee_meeting_agenda_items_query: str = f"""
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
WHERE [CommitteeMeetingAgendaItemID] IN ({agenda_item_id_string})
        """
        committee_meeting_agenda_items: List[Dict[str, Any]] = self.shared_db.execute_query(
                committee_meeting_agenda_items_query
        )
        self.data["committee_meeting_agenda_items"] = committee_meeting_agenda_items
        print(f"Gathered {len(committee_meeting_agenda_items)} committee meeting agenda items.")

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
        # TODO: is there an issue here? 
        # where the published actions could be out of sync with the item to actions?
        # well yes, the agenda item could have actions that were published and some that were not.
        self.data["committee_report_published_actions"] = committee_report_published_actions
        print(f"Gathered {len(committee_report_published_actions)} CommitteeReportPublishedActions.")
    

    # def gather_published_items(self) -> None:
    #     logging.info("Gathering published items...")
    #     # TODO: Add query and data processing for published items
    #
    # def gather_member_roll_calls(self) -> None:
    #     logging.info("Gathering member roll calls...")
    #     # TODO: Add query and data processing for member roll calls



    def gather_all_data(self) -> None:
        self.connect_databases()
        try:
            self.gather_committee_reports()
            self.gather_action_to_agenda_items()
            self.gather_published_actions()
            # self.gather_member_roll_calls()
            # self.gather_published_items()
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
