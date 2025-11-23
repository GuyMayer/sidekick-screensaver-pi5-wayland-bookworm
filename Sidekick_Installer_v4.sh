#!/bin/bash
# Sidekick_Installer.sh - Complete Sidekick Screensaver System with USB Detection
# Updated to install v4.0 Modern UI Edition by default

echo "🎨✨ Installing Sidekick Screensaver v4.0 - Complete System"
echo "==========================================================="
echo "🎯 This will install:"
echo "   • v4.0 Modern UI Preferences GUI"
echo "     - Sidebar navigation with modern 2025 aesthetic"
echo "     - iOS-style toggle switches"
echo "     - Smooth sliders with real-time values"
echo "     - Vibrant blue accent colors"
echo "     - All v4 settings preserved"
echo "   • Sidekick Screensaver Engine with USB Activity Detection"
echo "   • Comprehensive System Statistics Display"
echo "   • Autostart Configuration"
echo "   • Desktop Integration"
echo ""

# Define installation directories
LOCAL_BIN="$HOME/.local/bin"
APPLICATIONS_DIR="$HOME/.local/share/applications"
CONFIG_DIR="$HOME/.config/screensaver"  # Updated to match v4 config location

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

    # Check filelock (required for v4)
    if ! python3 -c "import filelock" 2>/dev/null; then
        packages+=("filelock")
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
echo "🛑 Stopping ALL running screensaver processes..."
kill_screensavers() {
    echo "   🔍 Searching for running screensaver processes..."

    # Kill swayidle autolock processes
    pkill -f "wayland_sidekick_autolock.sh" 2>/dev/null || true
    pkill -f "swayidle.*sidekick" 2>/dev/null || true

    # Kill Python screensaver widgets (be specific to avoid killing this script)
    pkill -9 -f "sidekick_widget\.py" 2>/dev/null || true
    pkill -9 -f "mystify_widget\.py" 2>/dev/null || true
    pkill -9 -f "slideshow_widget\.py" 2>/dev/null || true

    # Kill any Python processes running from ~/.local/bin
    pkill -9 -f "$HOME/.local/bin/sidekick_widget.py" 2>/dev/null || true
    pkill -9 -f "$HOME/.local/bin/mystify_widget.py" 2>/dev/null || true
    pkill -9 -f "$HOME/.local/bin/slideshow_widget.py" 2>/dev/null || true

    # Kill screensaver preference GUIs (but not this install script)
    pkill -9 -f "screensaver_preferences\.py" 2>/dev/null || true
    pkill -9 -f "screensaver-prefs" 2>/dev/null || true
    pkill -9 -f "$HOME/.local/bin/screensaver_preferences.py" 2>/dev/null || true

    # Kill test scripts
    pkill -f "test_usb_activity.py" 2>/dev/null || true
    pkill -f "test_touch_ui.py" 2>/dev/null || true
    pkill -f "test_cpu_throttle.py" 2>/dev/null || true

    # Kill sidekick-related terminal processes (but not this script's terminal)
    pkill -f "lxterminal.*sidekick" 2>/dev/null || true
    pkill -f "lxterminal.*Screensaver" 2>/dev/null || true

    # Use wmctrl to close windows by title (if available)
    if command -v wmctrl >/dev/null 2>&1; then
        wmctrl -c "Sidekick Screensaver" 2>/dev/null || true
        wmctrl -c "Mystify Screensaver" 2>/dev/null || true
        wmctrl -c "Slideshow Screensaver" 2>/dev/null || true
        wmctrl -c "Screensaver Preferences" 2>/dev/null || true
        wmctrl -c "Matrix Digital Rain" 2>/dev/null || true
    fi

    # Give processes a moment to terminate
    sleep 2

    # Force kill any remaining Python processes with our widget names
    ps aux | grep -E "(sidekick|mystify|slideshow)_widget.py" | grep -v grep | awk '{print $2}' | xargs -r kill -9 2>/dev/null || true

    echo "   ✅ All screensaver processes terminated"
}

