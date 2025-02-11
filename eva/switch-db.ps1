#  Sets up your API to point to QA
#  Used for debugging purposes
#  Use with caution, if the migrations between local and qa are out of sync,
#  The world will burn.
#  
#  Example:
#  ./switch-db.ps1 local
#  ./switch-db.ps1 qa
#
# Marcus Shepherd
# 11/08/24

if ($args[0] -ne "qa" -and $args[0] -ne "local") {
    write-host "Error: Use either qa or local as arguments"
}

# Project path
$APP_SETTINGS = "C:\Users\mshepherd\p\LegBone\EvaAPI\appsettings.development.json"

# Connection strings for Eva DB
$LOCAL_HOST_DB_CONNECTION_EVA = "Data Source=127.0.0.1,1433;Initial Catalog=Eva;User ID=SA;Password=Password1!"
$QA_DB_CONNECTION_EVA = "Data Source=tvmwsqls01,1433;Initial Catalog=Eva_QA;User ID=EvaQAUser;Password=eva4eva"

# Connection strings for shared DB
$LOCAL_HOST_DB_CONNECTION_SHARED = "Data Source=127.0.0.1,1433;Initial Catalog=Legislature;User=senate_dev_user;Password=Password1!"
$QA_DB_CONNECTION_SHARED = "Data Source=tvmwsqls01,1433;Initial Catalog=Legislature;User=senate_dev_user;Password=ThisIsQA!"

if ($args[0] -eq "qa") {
    Write-Host "Setting to QA"

    (Get-Content $APP_SETTINGS).Replace($LOCAL_HOST_DB_CONNECTION_EVA, $QA_DB_CONNECTION_EVA) | Set-Content $APP_SETTINGS
    (Get-Content $APP_SETTINGS).Replace($LOCAL_HOST_DB_CONNECTION_SHARED, $QA_DB_CONNECTION_SHARED) | Set-Content $APP_SETTINGS
}

if ($args[0] -eq "local") {
    Write-Host "Setting to local"

    (Get-Content $APP_SETTINGS).Replace($QA_DB_CONNECTION_EVA, $LOCAL_HOST_DB_CONNECTION_EVA) | Set-Content $APP_SETTINGS
    (Get-Content $APP_SETTINGS).Replace($QA_DB_CONNECTION_SHARED, $LOCAL_HOST_DB_CONNECTION_SHARED) | Set-Content $APP_SETTINGS
}
