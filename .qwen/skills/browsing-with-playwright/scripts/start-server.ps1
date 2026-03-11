# Start Playwright MCP server for browser-use skill
# Usage: .\start-server.ps1 [port]

param(
    [int]$Port = 8808
)

$PidFile = "$env:TEMP\playwright-mcp-$Port.pid"

# Check if already running
if (Test-Path $PidFile) {
    $StoredPid = Get-Content $PidFile
    $Process = Get-Process -Id $StoredPid -ErrorAction SilentlyContinue
    if ($Process) {
        Write-Host "Playwright MCP already running on port $Port (PID: $StoredPid)"
        exit 0
    }
}

# Start server using npx.cmd (Windows compatible)
Write-Host "Starting Playwright MCP on port $Port..."

# Use npx.cmd instead of npx for Windows compatibility
$Process = Start-Process -FilePath "npx.cmd" `
    -ArgumentList "@playwright/mcp@latest", "--port", $Port, "--shared-browser-context" `
    -PassThru `
    -NoNewWindow

# Save PID
$Process.Id | Out-File -FilePath $PidFile -Encoding ascii

# Wait for startup
Start-Sleep -Seconds 3

# Verify it's running
$RunningProcess = Get-Process -Id $Process.Id -ErrorAction SilentlyContinue
if ($RunningProcess) {
    Write-Host "Playwright MCP started on port $Port (PID: $($Process.Id))"
    Write-Host ""
    Write-Host "To stop the server, run:"
    Write-Host "  .\stop-server.ps1"
    exit 0
} else {
    Write-Host "Failed to start Playwright MCP"
    Remove-Item $PidFile -Force
    exit 1
}
