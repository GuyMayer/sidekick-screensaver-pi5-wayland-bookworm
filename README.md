# Sidekick Screensaver

> *"Necessity is the mother of all invention"* - and sometimes you just need to know if your Pi has crashed.

## The Story Behind Sidekick

What started as a simple need became a full-featured solution. When running critical automation systems on Raspberry Pi, visual feedback is essential - but finding a reliable screensaver for Wayland environments proved surprisingly challenging. Traditional X11 screensavers don't play well with modern Wayland compositors, leaving a gap in the ecosystem.

Rather than compromise, this project was born from the collaboration between practical necessity and modern development tools. Built with the assistance of GitHub Copilot and leveraging proven open-source libraries, Sidekick Screensaver bridges the gap between system monitoring and visual appeal.

What emerged is more than just a "crash detector" - it's a sophisticated screensaver system that combines real-time system statistics, anti-burn-in technology, and eye-catching visual effects. From Matrix-style digital rain to hypnotic geometric patterns, Sidekick proves that utilitarian software doesn't have to sacrifice style.

*Because every developer deserves to know their system is alive - and it might as well look good doing it.*

---

A modern, feature-rich screensaver system for Linux with PyQt6 GUI, multiple screensaver modes, performance monitoring, and intelligent power management.

## ✨ Features

### 🎬 Screensaver Modes
- **Matrix Digital Rain** - Classic green digital rain effect with customizable colors
- **Mystify** - Windows-style geometric patterns with configurable complexity
- **Slideshow** - Image slideshow with transition effects
- **None** - Disable screensaver but keep monitoring

### 📊 Performance Monitoring
- **Real-time Stats Display** - FPS, CPU usage, memory consumption
- **Anti-burn-in Drift** - Stats slowly move around screen edges (8-minute cycle)
- **Performance Overlay** - Optional statistics with color cycling
- **Intelligent FPS Throttling** - Automatic performance adjustment

### 🔧 System Integration
- **Complete Settings Persistence** - All preferences persist across reboots
- **Auto-regenerating Scripts** - Autolock script updates automatically on Apply
- **System Tray Persistence** - Remains accessible after interruptions
- **Auto-start Support** - Launches with system boot
- **USB Activity Detection** - Instant exit on mouse/keyboard activity
- **Multi-display Support** - Works with multiple monitors
- **Power Management** - Automatic display timeout

### 🎨 Professional GUI
- **Dark/Light Themes** - Professional QDarkStyle integration
- **Organized Layout** - Three logical sections (System, Screen, Timer)
- **Real-time Preview** - Test screensavers before applying
- **Comprehensive Settings** - Fine-tune all aspects of behavior

## 🚀 Quick Start

### Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/sidekick-screensaver.git
cd sidekick-screensaver

# Run the installer
sudo bash Sidekick_Installer.sh
```

### Usage
```bash
# Launch preferences GUI
screensaver-prefs

# Test installation
verify_installation.sh