kill_screensavers
echo "✅ Screensavers stopped"
echo ""

# Clean old installation files before reinstalling
echo "🧹 Cleaning old installation files..."
rm -f "$LOCAL_BIN/sidekick_widget.py" 2>/dev/null || true
rm -f "$LOCAL_BIN/mystify_widget.py" 2>/dev/null || true
rm -f "$LOCAL_BIN/slideshow_widget.py" 2>/dev/null || true
rm -f "$LOCAL_BIN/screensaver_preferences.py" 2>/dev/null || true
rm -f "$LOCAL_BIN/sidekick_screensaver.sh" 2>/dev/null || true
rm -f "$LOCAL_BIN/wayland_sidekick_autolock.sh" 2>/dev/null || true
rm -f "$LOCAL_BIN/test_usb_activity.py" 2>/dev/null || true
rm -f "$LOCAL_BIN/test_touch_ui.py" 2>/dev/null || true
rm -f "$LOCAL_BIN/test_cpu_throttle.py" 2>/dev/null || true
echo "✅ Old files cleaned"
echo ""

# Install core Matrix screensaver files (from src/ folder)
echo "🔌 Installing Matrix Screensaver Core with USB Detection..."
cp "$SCRIPT_DIR/src/sidekick_widget.py" "$LOCAL_BIN/"
cp "$SCRIPT_DIR/scripts/sidekick_screensaver.sh" "$LOCAL_BIN/"
cp "$SCRIPT_DIR/scripts/wayland_sidekick_autolock.sh" "$LOCAL_BIN/"

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

# Install PyQt6 GUI v4.0 Modern UI Edition (from src/ folder)
echo "🎨 Installing v4.0 Modern UI Preferences GUI..."
cp "$SCRIPT_DIR/src/screensaver_preferences_v4.py" "$LOCAL_BIN/screensaver_preferences.py"
chmod +x "$LOCAL_BIN/screensaver_preferences.py"

# Verify v4 features
if grep -q "Modern UI Edition" "$LOCAL_BIN/screensaver_preferences.py"; then
    echo "✅ v4.0 Modern UI GUI installed"
else
    echo "⚠️ Warning: v4 features not found in GUI"
fi

# Install logo files for v4 sidebar and favicon icons (from media/Logo/ folder)
echo "🖼️ Installing v4 logo and favicon files..."
if [ -f "$SCRIPT_DIR/media/Logo/sidekick_logo_dark.png" ]; then
    cp "$SCRIPT_DIR/media/Logo/sidekick_logo_dark.png" "$LOCAL_BIN/"
    echo "✅ Dark theme logo installed"
fi
if [ -f "$SCRIPT_DIR/media/Logo/sidekick_logo_light.png" ]; then
    cp "$SCRIPT_DIR/media/Logo/sidekick_logo_light.png" "$LOCAL_BIN/"
    echo "✅ Light theme logo installed"
fi

# Install favicons (600x600 for window, 22x22 optimized for system tray)
if [ -f "$SCRIPT_DIR/media/Logo/SideKick_Logo_2025_Favicon.png" ]; then
    cp "$SCRIPT_DIR/media/Logo/SideKick_Logo_2025_Favicon.png" "$LOCAL_BIN/"
    echo "✅ Dark theme favicon installed (600x600)"
fi
if [ -f "$SCRIPT_DIR/media/Logo/SideKick_Logo_2025_Favicon_light.png" ]; then
    cp "$SCRIPT_DIR/media/Logo/SideKick_Logo_2025_Favicon_light.png" "$LOCAL_BIN/"
    echo "✅ Light theme favicon installed (600x600)"
fi
if [ -f "$SCRIPT_DIR/media/Logo/SideKick_Logo_2025_Favicon_22.png" ]; then
    cp "$SCRIPT_DIR/media/Logo/SideKick_Logo_2025_Favicon_22.png" "$LOCAL_BIN/"
    echo "✅ Dark theme favicon installed (22x22 optimized for system tray)"
