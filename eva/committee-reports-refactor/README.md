COMMITTEE REPORT REFACTORING MIGRATION PROCESS

OVERVIEW
This document outlines the complete migration process for the Committee Report refactoring in the EVA database. The migration involves dropping several tables and creating new ones with a different schema structure, while ensuring no data is lost in the process.

REQUIREMENTS

1. Process Flow

   - Run pre-deployment data gathering script (pre_migration_data_script.py)
   - Deploy database changes and run EF migration
   - Run post-deployment data restoration script (post_migration_data_script.py)

2. Script Requirements
   - Connect to both EVA and Shared databases
   - Query all necessary data before tables are dropped
   - Organize data to match the new schema structure
   - Log all steps for troubleshooting
   - Be written clearly for easy iteration by LLMs or other developers
   - Handle errors gracefully
   - Contain no comments but be self-documenting

MIGRATION CONTEXT

The EF migration (CommitteeReportRefactor) is dropping the following tables:

- CommitteeMemberRollCalls
- CommitteeReportCommitteeActionToAgendaItems
- CommitteeReportPublishedActions
- CommitteeReportPublishedItems
- CommitteeReportRemovedAgendaItems

And creating new tables:

- CommitteeReportAgendaItems
- CommitteeReportAttendance
- CommitteeReportJointCommittees
- CommitteeReportActions
- CommitteeReportRollCalls

Additionally, the migration adds new columns to the CommitteeReports table:

- CommitteeName
- MeetingDate
- MeetingLocation
- MeetingTime

The goal is to transition the data from the old structure to the new one without data loss.

PRE-DEPLOYMENT DATA GATHERING SCRIPT

The pre-deployment script (pre_migration_data_script.py) performs the following functions:

1. Connects to both EVA and Shared databases
2. Extracts data from tables that will be dropped
3. Gathers additional context data from the Shared database
4. Organizes data to match the new schema structure
5. Saves all data as JSON for use by the post-deployment script

Script Components:

- DatabaseConnector: Manages database connections and query execution
- DateTimeEncoder: Custom JSON encoder for serializing datetime values
- DataGatherer: Main class containing methods to extract data from various tables
- gather_all_data(): Collects all required data in a single operation
- save_to_json(): Serializes the data to a JSON file

HOW TO USE THE PRE-DEPLOYMENT SCRIPT

1. Environment Setup
   Create a .env file with the following variables:

   ```
   EVA_DB_CONNECTION=your_eva_db_connection_string
   SHARED_DB_CONNECTION=your_shared_db_connection_string
   OUTPUT_PATH=path_to_output_json_file (default: migration_data.json)
   ```

2. Dependencies
   Install required Python packages:

   ```
   pip install pyodbc python-dotenv
   ```

3. Run the Script

   ```
   python pre_migration_data_script.py
   ```

4. Verify Output
   - Check the generated JSON file to ensure data was extracted correctly
   - Review the log file (migration_data_gathering.log) for any errors or warnings

POST-DEPLOYMENT DATA RESTORATION SCRIPT

The post-deployment script (post_migration_data_script.py) performs the following functions:

1. Connects to the EVA database
2. Loads the data from the JSON file created by the pre-deployment script
3. Updates existing CommitteeReports with additional fields
4. Inserts data into the new tables with appropriate relationships:
   - CommitteeReportAgendaItems
   - CommitteeReportAttendance
   - CommitteeReportJointCommittees
   - CommitteeReportActions
   - CommitteeReportRollCalls
5. Maintains relationships between tables using ID mappings
6. Handles the entire process in a single transaction for data consistency

Script Components:

- DatabaseConnector: Manages database connections and query execution with transaction support
- DataRestorer: Main class containing methods to restore data to the new schema
- restore_all_data(): Performs the entire data restoration process within a transaction

HOW TO USE THE POST-DEPLOYMENT SCRIPT

1. Environment Setup
   Create a .env file with the following variables:

   ```
   EVA_DB_CONNECTION=your_eva_db_connection_string
   INPUT_PATH=path_to_input_json_file (default: migration_data.json)
   ```

2. Dependencies
   Install required Python packages:

   ```
   pip install pyodbc python-dotenv
   ```

3. Run the Script

   ```
   python post_migration_data_script.py
   ```

4. Verify Results
   - Review the log file (migration_data_restoration.log) for any errors or warnings
   - Query the database to ensure all data was properly migrated

