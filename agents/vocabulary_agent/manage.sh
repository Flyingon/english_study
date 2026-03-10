#!/bin/bash

# Configuration
AGENT_NAME="vocabulary_agent"
PID_FILE="agent.pid"
LOG_FILE="agent.log"
PYTHON_CMD="python3.13" # Adjust if needed
MODULE_PATH="main"

# Function to check if the agent is running
check_status() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        # Use kill -0 to check process existence without sending signal
        if kill -0 $PID 2>/dev/null; then
            echo "✅ Agent is running (PID: $PID)"
            return 0
        else
            echo "⚠️  PID file exists but process not found. Cleaning up..."
            rm "$PID_FILE"
            return 1
        fi
    else
        echo "⚪ Agent is not running."
        return 1
    fi
}

# Function to start the agent
start_agent() {
    if check_status > /dev/null; then
        echo "❌ Agent is already running."
        exit 1
    fi

    echo "🚀 Starting $AGENT_NAME..."
    
    # Ensure PYTHONPATH includes site-packages and current directory
    # Also include the project root so absolute imports (e.g. agents.vocabulary_agent...) work if needed, 
    # but since we moved everything inside, we might rely on relative imports or current dir.
    # We add ../.. to PYTHONPATH to allow imports from project root if necessary.
    export PYTHONPATH=$PYTHONPATH:/Users/zy.yuan/.local/lib/python3.13/site-packages:$(pwd):$(pwd)/../..
    
    # Unset SSLKEYLOGFILE to avoid permission error
    unset SSLKEYLOGFILE

    # Start in background
    nohup $PYTHON_CMD -m $MODULE_PATH > "$LOG_FILE" 2>&1 &
    
    PID=$!
    echo $PID > "$PID_FILE"
    
    echo "✅ Agent started with PID $PID"
    echo "📝 Logs are being written to $LOG_FILE"
    echo "🔗 API available at http://localhost:8091/docs"
}

# Function to stop the agent
stop_agent() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if kill -0 $PID 2>/dev/null; then
            echo "🛑 Stopping agent (PID: $PID)..."
            kill $PID
            rm "$PID_FILE"
            echo "✅ Agent stopped."
        else
            echo "⚠️  Process not found. Removing PID file."
            rm "$PID_FILE"
        fi
    else
        echo "⚪ Agent is not running."
    fi
}

# Function to restart the agent
restart_agent() {
    echo "🔄 Restarting agent..."
    stop_agent
    sleep 2
    start_agent
}

# Function to show logs
show_logs() {
    if [ -f "$LOG_FILE" ]; then
        echo "📄 Tailing logs (Ctrl+C to exit)..."
        tail -f "$LOG_FILE"
    else
        echo "❌ Log file not found."
    fi
}

# Main logic
case "$1" in
    start)
        start_agent
        ;;
    stop)
        stop_agent
        ;;
    restart)
        restart_agent
        ;;
    status)
        check_status
        ;;
    logs)
        show_logs
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs}"
        exit 1
        ;;
esac
