# Contributing to Sidekick Screensaver

Thank you for your interest in contributing to Sidekick Screensaver! This document provides guidelines for contributing to the project.

## 🤝 Ways to Contribute

### 🐛 Bug Reports
- Use the [GitHub Issues](https://github.com/yourusername/sidekick-screensaver/issues) page
- Include detailed steps to reproduce
- Provide system information (OS, Python version, desktop environment)
- Include relevant log output

### 💡 Feature Requests
- Check existing issues first to avoid duplicates
- Describe the feature and its use case
- Consider implementation complexity
- Discuss with maintainers before starting large features

### 🔧 Code Contributions
- Fork the repository
- Create a feature branch (`git checkout -b feature/amazing-feature`)
- Make your changes
- Test thoroughly
- Submit a pull request

## 🛠️ Development Setup

### Prerequisites
```bash
# Install development dependencies
sudo apt update
sudo apt install python3 python3-pip python3-venv
sudo apt install python3-pyqt6 python3-psutil
sudo apt install git build-essential
```

### Local Development
```bash
# Clone your fork
git clone https://github.com/yourusername/sidekick-screensaver.git
cd sidekick-screensaver

# Create virtual environment (optional but recommended)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

### Testing Your Changes
```bash
# Run the application
python3 screensaver_preferences.py

# Test installation script
sudo bash Sidekick_Installer.sh

# Run verification
./verify_installation.sh
./verify-show-stats
```

## 📝 Coding Standards

### Python Style
- Follow [PEP 8](https://pep8.org/) style guide
- Use meaningful variable and function names
- Add docstrings for classes and functions
- Keep functions focused and small

### Code Organization
```python
# Good function structure
def calculate_drift_position(self, screen_width, screen_height):
    """Calculate current drift position for stats display.

    Args:
        screen_width (int): Screen width in pixels
        screen_height (int): Screen height in pixels

    Returns:
        tuple: (x, y) position for stats display
    """
    # Implementation here
    pass
```

### GUI Development
- Use PyQt6 best practices
- Implement proper error handling
- Ensure widgets are properly destroyed
- Test on different screen sizes

### System Integration
- Check for required dependencies
- Handle missing system components gracefully
- Provide meaningful error messages
- Test on multiple Linux distributions

## 🧪 Testing Guidelines

### Manual Testing Checklist
- [ ] GUI launches without errors
- [ ] All screensaver modes work correctly
- [ ] System tray icon persists after interruption
- [ ] Settings are saved and loaded correctly
- [ ] Installation script completes successfully
- [ ] Autostart functionality works
- [ ] USB detection interrupts screensaver
- [ ] Stats display and drift work properly

### Test Environments
Please test on:
- Different Linux distributions (Ubuntu, Debian, Fedora, etc.)
- Various desktop environments (GNOME, KDE, XFCE, LXDE)
- Multiple screen configurations
- Different Python versions (3.7+)

## 📋 Pull Request Process

### Before Submitting
1. **Test thoroughly** on your system
2. **Update documentation** if needed
3. **Add yourself** to the contributors list
4. **Write clear commit messages**

### Commit Message Format
```
type(scope): brief description

Longer description if needed

Fixes #issue-number
```

Examples:
```
feat(gui): add drift checkbox for stats display

Add user-controllable checkbox to enable/disable stats drift
feature. Default is enabled to prevent screen burn-in.

Fixes #123
```

```
fix(tray): prevent application quit on screensaver exit

Set setQuitOnLastWindowClosed(False) to ensure system tray
persists when screensaver widgets are closed.

Fixes #456
```

### Pull Request Description
Include:
- **What** changes were made
- **Why** the changes were necessary
- **How** to test the changes
- **Screenshots** for GUI changes
- **Breaking changes** if any

## 🐛 Bug Report Template

```markdown
**Bug Description**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '...'
3. See error

**Expected Behavior**
What you expected to happen.

**Screenshots**
If applicable, add screenshots.

**System Information:**
 - OS: [e.g. Ubuntu 22.04]
 - Desktop: [e.g. GNOME 42]
 - Python Version: [e.g. 3.10.6]
 - PyQt6 Version: [e.g. 6.4.0]

**Additional Context**
Any other context about the problem.

**Logs**
```
Include relevant log output here
```
```

## 💡 Feature Request Template

```markdown
**Is your feature request related to a problem?**
A clear description of what the problem is.

**Describe the solution you'd like**
A clear description of what you want to happen.

**Describe alternatives you've considered**
Other solutions you've thought about.

**Additional context**
Any other context or screenshots about the feature request.

**Implementation Ideas**
If you have ideas about how this could be implemented.
```

## 🏗️ Architecture Overview

### Core Components
- **screensaver_preferences.py** - Main GUI application
- **sidekick_widget.py** - Matrix screensaver implementation
- **mystify_widget.py** - Geometric pattern screensaver
- **slideshow_widget.py** - Image slideshow screensaver
- **Sidekick_Installer.sh** - Installation script

### Key Classes
- `ScreensaverPreferences` - Main GUI class
- `MatrixWidget` - Matrix rain implementation
- `MystifyWidget` - Geometric patterns
- `SlideshowWidget` - Image slideshow

### Settings Management
- **Configuration File**: `~/.config/screensaver/settings.json`
- **Auto-save**: Changes saved automatically on Apply button
- **Persistent Settings**: All preferences persist across reboots
- **Widget Loading**: Each widget script loads complete settings on startup
- **Autolock Script**: Automatically regenerates when settings change via `regenerate_autolock_script.py`

### Settings Persistence Flow
1. User changes settings in GUI → `auto_save_settings()` updates JSON
2. User clicks Apply → `apply_settings()` saves and calls `update_autostart_script()`
3. `update_autostart_script()` → Runs `regenerate_autolock_script.py`
4. Script reads settings → Determines correct screensaver type (Matrix/Mystify/Videos/Slideshow)
5. Generates `wayland_sidekick_autolock.sh` → Points to correct widget script
6. On boot/timeout → Widget loads ALL settings from `settings.json`

### Adding New Settings
```python
# In screensaver_preferences.py - add to default_settings dict
'my_new_setting': default_value,

# In auto_save_settings() and apply_settings() - add to settings.update()
'my_new_setting': self.safe_get_checkbox_value(self.my_checkbox, default_value),

# In widget script (e.g., sidekick_widget.py) - add to load_saved_settings()
'my_new_setting': default_value,

# Setting will now persist across sessions automatically
```

## 🎯 Development Priorities

### High Priority
- Bug fixes and stability improvements
- Performance optimizations
- Documentation improvements
- Cross-platform compatibility

### Medium Priority
- New screensaver modes
- Enhanced customization options
- Better error handling
- Automated testing

### Low Priority
- Advanced features
- Plugin system
- Remote control capabilities
- Mobile companion app

## 📞 Getting Help

### Communication Channels
- **GitHub Issues** - Bug reports and feature requests
- **GitHub Discussions** - General questions and community chat
- **Wiki** - Detailed documentation and guides

### Code Review Process
- All contributions require review
- Maintainers will provide constructive feedback
- Be patient and responsive to review comments
- Multiple iterations are normal and expected

## 🙏 Recognition

Contributors will be:
- Added to the contributors list in README.md
- Mentioned in release notes for significant contributions
- Credited in commit messages and pull request descriptions

Thank you for contributing to Sidekick Screensaver! 🎉
