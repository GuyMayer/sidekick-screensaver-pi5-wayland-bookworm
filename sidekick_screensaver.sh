#!/bin/bash
# sidekick_screensaver.sh - The Sidekick screensaver for Wayland
# The Python-based digital rain effect with stats and anti-burn-in

# Kill any existing screensaver processes
pkill -f "sidekick_widget.py" 2>/dev/null
pkill -f "mystify_widget.py" 2>/dev/null
pkill -f "slideshow_widget.py" 2>/dev/null
pkill -f "video_widget.py" 2>/dev/null
pkill -f "cvlc.*fullscreen" 2>/dev/null  # Kill any VLC instances from previous video screensaver

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

# Read screensaver settings from config file
CONFIG_FILE="$HOME/.config/screensaver/settings.json"
SCREENSAVER_TYPE="Matrix"  # Default to Matrix

if [ -f "$CONFIG_FILE" ]; then
    echo "📋 Reading config from: $CONFIG_FILE"

    # Check if screensaver is enabled
    ENABLED=$(grep -o '"enabled"[[:space:]]*:[[:space:]]*[^,}]*' "$CONFIG_FILE" | sed 's/.*: *//' | tr -d ' ')

    if [ "$ENABLED" = "false" ]; then
        echo "🚫 Screensaver disabled in config - exiting"
        exit 0
    fi

    # Determine screensaver type from mode flags
    VIDEO_MODE=$(grep -o '"video_mode"[[:space:]]*:[[:space:]]*[^,}]*' "$CONFIG_FILE" | sed 's/.*: *//' | tr -d ' ')
    SLIDESHOW_MODE=$(grep -o '"slideshow_mode"[[:space:]]*:[[:space:]]*[^,}]*' "$CONFIG_FILE" | sed 's/.*: *//' | tr -d ' ')
    MYSTIFY_MODE=$(grep -o '"mystify_mode"[[:space:]]*:[[:space:]]*[^,}]*' "$CONFIG_FILE" | sed 's/.*: *//' | tr -d ' ')
    MATRIX_MODE=$(grep -o '"matrix_mode"[[:space:]]*:[[:space:]]*[^,}]*' "$CONFIG_FILE" | sed 's/.*: *//' | tr -d ' ')

    # Priority order: Videos > Slideshow > Mystify > Matrix
    if [ "$VIDEO_MODE" = "true" ]; then
        SCREENSAVER_TYPE="Videos"
    elif [ "$SLIDESHOW_MODE" = "true" ]; then
        SCREENSAVER_TYPE="Slideshow"
    elif [ "$MYSTIFY_MODE" = "true" ]; then
        SCREENSAVER_TYPE="Mystify"
    elif [ "$MATRIX_MODE" = "true" ]; then
        SCREENSAVER_TYPE="Matrix"
    fi

    echo "📋 Screensaver type from config: $SCREENSAVER_TYPE"
else
    echo "⚠️ Config file not found at: $CONFIG_FILE"
    echo "⚠️ Using default: Matrix"
fi

# Launch the appropriate screensaver widget based on type
cd "$SCRIPT_DIR"

case "$SCREENSAVER_TYPE" in
    "Videos")
        echo "🎬 Starting Video Player Widget..."
        python3 video_widget.py &
        SIDEKICK_PID=$!
        echo "✅ Video player started with PID: $SIDEKICK_PID"
        ;;
    "Slideshow")
        echo "🖼️ Starting Slideshow Widget..."
        python3 slideshow_widget.py &
        SIDEKICK_PID=$!
        echo "✅ Slideshow widget started with PID: $SIDEKICK_PID"
        ;;
    "Mystify")
        echo "🌀 Starting Mystify Widget..."
        python3 mystify_widget.py &
        SIDEKICK_PID=$!
        echo "✅ Mystify widget started with PID: $SIDEKICK_PID"
        ;;
    "Matrix")
        echo "🟢💚 Starting Python Sidekick (Matrix) Widget..."
        python3 sidekick_widget.py &
        SIDEKICK_PID=$!
        echo "✅ Sidekick (Matrix) widget started with PID: $SIDEKICK_PID"
        ;;
    "None")
        echo "🚫 Screensaver disabled in config - exiting"
        exit 0
        ;;
    *)
        echo "⚠️ Unknown screensaver type: $SCREENSAVER_TYPE - defaulting to Matrix"
        python3 sidekick_widget.py &
        SIDEKICK_PID=$!
        echo "✅ Sidekick (Matrix) widget started with PID: $SIDEKICK_PID"
        ;;
esac

# Store the PID for later cleanup
echo $SIDEKICK_PID > /tmp/sidekick_screensaver.pid 2>/dev/null || true
