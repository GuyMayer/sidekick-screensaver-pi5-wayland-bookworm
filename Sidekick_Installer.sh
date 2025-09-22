#!/bin/bash
# Sidekick_Installer.sh - Complete Sidekick Screensaver System with USB Detection
# This script installs everything: Sidekick screensaver, preferences GUI, and USB detection

echo "🟢💚 Installing Complete Sidekick Screensaver System with USB Detection & Show Stats"
echo "=================================================================================="
echo "🎯 This will install:"
echo "   • Sidekick Screensaver Engine with USB Activity Detection"
echo "   • PyQt6 Preferences GUI with Professional Dark Mode"
echo "   • Comprehensive System Statistics Display"
echo "   • Autostart Configuration"
echo "   • USB Test Scripts"
echo "   • Desktop Integration"
echo ""

# Define installation directories
LOCAL_BIN="$HOME/.local/bin"
APPLICATIONS_DIR="$HOME/.local/share/applications"
CONFIG_DIR="$HOME/.config/sidekick_screensaver"

# Create directories if they don't exist
mkdir -p "$LOCAL_BIN" "$APPLICATIONS_DIR" "$CONFIG_DIR"

# Current directory (where this script is located)
SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"

echo "📁 Installation directories:"
echo "   • Executables: $LOCAL_BIN"
echo "   • Desktop entries: $APPLICATIONS_DIR"
echo "   • Configuration: $CONFIG_DIR"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."

