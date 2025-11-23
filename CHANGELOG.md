# Sidekick Screensaver Changelog

## [2025-11-23] - Launcher & Single Instance Fixes

### Fixed
- **Launcher Not Opening GUI** - Fixed desktop launcher and system menu shortcuts
  - Updated symlink `screensaver-prefs` to point to v4 instead of v3
  - Refreshed desktop database cache for immediate effect
  - Fixed autostart configuration to use correct v4 script

- **Single Instance Window Management** - Added intelligent window restoration
  - Created `screensaver-show-window` wrapper script
  - When launcher is clicked and app is running, shows and maximizes existing window
  - Uses `wmctrl` to find and restore hidden/minimized windows
  - Prevents "Another instance is already running" error blocking user access
  - Falls back to starting new instance if none exists

### Changed
- **Desktop Entry** - Updated to use wrapper script for better UX
  - `Exec=/home/guy/.local/bin/screensaver-show-window`
  - Handles both starting and showing existing instance seamlessly

### Technical Details
- **Wrapper Logic**:
  1. Checks if screensaver process is running (`pgrep`)
  2. If not running → Launches v4 normally
  3. If running → Uses `wmctrl` to show and maximize window
  4. Falls back to signal handling if wmctrl fails

- **Files Updated**:
  - `~/.local/bin/screensaver-show-window` - New wrapper script
  - `~/.local/share/applications/sidekick-screensaver-preferences.desktop` - Updated launcher
  - `~/.config/autostart/screensaver-preferences-v4.desktop` - Updated autostart
  - `~/.local/bin/screensaver-prefs` - Symlink now points to v4

### User Impact
- Clicking launcher icon now **always** shows the GUI
- No more confusion about whether app is running
- Seamless experience between first launch and subsequent clicks
- System tray icon remains optional fallback

---

## [Previous Versions]
See PowerMate/CHANGELOG.md for PowerMate controller updates.
