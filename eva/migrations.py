#!/usr/bin/env python3

"""
Eva Migration Manager
--------------------

This script manages Entity Framework migrations for the Eva project. It provides functionality to:
1. Update the database to a specific migration
2. Remove existing migrations
3. Checkout the model snapshot from develop branch
4. Add new migrations

Key Features:
- Interactive workflow for step-by-step migration management
- Automatic detection of previous migration for easy rollback
- Command-line arguments for direct operations
- Git integration for model snapshot management

Usage:
1. Interactive mode (no arguments):
   python migrate.py

2. Direct commands:
   - Update database: python migrate.py --update [MIGRATION_NAME]
   - Remove migration: python migrate.py --remove [COUNT]
   - Add migration: python migrate.py --add [MIGRATION_NAME]
   - Checkout snapshot: python migrate.py --checkout
   - Show git status: python migrate.py --st

The script will automatically suggest the previous migration when updating the database,
making it easier to rollback to the last known good state.

Author: Marcus Shepherd
Date: January 13, 2025
"""

import argparse
import os
import subprocess
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import Dict, Optional

PATH_TO_WORKING_DIRECTORY = "~/p/leb/EvaAPI"

EVA_ASCII = """
███████╗██╗   ██╗ █████╗ 
██╔════╝██║   ██║██╔══██╗
█████╗  ██║   ██║███████║
██╔══╝  ╚██╗ ██╔╝██╔══██║
███████╗ ╚████╔╝ ██║  ██║
╚══════╝  ╚═══╝  ╚═╝  ╚═╝
"""

class CommandType(Enum):
    UPDATE = auto()
    REMOVE = auto()
    CHECKOUT = auto()
    ADD = auto()

@dataclass
class MigrationCommand:
    description: str
    command_template: str
    success_message: str
    input_key: Optional[str] = None
    input_prompt: Optional[str] = None
    requires_confirmation: bool = True

