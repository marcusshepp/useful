#!/usr/bin/env python3
import os
import sys
import json
import logging
import datetime
import pyodbc
from dotenv import load_dotenv
import queries

load_dotenv()

class DatabaseConnector:
    def __init__(self, connection_string: str) -> None:
        self.connection_string: str = connection_string
        self.connection: pyodbc.Connection | None = None
        self.cursor: pyodbc.Cursor | None = None

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

    def execute_query(self, query: str, params: tuple | None = None) -> list[dict]:
        try:
            if not self.cursor:
                raise Exception("No database cursor available")
            
            param_log: str = str(params) if params else "None"
            logging.debug(f"Executing query with params: {param_log}")
                
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
                
            if self.cursor.description:
                columns: list[str] = [column[0] for column in self.cursor.description]
                results: list[dict] = []
                
                rows = self.cursor.fetchall()
                logging.debug(f"Query returned {len(rows)} rows")
                
                for row in rows:
                    results.append(dict(zip(columns, row)))
                
                # Debug check for Id column
                if results and "Id" in results[0]:
                    logging.debug(f"Query returned Id: {results[0]['Id']}")
                elif results:
                    logging.debug(f"Query result has no Id column. Available columns: {list(results[0].keys())}")
                    
                return results
            logging.debug("Query returned no results (no description)")
            return []
        except Exception as e:
            logging.error(f"Query execution error: {str(e)}\nQuery: {query}")
            if params:
                logging.error(f"Parameters: {params}")
            raise

    def execute_non_query(self, query: str, params: tuple | None = None) -> int:
        try:
            if not self.cursor:
                raise Exception("No database cursor available")
                
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
                
            self.connection.commit()
            return self.cursor.rowcount
        except Exception as e:
            if self.connection:
                self.connection.rollback()
            logging.error(f"Non-query execution error: {str(e)}\nQuery: {query}")
            raise

    def begin_transaction(self) -> None:
        if self.connection:
            self.connection.autocommit = False
            logging.info("Transaction started")

    def commit_transaction(self) -> None:
        if self.connection:
            self.connection.commit()
            self.connection.autocommit = True
            logging.info("Transaction committed")

    def rollback_transaction(self) -> None:
        if self.connection:
            self.connection.rollback()
            self.connection.autocommit = True
            logging.info("Transaction rolled back")

