docker run -e "ACCEPT_EULA=Y" -e "MSSQL_SA_PASSWORD=Password1!" -p 1433:1433 --name evadb --hostname evadb mcr.microsoft.com/mssql/server:2022-latest
