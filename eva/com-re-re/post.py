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
    def __init__(self, connection_string):
        self.connection_string = connection_string
        self.connection = None
        self.cursor = None

    def connect(self):
        try:
            self.connection = pyodbc.connect(self.connection_string)
            self.cursor = self.connection.cursor()
            logging.info("Database connection established")
        except Exception as e:
            logging.error(f"Database connection error: {str(e)}")
            raise

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        logging.info("Database connection closed")

    def execute_query(self, query, params=None):
        try:
            if not self.cursor:
                raise Exception("No database cursor available")
            
            param_log = str(params) if params else "None"
            logging.debug(f"Executing query with params: {param_log}")
                
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
                
            if self.cursor.description:
                columns = [column[0] for column in self.cursor.description]
                results = []
                
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

    def execute_non_query(self, query, params=None):
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

    def begin_transaction(self):
        if self.connection:
            self.connection.autocommit = False
            logging.info("Transaction started")

    def commit_transaction(self):
        if self.connection:
            self.connection.commit()
            self.connection.autocommit = True
            logging.info("Transaction committed")

    def rollback_transaction(self):
        if self.connection:
            self.connection.rollback()
            self.connection.autocommit = True
            logging.info("Transaction rolled back")

class DataRestorer:
    def __init__(self, eva_connection_string, shared_connection_string, json_file_path):
        self.eva_db = DatabaseConnector(eva_connection_string)
        self.shared_db = DatabaseConnector(shared_connection_string)
        self.json_file_path = json_file_path
        self.data = {}
        self.agenda_item_mapping = {}  # Old AgendaItemId -> New AgendaItemId
        self.committee_actions = {}  # ActionId -> Action details
        self.pre_counts = {}
        self.post_counts = {
            "committee_reports": 0,
            "agenda_items": 0,
            "published_agenda_items": 0,
            "roll_calls": 0,
            "published_roll_calls": 0,
            "agenda_item_actions": 0,
            "published_agenda_item_actions": 0,
            "removed_agenda_items": 0
        }

    def load_json_data(self):
        try:
            with open(self.json_file_path, 'r') as f:
                self.data = json.load(f)
            
            self.pre_counts = self.data.get("counts", {})
            logging.info(f"Data loaded from {self.json_file_path}")
            
            # Validate required data is present
            required_keys = [
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

    def connect_databases(self):
        self.eva_db.connect()
        self.shared_db.connect()

    def close_databases(self):
        self.eva_db.close()
        self.shared_db.close()

    def load_committee_actions(self):
        logging.info("Loading CommitteeReportCommitteeActions reference data...")
        actions = self.eva_db.execute_query(
            queries.get_committee_actions_query())
        
        self.committee_actions = {action["Id"]: action for action in actions}
        logging.info(f"Loaded {len(actions)} committee actions for reference")

    def update_committee_reports(self):
        logging.info("Updating CommitteeReports table with meeting details...")
        committee_reports = self.data.get("committee_reports", [])
        
        updated_count = 0
        for report in committee_reports:
            report_id = report.get("Id")
            meeting_id = report.get("MeetingId")
            
            if not meeting_id:
                logging.warning(f"Report ID {report_id} has no MeetingId, skipping update")
                continue
            
            # Get meeting details from shared database
            meeting_details = self.shared_db.execute_query(
                queries.get_meeting_details_query(), (meeting_id,))
            
            if not meeting_details:
                logging.warning(f"No meeting details found for Meeting ID {meeting_id}, skipping update")
                continue
            
            meeting = meeting_details[0]
            
            # Update report with meeting details
            rows_updated = self.eva_db.execute_non_query(
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
        
        self.post_counts["committee_reports"] = updated_count
        logging.info(f"Updated {updated_count} committee reports with meeting details")

    def get_published_items_set(self):
        logging.info("Creating set of published agenda item IDs...")
        published_items = self.data.get("published_items", [])
        published_item_ids = {item.get("AgendaItemId") for item in published_items if item.get("AgendaItemId")}
        logging.info(f"Found {len(published_item_ids)} published agenda item IDs")
        return published_item_ids

    def get_legislation_details(self, legislation_ids):
        if not legislation_ids:
            return {}
            
        legislation_ids_str = ",".join(str(id) for id in legislation_ids if id)
        legislation_details = self.shared_db.execute_query(
            queries.get_legislation_details_query(legislation_ids_str))
        
        return {leg.get("LegislationID"): leg for leg in legislation_details}

    def insert_agenda_items(self):
        logging.info("Inserting data into CommitteeReportAgendaItems...")
        committee_reports = self.data.get("committee_reports", [])
        agenda_items = self.data.get("committee_meeting_agenda_items", [])
        published_item_ids = self.get_published_items_set()
        
        # Group agenda items by meeting ID
        meeting_agenda_items = {}
        for item in agenda_items:
            meeting_id = item.get("CommitteeMeetingID")
            if meeting_id not in meeting_agenda_items:
                meeting_agenda_items[meeting_id] = []
            meeting_agenda_items[meeting_id].append(item)
        
        # Get unique legislation IDs for efficient lookup
        legislation_ids = [item.get("LegislationID") for item in agenda_items if item.get("LegislationID")]
        legislation_details = self.get_legislation_details(legislation_ids)
        
        inserted_count = 0
        published_count = 0
        
        for report in committee_reports:
            report_id = report.get("Id")
            meeting_id = report.get("MeetingId")
            
            if not meeting_id or meeting_id not in meeting_agenda_items:
                logging.warning(f"No agenda items found for Meeting ID {meeting_id}, skipping report {report_id}")
                continue
            
            items = meeting_agenda_items[meeting_id]
            
            for item in items:
                agenda_item_id = item.get("CommitteeMeetingAgendaItemID")
                legislation_id = item.get("LegislationID")
                is_published = agenda_item_id in published_item_ids
                
                prefix = None
                identifier = None
                
                # If we have legislation details, get prefix and identifier
                if legislation_id and legislation_id in legislation_details:
                    leg_details = legislation_details[legislation_id]
                    prefix = leg_details.get("Prefix")
                    identifier = leg_details.get("Identifier")
                
                # Insert the agenda item and get the new ID
                result = self.eva_db.execute_query(
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
                        item.get("LastModifiedBy", "SYSTEM"),
                        datetime.datetime.now(),
                        datetime.datetime.now(),
                        item.get("LastModifiedBy", "SYSTEM")
                    )
                )

                logging.info(f"\
                        inserted agenda item: \
                        reportId: {report_id} \
                        agendaItemId: {agenda_item_id} \
                        legId: {legislation_id}")
                logging.info(f"After inserting agenda item\
                        we got {result} as a result")
                
                if not result or len(result) == 0:

                    logging.warning(
                            f"Failed to get new ID\
                                    for agenda item {agenda_item_id}")
                    continue
                    
                new_agenda_item_id = result[0]["Id"]
                
                # Store mapping for later use with actions and roll calls
                self.agenda_item_mapping[agenda_item_id] = new_agenda_item_id
                
                inserted_count += 1
                if is_published:
                    published_count += 1
                
                logging.info(f"Inserted CommitteeReportAgendaItem ID {new_agenda_item_id} for agenda item {agenda_item_id}, published={is_published}")
        
        self.post_counts["agenda_items"] = inserted_count
        self.post_counts["published_agenda_items"] = published_count
        logging.info(f"Inserted {inserted_count} agenda items ({published_count} published)")

    def insert_actions(self):
        logging.info("Inserting data into CommitteeReportActions...")
        actions_to_agenda_items = self.data.get("action_to_agenda_items", [])
        published_actions = self.data.get("committee_report_published_actions", [])
        
        # Create a set of published action/agenda item combinations
        published_actions_set = {
            (action.get("CommitteeReportCommitteeActionId"), action.get("AgendaItemId"))
            for action in published_actions
            if action.get("CommitteeReportCommitteeActionId") and action.get("AgendaItemId")
        }
        
        # Group actions by agenda item ID
        agenda_item_actions = {}
        for action in actions_to_agenda_items:
            agenda_item_id = action.get("AgendaItemId")
            if agenda_item_id not in agenda_item_actions:
                agenda_item_actions[agenda_item_id] = []
            agenda_item_actions[agenda_item_id].append(action)
        
        inserted_count = 0
        published_count = 0
        
        for old_agenda_item_id, actions in agenda_item_actions.items():
            if old_agenda_item_id not in self.agenda_item_mapping:
                logging.warning(f"No mapping found for agenda item ID {old_agenda_item_id}, skipping its actions")
                continue
            
            new_agenda_item_id = self.agenda_item_mapping[old_agenda_item_id]
            
            for action in actions:
                action_id = action.get("CommitteeReportCommitteeActionId")
                is_published = (action_id, old_agenda_item_id) in published_actions_set
                
                # Get action text from committee actions reference table
                action_text = None
                is_recommendation = False
                if action_id and action_id in self.committee_actions:
                    action_text = self.committee_actions[action_id].get("Description")
                    is_recommendation = self.committee_actions[action_id].get("IsRecommendation", False)
                
                # Insert the action
                result = self.eva_db.execute_query(
                    queries.insert_action_query(),
                    (
                        new_agenda_item_id,
                        action_id,
                        action_text,
                        action.get("Sub"),
                        action.get("SortOrder", 0),
                        1 if is_recommendation else 0,
                        action.get("CustomRecommendedAction"),
                        action.get("CustomReportOutAction"),
                        1 if is_published else 0,
                        "SYSTEM",
                        datetime.datetime.now(),
                        datetime.datetime.now(),
                        "SYSTEM"
                    )
                )
                
                if not result or len(result) == 0:
                    logging.warning(f"Failed to get new ID for action {action_id} on agenda item {new_agenda_item_id}")
                    continue
                    
                new_action_id = result[0]["Id"]
                
                inserted_count += 1
                if is_published:
                    published_count += 1
                
                logging.info(f"Inserted CommitteeReportAction ID {new_action_id} for agenda item {new_agenda_item_id}, published={is_published}")
        
        self.post_counts["agenda_item_actions"] = inserted_count
        self.post_counts["published_agenda_item_actions"] = published_count
        logging.info(f"Inserted {inserted_count} actions ({published_count} published)")

    def insert_roll_calls(self):
        logging.info("Inserting data into CommitteeReportRollCalls...")
        roll_calls = self.data.get("member_roll_calls", [])
        
        inserted_count = 0
        published_count = 0
        
        for roll_call in roll_calls:
            old_agenda_item_id = roll_call.get("AgendaItemId")
            
            if old_agenda_item_id not in self.agenda_item_mapping:
                logging.warning(f"No mapping found for agenda item ID {old_agenda_item_id}, skipping its roll call")
                continue
            
            new_agenda_item_id = self.agenda_item_mapping[old_agenda_item_id]
            is_published = roll_call.get("PublishedDate") is not None
            
            # Insert the roll call
            result = self.eva_db.execute_query(
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
                    roll_call.get("CreatedBy", "SYSTEM"),
                    datetime.datetime.now(),
                    datetime.datetime.now(),
                    roll_call.get("ModifiedBy", "SYSTEM")
                )
            )
            
            if not result or len(result) == 0:
                logging.warning(f"Failed to get new ID for roll call for member {roll_call.get('MemberId')} on agenda item {new_agenda_item_id}")
                continue
                
            new_roll_call_id = result[0]["Id"]
            
            inserted_count += 1
            if is_published:
                published_count += 1
            
            logging.info(f"Inserted CommitteeReportRollCall ID {new_roll_call_id} for agenda item {new_agenda_item_id}, published={is_published}")
        
        self.post_counts["roll_calls"] = inserted_count
        self.post_counts["published_roll_calls"] = published_count
        logging.info(f"Inserted {inserted_count} roll calls ({published_count} published)")

    def compare_counts(self):
        logging.info("=== DATA MIGRATION COMPARISON (POST vs PRE) ===")
        
        # Define the mappings between pre and post count categories
        count_mappings = {
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
            pre_count = self.pre_counts.get(pre_category, 0)
            post_count = self.post_counts.get(post_category, 0)
            difference = post_count - pre_count
            
            status = "MATCHED" if post_count == pre_count else "MISMATCH"
            
            logging.info(f"{post_category.upper()}: PRE={pre_count}, POST={post_count}, DIFF={difference} - {status}")
            
            if post_count != pre_count:
                logging.warning(f"Count mismatch for {post_category}: expected {pre_count}, got {post_count}")
                
        total_pre = sum(self.pre_counts.get(pre_cat, 0) for pre_cat in count_mappings.values())
        total_post = sum(self.post_counts.get(post_cat, 0) for post_cat in count_mappings.keys())
        
        logging.info(f"TOTAL RECORDS: PRE={total_pre}, POST={total_post}, DIFF={total_post-total_pre}")

    def restore_all_data(self):
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
            
            self.compare_counts()
            
            logging.info("All data restored successfully")
        except Exception as e:
            self.eva_db.rollback_transaction()
            logging.error(f"Error during data restoration: {str(e)}")
            raise
        finally:
            self.close_databases()

def setup_logging():
    current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_format = "%(asctime)s - %(levelname)s - %(message)s"
    logs_dir = "./logs"
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

def main():
    setup_logging()
    logging.info("Starting post-deployment data restoration")
    
    eva_connection = os.getenv("EVA_DB_CONNECTION")
    shared_connection = os.getenv("SHARED_DB_CONNECTION")
    json_file_path = os.getenv("INPUT_PATH")
    
    if not json_file_path:
        files = [f for f in os.listdir('.') if f.startswith('predeployment_') and f.endswith('.json')]
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
    
    restorer = DataRestorer(eva_connection, shared_connection, json_file_path)
    
    try:
        restorer.restore_all_data()
        logging.info("Post-deployment data restoration completed successfully")
    except Exception as e:
        logging.error(f"Error during data restoration: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
