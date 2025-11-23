# Screensaver Preferences v4.0 - Modern UI Migration Guide

## 🎨 What's New in v4.0

### Modern 2025 Aesthetic
- **Sidebar Navigation** - Clean left sidebar with "General", "Display & Performance", and "Source" pages
- **iOS-Style Toggles** - Modern toggle switches replace traditional checkboxes
- **Segmented Controls** - Professional button groups for theme selection
- **Smooth Sliders** - Real-time value display with elegant blue accent handles
- **Generous Whitespace** - Sophisticated spacing with no cramped UI elements
- **Vibrant Blue Accents** - Professional #3B82F6 blue for active elements

### All Original Features Preserved
- ✅ Matrix, Mystify, and Slideshow screensaver modes
- ✅ System tray integration
- ✅ Auto-shutdown timer
- ✅ FPS throttling and performance settings
- ✅ Multi-display support
- ✅ Settings persistence
- ✅ Single instance protection

---

## 🧪 Testing v4.0 (Safe - Won't Affect Current System)

### Option 1: Run from Terminal
```bash
cd "/home/guy/projects/automation/Sidekick Screensaver"
./launch_gui_v4.sh
```

### Option 2: Direct Python
```bash
cd "/home/guy/projects/automation/Sidekick Screensaver"
python3 screensaver_preferences_v4.py
```

**Important:** v4 uses the **same settings file** (`~/.config/screensaver/settings.json`), so your existing preferences will be loaded automatically!

---

## 📸 Visual Comparison

### Before (v3.0)
- Traditional grouped boxes with borders
- Standard checkboxes
- Compact layout with less spacing
- Green accent color (Matrix theme)

### After (v4.0)
- Sidebar navigation with clean pages
- Modern toggle switches (iOS-style)
- Generous spacing and elegant typography
- Blue accent color (#3B82F6)

---

## 🔄 Switching to v4.0 Permanently

Once you've tested v4 and are happy with it, you can make it the default:

### Method 1: Update launch_gui.sh
```bash
cd "/home/guy/projects/automation/Sidekick Screensaver"

# Backup current launcher
cp launch_gui.sh launch_gui_v3_backup.sh

# Edit launch_gui.sh
nano launch_gui.sh
```

Change the line:
```bash
python3 screensaver_preferences.py
```

To:
```bash
python3 screensaver_preferences_v4.py
```

### Method 2: Rename Files (Safer)
```bash
cd "/home/guy/projects/automation/Sidekick Screensaver"

# Backup v3
mv screensaver_preferences.py screensaver_preferences_v3_backup.py

# Make v4 the default
cp screensaver_preferences_v4.py screensaver_preferences.py
```

### Method 3: Reinstall with v4
If you want to update the system-wide installation:

```bash
cd "/home/guy/projects/automation/Sidekick Screensaver"

# Edit Sidekick_Installer.sh to copy v4 instead of v3
# Then run the installer
./Sidekick_Installer.sh
```

---

## 🐛 Troubleshooting

### "Another instance is already running"
The old v3 GUI might still be open. Close it first:
```bash
pkill -f screensaver_preferences.py
```

Then launch v4:
```bash
./launch_gui_v4.sh
```

### "Module not found" errors
Make sure you're in the correct directory:
```bash
cd "/home/guy/projects/automation/Sidekick Screensaver"
python3 screensaver_preferences_v4.py
```

### Settings not loading
Both v3 and v4 use the same settings file, so this shouldn't happen. Check:
```bash
ls -la ~/.config/screensaver/settings.json
```

---

## 🔙 Rolling Back to v3

If you need to go back to v3:

```bash
cd "/home/guy/projects/automation/Sidekick Screensaver"

# Close v4 if running
pkill -f screensaver_preferences_v4.py

# Launch v3
./launch_gui.sh
```

Or restore from backup if you renamed files:
```bash
mv screensaver_preferences_v3_backup.py screensaver_preferences.py
```

---

## 📋 Quick Comparison Table

| Feature | v3.0 | v4.0 |
|---------|------|------|
| **UI Style** | Traditional grouped boxes | Modern sidebar navigation |
| **Toggles** | Checkboxes | iOS-style switches |
| **Theme** | Green Matrix cyberpunk | Blue 2025 modern |
| **Layout** | Compact vertical | Spacious with pages |
| **Settings File** | `~/.config/screensaver/settings.json` | Same file ✅ |
| **Features** | All features | All features ✅ |
| **System Tray** | Yes | Yes ✅ |
| **Single Instance** | Yes | Yes (separate lock) ✅ |

---

## 💡 Tips

1. **Test First** - Run v4 alongside v3 to compare
2. **Settings Transfer** - Your settings automatically carry over
3. **Both Can Coexist** - v3 and v4 can both be installed (different lock files)
4. **Launcher Scripts** - Use different launchers for easy switching

---

## 🎯 Recommended Migration Path

1. ✅ **Test v4** using `./launch_gui_v4.sh`
2. ✅ **Use it for a day** to ensure everything works
3. ✅ **Compare layouts** - make sure you prefer the new design
4. ✅ **Switch permanently** using Method 1 above
5. ✅ **Keep v3 as backup** in case you need to roll back

---

## 📞 Support

If you encounter issues with v4:
- Check the terminal output for error messages
- Compare with v3 behavior
- Report bugs with specific steps to reproduce

**Note:** v4 is a complete rewrite of the UI layer but preserves all backend functionality. Settings, timers, and screensaver logic remain identical to v3.
