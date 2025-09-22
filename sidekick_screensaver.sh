#!/bin/bash
# sidekick_screensaver.sh - The Sidekick screensaver for Wayland
# The Python-based digital rain effect with stats and anti-burn-in

# Kill any existing screensaver processes
pkill -f "sidekick_widget.py" 2>/dev/null
pkill -f "mystify_widget.py" 2>/dev/null
pkill -f "slideshow_widget.py" 2>/dev/null

# CLOSE ONLY SCREENSAVER SETTINGS GUI BEFORE SCREENSAVER STARTS
echo "🗄️ Closing screensaver settings windows..."

# List of screensaver-related applications to close
SCREENSAVER_APPS=(
    "screensaver_preferences.py"
    "screensaver_preferences.py"
)

# Close screensaver settings applications only
for app in "${SCREENSAVER_APPS[@]}"; do
    if pgrep -f "$app" >/dev/null 2>&1; then
        pkill -f "$app" 2>/dev/null
        echo "   🔸 Closed: $app"
    fi
done

# Close screensaver settings windows using wmctrl if available
if command -v wmctrl >/dev/null 2>&1; then
    echo "🗄️ Closing screensaver settings windows using wmctrl..."

    # Keywords to identify screensaver settings windows only
    SETTINGS_KEYWORDS=("screensaver" "matrix preferences" "preferences")

    # Get list of windows and close screensaver settings only
    wmctrl -l 2>/dev/null | while read line; do
        if [[ -n "$line" ]]; then
            window_id=$(echo "$line" | awk '{print $1}')
            window_title=$(echo "$line" | cut -d' ' -f4- | tr '[:upper:]' '[:lower:]')

            # Check if this is a screensaver settings window
            for keyword in "${SETTINGS_KEYWORDS[@]}"; do
                if [[ "$window_title" == *"$keyword"* ]]; then
                    wmctrl -i -c "$window_id" 2>/dev/null
                    echo "   🔸 Closed settings window: $window_title"
                    break
                fi
            done
        fi
    done
fi

echo "✅ Screensaver settings cleanup completed, starting Python sidekick widget..."

# Check if we're in a graphical environment
if [ -z "$DISPLAY" ] && [ -z "$WAYLAND_DISPLAY" ]; then
    echo "No display found"
    exit 1
fi

# Set up Wayland environment if needed
if [ -n "$WAYLAND_DISPLAY" ]; then
    export WAYLAND_DISPLAY=wayland-0
fi

# Get the script directory to find the Python widgets
SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"

# Launch the Python-based Sidekick widget directly
echo "🟢💚 Starting Python Sidekick Widget..."
cd "$SCRIPT_DIR"
python3 sidekick_widget.py &

# Store the PID for later cleanup
SIDEKICK_PID=$!
echo $SIDEKICK_PID > /tmp/sidekick_screensaver.pid 2>/dev/null || true

echo "✅ Sidekick widget started with PID: $SIDEKICK_PID"
