@echo off
REM Start Orchestrator for AI Employee
REM Usage: start-orchestrator.bat [vault_path] [--continuous]

cd /d "%~dp0"

if "%1"=="" (
    set VAULT_PATH=.
) else (
    set VAULT_PATH=%1
)

if "%2"=="--continuous" (
    echo Starting Orchestrator in continuous mode...
    echo Vault: %VAULT_PATH%
    python orchestrator.py %VAULT_PATH% --continuous
) else (
    echo Running single orchestration cycle...
    echo Vault: %VAULT_PATH%
    python orchestrator.py %VAULT_PATH%
)

echo.
echo To process pending items with Qwen Code, run:
echo   qwen --cd "%CD%"

pause
