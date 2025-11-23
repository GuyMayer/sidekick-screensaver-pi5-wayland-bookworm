#!/bin/bash
# restore_desktop.sh - Restore desktop environment and taskbar after screensaver

echo "🖥️ Restoring desktop environment..."

# Detect display server type
if [ -n "$WAYLAND_DISPLAY" ]; then
    echo "🌊 Detected Wayland display server"
    DISPLAY_TYPE="wayland"
elif [ -n "$DISPLAY" ]; then
    echo "🖼️ Detected X11 display server"
    DISPLAY_TYPE="x11"
else
    echo "❓ Unknown display server, assuming X11"
    DISPLAY_TYPE="x11"
fi

# Kill existing panels but preserve desktop background
pkill -f lxpanel 2>/dev/null

# Wait a moment
sleep 1

# Restart the desktop environment components
echo "🔄 Restarting LXDE components..."

# Start the panel (taskbar) with proper environment and suppress warnings
if [ "$DISPLAY_TYPE" = "wayland" ]; then
    # For Wayland, suppress GDK warnings and run in background
    echo "🌊 Starting panel for Wayland (suppressing compatibility warnings)..."
    (GDK_BACKEND=wayland WAYLAND_DISPLAY="$WAYLAND_DISPLAY" lxpanel 2>/dev/null &)
else
    # For X11
    DISPLAY="$DISPLAY" lxpanel &
fi
echo "✅ Panel (taskbar) restarted"

# Only restart desktop manager if it's not running (preserve background)
if ! pgrep -f "pcmanfm.*desktop" >/dev/null; then
    if [ "$DISPLAY_TYPE" = "wayland" ]; then
        echo "🌊 Starting desktop manager for Wayland..."
        (GDK_BACKEND=wayland WAYLAND_DISPLAY="$WAYLAND_DISPLAY" pcmanfm --desktop 2>/dev/null &)
    else
        DISPLAY="$DISPLAY" pcmanfm --desktop &
    fi
    echo "✅ Desktop manager restarted"
else
    echo "✅ Desktop manager already running - background preserved"
fi

# Refresh the display (only for X11)
if [ "$DISPLAY_TYPE" = "x11" ] && command -v xrefresh >/dev/null 2>&1; then
    xrefresh 2>/dev/null
    echo "✅ Display refreshed"
elif [ "$DISPLAY_TYPE" = "wayland" ]; then
    echo "✅ Wayland display - using compositor refresh"
    # Try to refresh Wayland compositor if possible
    if command -v swaymsg >/dev/null 2>&1; then
        swaymsg reload 2>/dev/null || true
    fi
fi

# Show desktop (only for X11)
if [ "$DISPLAY_TYPE" = "x11" ] && command -v wmctrl >/dev/null 2>&1; then
    wmctrl -k on 2>/dev/null
    echo "✅ Desktop brought to front"
elif [ "$DISPLAY_TYPE" = "wayland" ]; then
    echo "✅ Wayland desktop - compositor manages windows"
fi

# Give components time to initialize
sleep 0.5

echo "✅ Desktop environment restoration complete!"
echo "ℹ️ Note: Compatibility warnings between Wayland/X11 are normal and can be ignored"