class MigrationManager:
    def __init__(self, working_directory: str):
        self.working_directory: Path = Path(working_directory).expanduser()
        self.migrations_directory: Path = self.working_directory / "Migrations"
        self.commands: Dict[CommandType, MigrationCommand] = {
            CommandType.UPDATE: MigrationCommand(
                description="Update database to previous migration",
                command_template="dotnet ef database update {previous_migration} --context evadbcontext",
                success_message="Database Successfully Updated to Previous Migration! 🎉",
                input_key="previous_migration",
                input_prompt="Enter the name of the previous migration: "
            ),
            CommandType.REMOVE: MigrationCommand(
                description="Remove last migration(s)",
                command_template="dotnet ef migrations remove --context evadbcontext",
                success_message="Migration Successfully Removed! 🗑️"
            ),
            CommandType.CHECKOUT: MigrationCommand(
                description="Git checkout develop for the migration snapshot",
                command_template="git checkout develop -- .\\Migrations\\EvaDbContextModelSnapshot.cs",
                success_message="Model Snapshot Successfully Checked Out! 📥"
            ),
            CommandType.ADD: MigrationCommand(
                description="Add a new migration with a unique name",
                command_template="dotnet ef migrations add {new_migration} --context evadbcontext",
                success_message="New Migration Successfully Added! 🚀",
                input_key="new_migration",
                input_prompt="Enter the name for the new migration: "
            )
        }

    def get_previous_migration(self) -> Optional[str]:
        try:
            migration_files = [
                f for f in self.migrations_directory.glob("*.cs")
                if f.stem != "EvaDbContextModelSnapshot" and not f.stem.endswith(".Designer")
            ]
            
            if len(migration_files) < 2:
                return None
                
            # Sort by filename (which includes timestamp)
            sorted_files = sorted(migration_files, key=lambda x: x.stem)
            # Get second to last migration (previous one)
            previous_migration = sorted_files[-2].stem
            
            return previous_migration
            
        except Exception as e:
            print(f"Failed to get previous migration: {e}")
            return None

    def update_database_interactive(self, migration_name: Optional[str] = None) -> bool:
        previous_migration = self.get_previous_migration()
        
        if migration_name is None and previous_migration:
            print(f"Previous migration detected: {previous_migration}")
            if input("Update to this migration? (y/n): ").strip().lower() == 'y':
                migration_name = previous_migration
            else:
                migration_name = input(self.commands[CommandType.UPDATE].input_prompt).strip()
        elif migration_name is None:
            migration_name = input(self.commands[CommandType.UPDATE].input_prompt).strip()
            
        return self.execute_command(
            self.commands[CommandType.UPDATE].command_template,
            CommandType.UPDATE,
            {"previous_migration": migration_name}
        )

    def setup_working_directory(self) -> bool:
        try:
            if not self.working_directory.exists():
                print(f"Directory not found: {self.working_directory}")
                return False
            
            os.chdir(self.working_directory)
            return True
            
        except Exception as e:
            print(f"Failed to set working directory: {e}")
            return False

    def execute_command(self, command: str, command_type: CommandType, inputs: Dict[str, str]) -> bool:
        try:
            for key, value in inputs.items():
                command = command.replace(f"{{{key}}}", value)
            
            print(f"Executing: {command}")
            result = subprocess.run(
                command,
                shell=True,
                check=True,
                text=True,
                capture_output=True
            )
            
            if result.stdout:
                print(result.stdout)
            
            print("\n" + "=" * 50)
            print(f"✅ {self.commands[command_type].success_message}")
            print("=" * 50 + "\n")
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"Command failed: {e.stderr}")
            return False
        except Exception as e:
            print(f"Unexpected error: {e}")
            return False

    def show_git_status(self) -> None:
        try:
            result = subprocess.run(
                "git status",
                shell=True,
                check=True,
                text=True,
                capture_output=True
            )
            print("\nGit Status:")
            print(result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"Failed to get git status: {e.stderr}")

    def log_workflow_success(self) -> None:
        print("\n" + "=" * 50)
        print("✅ Workflow Completed Successfully! 🎉")
        print("=" * 50 + "\n")

    def run_interactive_workflow(self) -> None:
        success = True
        for command_type in CommandType:
            command = self.commands[command_type]
            print(f"\nStep: {command.description}")
            if input("Do you want to proceed? (y/n): ").strip().lower() == 'y':
                if command_type == CommandType.UPDATE:
                    if not self.update_database_interactive():
                        print(f"Failed at step: {command.description}")
                        success = False
                        break
                else:
                    inputs = {}
                    if command.input_key and command.input_prompt:
                        inputs[command.input_key] = input(command.input_prompt).strip()
                    
                    if not self.execute_command(command.command_template, command_type, inputs):
                        print(f"Failed at step: {command.description}")
                        success = False
                        break
        
        if success:
            self.show_git_status()
            self.log_workflow_success()

    def update_database(self, migration_name: Optional[str] = None) -> bool:
        return self.update_database_interactive(migration_name)

    def remove_migrations(self, count: int) -> bool:
        for _ in range(count):
            if not self.execute_command(
                self.commands[CommandType.REMOVE].command_template,
                CommandType.REMOVE,
                {}
            ):
                return False
        return True

    def add_migration(self, name: str) -> bool:
        return self.execute_command(
            self.commands[CommandType.ADD].command_template,
            CommandType.ADD,
            {"new_migration": name}
        )

    def checkout_snapshot(self) -> bool:
        return self.execute_command(
            self.commands[CommandType.CHECKOUT].command_template,
            CommandType.CHECKOUT,
            {}
        )

def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Entity Framework Migration Workflow Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--update",
        metavar="MIGRATION_NAME",
        help="Update database to a specific migration",
        nargs="?"
    )
    parser.add_argument(
        "--add",
        metavar="MIGRATION_NAME",
        help="Add a new migration with the specified name"
    )
    parser.add_argument(
        "--remove",
        type=int,
        metavar="COUNT",
        help="Remove specified number of migrations",
        nargs="?",
        const=1
    )
    parser.add_argument(
        "--checkout",
        "--co",
        action="store_true",
        help="Checkout model snapshot from develop branch"
    )
    parser.add_argument(
        "--st",
        action="store_true",
        help="Show git status after operation"
    )
    
    return parser.parse_args()

def main() -> None:
    print(EVA_ASCII)
    print("Welcome to the Eva Migration Manager! 🦴")
    print("Working Directory: ", PATH_TO_WORKING_DIRECTORY)
    
    args = parse_arguments()
    working_directory = os.path.expanduser(PATH_TO_WORKING_DIRECTORY)
    
    manager = MigrationManager(working_directory)
    
    if not manager.setup_working_directory():
        return

    if not any([args.update is not None, args.add, args.remove, args.checkout]):
        manager.run_interactive_workflow()
        return

    success = True

    if args.update is not None:
        if not manager.update_database(args.update):
            print("Failed to update database")
            success = False

    if args.add:
        if not manager.add_migration(args.add):
            print("Failed to add migration")
            success = False

    if args.remove is not None:
        if not manager.remove_migrations(args.remove):
            print("Failed to remove migrations")
            success = False

    if args.checkout:
        if not manager.checkout_snapshot():
            print("Failed to checkout snapshot")
            success = False

    if success and args.st:
        manager.show_git_status()

    if success:
        manager.log_workflow_success()

if __name__ == "__main__":
    main()
