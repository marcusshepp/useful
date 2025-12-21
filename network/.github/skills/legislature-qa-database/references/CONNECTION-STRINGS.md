# Legislature (M2) Database Connection Strings

## Connection String Format

All connection strings use SQL Server authentication with `TrustServerCertificate=True`.

## Environment Details

### M2-QA Environment (Most Common)

-   **Server:** tvmwsqls01:1433
-   **Database:** Legislature
-   **User:** senate_dev_user
-   **Password:** ThisIsQA!
-   **Connection String:** `Data Source=tvmwsqls01,1433;Initial Catalog=Legislature;User=senate_dev_user;Password=ThisIsQA!;TrustServerCertificate=True`

### M2-DEMO Environment

-   **Server:** MLSQL-QA.lsb.legislature.mi.gov:1433
-   **Database:** Legislature
-   **User:** senate_qa_user
-   **Password:** Calz0neAndP0p!
-   **Connection String:** `Data Source=MLSQL-QA.lsb.legislature.mi.gov,1433;Initial Catalog=Legislature;User=senate_qa_user;Password=Calz0neAndP0p!;TrustServerCertificate=True`

### M2-UAT Environment

-   **Server:** MLSQL-SUP.lsb.legislature.mi.gov:1433
-   **Database:** Legislature
-   **User:** senate_sup_user
-   **Password:** HalJ0rdanF01ls!
-   **Connection String:** `Data Source=MLSQL-SUP.lsb.legislature.mi.gov,1433;Initial Catalog=Legislature;User=senate_sup_user;Password=HalJ0rdanF01ls!;TrustServerCertificate=True`

### M2-Local Development

-   **Server:** localhost:1433
-   **Database:** Legislature
-   **User:** senate_dev_user
-   **Password:** Password1!
-   **Connection String:** `Data Source=localhost,1433;Initial Catalog=Legislature;User=senate_dev_user;Password=Password1!;TrustServerCertificate=True`

## Module Location

Connection strings are configured in: `C:\Users\mshepherd\p\network\EvaSql.psm1`

## Usage

You don't need to use connection strings directly. Instead, use the PowerShell functions with M2 environments:

```powershell
# Uses M2-QA environment
Invoke-EvaSql -Query "SELECT @@VERSION" -Environment M2-QA

# Other M2 environments
Invoke-EvaSql -Query "SELECT @@VERSION" -Environment M2-DEMO
Invoke-EvaSql -Query "SELECT @@VERSION" -Environment M2-UAT
Invoke-EvaSql -Query "SELECT @@VERSION" -Environment M2-Local
```

## Important Notes

-   **M2-QA is on same server as Eva QA** (tvmwsqls01) but different database
-   **M2-DEMO and M2-UAT** use LSB servers (different domain)
-   **Database name is always "Legislature"** across all environments
-   **User credentials differ** between environments

## Difference from Eva Connections

| Aspect        | Eva Databases             | Legislature (M2) Databases       |
| ------------- | ------------------------- | -------------------------------- |
| Database Name | Eva_QA, Eva_DEMO, Eva_UAT | Legislature (same for all)       |
| QA Server     | tvmwsqls01                | tvmwsqls01 (same server!)        |
| DEMO Server   | uvmwsqls01                | MLSQL-QA.lsb.legislature.mi.gov  |
| UAT Server    | uvmwsqls01                | MLSQL-SUP.lsb.legislature.mi.gov |
| User (QA)     | EvaQAUser                 | senate_dev_user                  |

## Security Notes

-   Connection strings contain credentials - keep EvaSql.psm1 secure
-   M2 databases contain official legislative data
-   QA/DEMO/UAT are test environments
-   Always test queries in QA before other environments
