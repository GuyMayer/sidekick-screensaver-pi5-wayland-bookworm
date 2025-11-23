# Development vs Production Folder Structure

## 📁 Folder Organization

This Pi has a **clear separation** between development and production code:

### 🛠️ Development Folder (Source Code)
```
~/projects/automation/Sidekick Screensaver/
```

**Purpose**: Active development, version control, source code
**Features**:
- ✅ Git repository (connected to GitHub)
- ✅ Full source code with comments
- ✅ Documentation and README files
- ✅ Install/update scripts
- ✅ Change history and version control

**Key Files**:
- `sidekick_widget.py` - Matrix screensaver source
- `mystify_widget.py` - Mystify screensaver source
- `slideshow_widget.py` - Slideshow screensaver source
- `video_widget.py` - Video player screensaver source
- `screensaver_preferences.py` - Main GUI application (PyQt6)
- `regenerate_autolock_script.py` - Autolock script generator
- `Sidekick_Installer.sh` - Installation script

**Workflow**:
1. Edit code here
2. Test changes
3. Commit to git
4. Push to GitHub
5. Install/copy to production
6. GUI automatically regenerates autolock script on Apply

---

### 🚀 Production Folder (Running Code)
```
~/.local/bin/
```

**Purpose**: Active running executables used by the system
**Features**:
- ✅ Optimized for execution
- ✅ Executable permissions set
- ✅ In system PATH
- ✅ Used by autostart and launchers
- ❌ No git (standalone files)

**Key Files**:
- `sidekick_widget.py` - Running Matrix screensaver
- `mystify_widget.py` - Running Mystify screensaver
- `slideshow_widget.py` - Running Slideshow screensaver
- `video_widget.py` - Running Video player screensaver
- `wayland_sidekick_autolock.sh` - Auto-generated autolock script (regenerates on Apply)
- `regenerate_autolock_script.py` - Script regeneration utility
- `launch_configured_screensaver.sh` - Launch script
- `sidekick_screensaver.sh` - Direct launcher

**Used By**:
- Screensaver preferences app
- Autostart configuration
- System launchers

---

## 🔄 Keeping Them in Sync

### Development → Production (Installing Updates)
```bash
# Method 1: Manual copy (what we just did)
cp ~/projects/automation/"Sidekick Screensaver"/*.py ~/.local/bin/

# Method 2: Use installer (recommended)
cd ~/projects/automation/"Sidekick Screensaver"
./Sidekick_Installer.sh --update

# Method 3: Individual widget
cp ~/projects/automation/"Sidekick Screensaver"/sidekick_widget.py ~/.local/bin/
chmod +x ~/.local/bin/sidekick_widget.py
```

### Production → Development (Saving Live Changes)
```bash
# Copy optimized running code back to development
cp ~/.local/bin/sidekick_widget.py ~/projects/automation/"Sidekick Screensaver"/

# Commit to git
cd ~/projects/automation/"Sidekick Screensaver"
git add sidekick_widget.py
git commit -m "Performance optimizations from production testing"
git push
```

---

## ⚠️ Important Rules

### **DO**:
- ✅ Edit in development folder
- ✅ Test in production folder
- ✅ Commit development changes to git
- ✅ Keep both folders in sync
- ✅ Document changes in commit messages

### **DON'T**:
- ❌ Edit files directly in `~/.local/bin/` (unless testing)
- ❌ Forget to copy changes back to development
- ❌ Run installers without checking development folder first
- ❌ Lose production optimizations by overwriting with old dev code

---

## 📊 Current Status (Nov 10, 2025)

### ✅ Synchronized!
Both folders now have the same optimized code with complete settings persistence:

**Recent Improvements**:
- ✅ Complete settings persistence system implemented
- ✅ All widget scripts load full settings from `~/.config/screensaver/settings.json`
- ✅ Autolock script auto-regenerates when Apply is clicked
- ✅ Screensaver type properly tracked and launched (Matrix/Mystify/Videos/Slideshow)
- ✅ All preferences persist across reboots (colors, speed, FPS, stats, etc.)
- ✅ Stats drift setting saved and loaded
- ✅ 15 FPS default with intelligent throttling
- ✅ Auto CPU limiting enabled by default
- ✅ Stats display with anti-burn-in drift

**Last Sync**: Nov 10, 2025
**Last Major Update**: Settings Persistence System (Nov 10, 2025)
**Committed**: [Pending]
**Pushed to GitHub**: [Pending]

---

## 🔗 Related Folders

### Other Development Folders:
```
~/projects/automation/                    # Main automation projects
~/projects/automation/Sidekick Screensaver/  # This screensaver
```

### Other Production Folders:
```
~/.local/bin/                            # User executables
~/.config/screensaver/settings.json      # Screensaver configuration
~/.config/autostart/                     # Autostart applications
```

---

## 🚀 Quick Reference

**Check what's running**:
```bash
ps aux | grep widget
```

**Test development version**:
```bash
cd ~/projects/automation/"Sidekick Screensaver"
python3 sidekick_widget.py
```

**Update production from development**:
```bash
cp ~/projects/automation/"Sidekick Screensaver"/sidekick_widget.py ~/.local/bin/
```

**Commit development changes**:
```bash
cd ~/projects/automation/"Sidekick Screensaver"
git add .
git commit -m "Your changes"
git push
```