class DataRestorer:
    def __init__(self, eva_connection_string: str, shared_connection_string: str, json_file_path: str) -> None:
        self.eva_db: DatabaseConnector = DatabaseConnector(eva_connection_string)
        self.shared_db: DatabaseConnector = DatabaseConnector(shared_connection_string)
        self.json_file_path: str = json_file_path
        self.data: dict = {}
        self.committee_actions: dict = {}  
        self.meetings_without_agenda_items: set[int] = set() 
        self.pre_counts: dict[str, int] = {}
        self.post_counts: dict[str, int] = {
            "committee_reports": 0,
            "agenda_items": 0,
            "published_agenda_items": 0,
            "roll_calls": 0,
            "published_roll_calls": 0,
            "agenda_item_actions": 0,
            "published_agenda_item_actions": 0,
            "removed_agenda_items": 0
        }

    def load_json_data(self) -> None:
        try:
            with open(self.json_file_path, 'r') as f:
                self.data = json.load(f)
            
            self.pre_counts = self.data.get("counts", {})
            logging.info(f"Data loaded from {self.json_file_path}")
            
            # Validate required data is present
            required_keys: list[str] = [
                "committee_reports", 
                "committee_report_ids", 
                "member_roll_calls", 
                "committee_report_published_actions", 
                "published_items", 
                "committee_meeting_agenda_items",
                "action_to_agenda_items"
            ]
            
            for key in required_keys:
                if key not in self.data:
                    logging.warning(f"Required key '{key}' not found in JSON data")
                else:
                    logging.info(f"Found {len(self.data[key])} items for {key}")
            
            logging.info("=== PRE-DEPLOYMENT DATA COUNTS (FROM JSON) ===")
            for category, count in self.pre_counts.items():
                logging.info(f"{category.upper()}: {count}")
            
        except Exception as e:
            logging.error(f"Error loading JSON data: {str(e)}")
            raise

    def connect_databases(self) -> None:
        self.eva_db.connect()
        self.shared_db.connect()

    def close_databases(self) -> None:
        self.eva_db.close()
        self.shared_db.close()

    def load_committee_actions(self) -> None:
        logging.info("Loading CommitteeReportCommitteeActions reference data...")
        actions: list[dict] = self.eva_db.execute_query(
            queries.get_committee_actions_query())
        
        self.committee_actions = {action["Id"]: action for action in actions}
        logging.info(f"Loaded {len(actions)} committee actions for reference")

    def update_committee_reports(self) -> None:
        logging.info("Updating CommitteeReports table with meeting details...")
        committee_reports: list[dict] = self.data.get("committee_reports", [])
        
        updated_count: int = 0
        missing_meetings: set[int] = set()  

        for report in committee_reports:
            report_id: int = report.get("Id")
            meeting_id: int = report.get("MeetingId")
            
            if not meeting_id:
                logging.warning(f"Report ID {report_id} has no MeetingId, skipping update")
                continue
            
            # Get meeting details from shared database
            meeting_details: list[dict] = self.shared_db.execute_query(
                queries.get_meeting_details_query(), (meeting_id,))
            
            if not meeting_details:
                missing_meetings.add(meeting_id)
                continue            

            meeting: dict = meeting_details[0]
            
            # Update report with meeting details
            rows_updated: int = self.eva_db.execute_non_query(
                queries.update_committee_report_query(),
                (
                    meeting.get("MeetingDate"),
                    meeting.get("MeetingTime"),
                    meeting.get("MeetingLocation"),
                    report_id
                )
            )
            
            if rows_updated > 0:
                updated_count += 1
                logging.info(f"Updated CommitteeReport ID {report_id} with meeting details")
            else:
                logging.warning(f"Failed to update CommitteeReport ID {report_id}")
        
            if missing_meetings:
                logging.warning(
                        f"Found {len(missing_meetings)} meetings with missing details: \
                            {', '.join(map(str, missing_meetings))}")
        self.post_counts["committee_reports"] = updated_count
        logging.info(f"Updated {updated_count} committee reports with meeting details")

    def get_published_items_set(self) -> set[int]:
        logging.info("Creating set of published agenda item IDs...")
        published_items: list[dict] = self.data.get("published_items", [])
        published_item_ids: set[int] = {item.get("AgendaItemId") for item in published_items if item.get("AgendaItemId")}
        logging.info(f"Found {len(published_item_ids)} published agenda item IDs")
        return published_item_ids

    def get_legislation_details(self, legislation_ids: list[int]) -> dict:
        if not legislation_ids:
            return {}
            
        legislation_ids_str: str = ",".join(str(id) for id in legislation_ids if id)
        legislation_details: list[dict] = self.shared_db.execute_query(
            queries.get_legislation_details_query(legislation_ids_str))
        
        return {leg.get("LegislationID"): leg for leg in legislation_details}

    def insert_agenda_items(self) -> None:
        logging.info("Inserting data into CommitteeReportAgendaItems...")
        committee_reports: list[dict] = self.data.get("committee_reports", [])
        agenda_items: list[dict] = self.data.get("committee_meeting_agenda_items", [])
        published_item_ids: set[int] = self.get_published_items_set()
        
        # Group agenda items by meeting ID
        meeting_agenda_items: dict[int, list[dict]] = {}
        for item in agenda_items:
            meeting_id: int = item.get("CommitteeMeetingID")
            if meeting_id not in meeting_agenda_items:
                meeting_agenda_items[meeting_id] = []
            meeting_agenda_items[meeting_id].append(item)
        
        # Get unique legislation IDs for efficient lookup
        legislation_ids: list[int] = [item.get("LegislationID") for item in agenda_items if item.get("LegislationID")]
        legislation_details: dict = self.get_legislation_details(legislation_ids)
        
        inserted_count: int = 0
        published_count: int = 0
        meetings_without_items: set[tuple[int, int]] = set()
        
        for report in committee_reports:
            report_id: int = report.get("Id")
            meeting_id: int = report.get("MeetingId")
            
            if not meeting_id or meeting_id not in meeting_agenda_items:
                meetings_without_items.add((meeting_id, report_id))
                continue
            
            items: list[dict] = meeting_agenda_items[meeting_id]
            
            for item in items:
                agenda_item_id: int = item.get("CommitteeMeetingAgendaItemID")
                legislation_id: int | None = item.get("LegislationID")
                is_published: bool = agenda_item_id in published_item_ids
                
                prefix: str | None = None
                identifier: str | None = None
                
                # If we have legislation details, get prefix and identifier
                if legislation_id and legislation_id in legislation_details:
                    leg_details: dict = legislation_details[legislation_id]
                    prefix = leg_details.get("Prefix")
                    identifier = leg_details.get("Identifier")
                
                # Preserve original timestamps and user information
                date_added: datetime.datetime = item.get("DateAdded") 
                if date_added is None:
                    date_added = datetime.datetime.now()
                    
                last_modified: datetime.datetime = item.get("LastModified")
                if last_modified is None:
                    last_modified = datetime.datetime.now()
                    
                last_modified_by: str = item.get("LastModifiedBy")
                if last_modified_by is None or last_modified_by == "":
                    last_modified_by = ""
                    
                created_by: str = item.get("CreatedBy", last_modified_by)
                if created_by is None or created_by == "":
                    created_by = ""
                
                # Insert the agenda item
                result: int = self.eva_db.execute_non_query(
                    queries.insert_agenda_item_query(),
                    (
                        report_id,
                        agenda_item_id,
                        legislation_id,
                        prefix,
                        identifier,
                        item.get("Description"),
                        item.get("SortOrder", 0),
                        1 if is_published else 0,
                        created_by,
                        date_added,
                        last_modified,
                        last_modified_by
                    )
                )

                logging.info(f"Inserted agenda item: reportId: {report_id} agendaItemId: {agenda_item_id} legId: {legislation_id}")
                
                inserted_count += 1
                if is_published:
                    published_count += 1
        
        # Log all meetings without agenda items at once
        if meetings_without_items:
            logging.warning(f"Found {len(meetings_without_items)} meetings without agenda items")
            for meeting_id, report_id in meetings_without_items:
                logging.debug(f"No agenda items found for Meeting ID {meeting_id}, skipping report {report_id}")
        
        self.post_counts["agenda_items"] = inserted_count
        self.post_counts["published_agenda_items"] = published_count
        logging.info(f"Inserted {inserted_count} agenda items ({published_count} published)")

    def insert_actions(self) -> None:
        logging.info("Inserting data into CommitteeReportActions...")
        actions_to_agenda_items: list[dict] = self.data.get("action_to_agenda_items", [])
        published_actions: list[dict] = self.data.get("committee_report_published_actions", [])
        
        published_actions_set: set[tuple] = {
            (action.get("CommitteeReportCommitteeActionId"), action.get("AgendaItemId"))
            for action in published_actions
            if action.get("CommitteeReportCommitteeActionId") and action.get("AgendaItemId")
        }
        
        inserted_count: int = 0
        published_count: int = 0
        
        for action in actions_to_agenda_items:
            old_agenda_item_id: int = action.get("AgendaItemId")
            action_id: int | None = action.get("CommitteeReportCommitteeActionId")
            is_published: bool = (action_id, old_agenda_item_id) in published_actions_set
            
            agenda_items: list[dict] = self.get_agenda_items(old_agenda_item_id)
            if not agenda_items:
                continue
            
            action_rows: list[tuple] = self.prepare_action_rows(action, action_id)
            
            for agenda_item in agenda_items:
                new_agenda_item_id: int = agenda_item["Id"]
                for action_row in action_rows:
                    self.insert_action_row(new_agenda_item_id, action, action_row, is_published)
                    inserted_count += 1
                    if is_published:
                        published_count += 1
        
        self.post_counts["agenda_item_actions"] = inserted_count
        self.post_counts["published_agenda_item_actions"] = published_count
        logging.info(f"Inserted {inserted_count} actions ({published_count} published)")

    def get_agenda_items(self, old_agenda_item_id: int) -> list[dict]:
        agenda_items: list[dict] = self.eva_db.execute_query(
            queries.find_committee_report_agenda_item_query(),
            (old_agenda_item_id,)
        )
        
        if not agenda_items:
            logging.warning(f"No matching agenda item found for original ID {old_agenda_item_id}, skipping action")
        
        return agenda_items

    def prepare_action_rows(self, action: dict, action_id: int | None) -> list[tuple]:
        custom_recommended: str | None = action.get("CustomRecommendedAction")
        custom_report_out: str | None = action.get("CustomReportOutAction")
        
        has_custom_recommended: bool = custom_recommended is not None and custom_recommended != ""
        has_custom_report_out: bool = custom_report_out is not None and custom_report_out != ""
        
        action_rows: list[tuple] = []
        
        if has_custom_recommended and has_custom_report_out:
            action_rows.append((
                action_id,
                True,
                custom_recommended,
                None
            ))
            
            action_rows.append((
                action_id,
                False,
                None,
                custom_report_out
            ))
        else:
            action_rows.append((
                action_id,
                has_custom_recommended,
                custom_recommended,
                custom_report_out
            ))
        
        return action_rows

    def insert_action_row(self, new_agenda_item_id: int, action: dict, action_row: tuple, is_published: bool) -> None:
        row_action_id: int | None
        is_recommendation: bool
        custom_recommended: str | None
        custom_report_out: str | None
        
        row_action_id, is_recommendation, custom_recommended, custom_report_out = action_row
        
        action_text: str | None = self.determine_action_text(
                row_action_id, is_recommendation, custom_recommended, custom_report_out)
        
        is_recommendation_int: int = 1 if is_recommendation else 0
        is_published_int: int = 1 if is_published else 0
        
        self.eva_db.execute_non_query(
            queries.insert_action_query(),
            (
                new_agenda_item_id,
                row_action_id,
                action_text,
                action.get("Sub"),
                action.get("SortOrder", 0),
                is_recommendation_int,
                custom_recommended,
                custom_report_out,
                is_published_int,
                "",
                datetime.datetime.now(),
                datetime.datetime.now(),
                ""
            )
        )
        
        logging.info(f"Inserted CommitteeReportAction for agenda item {new_agenda_item_id}, published={is_published}, is_recommendation={is_recommendation}")

    def determine_action_text(
            self,
            action_id: int | None, 
            is_recommendation: bool, 
            custom_recommended: str | None, 
            custom_report_out: str | None) -> str | None:

        if action_id and action_id in self.committee_actions:
            return self.committee_actions[action_id].get("Description")
        
        if is_recommendation and custom_recommended:
            return custom_recommended
        
        if custom_report_out:
            return custom_report_out
        
        return None

    def insert_roll_calls(self) -> None:
        logging.info("Inserting data into CommitteeReportRollCalls...")
        roll_calls: list[dict] = self.data.get("member_roll_calls", [])
        
        inserted_count: int = 0
        published_count: int = 0
        
        for roll_call in roll_calls:
            old_agenda_item_id: int = roll_call.get("AgendaItemId")
            
            # Find the corresponding CommitteeReportAgendaItem
            agenda_items: list[dict] = self.eva_db.execute_query(
                queries.find_committee_report_agenda_item_query(),
                (old_agenda_item_id,)
            )
            
            if not agenda_items:
                logging.warning(f"No matching agenda item found for original ID {old_agenda_item_id}, skipping roll call")
                continue
            
            for agenda_item in agenda_items:
                new_agenda_item_id: int = agenda_item["Id"]
                is_published: bool = roll_call.get("PublishedDate") is not None
                
                # Insert the roll call
                self.eva_db.execute_non_query(
                    queries.insert_roll_call_query(),
                    (
                        roll_call.get("SessionId"),
                        roll_call.get("CommitteeId"),
                        roll_call.get("MeetingId"),
                        roll_call.get("MemberId"),
                        new_agenda_item_id,
                        roll_call.get("RoleCallVote"),
                        roll_call.get("PublishedDate"),
                        roll_call.get("AddendaDate"),
                        roll_call.get("PublishedBy"),
                        roll_call.get("CreatedBy", ""),
                        datetime.datetime.now(),
                        datetime.datetime.now(),
                        roll_call.get("ModifiedBy", "")
                    )
                )
                
                inserted_count += 1
                if is_published:
                    published_count += 1
                
                logging.info(f"Inserted CommitteeReportRollCall for agenda item {new_agenda_item_id}, published={is_published}")
        
        self.post_counts["roll_calls"] = inserted_count
        self.post_counts["published_roll_calls"] = published_count
        logging.info(f"Inserted {inserted_count} roll calls ({published_count} published)")

    def compare_counts(self) -> None:
        logging.info("=== DATA MIGRATION COMPARISON (POST vs PRE) ===")
        
        # Define the mappings between pre and post count categories
        count_mappings: dict[str, str] = {
            "committee_reports": "committee_reports",
            "agenda_items": "agenda_items",
            "published_agenda_items": "published_agenda_items",
            "roll_calls": "roll_calls",
            "published_roll_calls": "published_roll_calls",
            "agenda_item_actions": "agenda_item_actions",
            "published_agenda_item_actions": "published_agenda_item_actions",
            "removed_agenda_items": "removed_agenda_items"
        }
        
        for post_category, pre_category in count_mappings.items():
            pre_count: int = self.pre_counts.get(pre_category, 0)
            post_count: int = self.post_counts.get(post_category, 0)
            difference: int = post_count - pre_count
            
            status: str = "MATCHED" if post_count == pre_count else "MISMATCH"
            
            logging.info(f"{post_category.upper()}: PRE={pre_count}, POST={post_count}, DIFF={difference} - {status}")
            
            if post_count != pre_count:
                logging.warning(f"Count mismatch for {post_category}: expected {pre_count}, got {post_count}")
                
        total_pre: int = sum(self.pre_counts.get(pre_cat, 0) for pre_cat in count_mappings.values())
        total_post: int = sum(self.post_counts.get(post_cat, 0) for post_cat in count_mappings.keys())
        
        logging.info(f"TOTAL RECORDS: PRE={total_pre}, POST={total_post}, DIFF={total_post-total_pre}")

    def restore_all_data(self) -> None:
        self.connect_databases()
        try:
            self.eva_db.begin_transaction()
            
            self.load_json_data()
            self.load_committee_actions()
            self.update_committee_reports()
            self.insert_agenda_items()
            self.insert_actions()
            self.insert_roll_calls()
            
            self.eva_db.commit_transaction()
            
            logging.info("=== POST-DEPLOYMENT DATA COUNTS ===")
            for category, count in self.post_counts.items():
                logging.info(f"{category.upper()}: {count}")
            logging.info(f"MEETINGS_WITHOUT_AGENDA_ITEMS: {len(self.meetings_without_agenda_items)}")
            
            self.compare_counts()
            
            logging.info("All data restored successfully")
        except Exception as e:
            self.eva_db.rollback_transaction()
            logging.error(f"Error during data restoration: {str(e)}")
            raise
        finally:
            self.close_databases()

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
            logging.FileHandler(f"{logs_dir}/post_debug_{current_time}.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )

def main() -> None:
    setup_logging()
    logging.info("Starting post-deployment data restoration")
    
    eva_connection: str | None = os.getenv("EVA_DB_CONNECTION")
    shared_connection: str | None = os.getenv("SHARED_DB_CONNECTION")
    json_file_path: str | None = os.getenv("INPUT_PATH")
    
    if not json_file_path:
        files: list[str] = [f for f in os.listdir('.') if f.startswith('predeployment_') and f.endswith('.json')]
        if files:
            files.sort(reverse=True)  # Get the most recent file
            json_file_path = files[0]
            logging.info(f"Using most recent predeployment file: {json_file_path}")
        else:
            json_file_path = "migration_data.json"
            logging.warning(f"No predeployment file found, defaulting to {json_file_path}")
    
    if not eva_connection or not shared_connection:
        logging.error("Database connection strings not found in environment variables")
        sys.exit(1)
    
    if not os.path.exists(json_file_path):
        logging.error(f"JSON file not found at {json_file_path}")
        sys.exit(1)
    
    restorer: DataRestorer = DataRestorer(eva_connection, shared_connection, json_file_path)
    
    try:
        restorer.restore_all_data()
        logging.info("Post-deployment data restoration completed successfully")
    except Exception as e:
        logging.error(f"Error during data restoration: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