# Verify features
verify-show-stats
```

## 💝 Support This Project

If Sidekick Screensaver has been useful to you, consider supporting its development:

<a href="https://github.com/sponsors/GuyMayer">
  <img src="https://img.shields.io/badge/Sponsor-GitHub-pink?style=for-the-badge&logo=githubsponsors" alt="GitHub Sponsors"/>
</a>
<a href="https://ko-fi.com/guymayer">
  <img src="https://img.shields.io/badge/Support-Ko--fi-orange?style=for-the-badge&logo=kofi" alt="Ko-fi"/>
</a>
<a href="https://buymeacoffee.com/studiomailt">
  <img src="https://img.shields.io/badge/Buy%20Me%20A%20Coffee-yellow?style=for-the-badge&logo=buymeacoffee" alt="Buy Me A Coffee"/>
</a>
<a href="https://paypal.me/guymayer">
  <img src="https://img.shields.io/badge/PayPal-blue?style=for-the-badge&logo=paypal" alt="PayPal"/>
</a>

Your support helps maintain and improve this project! ☕ Even a small coffee donation makes a difference and motivates continued development of new features and improvements.

## 📁 Essential Files

### Core Installation
- `Sidekick_Installer.sh` - Main installation script
- `verify_installation.sh` - Verify installation success
- `verify_show_stats_installation.sh` - Verify stats feature

### Screensaver Engine
- `sidekick_widget.py` - Matrix screensaver with USB detection
- `mystify_widget.py` - Geometric patterns screensaver
- `slideshow_widget.py` - Slideshow screensaver
- `video_widget.py` - Video player screensaver
- `screensaver_preferences.py` - PyQt6 GUI application
- `regenerate_autolock_script.py` - Autolock script generator
- `sidekick_screensaver.sh` - Screensaver launcher
- `wayland_sidekick_autolock.sh` - Auto-generated autostart script

### Configuration
- `~/.config/screensaver/settings.json` - Persistent settings storage
- Auto-regenerates on Apply to ensure correct screensaver launches

### Utility Scripts
- `close_all_guis.sh` - Close all GUI instances
- `restore_desktop.sh` - Restore desktop environment
- `restore_taskbar_quiet.sh` - Silent taskbar restoration
- `restore_background.sh` - Restore desktop background
- `quick_start_guide.sh` - Quick setup guide

### Assets
- `README.md` - This documentation file

## 🎮 Usage

After installation:
- **Launch GUI**: `screensaver-prefs`
- **From menu**: Applications → Sidekick screensaver
- **Test USB detection**: `test-usb`
- **Manual test**: `./sidekick_screensaver.sh`

## 🔧 Features

- ✅ **Sidekick Digital Rain**: Classic matrix-style falling characters
- ✅ **USB Activity Detection**: Instant exit on mouse/keyboard activity
- ✅ **System Statistics**: Real-time FPS, CPU, and memory monitoring
- ✅ **Professional Dark Mode**: QDarkStyle-powered dark theme with auto-restart
- ✅ **Mystify Geometric**: Windows-style geometric screensaver patterns
- ✅ **Slideshow Mode**: Image slideshow with statistics overlay
- ✅ **Auto-start Configuration**: Automatic activation after idle time
- ✅ **Desktop Integration**: Clean menu integration and restoration
- ✅ **Wayland/X11 Compatibility**: Works across desktop environments

## 🌙 Dark Mode

The GUI includes a professional dark mode feature:

- **Toggle**: Click "🌙 Dark Mode" checkbox in the top row
- **Auto-Restart**: GUI automatically restarts to apply theme
- **Professional**: Uses QDarkStyle library for industry-standard appearance
- **Persistent**: Theme choice saved and restored on startup
- **Working Controls**: All spinboxes, dropdowns, and controls function perfectly
- **No Squares**: Proper native Qt icons instead of broken CSS triangles

**Quick Usage:**
1. Launch `screensaver-prefs`
2. Click "🌙 Dark Mode" checkbox
3. GUI restarts automatically with dark theme applied
4. All controls work perfectly with proper icons

For detailed documentation, see [DARK_MODE_DOCUMENTATION.md](DARK_MODE_DOCUMENTATION.md)

## 📊 System Statistics Display

When enabled, shows:
- Real-time FPS monitoring (current vs target)
- System CPU usage (10-sample average)
- Screensaver process CPU usage
- System memory percentage
- Screensaver process memory (MB)
- Anti-burn-in color cycling (every 5 seconds)

## 🔌 USB Detection

- Monitors USB interrupts at 500ms intervals
- Instant screensaver exit on USB mouse movement
- Instant screensaver exit on USB keyboard activity
- Hardware-level activity detection
- Dual detection system (USB + PyQt6 events)

## 🎬 Screensaver Timeline

- **0-5 minutes**: Normal desktop use
- **5-10 minutes**: Sidekick digital rain starts! 🟢💚
  - USB mouse/keyboard = INSTANT EXIT
- **10+ minutes**: Screen turns off (power saving)

## 🧪 Quick Test

1. Run: `screensaver-prefs`
2. Enable '📊 Show Stats' checkbox
3. Click 'Test Sidekick'
4. See stats in top-left corner (FPS, CPU, Memory)
5. Move USB mouse or press USB keyboard
6. Screensaver should exit immediately!

## 🔄 Next Steps

1. Restart your desktop session to activate autostart
2. Test the USB detection with: `test-usb`
3. Verify Show Stats with: `verify-show-stats`
4. Configure preferences with: `screensaver-prefs`
5. Enjoy your Sidekick screensaver with USB detection & stats! 🔌📊⌨️🖱️
