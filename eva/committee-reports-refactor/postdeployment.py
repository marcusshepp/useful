#!/usr/bin/env python3
import os
import sys
import json
import logging
import datetime
from typing import Dict, List, Any, Optional, Tuple, Set
import pyodbc
from dotenv import load_dotenv

load_dotenv()

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
                
            if self.cursor.description:
                columns = [column[0] for column in self.cursor.description]
                results = []
                
                for row in self.cursor.fetchall():
                    results.append(dict(zip(columns, row)))
                    
                return results
            return []
        except Exception as e:
            logging.error(f"Query execution error: {str(e)}\nQuery: {query}")
            raise

    def execute_non_query(self, query: str, params: Optional[Tuple] = None) -> int:
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
    def __init__(self, eva_connection_string: str, json_file_path: str) -> None:
        self.eva_db: DatabaseConnector = DatabaseConnector(eva_connection_string)
        self.json_file_path: str = json_file_path
        self.data: Dict[str, Any] = {}
        self.agenda_item_mapping: Dict[Tuple[int, int], int] = {}
        self.report_id_mapping: Dict[int, int] = {}
        self.pre_counts: Dict[str, int] = {}
        self.post_counts: Dict[str, int] = {
            "committee_reports": 0,
            "agenda_items": 0,
            "removed_agenda_items": 0,
            "published_agenda_items": 0,
            "roll_calls": 0,
            "published_roll_calls": 0,
            "agenda_item_actions": 0,
            "published_agenda_item_actions": 0
        }

    def load_json_data(self) -> None:
        try:
            with open(self.json_file_path, 'r') as f:
                self.data = json.load(f)
            
            self.pre_counts = self.data.get("counts", {})
            logging.info(f"Data loaded from {self.json_file_path}")
            
            logging.info("=== PRE-DEPLOYMENT DATA COUNTS (FROM JSON) ===")
            logging.info(f"Committee Reports: {self.pre_counts.get('committee_reports', 0)}")
            logging.info(f"Agenda Items: {self.pre_counts.get('agenda_items', 0)}")
            logging.info(f"Removed Agenda Items: {self.pre_counts.get('removed_agenda_items', 0)}")
            logging.info(f"Published Agenda Items: {self.pre_counts.get('published_agenda_items', 0)}")
            logging.info(f"Roll Calls: {self.pre_counts.get('roll_calls', 0)}")
            logging.info(f"Published Roll Calls: {self.pre_counts.get('published_roll_calls', 0)}")
            logging.info(f"Agenda Item Actions: {self.pre_counts.get('agenda_item_actions', 0)}")
            logging.info(f"Published Agenda Item Actions: {self.pre_counts.get('published_agenda_item_actions', 0)}")
            
        except Exception as e:
            logging.error(f"Error loading JSON data: {str(e)}")
            raise

    def connect_database(self) -> None:
        self.eva_db.connect()

    def close_database(self) -> None:
        self.eva_db.close()

    def update_committee_reports(self) -> None:
        logging.info("Updating CommitteeReports table with additional fields...")
        count: int = 0
        
        for report in self.data.get("committee_reports", []):
            report_id: int = report.get("Id")
            meeting_id: int = report.get("MeetingId") 
            committee_name: str = report.get("CommitteeName", "")
            meeting_date: str = report.get("MeetingDate", "")
            meeting_location: str = report.get("MeetingLocation", "")
            meeting_time: str = report.get("MeetingTime", "")
            
            if not meeting_date:
                meeting_date = "1900-01-01"
                
            query: str = """
            UPDATE CommitteeReports 
            SET MeetingDate = ?, MeetingLocation = ?, MeetingTime = ? 
            WHERE Id = ?
            """
            
            params: Tuple = (meeting_date, meeting_location, meeting_time, report_id)
            rows_affected: int = self.eva_db.execute_non_query(query, params)
            
            if rows_affected > 0:
                count += 1
                self.report_id_mapping[meeting_id] = report_id
            else:
                logging.warning(f"Committee report with ID {report_id} not found during update")
                
        logging.info(f"Updated {count} committee reports with additional fields")
        self.post_counts["committee_reports"] = count

    def insert_agenda_items(self) -> None:
        logging.info("Inserting data into CommitteeReportAgendaItems...")
        
        # Create quick lookup sets using tuples of (MeetingId, AgendaItemId)
        published_item_ids: Set[Tuple[int, int]] = set()
        for item in self.data.get("published_items", []):
            meeting_id: int = item.get("MeetingId")
            agenda_item_id: int = item.get("AgendaItemId")
            if meeting_id and agenda_item_id:
                published_item_ids.add((meeting_id, agenda_item_id))
        
        removed_item_ids: Set[Tuple[int, int]] = set()
        for item in self.data.get("removed_agenda_items", []):
            meeting_id: int = item.get("MeetingId")
            agenda_item_id: int = item.get("AgendaItemId")
            if meeting_id and agenda_item_id:
                removed_item_ids.add((meeting_id, agenda_item_id))
        
        logging.info(f"Found {len(published_item_ids)} published items and {len(removed_item_ids)} removed items")
        
        # Organize agenda items by meeting for easier processing
        all_agenda_items_by_meeting: Dict[int, List[Dict[str, Any]]] = {}
        for item in self.data.get("agenda_items", []):
            meeting_id: int = item["MeetingId"]
            if meeting_id not in all_agenda_items_by_meeting:
                all_agenda_items_by_meeting[meeting_id] = []
            all_agenda_items_by_meeting[meeting_id].append(item)
        
        count: int = 0
        published_count: int = 0
        removed_count: int = 0
        
        for meeting_id, report_id in self.report_id_mapping.items():
            meeting_agenda_items: List[Dict[str, Any]] = all_agenda_items_by_meeting.get(meeting_id, [])
            
            for item in meeting_agenda_items:
                original_id: int = item.get("Id")
                is_published: bool = (meeting_id, original_id) in published_item_ids
                is_removed: bool = (meeting_id, original_id) in removed_item_ids
                
                # Log flagged items for debugging
                if is_published:
                    logging.info(f"Flagging item as published: Meeting ID {meeting_id}, Agenda Item ID {original_id}")
                if is_removed:
                    logging.info(f"Flagging item as removed: Meeting ID {meeting_id}, Agenda Item ID {original_id}")
                
                query: str = """
                INSERT INTO CommitteeReportAgendaItems 
                (ReportId, Prefix, Identifier, Description, SortOrder, LegislationId,
                IsPublished, IsRemoved, CreatedBy, Created, Modified, ModifiedBy) 
                OUTPUT INSERTED.Id
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, GETDATE(), GETDATE(), ?)
                """
                
                params: Tuple = (
                    report_id, 
                    item.get("Prefix", ""),
                    item.get("Identifier", ""),
                    item.get("Description", ""),
                    item.get("SortOrder", 0),
                    item.get("LegislationId"),
                    is_published,
                    is_removed,
                    "MigrationScript",
                    "MigrationScript"
                )
                
                result: List[Dict[str, Any]] = self.eva_db.execute_query(query, params)
                if result and len(result) > 0:
                    new_id: int = result[0]["Id"]
                    self.agenda_item_mapping[(meeting_id, original_id)] = new_id
                    count += 1
                    
                    if is_published:
                        published_count += 1
                    if is_removed:
                        removed_count += 1
        
        logging.info(f"Inserted {count} agenda items")
        logging.info(f"Published agenda items: {published_count}")
        logging.info(f"Removed agenda items: {removed_count}")
        self.post_counts["agenda_items"] = count
        self.post_counts["published_agenda_items"] = published_count
        self.post_counts["removed_agenda_items"] = removed_count

    def insert_attendance_records(self) -> None:
        logging.info("Inserting data into CommitteeReportAttendance...")
        count: int = 0
        
        for record in self.data.get("attendance_records", []):
            meeting_id: int = record.get("MeetingId")
            report_id: int = self.report_id_mapping.get(meeting_id)
            
            if not report_id:
                logging.warning(f"No report found for meeting ID {meeting_id}, skipping attendance record")
                continue
                
            query: str = """
            INSERT INTO CommitteeReportAttendance 
            (ReportId, MemberId, MemberName, AttendanceTypeId, CreatedBy, Created, Modified, ModifiedBy) 
            VALUES (?, ?, ?, ?, ?, GETDATE(), GETDATE(), ?)
            """
            
            params: Tuple = (
                report_id,
                record.get("MemberId"),
                record.get("MemberName", ""),
                record.get("AttendanceTypeId"),
                record.get("CreatedBy", "MigrationScript"),
                record.get("ModifiedBy", "MigrationScript")
            )
            
            rows_affected: int = self.eva_db.execute_non_query(query, params)
            if rows_affected > 0:
                count += 1
                
        logging.info(f"Inserted {count} attendance records")

    def insert_joint_committees(self) -> None:
        logging.info("Inserting data into CommitteeReportJointCommittees...")
        count: int = 0
        
        for committee in self.data.get("joint_committees", []):
            meeting_id: int = committee.get("MeetingId")
            report_id: int = self.report_id_mapping.get(meeting_id)
            
            if not report_id:
                logging.warning(f"No report found for meeting ID {meeting_id}, skipping joint committee")
                continue
                
            query: str = """
            INSERT INTO CommitteeReportJointCommittees 
            (ReportId, JointCommitteeId, JointCommitteeName, CreatedBy, Created, Modified, ModifiedBy) 
            VALUES (?, ?, ?, ?, GETDATE(), GETDATE(), ?)
            """
            
            params: Tuple = (
                report_id,
                committee.get("JointCommitteeId"),
                committee.get("JointCommitteeName", ""),
                committee.get("CreatedBy", "MigrationScript"),
                committee.get("ModifiedBy", "MigrationScript")
            )
            
            rows_affected: int = self.eva_db.execute_non_query(query, params)
            if rows_affected > 0:
                count += 1
                
        logging.info(f"Inserted {count} joint committees")

    def insert_actions(self) -> None:
        logging.info("Inserting data into CommitteeReportActions...")
        
        # Combine both unpublished and published actions into a single collection
        action_items: List[Dict[str, Any]] = self.data.get("committee_action_to_agenda_items", [])
        published_actions: List[Dict[str, Any]] = self.data.get("published_actions", [])
        
        all_actions: List[Dict[str, Any]] = []
        
        # Process unpublished actions
        for item in action_items:
            all_actions.append({
                "MeetingId": item.get("MeetingId"),
                "AgendaItemId": item.get("AgendaItemId"),
                "ActionText": item.get("CustomReportOutAction", ""),
                "ActionSubText": item.get("Sub", ""),
                "CommitteeReportCommitteeActionId": item.get("CommitteeReportCommitteeActionId"),
                "IsPublished": False
            })
        
        # Process published actions
        for item in published_actions:
            all_actions.append({
                "MeetingId": item.get("MeetingId"),
                "AgendaItemId": item.get("AgendaItemId"),
                "ActionText": item.get("CustomReportOutAction", ""),
                "ActionSubText": item.get("Sub", ""),
                "CommitteeReportCommitteeActionId": item.get("CommitteeReportCommitteeActionId"),
                "IsPublished": True
            })
        
        logging.info(f"Total actions to process: {len(all_actions)}")
        
        count: int = 0
        published_count: int = 0
        skipped_count: int = 0
        
        for action in all_actions:
            meeting_id: int = action.get("MeetingId")
            original_agenda_id: int = action.get("AgendaItemId")
            new_agenda_id: int = self.agenda_item_mapping.get((meeting_id, original_agenda_id))
            is_published: bool = action.get("IsPublished", False)
            
            if not new_agenda_id:
                logging.warning(f"No new agenda item ID found for meeting ID {meeting_id} and agenda item ID {original_agenda_id}, skipping action")
                skipped_count += 1
                continue
            
            query: str = """
            INSERT INTO CommitteeReportActions 
            (AgendaItemId, CommitteeReportAgendaItemActionId, ActionText, ActionSubText, IsPublished, 
            CreatedBy, Created, Modified, ModifiedBy) 
            VALUES (?, ?, ?, ?, ?, 'MigrationScript', GETDATE(), GETDATE(), 'MigrationScript')
            """
            
            params: Tuple = (
                new_agenda_id,
                action.get("CommitteeReportCommitteeActionId"),
                action.get("ActionText", ""),
                action.get("ActionSubText", ""),
                is_published
            )
            
            try:
                rows_affected: int = self.eva_db.execute_non_query(query, params)
                if rows_affected > 0:
                    count += 1
                    if is_published:
                        published_count += 1
            except Exception as e:
                logging.error(f"Error inserting action for agenda item {new_agenda_id}: {str(e)}")
                skipped_count += 1
        
        logging.info(f"Inserted {count} action records, {published_count} published, {skipped_count} skipped")
        self.post_counts["agenda_item_actions"] = count
        self.post_counts["published_agenda_item_actions"] = published_count

    def insert_roll_calls(self) -> None:
        logging.info("Inserting data into CommitteeReportRollCalls...")
        count: int = 0
        published_count: int = 0
        skipped_count: int = 0
        error_count: int = 0
        
        # Create a report of mappings for debugging
        for (meeting_id, agenda_id), new_id in list(self.agenda_item_mapping.items())[:10]:
            logging.info(f"Agenda item mapping sample: ({meeting_id}, {agenda_id}) -> {new_id}")
        
        for roll_call in self.data.get("member_roll_calls", []):
            meeting_id: int = roll_call.get("MeetingId")
            original_agenda_id: int = roll_call.get("AgendaItemId")
            
            # Handle potential naming discrepancy for vote field
            roll_call_vote: str = ""
            if "RollCallVote" in roll_call:
                roll_call_vote = roll_call.get("RollCallVote", "")
            elif "RoleCallVote" in roll_call:
                roll_call_vote = roll_call.get("RoleCallVote", "")
            
            new_agenda_id: int = self.agenda_item_mapping.get((meeting_id, original_agenda_id))
            
            if not new_agenda_id:
                logging.warning(f"No new agenda item ID found for meeting ID {meeting_id} and agenda item ID {original_agenda_id}, skipping roll call")
                skipped_count += 1
                continue
                
            query: str = """
            INSERT INTO CommitteeReportRollCalls 
            (SessionId, CommitteeId, MeetingId, MemberId, AgendaItemId, RollCallVote, 
            PublishedDate, AddendaDate, PublishedBy, 
            CreatedBy, Created, Modified, ModifiedBy) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, GETDATE(), GETDATE(), ?)
            """
            
            params: Tuple = (
                roll_call.get("SessionId"),
                roll_call.get("CommitteeId"),
                roll_call.get("MeetingId"),
                roll_call.get("MemberId"),
                new_agenda_id,
                roll_call_vote,
                roll_call.get("PublishedDate"),
                roll_call.get("AddendaDate"),
                roll_call.get("PublishedBy", ""),
                roll_call.get("CreatedBy", "MigrationScript"),
                roll_call.get("ModifiedBy", "MigrationScript")
            )
            
            try:
                rows_affected: int = self.eva_db.execute_non_query(query, params)
                if rows_affected > 0:
                    count += 1
                    if roll_call.get("PublishedDate") is not None:
                        published_count += 1
            except Exception as e:
                logging.error(f"Error inserting roll call for agenda item {new_agenda_id}: {str(e)}")
                error_count += 1
                
        logging.info(f"Inserted {count} roll call records, {published_count} published")
        logging.info(f"Skipped {skipped_count} roll calls due to missing agenda item mapping")
        logging.info(f"Failed to insert {error_count} roll calls due to errors")
        
        self.post_counts["roll_calls"] = count
        self.post_counts["published_roll_calls"] = published_count

    def restore_all_data(self) -> None:
        self.connect_database()
        try:
            self.eva_db.begin_transaction()
            
            self.load_json_data()
            self.update_committee_reports()
            self.insert_agenda_items()
            self.insert_attendance_records()
            self.insert_joint_committees()
            self.insert_actions()
            self.insert_roll_calls()
            
            self.eva_db.commit_transaction()
            
            logging.info("=== POST-DEPLOYMENT DATA COUNTS ===")
            logging.info(f"Committee Reports: {self.post_counts['committee_reports']}")
            logging.info(f"Agenda Items: {self.post_counts['agenda_items']}")
            logging.info(f"Removed Agenda Items: {self.post_counts['removed_agenda_items']}")
            logging.info(f"Published Agenda Items: {self.post_counts['published_agenda_items']}")
            logging.info(f"Roll Calls: {self.post_counts['roll_calls']}")
            logging.info(f"Published Roll Calls: {self.post_counts['published_roll_calls']}")
            logging.info(f"Agenda Item Actions: {self.post_counts['agenda_item_actions']}")
            logging.info(f"Published Agenda Item Actions: {self.post_counts['published_agenda_item_actions']}")
            
            logging.info("=== DATA COMPARISON (POST vs PRE) ===")
            self.compare_counts()
            
            logging.info("All data restored successfully")
        except Exception as e:
            self.eva_db.rollback_transaction()
            logging.error(f"Error during data restoration: {str(e)}")
            raise
        finally:
            self.close_database()
            
    def compare_counts(self) -> None:
        categories: List[str] = [
            "committee_reports",
            "agenda_items",
            "removed_agenda_items",
            "published_agenda_items",
            "roll_calls",
            "published_roll_calls",
            "agenda_item_actions",
            "published_agenda_item_actions"
        ]
        
        for category in categories:
            pre_count: int = self.pre_counts.get(category, 0)
            post_count: int = self.post_counts.get(category, 0)
            difference: int = post_count - pre_count
            
            status: str = "MATCHED" if post_count == pre_count else "MISMATCH"
            
            logging.info(f"{category.upper()}: PRE={pre_count}, POST={post_count}, DIFF={difference} - {status}")
            
            if post_count != pre_count:
                logging.warning(f"Count mismatch for {category}: expected {pre_count}, got {post_count}")
                
        total_pre: int = sum(self.pre_counts.get(cat, 0) for cat in categories)
        total_post: int = sum(self.post_counts.get(cat, 0) for cat in categories)
        
        logging.info(f"TOTAL RECORDS: PRE={total_pre}, POST={total_post}, DIFF={total_post-total_pre}")

def setup_logging() -> None:
    log_format: str = "%(asctime)s - %(levelname)s - %(message)s"
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.FileHandler("migration_data_restoration.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )

def main() -> None:
    setup_logging()
    logging.info("Starting post-deployment data restoration")
    
    eva_connection: str = os.getenv("EVA_DB_CONNECTION")
    json_file_path: str = os.getenv("INPUT_PATH", "migration_data.json")
    
    if not eva_connection:
        logging.error("EVA database connection string not found in environment variables")
        sys.exit(1)
    
    if not os.path.exists(json_file_path):
        logging.error(f"JSON file not found at {json_file_path}")
        sys.exit(1)
    
    restorer: DataRestorer = DataRestorer(eva_connection, json_file_path)
    
    try:
        restorer.restore_all_data()
        logging.info("Post-deployment data restoration completed successfully")
    except Exception as e:
        logging.error(f"Error during data restoration: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
