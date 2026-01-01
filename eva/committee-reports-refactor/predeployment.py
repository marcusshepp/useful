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

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> Any:
        if isinstance(obj, (datetime.datetime, datetime.date)):
            return obj.isoformat()
        return super().default(obj)

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
            "member_roll_calls": [],
            "committee_action_to_agenda_items": [],
            "published_actions": [],
            "published_items": [],
            "removed_agenda_items": []
        }
        self.counts: Dict[str, int] = {
            "committee_reports": 0,
            "agenda_items": 0,
            "removed_agenda_items": 0,
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
        committee_reports: List[Dict[str, Any]] = self.eva_db.execute_query(query)
        
        for report in committee_reports:
            meeting_query: str = """
            SELECT 
                cm.MeetingDate,
                cm.MeetingTime,
                cm.MeetingLocation,
                c.CommitteeName
            FROM CommitteeMeeting cm
            JOIN CommitteeMeetingCommittee cmc ON cm.CommitteeMeetingID = cmc.CommitteeMeetingId
            JOIN Committee c ON cmc.CommitteeId = c.CommitteeID
            WHERE cm.CommitteeMeetingID = ? AND cmc.IsPrimary = 1
            """
            meeting_details: List[Dict[str, Any]] = self.shared_db.execute_query(meeting_query, (report["MeetingId"],))
            
            if meeting_details:
                report["MeetingDate"] = meeting_details[0]["MeetingDate"]
                report["MeetingTime"] = meeting_details[0]["MeetingTime"]
                report["MeetingLocation"] = meeting_details[0]["MeetingLocation"]
                report["CommitteeName"] = meeting_details[0]["CommitteeName"]
            
            if "PublishedReportDocument" in report and report["PublishedReportDocument"]:
                report["PublishedReportDocument"] = "BINARY_DATA"
            if "PublishedAttendanceReportDocument" in report and report["PublishedAttendanceReportDocument"]:
                report["PublishedAttendanceReportDocument"] = "BINARY_DATA"
            
            self.data["committee_reports"].append(report)
        
        self.counts["committee_reports"] = len(committee_reports)
        logging.info(f"Gathered {self.counts['committee_reports']} committee reports")

    def gather_member_roll_calls(self) -> None:
        query: str = """
        SELECT 
            Id,
            SessionId,
            CommitteeId,
            MeetingId,
            MemberId,
            AgendaItemId,
            RoleCallVote,  -- Ensure this matches the actual column name in the database
            PublishedDate,
            AddendaDate,
            PublishedBy,
            CreatedBy,
            Created,
            Modified,
            ModifiedBy
        FROM CommitteeMemberRollCalls
        """
        roll_calls: List[Dict[str, Any]] = self.eva_db.execute_query(query)
        
        # Check if we need to handle a column name discrepancy
        if roll_calls and "RoleCallVote" in roll_calls[0] and "RollCallVote" not in roll_calls[0]:
            # Normalize the column name to maintain consistency throughout the code
            for roll_call in roll_calls:
                roll_call["RollCallVote"] = roll_call.pop("RoleCallVote")
        
        published_roll_calls_count: int = 0
        for roll_call in roll_calls:
            member_query: str = """
            SELECT 
                p.FirstName + ' ' + p.LastName AS MemberName
            FROM CommitteeMember cm
            JOIN Provisional_UserProfile p ON cm.PersonId = p.PersonId
            WHERE cm.CommitteeMemberID = ?
            """
            member_details: List[Dict[str, Any]] = self.shared_db.execute_query(member_query, (roll_call["MemberId"],))
            
            if member_details:
                roll_call["MemberName"] = member_details[0]["MemberName"]
            else:
                roll_call["MemberName"] = f"Unknown Member {roll_call['MemberId']}"
                
            self.data["member_roll_calls"].append(roll_call)
            
            if roll_call["PublishedDate"] is not None:
                published_roll_calls_count += 1
            
        self.counts["roll_calls"] = len(roll_calls)
        self.counts["published_roll_calls"] = published_roll_calls_count
        logging.info(f"Gathered {self.counts['roll_calls']} member roll calls, {self.counts['published_roll_calls']} published")

    def gather_action_to_agenda_items(self) -> None:
        query: str = """
        SELECT 
            Id,
            MeetingId,
            AgendaItemId,
            Sub,
            SortOrder,
            CommitteeReportCommitteeActionId,
            CustomReportOutAction,
            CustomRecommendedAction
        FROM CommitteeReportCommitteeActionToAgendaItems
        """
        actions: List[Dict[str, Any]] = self.eva_db.execute_query(query)
        self.data["committee_action_to_agenda_items"] = actions
        self.counts["agenda_item_actions"] = len(actions)
        logging.info(f"Gathered {self.counts['agenda_item_actions']} committee action to agenda items")

    def gather_published_actions(self) -> None:
        query: str = """
        SELECT 
            Id,
            MeetingId,
            AgendaItemId,
            Sub,
            SortOrder,
            CommitteeReportCommitteeActionId,
            CustomReportOutAction,
            CustomRecommendedAction
        FROM CommitteeReportPublishedActions
        """
        published_actions: List[Dict[str, Any]] = self.eva_db.execute_query(query)
        self.data["published_actions"] = published_actions
        self.counts["published_agenda_item_actions"] = len(published_actions)
        logging.info(f"Gathered {self.counts['published_agenda_item_actions']} published actions")

    def gather_published_items(self) -> None:
        query: str = """
        SELECT 
            Id,
            MeetingId,
            AgendaItemId,
            CreatedBy,
            Created,
            Modified,
            ModifiedBy
        FROM CommitteeReportPublishedItems
        """
        published_items: List[Dict[str, Any]] = self.eva_db.execute_query(query)
        self.data["published_items"] = published_items
        self.counts["published_agenda_items"] = len(published_items)
        logging.info(f"Gathered {self.counts['published_agenda_items']} published items")

    def gather_removed_agenda_items(self) -> None:
        query: str = """
        SELECT 
            MeetingId,
            AgendaItemId
        FROM CommitteeReportRemovedAgendaItems
        """
        removed_items: List[Dict[str, Any]] = self.eva_db.execute_query(query)
        self.data["removed_agenda_items"] = removed_items
        self.counts["removed_agenda_items"] = len(removed_items)
        logging.info(f"Gathered {self.counts['removed_agenda_items']} removed agenda items")

    def gather_agenda_items(self) -> None:
        logging.info("Gathering agenda items from shared database...")
        
        meeting_ids: List[int] = [report["MeetingId"] for report in self.data["committee_reports"]]
        
        if not meeting_ids:
            logging.warning("No meeting IDs found, skipping agenda items gathering")
            return
            
        batch_size: int = 500
        all_agenda_items: List[Dict[str, Any]] = []
        
        for i in range(0, len(meeting_ids), batch_size):
            batch: List[int] = meeting_ids[i:i+batch_size]
            placeholders: str = ','.join(['?' for _ in batch])
            
            query: str = f"""
            SELECT 
                cma.CommitteeMeetingAgendaItemID as Id,
                cma.CommitteeMeetingId as MeetingId,
                cma.LegislationId,
                cma.Description,
                cma.SortOrder,
                l.Identifier,
                l.Prefix
            FROM CommitteeMeetingAgendaItem cma
            LEFT JOIN Legislation l ON cma.LegislationId = l.LegislationID
            WHERE cma.CommitteeMeetingId IN ({placeholders})
            """
            
            batch_items: List[Dict[str, Any]] = self.shared_db.execute_query(query, tuple(batch))
            all_agenda_items.extend(batch_items)
            
        self.data["agenda_items"] = all_agenda_items
        self.counts["agenda_items"] = len(all_agenda_items)
        logging.info(f"Gathered {self.counts['agenda_items']} agenda items from shared database")

    def gather_attendance_records(self) -> None:
        logging.info("Gathering attendance records from shared database...")
        
        meeting_ids: List[int] = [report["MeetingId"] for report in self.data["committee_reports"]]
        
        if not meeting_ids:
            logging.warning("No meeting IDs found, skipping attendance records gathering")
            return
            
        batch_size: int = 500
        all_attendance_records: List[Dict[str, Any]] = []
        
        for i in range(0, len(meeting_ids), batch_size):
            batch: List[int] = meeting_ids[i:i+batch_size]
            placeholders: str = ','.join(['?' for _ in batch])
            
            query: str = f"""
            SELECT 
                cmar.CommitteeMeetingAttendanceRecordID as Id,
                cmar.CommitteeMeetingId as MeetingId,
                cmar.CommitteeMemberId as MemberId,
                cmar.AttendanceTypeId,
                p.FirstName + ' ' + p.LastName AS MemberName,
                cmar.LastModifiedBy as ModifiedBy,
                cmar.DateAdded as Created,
                cmar.LastModified as Modified
            FROM CommitteeMeetingAttendanceRecord cmar
            JOIN CommitteeMember cm ON cmar.CommitteeMemberId = cm.CommitteeMemberID
            JOIN Provisional_UserProfile p ON cm.PersonId = p.PersonId
            WHERE cmar.CommitteeMeetingId IN ({placeholders})
            """
            
            batch_records: List[Dict[str, Any]] = self.shared_db.execute_query(query, tuple(batch))
            all_attendance_records.extend(batch_records)
            
        self.data["attendance_records"] = all_attendance_records
        logging.info(f"Gathered {len(all_attendance_records)} attendance records from shared database")

    def gather_joint_committees(self) -> None:
        logging.info("Gathering joint committee information from shared database...")
        
        meeting_ids: List[int] = [report["MeetingId"] for report in self.data["committee_reports"]]
        
        if not meeting_ids:
            logging.warning("No meeting IDs found, skipping joint committee gathering")
            return
            
        batch_size: int = 500
        all_joint_committees: List[Dict[str, Any]] = []
        
        for i in range(0, len(meeting_ids), batch_size):
            batch: List[int] = meeting_ids[i:i+batch_size]
            placeholders: str = ','.join(['?' for _ in batch])
            
            query: str = f"""
            SELECT 
                cmc.CommitteeMeetingId as MeetingId,
                cmc.CommitteeId as JointCommitteeId,
                c.CommitteeName as JointCommitteeName,
                cmc.LastModifiedBy as ModifiedBy,
                cmc.DateAdded as Created,
                cmc.LastModified as Modified
            FROM CommitteeMeetingCommittee cmc
            JOIN Committee c ON cmc.CommitteeId = c.CommitteeID
            WHERE cmc.CommitteeMeetingId IN ({placeholders})
            AND cmc.IsPrimary = 0
            """
            
            batch_committees: List[Dict[str, Any]] = self.shared_db.execute_query(query, tuple(batch))
            all_joint_committees.extend(batch_committees)
            
        self.data["joint_committees"] = all_joint_committees
        logging.info(f"Gathered {len(all_joint_committees)} joint committees from shared database")

    def gather_all_data(self) -> None:
        self.connect_databases()
        try:
            self.gather_committee_reports()
            self.gather_member_roll_calls()
            self.gather_action_to_agenda_items()
            self.gather_published_actions()
            self.gather_published_items()
            self.gather_removed_agenda_items()
            self.gather_agenda_items()
            self.gather_attendance_records()
            self.gather_joint_committees()
            
            logging.info("=== PRE-DEPLOYMENT DATA COUNTS ===")
            logging.info(f"Committee Reports: {self.counts['committee_reports']}")
            logging.info(f"Agenda Items: {self.counts['agenda_items']}")
            logging.info(f"Removed Agenda Items: {self.counts['removed_agenda_items']}")
            logging.info(f"Published Agenda Items: {self.counts['published_agenda_items']}")
            logging.info(f"Roll Calls: {self.counts['roll_calls']}")
            logging.info(f"Published Roll Calls: {self.counts['published_roll_calls']}")
            logging.info(f"Agenda Item Actions: {self.counts['agenda_item_actions']}")
            logging.info(f"Published Agenda Item Actions: {self.counts['published_agenda_item_actions']}")
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
    log_format: str = "%(asctime)s - %(levelname)s - %(message)s"
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.FileHandler("migration_data_gathering.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )

def main() -> None:
    setup_logging()
    logging.info("Starting pre-deployment data gathering")
    
    eva_connection: str = os.getenv("EVA_DB_CONNECTION")
    shared_connection: str = os.getenv("SHARED_DB_CONNECTION")
    output_path: str = os.getenv("OUTPUT_PATH", "migration_data.json")
    
    if not eva_connection or not shared_connection:
        logging.error("Database connection strings not found in environment variables")
        sys.exit(1)
    
    gatherer: DataGatherer = DataGatherer(eva_connection, shared_connection)
    
    try:
        gatherer.gather_all_data()
        gatherer.save_to_json(output_path)
        logging.info("Pre-deployment data gathering completed successfully")
    except Exception as e:
        logging.error(f"Error during data gathering: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