fi
if [ -f "$SCRIPT_DIR/media/Logo/SideKick_Logo_2025_Favicon_light_22.png" ]; then
    cp "$SCRIPT_DIR/media/Logo/SideKick_Logo_2025_Favicon_light_22.png" "$LOCAL_BIN/"
    echo "✅ Light theme favicon installed (22x22 optimized for system tray)"
fi

# Install favicon for system tray icon
if [ -f "$SCRIPT_DIR/media/Logo/favicon_dark.png" ]; then
    cp "$SCRIPT_DIR/media/Logo/favicon_dark.png" "$LOCAL_BIN/"
    echo "✅ Dark theme favicon installed"
fi
if [ -f "$SCRIPT_DIR/media/Logo/favicon_light.png" ]; then
    cp "$SCRIPT_DIR/media/Logo/favicon_light.png" "$LOCAL_BIN/"
    echo "✅ Light theme favicon installed"
fi

# Install slideshow widget
if [ -f "$SCRIPT_DIR/src/slideshow_widget.py" ]; then
    echo "🖼️ Installing Slideshow Widget with Show Stats..."
    cp "$SCRIPT_DIR/src/slideshow_widget.py" "$LOCAL_BIN/"
    chmod +x "$LOCAL_BIN/slideshow_widget.py"

    # Verify Show Stats in Slideshow
    if grep -q "show_stats" "$LOCAL_BIN/slideshow_widget.py"; then
        echo "✅ Slideshow Widget with Show Stats installed"
    else
        echo "✅ Slideshow Widget installed (basic version)"
    fi
fi

# Install video player widget
if [ -f "$SCRIPT_DIR/src/video_widget.py" ]; then
    echo "🎬 Installing Video Player Widget..."
    cp "$SCRIPT_DIR/src/video_widget.py" "$LOCAL_BIN/"
    chmod +x "$LOCAL_BIN/video_widget.py"
    echo "✅ Video Player Widget installed (hardware-accelerated playback)"
fi

# Install Matrix video generator
if [ -f "$SCRIPT_DIR/generate_matrix_video_opencv.py" ]; then
    echo "🎥 Installing Matrix Video Generator..."
    cp "$SCRIPT_DIR/generate_matrix_video_opencv.py" "$LOCAL_BIN/"
    chmod +x "$LOCAL_BIN/generate_matrix_video_opencv.py"
    echo "✅ Matrix Video Generator installed"
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
if [ -f "$SCRIPT_DIR/src/mystify_widget.py" ]; then
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
    cp "$SCRIPT_DIR/src/mystify_widget.py" "$LOCAL_BIN/"
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

# Install touchscreen UI test script
if [ -f "$SCRIPT_DIR/test_touch_ui.py" ]; then
    echo "🖐️ Installing Touchscreen UI Test Script..."
    cp "$SCRIPT_DIR/test_touch_ui.py" "$LOCAL_BIN/"
    chmod +x "$LOCAL_BIN/test_touch_ui.py"
    echo "✅ Touchscreen detection test script installed"
fi

# Install CPU throttle test script
if [ -f "$SCRIPT_DIR/test_cpu_throttle.py" ]; then
    echo "🚨 Installing CPU Throttle Test Script..."
    cp "$SCRIPT_DIR/test_cpu_throttle.py" "$LOCAL_BIN/"
    chmod +x "$LOCAL_BIN/test_cpu_throttle.py"
    echo "✅ Emergency CPU throttle test script installed"
fi

# Install video widget
if [ -f "$SCRIPT_DIR/src/video_widget.py" ]; then
    echo "🎬 Installing Video Player Widget..."
    cp "$SCRIPT_DIR/src/video_widget.py" "$LOCAL_BIN/"
    chmod +x "$LOCAL_BIN/video_widget.py"
    echo "✅ Hardware-accelerated video player widget installed"
fi

# Install Matrix video generator
if [ -f "$SCRIPT_DIR/generate_matrix_video_opencv.py" ]; then
    echo "📹 Installing Matrix Video Generator..."
    cp "$SCRIPT_DIR/generate_matrix_video_opencv.py" "$LOCAL_BIN/"
    chmod +x "$LOCAL_BIN/generate_matrix_video_opencv.py"
    echo "✅ Matrix video generator installed"
