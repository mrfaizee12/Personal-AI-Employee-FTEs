#!/bin/bash
# Start File System Watcher for AI Employee
# Usage: ./start-watcher.sh [vault_path]

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

if [ -z "$1" ]; then
    echo "Starting File System Watcher..."
    echo "Watching: $SCRIPT_DIR"
    python watchers/filesystem_watcher.py .
else
    echo "Starting File System Watcher..."
    echo "Watching: $1"
    python watchers/filesystem_watcher.py "$1"
fi
