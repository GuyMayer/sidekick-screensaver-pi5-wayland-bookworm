#!/bin/bash
# Sidekick Screensaver v4 GUI Launcher
# Test the new modern UI without affecting the current system

echo "🎬 Launching Sidekick Screensaver v4 (Modern UI Edition)..."

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

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found!"
    exit 1
fi

echo ""
echo "✨ NEW in v4.0:"
echo "   • Modern 2025 aesthetic with sidebar navigation"
echo "   • iOS-style toggle switches"
echo "   • Smooth sliders with real-time value display"
echo "   • Vibrant blue accent colors"
echo "   • Generous whitespace and elegant spacing"
echo ""
echo "📝 Note: This is a TEST version - your current settings are safe"
echo ""

# Launch the v4 GUI
python3 screensaver_preferences_v4.py

echo "✅ v4 GUI closed"
