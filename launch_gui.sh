#!/bin/bash
# Sidekick Screensaver GUI Launcher
# Ensures the GUI launches properly from the correct directory

echo "🎬 Launching Sidekick Screensaver GUI..."

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "📁 Working directory: $SCRIPT_DIR"

# Check for desktop environment
if [ -z "$DISPLAY" ] && [ -z "$WAYLAND_DISPLAY" ]; then
    echo "❌ No desktop environment detected!"
    echo "   This must be run from the physical Pi desktop, not SSH"
    exit 1
fi

# Launch the GUI
python3 screensaver_preferences.py

echo "✅ GUI closed"
