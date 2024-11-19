# Import the Active Directory module
Import-Module ActiveDirectory

# Get the replication status for all domain controllers
$replicationStatus = Get-ADReplicationFailure -Scope Forest

# Check if there are any replication failures
if ($replicationStatus.Count -eq 0) {
    Write-Output "0 AD_Replication_Status - All replications are successful."
} else {
    $failureCount = $replicationStatus.Count
    Write-Output "2 AD_Replication_Status count=$failureCount There are $failureCount replication failures."
}