@echo off
REM Start File System Watcher for AI Employee
REM Usage: start-watcher.bat [vault_path]

cd /d "%~dp0"

if "%1"=="" (
    echo Starting File System Watcher...
    echo Watching: %CD%
    python watchers\filesystem_watcher.py .
) else (
    echo Starting File System Watcher...
    echo Watching: %1
    python watchers\filesystem_watcher.py %1
)

pause
