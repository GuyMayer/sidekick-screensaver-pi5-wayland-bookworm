#!/bin/bash
echo "Testing HDMI power management..."

echo "Current display status:"
export WAYLAND_DISPLAY=wayland-0
wlopm

echo ""
echo "Turning off display in 3 seconds..."
sleep 3
export WAYLAND_DISPLAY=wayland-0 && wlopm --off HDMI-A-1
echo "Display should be OFF now"

echo ""
echo "Waiting 5 seconds, then turning display back on..."
sleep 5
export WAYLAND_DISPLAY=wayland-0 && wlopm --on HDMI-A-1
echo "Display should be ON now"

echo ""
echo "Final display status:"
export WAYLAND_DISPLAY=wayland-0
wlopm
