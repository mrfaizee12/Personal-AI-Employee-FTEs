# Stop Playwright MCP server
# Usage: .\stop-server.ps1 [port]

param(
    [int]$Port = 8808
)

$PidFile = "$env:TEMP\playwright-mcp-$Port.pid"

# Close browser first via MCP client
Write-Host "Closing browser..."
try {
    $Response = Invoke-WebRequest -Uri "http://localhost:$Port/mcp" -Method Post -ContentType "application/json" -Body '{"jsonrpc":"2.0","id":1,"method":"browser_close","params":{}}' -UseBasicParsing -ErrorAction SilentlyContinue
} catch {
    # Ignore errors - browser might already be closed
}

# Stop the process
if (Test-Path $PidFile) {
    $StoredPid = Get-Content $PidFile
    $Process = Get-Process -Id $StoredPid -ErrorAction SilentlyContinue
    if ($Process) {
        Write-Host "Stopping Playwright MCP (PID: $StoredPid)..."
        Stop-Process -Id $StoredPid -Force
        Write-Host "Playwright MCP stopped"
    } else {
        Write-Host "Process not running"
    }
    Remove-Item $PidFile -Force
} else {
    # Try to find by process name
    $Processes = Get-Process | Where-Object { $_.ProcessName -like "*node*" -and $_.CommandLine -like "*@playwright/mcp*" }
    if ($Processes) {
        foreach ($Proc in $Processes) {
            Write-Host "Stopping $($Proc.ProcessName) (PID: $($Proc.Id))..."
            Stop-Process -Id $Proc.Id -Force
        }
        Write-Host "Playwright MCP stopped"
    } else {
        Write-Host "No Playwright MCP process found"
    }
}