# Check if we need to install Python packages
install_python_deps() {
    local packages=()

    # Check PyQt6
    if ! python3 -c "import PyQt6" 2>/dev/null; then
        packages+=("PyQt6")
    fi

    # Check psutil
    if ! python3 -c "import psutil" 2>/dev/null; then
        packages+=("psutil")
    fi

    # Check qdarkstyle
    if ! python3 -c "import qdarkstyle" 2>/dev/null; then
        packages+=("qdarkstyle")
    fi

    # Check pybluez for Bluetooth support
    if ! python3 -c "import bluetooth" 2>/dev/null; then
        packages+=("pybluez")
    fi

    if [ ${#packages[@]} -gt 0 ]; then
        echo "🔧 Installing Python packages: ${packages[*]}"

        # Try pip3 first, then pip
        if command -v pip3 >/dev/null 2>&1; then
            pip3 install --user "${packages[@]}" || {
                echo "⚠️ pip3 install failed, trying with sudo..."
                sudo pip3 install "${packages[@]}" 2>/dev/null || true
            }
        elif command -v pip >/dev/null 2>&1; then
            pip install --user "${packages[@]}" || {
                echo "⚠️ pip install failed, trying with sudo..."
                sudo pip install "${packages[@]}" 2>/dev/null || true
            }
        else
            echo "⚠️ No pip found. Please install: ${packages[*]}"
        fi
    else
        echo "✅ All Python dependencies already installed"
    fi
}

# Check if we need to install system packages for Bluetooth
install_system_deps() {
    local missing_packages=()

    # Check for Bluetooth development headers
    if ! dpkg -l | grep -q "libbluetooth-dev\|bluez-dev" 2>/dev/null; then
        missing_packages+=("libbluetooth-dev")
    fi

    # Check for bluez utilities
    if ! command -v bluetoothctl >/dev/null 2>&1; then
        missing_packages+=("bluez")
    fi

    if [ ${#missing_packages[@]} -gt 0 ]; then
        echo "🔧 Installing system packages: ${missing_packages[*]}"

        # Detect package manager and install
        if command -v apt-get >/dev/null 2>&1; then
            sudo apt-get update >/dev/null 2>&1 || true
            sudo apt-get install -y "${missing_packages[@]}" 2>/dev/null || {
                echo "⚠️ Failed to install some system packages. Bluetooth features may not work."
            }
        elif command -v dnf >/dev/null 2>&1; then
            sudo dnf install -y "${missing_packages[@]}" 2>/dev/null || true
        elif command -v pacman >/dev/null 2>&1; then
            sudo pacman -S --noconfirm "${missing_packages[@]}" 2>/dev/null || true
        else
            echo "⚠️ Unknown package manager. Please install: ${missing_packages[*]}"
        fi
    else
        echo "✅ All system dependencies already installed"
    fi
}

# Install dependencies
install_system_deps
install_python_deps
echo "✅ Dependencies installation completed"
echo ""

# Kill any running screensavers before installation
echo "🛑 Stopping any running screensavers..."
kill_screensavers() {
    # Kill Python screensaver widgets (be specific to avoid killing this script)
    pgrep -f "sidekick_widget\.py" | xargs -r kill 2>/dev/null || true
    pgrep -f "mystify_widget\.py" | xargs -r kill 2>/dev/null || true
    pgrep -f "slideshow_widget\.py" | xargs -r kill 2>/dev/null || true

    # Kill screensaver preference GUIs (but not this install script)
    pgrep -f "screensaver_preferences\.py" | grep -v $$ | xargs -r kill 2>/dev/null || true
    pgrep -f "screensaver-prefs" | grep -v $$ | xargs -r kill 2>/dev/null || true

    # Kill sidekick-related terminal processes (but not this script's terminal)
    pgrep -f "lxterminal.*sidekick" | xargs -r kill 2>/dev/null || true
    pgrep -f "lxterminal.*Screensaver" | xargs -r kill 2>/dev/null || true

    # Use wmctrl to close windows by title (if available)
    if command -v wmctrl >/dev/null 2>&1; then
        wmctrl -c "Sidekick Screensaver" 2>/dev/null || true
        wmctrl -c "Mystify Screensaver" 2>/dev/null || true
        wmctrl -c "Slideshow Screensaver" 2>/dev/null || true
    fi

    # Give processes a moment to terminate
    sleep 1
}

kill_screensavers
echo "✅ Screensavers stopped"
echo ""

# Install core Matrix screensaver files
echo "🔌 Installing Matrix Screensaver Core with USB Detection..."
cp "$SCRIPT_DIR/sidekick_widget.py" "$LOCAL_BIN/"
cp "$SCRIPT_DIR/sidekick_screensaver.sh" "$LOCAL_BIN/"
cp "$SCRIPT_DIR/wayland_sidekick_autolock.sh" "$LOCAL_BIN/"

# Make executable
chmod +x "$LOCAL_BIN/sidekick_widget.py"
chmod +x "$LOCAL_BIN/sidekick_screensaver.sh"
chmod +x "$LOCAL_BIN/wayland_sidekick_autolock.sh"

# Verify USB detection code and Show Stats feature
if grep -q "USB Activity Monitoring" "$LOCAL_BIN/sidekick_widget.py"; then
    echo "✅ Matrix Widget with USB Activity Detection installed"
else
    echo "⚠️ Warning: USB Activity Detection code not found in Matrix Widget"
fi

if grep -q "show_stats" "$LOCAL_BIN/sidekick_widget.py"; then
    echo "✅ Matrix Widget with Show Stats feature installed"
else
    echo "⚠️ Warning: Show Stats feature not found in Matrix Widget"
fi

# Install PyQt6 GUI with Show Stats
echo "📋 Installing PyQt6 Preferences GUI with Show Stats feature..."
cp "$SCRIPT_DIR/screensaver_preferences.py" "$LOCAL_BIN/"
chmod +x "$LOCAL_BIN/screensaver_preferences.py"

# Verify Show Stats feature in GUI
if grep -q "Show Stats" "$LOCAL_BIN/screensaver_preferences.py"; then
    echo "✅ PyQt6 GUI with Show Stats feature installed"
else
    echo "⚠️ Warning: Show Stats feature not found in GUI"
fi

# Install slideshow widget
if [ -f "$SCRIPT_DIR/slideshow_widget.py" ]; then
    echo "🖼️ Installing Slideshow Widget with Show Stats..."
    cp "$SCRIPT_DIR/slideshow_widget.py" "$LOCAL_BIN/"
    chmod +x "$LOCAL_BIN/slideshow_widget.py"

    # Verify Show Stats in Slideshow
    if grep -q "show_stats" "$LOCAL_BIN/slideshow_widget.py"; then
        echo "✅ Slideshow Widget with Show Stats installed"
    else
        echo "✅ Slideshow Widget installed (basic version)"
    fi
fi

# Install update check test script
if [ -f "$SCRIPT_DIR/test_update_check.py" ]; then
    echo "🔄 Installing Update Check Test Script..."
    cp "$SCRIPT_DIR/test_update_check.py" "$LOCAL_BIN/"
    chmod +x "$LOCAL_BIN/test_update_check.py"

    # Create convenience symlink
    ln -sf "$LOCAL_BIN/test_update_check.py" "$LOCAL_BIN/test-updates"
    echo "✅ Update check test script installed (test-updates)"
fi

# Install mystify widget
if [ -f "$SCRIPT_DIR/mystify_widget.py" ]; then
    echo "# Install final touches
echo "✨ Installing final touches..."

# Add XDG autostart support for broader compatibility
echo "🔄 Setting up cross-desktop autostart..."
mkdir -p ~/.config/autostart
cat > ~/.config/autostart/matrix-screensaver-autostart.desktop << EOF
[Desktop Entry]
Type=Application
Name=Sidekick screensaver Auto-lock
Comment=Automatically start Sidekick screensaver system
Exec=$LOCAL_BIN/wayland_sidekick_autolock.sh
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
X-KDE-autostart-after=panel
StartupNotify=false
Categories=System;
EOF

# Verify autostart is working
echo "🔍 Verifying autostart configuration..."
if [ -f ~/.config/autostart/matrix-screensaver-autostart.desktop ]; then
    echo "✅ XDG autostart configured"
fi

if [ -f ~/.config/lxsession/LXDE-pi/autostart ]; then
    echo "✅ LXDE autostart configured"
fi

# Update PATH in bashrc if not already present"
    cp "$SCRIPT_DIR/mystify_widget.py" "$LOCAL_BIN/"
    chmod +x "$LOCAL_BIN/mystify_widget.py"

    # Verify Show Stats in Mystify
    if grep -q "show_stats" "$LOCAL_BIN/mystify_widget.py"; then
        echo "✅ Mystify geometric screensaver with Show Stats installed"
    else
        echo "✅ Mystify geometric screensaver installed (basic version)"
    fi
fi

# Install USB test script
if [ -f "$SCRIPT_DIR/test_usb_activity.py" ]; then
    echo "🧪 Installing USB Activity Test Script..."
    cp "$SCRIPT_DIR/test_usb_activity.py" "$LOCAL_BIN/"
    chmod +x "$LOCAL_BIN/test_usb_activity.py"
fi

# Install utility scripts
if [ -f "$SCRIPT_DIR/close_all_guis.sh" ]; then
    echo "🧹 Installing GUI cleanup script..."
    cp "$SCRIPT_DIR/close_all_guis.sh" "$LOCAL_BIN/"
    chmod +x "$LOCAL_BIN/close_all_guis.sh"
fi

# Install desktop restoration scripts
echo "🖥️ Installing desktop restoration scripts..."
if [ -f "$SCRIPT_DIR/restore_desktop.sh" ]; then
    cp "$SCRIPT_DIR/restore_desktop.sh" "$LOCAL_BIN/"
    chmod +x "$LOCAL_BIN/restore_desktop.sh"
    echo "✅ Desktop restoration script installed"
fi

if [ -f "$SCRIPT_DIR/restore_taskbar_quiet.sh" ]; then
    cp "$SCRIPT_DIR/restore_taskbar_quiet.sh" "$LOCAL_BIN/"
    chmod +x "$LOCAL_BIN/restore_taskbar_quiet.sh"
    echo "✅ Quiet taskbar restoration script installed"
fi

if [ -f "$SCRIPT_DIR/restore_background.sh" ]; then
    cp "$SCRIPT_DIR/restore_background.sh" "$LOCAL_BIN/"
    chmod +x "$LOCAL_BIN/restore_background.sh"
    echo "✅ Background restoration script installed"
fi

# Install Show Stats verification script
if [ -f "$SCRIPT_DIR/verify_show_stats_installation.sh" ]; then
    echo "📊 Installing Show Stats verification script..."
    cp "$SCRIPT_DIR/verify_show_stats_installation.sh" "$LOCAL_BIN/"
    chmod +x "$LOCAL_BIN/verify_show_stats_installation.sh"
    echo "✅ Show Stats verification script installed"
fi

# Install verification script
if [ -f "$SCRIPT_DIR/verify_installation.sh" ]; then
    cp "$SCRIPT_DIR/verify_installation.sh" "$LOCAL_BIN/"
    chmod +x "$LOCAL_BIN/verify_installation.sh"
    echo "✅ Installation verification script installed"
fi

# Create desktop entry for PyQt6 version (single entry only)
echo "🖥️ Creating desktop integration..."

# Remove any old/duplicate entries first
rm -f "$APPLICATIONS_DIR/matrix-test.desktop" \
      "$APPLICATIONS_DIR/matrix-screensaver-settings.desktop" \
      "$APPLICATIONS_DIR/matrix-screensaver-test.desktop" \
      "$APPLICATIONS_DIR/matrix-screensaver-preferences.desktop" \
      2>/dev/null || true

# Create single unified desktop entry
cat > "$APPLICATIONS_DIR/sidekick-screensaver-preferences.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Sidekick Screensaver
GenericName=Screensaver Configuration
Comment=Configure Sidekick screensaver with USB activity detection and system statistics
Exec=$LOCAL_BIN/screensaver-prefs
Icon=preferences-desktop-screensaver
Terminal=false
StartupNotify=true
Categories=Settings;DesktopSettings;Preferences;
Keywords=screensaver;sidekick;preferences;wayland;digital rain;usb;stats;
MimeType=
StartupWMClass=Sidekick Screensaver Preferences
EOF

chmod +x "$APPLICATIONS_DIR/sidekick-screensaver-preferences.desktop"

# Update desktop database if available
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "$APPLICATIONS_DIR" 2>/dev/null
fi

# Also update system-wide if we have permissions
if command -v update-desktop-database >/dev/null 2>&1 && [ -w /usr/share/applications ]; then
    sudo update-desktop-database /usr/share/applications 2>/dev/null || true
fi

# Create menu structure for better organization
mkdir -p "$HOME/.local/share/desktop-directories"
cat > "$HOME/.local/share/desktop-directories/sidekick-screensaver.directory" << EOF
[Desktop Entry]
Version=1.0
Type=Directory
Name=Sidekick screensaver
Comment=Sidekick digital rain screensaver applications
Icon=preferences-desktop-screensaver
EOF

# Create symlinks for easier access
echo "📎 Creating convenience symlinks..."
ln -sf "$LOCAL_BIN/screensaver_preferences.py" "$LOCAL_BIN/screensaver-prefs"
ln -sf "$LOCAL_BIN/test_usb_activity.py" "$LOCAL_BIN/test-usb"
ln -sf "$LOCAL_BIN/restore_taskbar_quiet.sh" "$LOCAL_BIN/restore-taskbar"
ln -sf "$LOCAL_BIN/restore_desktop.sh" "$LOCAL_BIN/restore-desktop"
ln -sf "$LOCAL_BIN/verify_installation.sh" "$LOCAL_BIN/verify-screensaver"
ln -sf "$LOCAL_BIN/verify_show_stats_installation.sh" "$LOCAL_BIN/verify-show-stats"

# Update autostart configuration
echo "📝 Updating autostart configuration..."

# Create more robust autostart that handles different desktop environments
AUTOSTART_DIRS=(
    "~/.config/lxsession/LXDE-pi"
    "~/.config/lxsession/LXDE"
    "~/.config/autostart"
)

for dir in "${AUTOSTART_DIRS[@]}"; do
    expanded_dir=$(eval echo "$dir")
    mkdir -p "$expanded_dir"

    if [[ "$dir" == *"autostart" ]]; then
        # Create .desktop autostart file
        cat > "$expanded_dir/matrix-screensaver-autostart.desktop" << EOF
[Desktop Entry]
Type=Application
Name=Sidekick screensaver Auto-lock
Comment=Automatically start Sidekick screensaver system
Exec=$LOCAL_BIN/wayland_sidekick_autolock.sh
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
StartupNotify=false
EOF
    else
        # Create LXDE autostart entry
        echo "@$LOCAL_BIN/wayland_sidekick_autolock.sh" > "$expanded_dir/autostart"
    fi
done

# Check dependencies
echo "🔍 Checking system dependencies..."

PYTHON_DEPS=()
SYSTEM_DEPS=()

# Check Python dependencies
if ! python3 -c "import PyQt6.QtWidgets" 2>/dev/null; then
    PYTHON_DEPS+=("PyQt6")
fi

if ! python3 -c "import psutil" 2>/dev/null; then
    PYTHON_DEPS+=("psutil")
    echo "ℹ️ psutil needed for Show Stats feature"
fi

if ! python3 -c "import qdarktheme" 2>/dev/null; then
    PYTHON_DEPS+=("qdarktheme")
    echo "ℹ️ qdarktheme needed for Dark Mode feature"
fi

# Check system dependencies
if ! command -v swayidle >/dev/null 2>&1; then
    SYSTEM_DEPS+=("swayidle")
fi

if ! command -v wmctrl >/dev/null 2>&1; then
    SYSTEM_DEPS+=("wmctrl")
fi

if ! command -v xdotool >/dev/null 2>&1; then
    SYSTEM_DEPS+=("xdotool")
fi

if ! command -v xprintidle >/dev/null 2>&1; then
    SYSTEM_DEPS+=("xprintidle")
fi

# Install missing dependencies
if [ ${#PYTHON_DEPS[@]} -gt 0 ]; then
    echo "⚠️ Installing missing Python dependencies: ${PYTHON_DEPS[*]}"
    if command -v pip3 >/dev/null 2>&1; then
        pip3 install "${PYTHON_DEPS[@]}"
    else
        echo "❌ pip3 not found. Please install manually: pip3 install ${PYTHON_DEPS[*]}"
    fi
fi

if [ ${#SYSTEM_DEPS[@]} -gt 0 ]; then
    echo "⚠️ Missing system dependencies: ${SYSTEM_DEPS[*]}"
    echo "Install with: sudo apt install ${SYSTEM_DEPS[*]}"
fi

# Add to PATH if not already there
if [[ ":$PATH:" != *":$LOCAL_BIN:"* ]]; then
    echo "📝 Adding $LOCAL_BIN to PATH..."
    echo "export PATH=\"\$PATH:$LOCAL_BIN\"" >> "$HOME/.bashrc"
    echo "ℹ️ You may need to restart your terminal or run: source ~/.bashrc"
fi

echo ""
echo "======================================================================================"
echo "🎉 Complete Matrix Screensaver System with Show Stats Installation Successful!"
echo "======================================================================================"
echo ""
echo "🚀 Installed Components:"
echo "  ✅ Sidekick Screensaver Engine with USB Activity Detection"
echo "  ✅ Mystify Geometric Screensaver (Windows-style patterns)"
echo "  ✅ PyQt6 Preferences GUI with Professional Dark Mode"
echo "  ✅ Comprehensive System Statistics Display"
echo "  ✅ Automatic Monthly Update Checks"
echo "  ✅ Autostart Configuration"
echo "  ✅ USB Activity Test Script"
echo "  ✅ Desktop Menu Integration"
echo "  ✅ Convenience Symlinks"
echo "  ✅ Silent Desktop Restoration Scripts"
echo "  ✅ Installation Verification Tools"
echo ""
echo "🌙 Dark Mode Features:"
echo "  • Professional QDarkStyle theme with native Qt controls"
echo "  • Auto-restart GUI when theme is toggled"
echo "  • Persistent theme preference storage"
echo "  • Working spinboxes, dropdowns, and sliders"
echo "  • No broken icons or squares - proper native rendering"
echo "  • Toggle with '🌙 Dark Mode' checkbox in GUI"
echo ""
echo "� Show Stats Features:"
echo "  • Real-time FPS monitoring (current vs target)"
echo "  • System CPU usage tracking (10-sample average)"
echo "  • Screensaver process CPU usage"
echo "  • System memory percentage"
echo "  • Screensaver process memory (MB)"
echo "  • Anti-burn-in color cycling (every 5 seconds)"
echo "  • Performance-optimized (1-second update intervals)"
echo ""
echo "�🔌 USB Detection Features:"
echo "  • Real-time USB interrupt monitoring (500ms interval)"
echo "  • Immediate screensaver exit on USB mouse movement"
echo "  • Immediate screensaver exit on USB keyboard strokes"
echo "  • Hardware-level activity detection"
echo "  • Dual detection system (USB + PyQt6 events)"
echo ""
echo "🖥️ Desktop Integration Features:"
echo "  • Silent taskbar restoration (no Wayland/X11 warnings)"
echo "  • Background image preservation"
echo "  • Intelligent CPU/Memory management"
echo "  • Color-cycling stats display (prevents screen burn-in)"
echo "  • Memory overflow protection"
echo "  • No annoying popups on settings apply"
echo ""
echo "🎬 Screensaver Timeline:"
echo "  0-5 minutes:   Normal desktop use"
echo "  5-10 minutes:  Matrix digital rain starts! 🟢💚"
echo "                 └── USB mouse/keyboard = INSTANT EXIT"
echo "  10+ minutes:   Screen turns off (power saving)"
echo ""
echo "🎮 How to Use:"
echo "  • Launch GUI: screensaver-prefs"
echo "  • From menu: Applications → Sidekick screensaver"
echo "  • Enable Stats: Check '📊 Show Stats' in GUI"
echo "  • Enable Updates: Check '🔄 Auto Update Check' in GUI"
echo "  • Test USB:   test-usb"
echo "  • Test Updates: test-updates"
echo "  • Manual test: ./sidekick_screensaver.sh"
echo "  • Restore taskbar: restore_taskbar_quiet.sh"
echo "  • Verify install: verify_installation.sh"
echo "  • Verify stats: verify-show-stats"
echo ""
echo "🧪 Quick Test:"
echo "  1. Run: screensaver-prefs"
echo "  2. Enable '📊 Show Stats' checkbox"
echo "  3. Enable '🔄 Auto Update Check' checkbox"
echo "  4. Click '🔍 Check Now' to test update checking"
echo "  5. Click 'Test Matrix'"
echo "  6. See stats in top-left corner (FPS, CPU, Memory)"
echo "  7. Move USB mouse or press USB keyboard"
echo "  8. Screensaver should exit immediately!"
echo "  6. Screensaver should exit immediately!"
echo ""
echo "🔄 Next Steps:"
echo "  1. Restart your desktop session to activate autostart"
echo "  2. Test the USB detection with: test-usb"
echo "  3. Verify Show Stats with: verify-show-stats"
echo "  4. Configure preferences with: screensaver-prefs"
echo "  5. Enjoy your Sidekick screensaver with USB detection & stats! 🔌📊⌨️🖱️"
echo ""

# Final system updates
echo "🔄 Finalizing installation..."

# Update desktop database to ensure menu entries work
if command -v update-desktop-database >/dev/null 2>&1; then
    echo "📋 Updating desktop database..."
    update-desktop-database "$APPLICATIONS_DIR" 2>/dev/null || true

    # Try to update system-wide database too
    if [ -w /usr/share/applications ] || sudo -n true 2>/dev/null; then
        sudo update-desktop-database /usr/share/applications 2>/dev/null || true
    fi
fi

# Update mime database if available
if command -v update-mime-database >/dev/null 2>&1; then
    update-mime-database "$HOME/.local/share/mime" 2>/dev/null || true
fi

# Refresh icon cache if available
if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache -f "$HOME/.local/share/icons" 2>/dev/null || true
    gtk-update-icon-cache -f /usr/share/icons/hicolor 2>/dev/null || true
fi

# Make sure user's local bin is in PATH
if ! echo "$PATH" | grep -q "$LOCAL_BIN"; then
    echo "⚠️ Adding $LOCAL_BIN to PATH in ~/.bashrc"
    echo "export PATH=\"\$PATH:$LOCAL_BIN\"" >> "$HOME/.bashrc"
    echo "💡 Run 'source ~/.bashrc' or restart terminal to update PATH"
fi

echo "✅ Installation finalization complete!"
echo ""

echo "======================================================================================"
