#!/bin/bash
# verify_installation.sh - Quick verification of Sidekick screensaver installation

echo "🔍 Sidekick Screensaver Installation Verification"
echo "=============================================="

# Check if files exist
echo "📁 Checking installed files..."
files_to_check=(
    "/home/guy/.local/bin/sidekick_widget.py"
    "/home/guy/.local/bin/screensaver_preferences.py"
    "/home/guy/.local/bin/restore_desktop.sh"
    "/home/guy/.local/bin/restore_taskbar_quiet.sh"
    "/home/guy/.local/bin/screensaver-prefs"
)

for file in "${files_to_check[@]}"; do
    if [ -f "$file" ] || [ -L "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file (missing)"
    fi
done

# Check dependencies
echo ""
echo "🔧 Checking dependencies..."
deps_to_check=(
    "python3"
    "lxpanel"
    "pcmanfm"
)

for dep in "${deps_to_check[@]}"; do
    if command -v "$dep" >/dev/null 2>&1; then
        echo "✅ $dep"
    else
        echo "❌ $dep (not found)"
    fi
done

# Check Python modules
echo ""
echo "🐍 Checking Python modules..."
python_modules=(
    "PyQt6.QtWidgets"
    "psutil"
)

for module in "${python_modules[@]}"; do
    if python3 -c "import $module" 2>/dev/null; then
        echo "✅ $module"
    else
        echo "❌ $module (not available)"
    fi
done

# Test taskbar restoration
echo ""
echo "🖥️ Testing taskbar restoration..."
if /home/guy/.local/bin/restore_taskbar_quiet.sh; then
    echo "✅ Taskbar restoration working"
else
    echo "❌ Taskbar restoration failed"
fi

echo ""
echo "🎉 Installation verification complete!"
echo "🚀 Ready to use: screensaver-prefs"
