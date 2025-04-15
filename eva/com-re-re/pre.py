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
import queries

load_dotenv()

# Dictionary keys
KEY_COMMITTEE_REPORTS = "committee_reports"
KEY_COMMITTEE_REPORT_IDS = "committee_report_ids"
KEY_MEMBER_ROLL_CALLS = "member_roll_calls"
KEY_COMMITTEE_REPORT_PUBLISHED_ACTIONS = "committee_report_published_actions"
KEY_PUBLISHED_ITEMS = "published_items"
KEY_COMMITTEE_MEETING_AGENDA_ITEMS = "committee_meeting_agenda_items"
KEY_ACTION_TO_AGENDA_ITEMS = "action_to_agenda_items"
KEY_REMOVED_AGENDA_ITEMS = "removed_agenda_items"
KEY_LEGISLATION_ITEMS = "legislation_items"
KEY_COMMITTEE_ACTIONS = "committee_actions"

# Count keys
COUNT_COMMITTEE_REPORTS = "committee_reports"
COUNT_AGENDA_ITEMS = "agenda_items"
COUNT_PUBLISHED_AGENDA_ITEMS = "published_agenda_items"
COUNT_ROLL_CALLS = "roll_calls"
COUNT_PUBLISHED_ROLL_CALLS = "published_roll_calls"
COUNT_AGENDA_ITEM_ACTIONS = "agenda_item_actions"
COUNT_PUBLISHED_AGENDA_ITEM_ACTIONS = "published_agenda_item_actions"
COUNT_REMOVED_AGENDA_ITEMS = "removed_agenda_items"
COUNT_LEGISLATION_ITEMS = "legislation_items"
COUNT_COMMITTEE_ACTIONS = "committee_actions"

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
            KEY_LEGISLATION_ITEMS: [],
        }
        self.counts: Dict[str, int] = {
            COUNT_COMMITTEE_REPORTS: 0,
            COUNT_AGENDA_ITEMS: 0,
            COUNT_PUBLISHED_AGENDA_ITEMS: 0,
            COUNT_ROLL_CALLS: 0,
            COUNT_PUBLISHED_ROLL_CALLS: 0,
            COUNT_AGENDA_ITEM_ACTIONS: 0,
            COUNT_PUBLISHED_AGENDA_ITEM_ACTIONS: 0,
            COUNT_REMOVED_AGENDA_ITEMS: 0,
            COUNT_LEGISLATION_ITEMS: 0,
        }

    def connect_databases(self) -> None:
        self.eva_db.connect()
        self.shared_db.connect()

    def close_databases(self) -> None:
        self.eva_db.close()
        self.shared_db.close()

    def get_removed_agenda_items(self) -> str:
        logging.info("Gathering all removed agenda items...")
        removed_agenda_items: List[Dict[str, Any]] = self.eva_db.execute_query(
                queries.get_removed_agenda_items_query())
        
        logging.info(f"Found {len(removed_agenda_items)} removed agenda items")
        self.counts[COUNT_REMOVED_AGENDA_ITEMS] = len(removed_agenda_items)
        self.data[KEY_REMOVED_AGENDA_ITEMS] = removed_agenda_items
        
        removed_agenda_item_ids: List[int] = [
                item["AgendaItemId"] for item in removed_agenda_items]
        removed_agenda_item_ids_string: str = ",".join(
                [str(i) for i in removed_agenda_item_ids])
        return removed_agenda_item_ids_string

    def gather_committee_reports_and_agenda_items(self) -> None:
        """
        Get all Committee Reports 
        Then get all the meetings that have a report
        And gather all their agenda items that aren't removed
        """
        logging.info("Gathering committee reports...")
        committee_reports: List[Dict[str, Any]] = self.eva_db.execute_query(
            queries.get_committee_reports_query())
        
        # Remove binary data and convert datetime to ISO format
        # Binary data is preserved by the migration
        for report in committee_reports:
            if report.get("PublishedReportDocument"):
                report["PublishedReportDocument"] = "BINARY_DATA"
            if report.get("PublishedAttendanceReportDocument"):
                report["PublishedAttendanceReportDocument"] = "BINARY_DATA"
            for key, value in list(report.items()):
                if isinstance(value, datetime.datetime):
                    report[key] = value.isoformat()
        
        # Store committee reports data
        self.counts[COUNT_COMMITTEE_REPORTS] = len(committee_reports)
        self.data[KEY_COMMITTEE_REPORTS] = committee_reports
        self.data[KEY_COMMITTEE_REPORT_IDS] = [report["Id"] for report in committee_reports]
        
        # Extract meeting IDs from committee reports
        meeting_ids: List[int] = [
                report["MeetingId"] 
                for report in committee_reports 
                if report["MeetingId"] is not None]
        meeting_ids_string: str = ",".join(
                str(id) for id in meeting_ids) if meeting_ids else "0"
        logging.info(f"Found {len(meeting_ids)} meetings with committee reports")
        
        # Get removed agenda items then get all C|ommitteeMeetingAgendaItems
        # that are not removed
        removed_agenda_item_ids_string: str = self.get_removed_agenda_items()
        logging.info("Gathering committee meeting agenda items for these meetings that aren't removed...")
        agenda_items: List[Dict[str, Any]] = self.shared_db.execute_query(
            queries.get_agenda_items_query(
                meeting_ids_string, removed_agenda_item_ids_string))

        # get legislation for all legislation ids in agenda items if not None
        legislation_ids: Set[int] = {
            item["LegislationID"] for item in agenda_items if item["LegislationID"] is not None
        }
        legislation_results: List[Dict[str, Any]] = self.shared_db.execute_query(
            queries.get_legislation_items_query(legislation_ids))
        logging.info(f"Found {len(legislation_results)} legislation items for agenda items")
        self.counts[COUNT_LEGISLATION_ITEMS] = len(legislation_results)
        self.data[KEY_LEGISLATION_ITEMS] = legislation_results
        # for each agenda item, if the legislation id is in the legislation results
        # add prefix and identifier to the agenda item
        legs_not_found: List[str] = []
        for item in agenda_items:
            legislation_id: int = item["LegislationID"]
            legislation_matching: Dict[str, Any] | None = next((
                leg for leg in legislation_results 
                if leg["LegislationID"] == legislation_id and legislation_id is not None), None)
            if not legislation_matching and legislation_id is not None:
                legs_not_found.append(
                        f"legislationid: {legislation_id},\
                                CommitteeMeetingAgendaItems.Id: {item['CommitteeMeetingAgendaItemID']}")
            elif legislation_matching:
                item["LegislationPrefix"] = legislation_matching["Prefix"]
                item["LegislationIdentifier"] = legislation_matching["Identifier"]
        if legs_not_found and len(legs_not_found) > 0:
            logging.warning(f"** Legislation items not found for agenda items: {legs_not_found}")

        
        # Store agenda items
        self.counts[COUNT_AGENDA_ITEMS] = len(agenda_items)
        self.data[KEY_COMMITTEE_MEETING_AGENDA_ITEMS] = agenda_items
        
        logging.info(f"Found {len(agenda_items)} agenda items connected to meetings with committee reports")
        
        # Get additional meeting and committee info
        if meeting_ids:
            logging.info("Gathering additional meeting and committee information...")
            meeting_committee_info: List[Dict[str, Any]] = self.shared_db.execute_query(
                queries.get_meeting_committee_info_query(meeting_ids_string))
            
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
        results: List[Dict[str, Any]] = self.eva_db.execute_query(
            queries.get_action_to_agenda_items_query())
        self.counts[COUNT_AGENDA_ITEM_ACTIONS] = len(results)
        self.data[KEY_ACTION_TO_AGENDA_ITEMS] = results
        logging.info(f"Gathered {len(results)} action to agenda items.")

    def gather_published_agenda_items(self) -> None:
        logging.info("Gathering CommitteeReportPublishedItems...")
        published_items_results_from_query: List[Dict[str, Any]] = self.eva_db.execute_query(
            queries.get_published_items_query())
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
        committee_report_published_actions: List[Dict[str, Any]] = self.eva_db.execute_query(
            queries.get_published_actions_query()
        )
        self.counts[COUNT_PUBLISHED_AGENDA_ITEM_ACTIONS] = len(committee_report_published_actions)
        self.data[KEY_COMMITTEE_REPORT_PUBLISHED_ACTIONS] = committee_report_published_actions
        logging.info(f"Gathered {len(committee_report_published_actions)} CommitteeReportPublishedActions.")

    def gather_member_roll_calls(self) -> None:
        logging.info("Gathering member roll calls...")
        member_roll_calls: List[Dict[str, Any]] = self.eva_db.execute_query(
            queries.get_roll_call_query()
        )
        self.counts[COUNT_ROLL_CALLS] = len(member_roll_calls)
        self.data[KEY_MEMBER_ROLL_CALLS] = member_roll_calls
    
    def gather_committee_actions(self) -> None:
        logging.info("Gathering committee actions...")
        committee_actions: List[Dict[str, Any]] = self.eva_db.execute_query(
            queries.get_committee_actions_query()
        )
        self.counts[COUNT_COMMITTEE_ACTIONS] = len(committee_actions)
        self.data[KEY_COMMITTEE_ACTIONS] = committee_actions
        logging.info(f"Gathered {len(committee_actions)} committee actions.")

    def gather_all_data(self) -> None:
        self.connect_databases()
        try:
            self.gather_committee_actions()
            self.gather_committee_reports_and_agenda_items()
            self.gather_published_agenda_items()
            self.gather_action_to_agenda_items()
            self.gather_published_actions()
            self.gather_member_roll_calls()
            
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
    logs_dir: str = "./logs"
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.FileHandler(f"{logs_dir}/pre_debug_{current_time}.log"),
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
