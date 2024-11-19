# Define the URL of the local LibreSpeed server
$libreSpeedUrl = "http://localhost:3000/api/v1/speedtest"

# Perform the speed test
$response = Invoke-RestMethod -Uri $libreSpeedUrl -Method Get

# Extract the results
$downloadSpeed = $response.download
$uploadSpeed = $response.upload
$ping = $response.ping

# Output the results in Checkmk local check format
Write-Output "0 LibreSpeed_DownloadSpeed download=$downloadSpeed Download Speed: $downloadSpeed Mbps"
Write-Output "0 LibreSpeed_UploadSpeed upload=$uploadSpeed Upload Speed: $uploadSpeed Mbps"
Write-Output "0 LibreSpeed_Ping ping=$ping Ping: $ping ms"