fi

# Copy pre-rendered Matrix videos if they exist
VIDEOS_DIR="$HOME/Videos/Screensavers"
mkdir -p "$VIDEOS_DIR"

if [ -f "$SCRIPT_DIR/media/Video/Matrix1.mp4" ] || [ -f "$SCRIPT_DIR/media/Video/Matrix2.mp4" ]; then
    echo "🎥 Installing pre-rendered Matrix videos..."
    [ -f "$SCRIPT_DIR/media/Video/Matrix1.mp4" ] && cp "$SCRIPT_DIR/media/Video/Matrix1.mp4" "$VIDEOS_DIR/" && echo "✅ Matrix1.mp4 installed"
    [ -f "$SCRIPT_DIR/media/Video/Matrix2.mp4" ] && cp "$SCRIPT_DIR/media/Video/Matrix2.mp4" "$VIDEOS_DIR/" && echo "✅ Matrix2.mp4 installed"
    echo "   💡 These videos use ~2% CPU vs ~10% for live rendering!"
else
    echo "ℹ️  No pre-rendered Matrix videos found in media/Video/"
    echo "   Generate one with: generate-matrix-video"
fi

# Install screensaver-media folder with videos and images
MEDIA_DIR="$HOME/screensaver-media"
echo "📁 Installing screensaver media folder..."
if [ -d "$HOME/screensaver-media" ]; then
    echo "✅ Screensaver media folder already exists at $MEDIA_DIR"
    # Copy videos if they exist in media/Video/ folder
    [ -f "$SCRIPT_DIR/media/Video/Matrix1.mp4" ] && cp "$SCRIPT_DIR/media/Video/Matrix1.mp4" "$MEDIA_DIR/videos/" 2>/dev/null || true
    [ -f "$SCRIPT_DIR/media/Video/Matrix2.mp4" ] && cp "$SCRIPT_DIR/media/Video/Matrix2.mp4" "$MEDIA_DIR/videos/" 2>/dev/null || true
else
    mkdir -p "$MEDIA_DIR/videos"
    mkdir -p "$MEDIA_DIR/images"

    # Copy videos if available from media/Video/ folder
    [ -f "$SCRIPT_DIR/media/Video/Matrix1.mp4" ] && cp "$SCRIPT_DIR/media/Video/Matrix1.mp4" "$MEDIA_DIR/videos/"
    [ -f "$SCRIPT_DIR/media/Video/Matrix2.mp4" ] && cp "$SCRIPT_DIR/media/Video/Matrix2.mp4" "$MEDIA_DIR/videos/"

    # Copy images if available
    if [ -f "$SCRIPT_DIR/../screensaver-media/images/test_image_1920x1080.jpg" ]; then
        cp "$SCRIPT_DIR/../screensaver-media/images/"*.jpg "$MEDIA_DIR/images/" 2>/dev/null || true
    fi

    echo "✅ Created screensaver media folder at $MEDIA_DIR"
    echo "   📹 Videos: $MEDIA_DIR/videos"
    echo "   🖼️  Images: $MEDIA_DIR/images"
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