DATA RELATIONSHIPS IN THE NEW SCHEMA

The new schema establishes the following relationships:

- CommitteeReports is the main table
- CommitteeReportAgendaItems belongs to CommitteeReports (ReportId)
- CommitteeReportAttendance belongs to CommitteeReports (ReportId)
- CommitteeReportJointCommittees belongs to CommitteeReports (ReportId)
- CommitteeReportActions belongs to CommitteeReportAgendaItems (AgendaItemId)
- CommitteeReportRollCalls belongs to CommitteeReportAgendaItems (CommitteeReportAgendaItemId)

MAPPING OLD DATA TO NEW SCHEMA

The key data mappings made by the post-deployment script:

1. CommitteeMemberRollCalls → CommitteeReportRollCalls
2. CommitteeReportPublishedItems → CommitteeReportAgendaItems (with IsPublished = true)
3. CommitteeReportRemovedAgendaItems → CommitteeReportAgendaItems (with IsRemoved = true)
4. CommitteeReportCommitteeActionToAgendaItems & CommitteeReportPublishedActions → CommitteeReportActions

SPECIAL CONSIDERATIONS

1. Binary Data
   The CommitteeReports table contains binary data fields (PublishedReportDocument and PublishedAttendanceReportDocument). The pre-deployment script marks these with a placeholder, but does not alter the actual binary data in the database.

2. Performance
   For large databases, both scripts use batching to avoid memory issues or query size limits.

3. Transaction Management
   The post-deployment script uses a transaction to ensure data consistency during restoration.

4. Error Handling
   Both scripts include error handling to prevent data loss and log all operations.

5. ID Mapping
   The post-deployment script maintains mappings between old and new IDs to preserve relationships:
   - MeetingId to ReportId mapping
   - (MeetingId, AgendaItemId) to new CommitteeReportAgendaItemId mapping

COMPLETE MIGRATION WORKFLOW

1. Pre-Migration:

   - Back up the database
   - Run pre_migration_data_script.py to extract and save all data
   - Verify the JSON output contains all expected data

2. Migration:

   - Deploy database changes
   - Run Entity Framework migration

3. Post-Migration:

   - Run post_migration_data_script.py to restore data to new schema
   - Verify data integrity with queries

4. Validation:
   - Compare record counts between old and new tables
   - Spot-check specific records to ensure data integrity
   - Verify application functionality

VERIFICATION QUERIES

After migration, you can run the following queries to verify data integrity:

1. Compare Committee Report counts:

   ```sql
   SELECT COUNT(*) FROM CommitteeReports
   ```

2. Check agenda items:

   ```sql
   SELECT cr.Id AS ReportId, COUNT(crai.Id) AS AgendaItemCount
   FROM CommitteeReports cr
   LEFT JOIN CommitteeReportAgendaItems crai ON cr.Id = crai.ReportId
   GROUP BY cr.Id
   ```

3. Verify attendance records:

   ```sql
   SELECT cr.Id AS ReportId, COUNT(cra.Id) AS AttendanceCount
   FROM CommitteeReports cr
   LEFT JOIN CommitteeReportAttendance cra ON cr.Id = cra.ReportId
   GROUP BY cr.Id
   ```

4. Check roll calls:
   ```sql
   SELECT crai.Id AS AgendaItemId, COUNT(crrc.Id) AS RollCallCount
   FROM CommitteeReportAgendaItems crai
   LEFT JOIN CommitteeReportRollCalls crrc ON crai.Id = crrc.CommitteeReportAgendaItemId
   GROUP BY crai.Id
   ```

TROUBLESHOOTING

Common issues and solutions:

1. Missing Data:

   - Check log files for warnings about skipped records
   - Verify JSON file contains expected data
   - Check ID mappings in the post-deployment script

2. Foreign Key Violations:

   - Ensure data is inserted in the correct order
   - Check that all referenced IDs exist

3. Transaction Failures:

   - Transactions may fail if the database is large
   - Consider breaking the process into smaller transactions

4. Performance Issues:
   - For very large databases, modify scripts to process data in smaller batches

CONCLUSION

This document provides a comprehensive overview of the Committee Report refactoring migration process. Both scripts work together to ensure a seamless transition from the old schema to the new one without data loss. The pre-deployment script captures all necessary data before the schema changes, and the post-deployment script restores this data into the new schema structure.
