# Import the Active Directory module
Import-Module ActiveDirectory

# Define the AD Controller name
$ADController = "DeinADControllerName"    # change to your controller

# Get all sessions on the domain controller
$sessions = Get-WmiObject -Class Win32_LogonSession -ComputerName $ADController

# Filter for active logon sessions
$activeSessions = $sessions | Where-Object { $_.LogonType -eq 2 }

# Get the unique users from the active sessions
$uniqueUsers = $activeSessions | ForEach-Object {
    $user = Get-WmiObject -Class Win32_LoggedOnUser -Filter "LogonId = '$($_.LogonId)'" -ComputerName $ADController
    $user.Antecedent -match '\\(.+)$' | Out-Null
    $matches[1]
} | Select-Object -Unique

# Output the count of unique users
$uniqueUsersCount = $uniqueUsers.Count
Write-Output "0 AD_LoggedInUsers count=$uniqueUsersCount Anzahl der aktuell angemeldeten Benutzer: $uniqueUsersCount"