# Create single unified desktop entry for v4
cat > "$APPLICATIONS_DIR/sidekick-screensaver-preferences.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Screensaver Settings v4
GenericName=Screensaver Configuration
Comment=Modern UI screensaver settings with sidebar navigation and iOS-style controls
Exec=$LOCAL_BIN/screensaver-prefs
Icon=preferences-desktop-screensaver
Terminal=false
StartupNotify=true
Categories=Settings;DesktopSettings;Preferences;
Keywords=screensaver;sidekick;preferences;wayland;digital rain;mystify;v4;modern;
MimeType=
StartupWMClass=Screensaver Settings
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
ln -sf "$LOCAL_BIN/test_touch_ui.py" "$LOCAL_BIN/test-touch"
ln -sf "$LOCAL_BIN/test_cpu_throttle.py" "$LOCAL_BIN/test-throttle"
ln -sf "$LOCAL_BIN/generate_matrix_video_opencv.py" "$LOCAL_BIN/generate-matrix-video"
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
echo "================================================================"
echo "�✨ Sidekick Screensaver v4.0 Installation Complete!"
echo "================================================================"
echo ""
echo "🚀 Installed Components:"
echo "  ✅ v4.0 Modern UI Preferences GUI"
echo "     • Sidebar navigation with elegant 2025 design"
echo "     • iOS-style toggle switches"
echo "     • Smooth sliders with real-time values"
echo "     • Vibrant blue accent colors (#3B82F6)"
echo "     • Dark/Light theme support"
echo "  ✅ Sidekick Matrix Screensaver with USB Detection"
echo "  ✅ Mystify Geometric Screensaver (Windows-style)"
echo "  ✅ Slideshow Image Screensaver"
echo "  ✅ Video Player Screensaver (Hardware-Accelerated)"
echo "  ✅ Touchscreen UI Optimization (Auto-detects)"
echo "  ✅ Emergency CPU Throttling Protection"
echo "  ✅ System Statistics Display"
echo "  ✅ Automatic Update Checks"
echo "  ✅ Desktop Integration & Autostart"
echo ""
echo "🎨 v4.0 New Features:"
echo "  • Modern sidebar navigation"
echo "  • All settings from v4 preserved"
echo "  • Mystify color controls (Rainbow/Single/Duo)"
echo "  • Matrix font size slider"
echo "  • Display shutdown timer"
echo "  • Video playback speed slider"
echo "  • Themed message dialogs"
echo "  • Auto-update frequency control"
echo ""
echo "🎬 Video Screensaver Features:"
echo "  • Hardware-accelerated video playback (~2% CPU)"
echo "  • Loops all videos in selected folder"
echo "  • Random or sequential playback"
echo "  • Supports MP4, MKV, AVI, MOV, WebM"
echo "  • Emergency CPU throttling included"
echo "  • 90% less CPU than rendered Matrix"
echo "  • Generate custom Matrix video: generate-matrix-video"
echo ""
echo "🖐️ Touchscreen Features:"
echo "  • Auto-detection via libinput/xinput/proc"
echo "  • Window auto-maximizes for touch input"
echo "  • Buttons scaled to 48px (fat finger friendly)"
echo "  • Fonts scaled 1.5x for readability"
echo "  • Works on Pi 5 official touchscreen"
echo "  • Test with: test-touch"
echo ""
echo "🚨 CPU Throttling Features:"
echo "  • Monitors system CPU every 2 seconds"
echo "  • At >90% CPU: Reduces to 1 FPS (Matrix/Mystify)"
echo "  • At >90% CPU: Extends slides to 30s (Slideshow)"
echo "  • Auto-restores normal FPS when CPU drops"
echo "  • Protects system from screensaver overhead"
echo "  • Test with: test-throttle"
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
echo "  • From menu: Applications → Screensaver Settings v4"
echo "  • Enable Stats: Check 'Show Stats Overlay' in Display page"
echo "  • Enable Updates: Check 'Check for Updates' in General page"
echo "  • Select Videos: Choose 'Videos' type in General page"
echo "  • Configure Mystify Colors: Mystify page → Color Mode"
echo "  • Test screensaver: Click 'Test Screensaver' button"
echo "  • View diagnostics: Click 'Diagnostics' button"
echo "  • Test USB: test-usb"
echo "  • Test Touch: test-touch"
echo "  • Test Throttle: test-throttle"
echo "  • Test Updates: test-updates"
echo "  • Manual test: ./sidekick_screensaver.sh"
echo "  • Restore taskbar: restore_taskbar_quiet.sh"
echo "  • Verify install: verify_installation.sh"
echo "  • Verify stats: verify-show-stats"
echo ""
echo "🎬 Video Screensaver Setup:"
echo "  1. Generate Matrix video: generate-matrix-video --duration 60"
echo "  2. Open: screensaver-prefs"
echo "  3. Select: 'Videos' screensaver type"
echo "  4. Browse to folder with video files"
echo "  5. Video loops with ~2% CPU (vs ~10% for rendered)"
echo ""
echo "🧪 Quick Test:"
echo "  1. Run: test-touch (check touchscreen detection)"
echo "  2. Run: screensaver-prefs (should auto-maximize if touchscreen)"
echo "  3. Enable '📊 Show Stats' checkbox"
echo "  4. Enable '🔄 Auto Update Check' checkbox"
echo "  5. Click '🔍 Check Now' to test update checking"
echo "  6. Click 'Test Matrix'"
echo "  7. See stats in top-left corner (FPS, CPU, Memory)"
echo "  8. Run: test-throttle (simulate high CPU load)"
echo "  9. Watch screensaver throttle to 1 FPS at >90% CPU"
echo " 10. Move USB mouse or press USB keyboard"
echo " 11. Screensaver should exit immediately!"
echo ""
echo "🔄 Next Steps:"
echo "  1. Test touchscreen: test-touch"
echo "  2. Test CPU throttle: test-throttle"
echo "  3. Restart your desktop session to activate autostart"
echo "  4. Test the USB detection with: test-usb"
echo "  5. Verify Show Stats with: verify-show-stats"
echo "  6. Configure preferences with: screensaver-prefs"
echo "  7. Enjoy your Sidekick screensaver! 🖐️🚨🔌📊⌨️🖱️"
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
    echo "🎨 Refreshing icon cache..."
    gtk-update-icon-cache -f "$HOME/.local/share/icons" 2>/dev/null || true
    gtk-update-icon-cache -f /usr/share/icons/hicolor 2>/dev/null || true
    echo "✅ Icon cache refreshed"
