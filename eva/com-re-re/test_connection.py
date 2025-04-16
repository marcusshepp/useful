#!/usr/bin/env python3
import os
import sys
import logging
from typing import Optional
import pyodbc
from dotenv import load_dotenv

class DatabaseConnectionTester:
    def __init__(self) -> None:
        self.eva_connection_string: Optional[str] = None
        self.shared_connection_string: Optional[str] = None
        self.setup_logging()
        self.load_environment_variables()

    def setup_logging(self) -> None:
        log_format: str = "%(asctime)s - %(levelname)s - %(message)s"
        logging.basicConfig(
            level=logging.INFO,
            format=log_format,
            handlers=[
                logging.StreamHandler(sys.stdout)
            ]
        )

    def load_environment_variables(self) -> None:
        load_dotenv()
        self.eva_connection_string = os.getenv("EVA_DB_CONNECTION")
        self.shared_connection_string = os.getenv("SHARED_DB_CONNECTION")
        
        if not self.eva_connection_string:
            logging.error("EVA_DB_CONNECTION not found in .env file")
        
        if not self.shared_connection_string:
            logging.error("SHARED_DB_CONNECTION not found in .env file")

    def test_connection(self, connection_string: str, db_name: str) -> bool:
        connection: Optional[pyodbc.Connection] = None
        
        try:
            logging.info(f"Testing connection to {db_name} database...")
            connection = pyodbc.connect(connection_string)
            cursor = connection.cursor()
            
            cursor.execute("SELECT @@VERSION")
            row = cursor.fetchone()
            logging.info(f"Successfully connected to {db_name} database")
            logging.info(f"Database version: {row[0]}")
            
            return True
            
        except Exception as e:
            logging.error(f"Failed to connect to {db_name} database: {str(e)}")
            return False
            
        finally:
            if connection:
                connection.close()
                logging.info(f"Connection to {db_name} database closed")

    def run_tests(self) -> None:
        eva_success: bool = False
        shared_success: bool = False
        
        if self.eva_connection_string:
            eva_success = self.test_connection(self.eva_connection_string, "EVA")
        
        if self.shared_connection_string:
            shared_success = self.test_connection(self.shared_connection_string, "SHARED")
        
        if eva_success and shared_success:
            logging.info("All database connections are working correctly!")
        else:
            logging.error("Some database connections failed. Please check your .env file.")
            sys.exit(1)

def main() -> None:
    tester: DatabaseConnectionTester = DatabaseConnectionTester()
    tester.run_tests()

if __name__ == "__main__":
    main()
