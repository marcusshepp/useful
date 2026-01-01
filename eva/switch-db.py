#!/usr/bin/env python3

"""
Database Connection Switcher
---------------------------

A utility script for switching database connections between local and QA environments.
Modifies appsettings.development.json to update connection strings.

WARNING: Use with caution. Mismatched migrations between environments can cause issues.

Usage:
    python switch_db.py local
    python switch_db.py qa

Environment Variables Required:
    EVA_LOCAL_PASSWORD: Password for local Eva database
    EVA_QA_PASSWORD: Password for QA Eva database
    SHARED_LOCAL_PASSWORD: Password for local Legislature database
    SHARED_QA_PASSWORD: Password for QA Legislature database

Author: Marcus Shepherd
Date: January 13, 2025
"""

import json
import os
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, Optional

class Environment(str, Enum):
    LOCAL = "local"
    QA = "qa"

    @classmethod
    def values(cls) -> list[str]:
        return [e.value for e in cls]

@dataclass
class DatabaseConfig:
    name: str
    local_connection: str
    qa_connection: str
    local_password_env: str
    qa_password_env: str

class ConnectionSwitcher:
    def __init__(self, config_path: Path):
        self.config_path = config_path
        self.databases = {
            "Eva": DatabaseConfig(
                name="Eva",
                local_connection="Data Source=127.0.0.1,1433;Initial Catalog=Eva;User ID=SA;Password={password}",
                qa_connection="Data Source=tvmwsqls01,1433;Initial Catalog=Eva_QA;User ID=EvaQAUser;Password={password}",
                local_password_env="EVA_LOCAL_PASSWORD",
                qa_password_env="EVA_QA_PASSWORD"
            ),
            "Legislature": DatabaseConfig(
                name="Legislature",
                local_connection="Data Source=127.0.0.1,1433;Initial Catalog=Legislature;User=senate_dev_user;Password={password}",
                qa_connection="Data Source=tvmwsqls01,1433;Initial Catalog=Legislature;User=senate_dev_user;Password={password}",
                local_password_env="SHARED_LOCAL_PASSWORD",
                qa_password_env="SHARED_QA_PASSWORD"
            )
        }

    def _get_password(self, env_var: str) -> str:
        """Get password from environment variable with error handling."""
        password = os.getenv(env_var)
        if not password:
            raise ValueError(f"Missing environment variable: {env_var}")
        return password

    def _load_config(self) -> Dict:
        """Load the appsettings.development.json file."""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON in config file: {self.config_path}")

    def _save_config(self, config: Dict) -> None:
        """Save the modified config back to file."""
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)

    def _get_connection_string(self, db_config: DatabaseConfig, env: Environment) -> str:
        """Generate connection string for specified environment."""
        if env == Environment.LOCAL:
            password = self._get_password(db_config.local_password_env)
            return db_config.local_connection.format(password=password)
        else:
            password = self._get_password(db_config.qa_password_env)
            return db_config.qa_connection.format(password=password)

    def switch_environment(self, target_env: Environment) -> None:
        """Switch database connections to specified environment."""
        print(f"Switching to {target_env.upper()} environment...")
        
        config = self._load_config()
        
        # Get the ConnectionStrings section
        conn_strings = config.get("ConnectionStrings")
        if not conn_strings:
            raise ValueError("No ConnectionStrings section found in config file")

        # Update connection strings for each database
        for db_name, db_config in self.databases.items():
            if db_name not in conn_strings:
                print(f"Warning: {db_name} connection string not found in config")
                continue

            new_connection = self._get_connection_string(db_config, target_env)
            conn_strings[db_name] = new_connection
            print(f"Updated {db_name} connection string")

        self._save_config(config)
        print(f"Successfully switched to {target_env.upper()} environment")

def main() -> None:
    if len(sys.argv) != 2 or sys.argv[1].lower() not in Environment.values():
        print(f"Error: Please specify environment: {' or '.join(Environment.values())}")
        print(f"Usage: {sys.argv[0]} <environment>")
        sys.exit(1)

    config_path = Path.home() / "p" / "LegBone" / "EvaAPI" / "appsettings.development.json"
    target_env = Environment(sys.argv[1].lower())

    try:
        switcher = ConnectionSwitcher(config_path)
        switcher.switch_environment(target_env)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