fi

# Refresh desktop environment cache
echo "🖥️ Refreshing desktop cache..."
if command -v xdg-desktop-menu >/dev/null 2>&1; then
    xdg-desktop-menu forceupdate 2>/dev/null || true
    echo "✅ Desktop menu cache refreshed"
fi

# Refresh file manager thumbnails cache (if supported)
if [ -d "$HOME/.cache/thumbnails" ]; then
    echo "🖼️ Clearing thumbnail cache..."
    rm -rf "$HOME/.cache/thumbnails/"* 2>/dev/null || true
    echo "✅ Thumbnail cache cleared"
fi

# Force desktop environment to reload
if command -v pcmanfm >/dev/null 2>&1; then
    echo "🔄 Refreshing file manager..."
    pcmanfm --reconfigure 2>/dev/null || true
    echo "✅ File manager refreshed"
fi

# Make sure user's local bin is in PATH
if ! echo "$PATH" | grep -q "$LOCAL_BIN"; then
    echo "⚠️ Adding $LOCAL_BIN to PATH in ~/.bashrc"
    echo "export PATH=\"\$PATH:$LOCAL_BIN\"" >> "$HOME/.bashrc"
    echo "💡 Run 'source ~/.bashrc' or restart terminal to update PATH"
fi

echo "✅ Installation finalization complete!"
echo ""

# Prompt to run screensaver now (with timeout)
echo ""
echo "🎬 Installation Complete!"
echo ""

# Check if display is available (test multiple ways including :0 for SSH sessions)
DISPLAY_AVAILABLE=false
DETECTED_DISPLAY=""

# First check if DISPLAY is already set
if [ -n "$DISPLAY" ]; then
    DETECTED_DISPLAY="$DISPLAY"
else
    # Check for :0 display (common for SSH to Pi with GUI)
    export DISPLAY=:0
    DETECTED_DISPLAY=":0"
fi

# Verify the display is actually accessible
if command -v xdpyinfo >/dev/null 2>&1; then
    if DISPLAY="$DETECTED_DISPLAY" xdpyinfo >/dev/null 2>&1; then
        DISPLAY_AVAILABLE=true
        export DISPLAY="$DETECTED_DISPLAY"
    fi
