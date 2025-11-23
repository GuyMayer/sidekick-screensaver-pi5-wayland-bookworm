# Automatic Update Check System

## Overview

Sidekick Screensaver now includes an automatic monthly update check system that helps keep your installation current with the latest features and bug fixes.

## Features

### 🔄 **Automatic Checking**
- **Monthly Schedule**: Checks for updates every 30 days by default
- **Background Operation**: Runs in background threads without blocking the GUI
- **Smart Timing**: Only checks when it's actually time (avoids unnecessary network requests)
- **Persistent Settings**: Remembers when you last checked and your preferences

### 📱 **User Interface**
- **GUI Controls**: Easy toggle in System Settings section
- **Manual Check**: "🔍 Check Now" button for immediate checking
- **Status Updates**: Progress shown in status bar
- **Settings Integration**: Saves preferences automatically

### 🔔 **Notifications**
- **System Tray**: Update notifications appear in system tray
- **Dialog Boxes**: Detailed update information with release notes
- **User Choice**: Download update, remind later, or disable notifications
- **Respectful**: Only shows notifications when updates are actually available

## How It Works

### Version Comparison
```python
# Semantic versioning comparison (e.g., 3.1.0 > 3.0.0)
latest_parts = [3, 1, 0]
current_parts = [3, 0, 0]
# Returns True if latest > current
```

### GitHub API Integration
- **Repository**: Checks `https://api.github.com/repos/GuyMayer/sidekick-screensaver/releases/latest`
- **User Agent**: Identifies as "Sidekick-Screensaver-UpdateChecker/1.0"
- **Error Handling**: Graceful fallback if network is unavailable
- **Timeout**: 10-second timeout to avoid hanging

### Update Schedule
```
Day 0:  Install Sidekick Screensaver
Day 30: First automatic update check
Day 60: Second automatic update check
...
```

## GUI Integration

### System Settings Section
```
🔧 System Settings
├── 📱 Show Taskbar Icon
├── 🚀 Start on Boot
├── 🌙 Dark Mode
├── 🔄 Auto Update Check    [NEW]
└── 🔍 Check Now           [NEW]
```

### Update Dialog Options
- **🌐 Download Update**: Opens browser to GitHub release page
- **⏭️ Remind Later**: Will check again next month
- **🔕 Disable Updates**: Turns off automatic checking

## Settings Storage

### Configuration File
```json
{
  "auto_update_check": true,
  "last_update_check": "2025-09-08T10:30:00",
  "update_check_frequency": 30,
  "update_notification": true
}
```

### Location
- **Path**: `~/.config/screensaver/settings.json`
- **Automatic**: Created and updated automatically
- **Persistent**: Survives system reboots and upgrades

## Testing

### Test Command
```bash
# Run comprehensive update check tests
test-updates

# Manual test in terminal
python3 test_update_check.py
```

### Test Coverage
- ✅ Version comparison logic
- ✅ Update timing calculations
- ✅ GitHub API accessibility
- ✅ Settings file handling
- ✅ Error handling scenarios

## Error Handling

### Network Issues
- **Graceful Fallback**: No error dialogs for network problems
- **Silent Retry**: Will try again next scheduled time
- **User Feedback**: Only shows errors for manual checks

### Invalid Data
- **Default Behavior**: Assumes update needed if data is invalid
- **Logging**: Errors logged to console for debugging
- **Recovery**: System continues working even with bad data

## Privacy & Security

### Data Collection
- **Minimal**: Only checks version numbers and release info
- **No Tracking**: No user data sent to servers
- **Open Source**: All code visible and auditable

### Network Requests
- **HTTPS Only**: Secure connections to GitHub API
- **Read Only**: Only downloads public release information
- **Timeout**: Limited request time to avoid hanging

## Customization

### Change Check Frequency
```python
# In settings.json, change update_check_frequency
"update_check_frequency": 7,  # Check weekly instead of monthly
```

### Disable Completely
- **GUI Method**: Uncheck "🔄 Auto Update Check"
- **Manual Method**: Set `"auto_update_check": false` in settings
- **Permanent**: Choice is remembered across restarts

## Repository Setup

When you publish to GitHub, the update checker will automatically work with:

### Required Repository Structure
```
GuyMayer/sidekick-screensaver/
├── releases/
│   └── v3.1.0 (with release notes)
└── README.md
```

### Release Tags
- **Format**: `v3.1.0` (semantic versioning with 'v' prefix)
- **Detection**: Automatically strips 'v' prefix for comparison
- **Fallback**: Works with or without 'v' prefix

## Benefits

### For Users
- **Always Current**: Automatic notifications about improvements
- **Security**: Get security fixes promptly
- **Features**: Don't miss new screensaver modes and capabilities
- **Choice**: Full control over update notifications

### For Developer
- **Engagement**: Users stay current with latest version
- **Feedback**: More users on latest version = better bug reports
- **Distribution**: Reduces need for manual update announcements
- **Professional**: Shows commitment to ongoing maintenance

## Implementation Details

### Threading
- **Background**: Network requests run in daemon threads
- **Non-blocking**: GUI remains responsive during checks
- **Thread Safety**: Uses QTimer.singleShot for main thread updates

### Performance
- **Lightweight**: Minimal memory and CPU usage
- **Efficient**: Only checks when actually needed
- **Cached**: Remembers last check to avoid redundant requests

### Compatibility
- **Python 3.6+**: Uses modern async patterns
- **PyQt6**: Integrates with existing Qt event system
- **Cross-platform**: Works on Linux, Windows, macOS

## Future Enhancements

### Possible Additions
- **Automatic Downloads**: Option to download updates automatically
- **Beta Channel**: Opt-in to test pre-release versions
- **Change Log Display**: Show detailed release notes in GUI
- **Update History**: Track update installation history

### Configuration Options
- **Custom Repository**: Point to different GitHub repository
- **Update Channel**: Stable vs beta release tracking
- **Notification Style**: System notifications vs GUI dialogs
- **Download Directory**: Choose where to save update files

## Conclusion

The automatic update check system provides a professional, user-friendly way to keep Sidekick Screensaver current while respecting user choice and privacy. It integrates seamlessly with the existing GUI and provides comprehensive testing and error handling.

Users get the benefits of staying current with minimal effort, while maintaining full control over their update experience.
