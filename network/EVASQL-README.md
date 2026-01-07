# EvaSql PowerShell Module

PowerShell module for querying Eva and Legislature (M2) databases across multiple environments.

```
## Overview

This module provides two main functions for database operations:

-   `Invoke-EvaSql` - For SELECT queries that return data
-   `Invoke-EvaSqlNonQuery` - For INSERT, UPDATE, DELETE operations



```powershell
. c:\Users\mshepherd\p\useful\env-vars.ps1
$env:M2_QA_PASSWORD = $env:SHARED_QA_PASSWORD  # Set M2 password from shared password
```
