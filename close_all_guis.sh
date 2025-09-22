#!/bin/bash
# close_screensaver_settings.sh - Close only screensaver settings windows before screensaver starts
# This script ensures a clean screensaver experience by closing only the settings GUI

echo "🗄️ Closing screensaver settings windows before screensaver..."

# List of screensaver-related applications to close (not all GUI apps!)
SCREENSAVER_APPS=(
    "screensaver_preferences.py"
    "screensaver_preferences.py"
)

# Method 1: Kill specific screensaver settings processes by name
echo "📱 Closing screensaver settings by process name..."
for app in "${SCREENSAVER_APPS[@]}"; do
    if pgrep -f "$app" >/dev/null 2>&1; then
        pkill -f "$app" 2>/dev/null
        echo "   🔸 Closed: $app"
    fi
done

# Method 2: Close screensaver settings windows using wmctrl (if available)
if command -v wmctrl >/dev/null 2>&1; then
    echo "🗄️ Closing screensaver settings windows using wmctrl..."

    # Keywords to identify screensaver settings windows ONLY
    SETTINGS_KEYWORDS=(
        "screensaver" "matrix preferences" "preferences"
    )

    # Get list of windows and close screensaver settings only
    wmctrl -l 2>/dev/null | while IFS= read -r line; do
        if [[ -n "$line" ]]; then
            window_id=$(echo "$line" | awk '{print $1}')
            window_title=$(echo "$line" | cut -d' ' -f4- | tr '[:upper:]' '[:lower:]')

            # Check if this is a screensaver settings window
            for keyword in "${SETTINGS_KEYWORDS[@]}"; do
                if [[ "$window_title" == *"$keyword"* ]]; then
                    if wmctrl -i -c "$window_id" 2>/dev/null; then
                        echo "   🔸 Closed settings window: $window_title"
                    fi
                    break
                fi
            done
        fi
    done
else
    echo "   ⚠️ wmctrl not available, skipping window-based cleanup"
fi

# Method 3: Close any remaining screensaver settings using xdotool (if available)
if command -v xdotool >/dev/null 2>&1; then
    echo "🖱️ Closing remaining screensaver settings windows using xdotool..."

    # Get all window IDs
    window_ids=$(xdotool search --name ".*" 2>/dev/null)

    if [[ -n "$window_ids" ]]; then
        echo "$window_ids" | while IFS= read -r wid; do
            if [[ -n "$wid" && "$wid" =~ ^[0-9]+$ ]]; then
                # Get window name
                window_name=$(xdotool getwindowname "$wid" 2>/dev/null | tr '[:upper:]' '[:lower:]')

                if [[ -n "$window_name" ]]; then
                    # Check if this is a screensaver settings window
                    for keyword in "${SETTINGS_KEYWORDS[@]}"; do
                        if [[ "$window_name" == *"$keyword"* ]]; then
                            if xdotool windowclose "$wid" 2>/dev/null; then
                                echo "   🔸 Closed xdotool window: $window_name"
                            fi
                            break
                        fi
                    done
                fi
            fi
        done
    fi
else
    echo "   ⚠️ xdotool not available, skipping xdotool cleanup"
fi

echo "✅ Screensaver settings cleanup completed!"

# Optional: Show remaining screensaver processes for debugging
if [[ "$1" == "--verbose" || "$1" == "-v" ]]; then
    echo ""
    echo "🔍 Remaining screensaver processes (for debugging):"
    for app in "${SCREENSAVER_APPS[@]}"; do
        if pgrep -f "$app" >/dev/null 2>&1; then
            echo "   ⚠️ Still running: $app"
        fi
    done
fi
