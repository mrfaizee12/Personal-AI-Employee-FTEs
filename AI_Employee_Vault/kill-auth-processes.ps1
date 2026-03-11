# Kill any stuck Python authentication processes
# Run this if port 8080 is busy

Write-Host "Stopping stuck authentication processes..." -ForegroundColor Yellow

# Find and kill Python processes with 'google' or 'auth' in command line
$processes = Get-CimInstance Win32_Process | Where-Object {
    $_.CommandLine -like '*google*' -or 
    $_.CommandLine -like '*auth*' -or
    ($_.ProcessName -eq 'python.exe' -and $_.CommandLine -like '*8080*')
}

if ($processes) {
    foreach ($proc in $processes) {
        Write-Host "Stopping PID $($proc.ProcessId): $($proc.CommandLine)" -ForegroundColor Red
        Stop-Process -Id $proc.ProcessId -Force
    }
    Write-Host "Done! You can now run authentication." -ForegroundColor Green
} else {
    Write-Host "No stuck processes found." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Now run:" -ForegroundColor Cyan
Write-Host "  python mcp_servers\email_mcp.py --authenticate" -ForegroundColor White
