#!/bin/bash
# restore_taskbar_quiet.sh - Quietly restore just the taskbar

# Kill existing panel
pkill -f lxpanel 2>/dev/null

# Wait briefly
sleep 0.5

# Restart panel quietly (suppress all warnings)
if [ -n "$WAYLAND_DISPLAY" ]; then
    # Wayland with suppressed warnings
    GDK_BACKEND=wayland nohup lxpanel >/dev/null 2>&1 &
else
    # X11
    nohup lxpanel >/dev/null 2>&1 &
fi

echo "✅ Taskbar restored quietly"
