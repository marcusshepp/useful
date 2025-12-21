# Eva Database Connection Strings

## Connection String Format

All connection strings use SQL Server authentication with `TrustServerCertificate=True`.

## Environment Details

### QA Environment

-   **Server:** tvmwsqls01:1433
-   **Database:** Eva_QA
-   **User:** EvaQAUser
-   **Password:** eva4eva
-   **Connection String:** `Data Source=tvmwsqls01,1433;Initial Catalog=Eva_QA;User ID=EvaQAUser;Password=eva4eva;TrustServerCertificate=True`

### DEMO Environment

-   **Server:** uvmwsqls01:1433
-   **Database:** Eva_DEMO
-   **User:** EvaDEMOUser
-   **Password:** evaDemo4eva
-   **Connection String:** `Data Source=uvmwsqls01,1433;Initial Catalog=Eva_DEMO;User ID=EvaDEMOUser;Password=evaDemo4eva;TrustServerCertificate=True`

### UAT Environment

-   **Server:** uvmwsqls01:1433
-   **Database:** Eva_UAT
-   **User:** EvaUATUser
-   **Password:** evaUATuser
-   **Connection String:** `Data Source=uvmwsqls01,1433;Initial Catalog=Eva_UAT;User ID=EvaUATUser;Password=evaUATuser;TrustServerCertificate=True`

### Local Development

-   **Server:** localhost:1433
-   **Database:** Eva
-   **User:** SA
-   **Password:** Password1!
-   **Connection String:** `Data Source=localhost,1433;Initial Catalog=Eva;User ID=SA;Password=Password1!;TrustServerCertificate=True`

## Module Location

Connection strings are configured in: `C:\Users\mshepherd\p\network\EvaSql.psm1`

## Usage

You don't need to use connection strings directly. Instead, use the PowerShell functions:

```powershell
# Uses QA by default
Invoke-EvaSql -Query "SELECT @@VERSION"

# Specify environment explicitly
Invoke-EvaSql -Query "SELECT @@VERSION" -Environment DEMO
Invoke-EvaSql -Query "SELECT @@VERSION" -Environment UAT
Invoke-EvaSql -Query "SELECT @@VERSION" -Environment Local
```

## Security Notes

-   Connection strings contain credentials - keep EvaSql.psm1 secure
-   Never commit real passwords to public repositories
-   QA/DEMO/UAT are test environments - credentials are for testing only
-   Local environment uses default SA password for development
