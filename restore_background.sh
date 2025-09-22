#!/bin/bash
# restore_background.sh - Restore desktop background if lost

echo "🖼️ Restoring desktop background..."

# Common background locations on Raspberry Pi
BACKGROUND_PATHS=(
    "/usr/share/pixmaps/raspberry-pi-logo.png"
    "/usr/share/pixmaps/debian-blue.svg"
    "/usr/share/rpd-wallpaper/temple.jpg"
    "/usr/share/rpd-wallpaper/road.jpg"
    "/home/pi/Pictures/*"
    "/home/guy/Pictures/*"
)

# Try to find and set a background
for bg_path in "${BACKGROUND_PATHS[@]}"; do
    if ls $bg_path 1> /dev/null 2>&1; then
        echo "📷 Found background: $bg_path"
        # Set background using pcmanfm
        pcmanfm --set-wallpaper="$bg_path" 2>/dev/null
        echo "✅ Background restored"
        exit 0
    fi
done

# If no background found, try using the LXDE default
if command -v pcmanfm >/dev/null 2>&1; then
    pcmanfm --wallpaper-mode=stretch 2>/dev/null
    echo "✅ Default background mode set"
else
    echo "⚠️ Could not restore background - pcmanfm not available"
fi