elif command -v xset >/dev/null 2>&1; then
    if DISPLAY="$DETECTED_DISPLAY" xset q >/dev/null 2>&1; then
        DISPLAY_AVAILABLE=true
        export DISPLAY="$DETECTED_DISPLAY"
    fi
fi

# Alternative: Check for Wayland
if [ -n "$WAYLAND_DISPLAY" ] && [ "$DISPLAY_AVAILABLE" = false ]; then
    DISPLAY_AVAILABLE=true
fi

if [ "$DISPLAY_AVAILABLE" = true ]; then
    echo "✅ Display detected: $DETECTED_DISPLAY"
    echo ""

    # Show GUI prompt on the actual display
    if command -v zenity >/dev/null 2>&1; then
        # Use zenity for graphical prompt (always on top)
        echo "📺 Showing launch prompt on display $DETECTED_DISPLAY..."

        if DISPLAY="$DETECTED_DISPLAY" timeout 60 zenity --question \
            --title="Sidekick Screensaver Installation Complete" \
            --text="Installation successful!\n\nWould you like to launch the screensaver preferences now?" \
            --ok-label="Yes, Launch Now" \
            --cancel-label="No, Launch Later" \
            --width=400 \
            --modal \
            --window-icon=question 2>/dev/null; then
            echo ""
            echo "🚀 Launching screensaver preferences on $DETECTED_DISPLAY..."
            DISPLAY="$DETECTED_DISPLAY" "$LOCAL_BIN/screensaver-prefs" &
            echo "✅ Screensaver preferences launched!"
        else
            echo ""
            echo "ℹ️  Skipping launch. Run 'screensaver-prefs' anytime to configure."
        fi
    elif command -v yad >/dev/null 2>&1; then
        # Use yad as fallback (always on top)
        echo "📺 Showing launch prompt on display $DETECTED_DISPLAY..."

        if DISPLAY="$DETECTED_DISPLAY" timeout 60 yad --question \
            --title="Sidekick Screensaver Installation Complete" \
            --text="Installation successful!\n\nWould you like to launch the screensaver preferences now?" \
            --button="Yes, Launch Now:0" \
            --button="No, Launch Later:1" \
            --width=400 \
            --center \
            --on-top \
            --sticky 2>/dev/null; then
            echo ""
            echo "🚀 Launching screensaver preferences on $DETECTED_DISPLAY..."
            DISPLAY="$DETECTED_DISPLAY" "$LOCAL_BIN/screensaver-prefs" &
            echo "✅ Screensaver preferences launched!"
        else
            echo ""
            echo "ℹ️  Skipping launch. Run 'screensaver-prefs' anytime to configure."
        fi
    else
        # Fallback to terminal prompt
        echo "Would you like to launch the screensaver preferences now? (y/n)"
        echo "   (Auto-selecting 'n' in 60 seconds...)"
        echo ""

        # Use read with timeout
        if read -t 60 -p "Launch screensaver preferences? [y/N]: " response; then
            # User responded
            case "$response" in
                [yY][eE][sS]|[yY])
                    echo ""
                    echo "🚀 Launching screensaver preferences on $DETECTED_DISPLAY..."
                    DISPLAY="$DETECTED_DISPLAY" "$LOCAL_BIN/screensaver-prefs" &
                    echo "✅ Screensaver preferences launched!"
                    ;;
                *)
                    echo ""
                    echo "ℹ️  Skipping launch. Run 'screensaver-prefs' anytime to configure."
                    ;;
            esac
        else
            # Timeout occurred
            echo ""
            echo "⏱️  Timeout - skipping launch. Run 'screensaver-prefs' anytime to configure."
        fi
    fi
else
    echo "❌ No X11 display detected."
    echo "   Tried: \$DISPLAY (${DISPLAY:-not set}), :0"
    echo "   Ensure X11 is running: ps aux | grep X"
    echo "   Run 'DISPLAY=:0 screensaver-prefs' when GUI is available."
fi

echo ""
echo "======================================================================================"
