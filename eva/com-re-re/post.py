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
            for category, count in self.pre_counts.items():
                logging.info(f"{category.upper()}: {count}")
            
        except Exception as e:
            logging.error(f"Error loading JSON data: {str(e)}")
            raise

    def connect_database(self) -> None:
        self.eva_db.connect()

    def close_database(self) -> None:
        self.eva_db.close()

    def update_committee_reports(self) -> None:
        logging.info("Updating CommitteeReports table with additional fields...")
        # TODO: Implement update logic for committee reports

    def insert_agenda_items(self) -> None:
        logging.info("Inserting data into CommitteeReportAgendaItems...")
        # TODO: Implement insert logic for agenda items

    def insert_attendance_records(self) -> None:
        logging.info("Inserting data into CommitteeReportAttendance...")
        # TODO: Implement insert logic for attendance records

    def insert_joint_committees(self) -> None:
        logging.info("Inserting data into CommitteeReportJointCommittees...")
        # TODO: Implement insert logic for joint committees

    def insert_actions(self) -> None:
        logging.info("Inserting data into CommitteeReportActions...")
        # TODO: Implement insert logic for actions

    def insert_roll_calls(self) -> None:
        logging.info("Inserting data into CommitteeReportRollCalls...")
        # TODO: Implement insert logic for roll calls

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
            for category, count in self.post_counts.items():
                logging.info(f"{category.upper()}: {count}")
            
            logging.info("=== DATA COMPARISON (POST vs PRE) ===")
            self.compare_counts()
            
            logging.info("All data restored successfully")
        except Exception as e:
            self.eva_db.rollback_transaction()
            logging.error(f"Error during data restoration: {str(e)}")
            raise
        finally:
            self.close_database()

def setup_logging() -> None:
    current_time: str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_format: str = "%(asctime)s - %(levelname)s - %(message)s"
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.FileHandler(f"post_debug_{current_time}.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )

def main() -> None:
    setup_logging()
    logging.info("Starting post-deployment data restoration")
    
    eva_connection: str | None = os.getenv("EVA_DB_CONNECTION")
    json_file_path: str | None = os.getenv("INPUT_PATH")
    
    if not json_file_path:
        files: List[str] = [f for f in os.listdir('.') if f.startswith('predeployment_') and f.endswith('.json')]
        if files:
            files.sort(reverse=True)  # Get the most recent file
            json_file_path = files[0]
            logging.info(f"Using most recent predeployment file: {json_file_path}")
        else:
            json_file_path = "migration_data.json"
            logging.warning(f"No predeployment file found, defaulting to {json_file_path}")
    
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
