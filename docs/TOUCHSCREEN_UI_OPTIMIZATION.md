# Touchscreen UI Optimization - Sidekick Screensaver

## Feature Overview

The Sidekick Screensaver preferences GUI now automatically detects touchscreen devices and optimizes the user interface for fat finger touch input. When a touchscreen is detected, the application maximizes and scales all controls for easier touch interaction.

## Automatic Detection

### Detection Methods

The system uses 4 detection methods (any positive result enables touch mode):

1. **xinput** - X11 input device listing
   ```bash
   xinput list | grep -i touch
   ```

2. **libinput** - Wayland-native device listing (most reliable on Pi 5)
   ```bash
   libinput list-devices | grep -i touchscreen
   ```

3. **/proc/bus/input/devices** - Universal kernel interface
   ```bash
   cat /proc/bus/input/devices | grep -i touchscreen
   ```

4. **/dev/input/** - Device node enumeration
   ```bash
   ls /dev/input/ | grep -i touchscreen
   ```

### Testing Detection

Run the test script to see which methods detect your touchscreen:

```bash
cd "/home/guy/projects/automation/Sidekick Screensaver"
python3 test_touch_ui.py
```

Example output on Raspberry Pi 5 with touchscreen:
```
✅ Method 2 (libinput): Touchscreen DETECTED
✅ Method 3 (/proc): Touchscreen DETECTED

✅ TOUCHSCREEN MODE ENABLED
   UI will be optimized for touch input:
   • Window will maximize automatically
   • Buttons increased to 48px height (touch-friendly)
   • Font sizes scaled up 1.5x
   • Controls enlarged for fat finger use
```

## UI Optimizations

### Touch Mode (Touchscreen Detected)

**Window Behavior:**
- ✅ Auto-maximizes on startup
- ✅ Window size: 900x1200 (larger for scrolling content)
- ✅ No maximum width restriction

**Control Sizing:**
- ✅ Buttons: 48px minimum height (Apple HIG touch target size)
- ✅ Checkboxes: 48px minimum height
- ✅ Input controls: 44px minimum height (combo boxes, spinboxes)
- ✅ Sliders: 40px minimum height (easier grabbing)

**Font Scaling:**
- ✅ All text scaled by 1.5x
- ✅ Labels scaled by 1.3x
- ✅ Group box titles scaled by 1.4x and bolded

**Affected Widgets:**
- System settings checkboxes
- Screensaver type dropdown
- FPS and display target selectors
- Timeout spinboxes
- All buttons (Test, Apply, Reset, etc.)
- Matrix/Mystify/Slideshow controls
- Optional widgets (conditional on screensaver type)

### Mouse Mode (No Touchscreen)

**Window Behavior:**
- Standard 600x800 window size
- Maximum width limited to 600px
- Compact layout

**Control Sizing:**
- Default PyQt6 widget sizes
- Normal button heights (≈24-30px)
- Standard fonts

## Code Architecture

### Core Components

**1. Touchscreen Detection (`detect_touchscreen()`):**
```python
def detect_touchscreen(self) -> bool:
    """Detect if a touchscreen is connected for UI optimization"""
    # Tests 4 methods, returns True if any detect touchscreen
```

**2. Touch Scaling Application (`apply_touch_scaling()`):**
```python
def apply_touch_scaling(self, widget):
    """Apply touch-friendly sizing to a widget based on touchscreen detection"""
    # Scales individual widgets by 1.5x factor
```

**3. Batch Scaling (`apply_touch_scaling_to_all_widgets()`):**
```python
def apply_touch_scaling_to_all_widgets(self):
    """Apply touch-friendly scaling to all interactive widgets"""
    # Called at end of create_widgets() if touchscreen detected
```

### Initialization Flow

```python
class ScreensaverPreferences(QMainWindow):
    def __init__(self):
        # 1. Detect touchscreen
        self.is_touchscreen = self.detect_touchscreen()
        self.ui_scale_factor = 1.5 if self.is_touchscreen else 1.0

        # 2. Set window size based on detection
        if self.is_touchscreen:
            self.setGeometry(100, 100, 900, 1200)
            self.showMaximized()
        else:
            self.setGeometry(100, 100, 600, 800)
            self.setMaximumWidth(600)

        # 3. Create widgets normally
        self.create_widgets()

        # 4. Apply scaling at end of create_widgets()
        if self.is_touchscreen:
            self.apply_touch_scaling_to_all_widgets()
```

## Touch Target Guidelines

Based on Apple Human Interface Guidelines and Material Design:

| Control Type | Touch Size | Mouse Size | Guideline |
|--------------|-----------|------------|-----------|
| Primary Button | 48px | 24-30px | Apple HIG minimum |
| Checkbox | 48px | 20-24px | Material Design |
| Input Control | 44px | 24-28px | Apple HIG input |
| Slider | 40px | 16-20px | Easier grabbing |

## Platform Support

**✅ Fully Supported:**
- Raspberry Pi 5 with official touchscreen
- Raspberry Pi 4 with official touchscreen
- Raspberry Pi 3 with compatible touchscreens
- Any Linux system with touchscreen support

**🔧 Detection Methods by Platform:**
- **Wayland (Pi OS Bookworm)**: libinput, /proc (most reliable)
- **X11 (older systems)**: xinput, /proc
- **Fallback**: /proc/bus/input/devices (universal)

## Troubleshooting

### Touchscreen Not Detected

1. **Verify touchscreen is working:**
   ```bash
   libinput list-devices
   ```
   Should show a device with "touchscreen" in name.

2. **Check kernel detection:**
   ```bash
   cat /proc/bus/input/devices | grep -i touch
   ```

3. **Manual override (for testing):**
   Edit `screensaver_preferences.py`:
   ```python
   def detect_touchscreen(self) -> bool:
       return True  # Force touch mode
   ```

### Touch Mode Activates Without Touchscreen

This can happen if:
- Touchpad is misidentified as touchscreen
- Device naming includes "touch" (e.g., "TouchPad")

**Solution**: Make detection more specific:
```python
# Only detect actual touchscreens, not touchpads
if 'touchscreen' in content and 'touchpad' not in content:
    return True
```

### UI Too Large/Small

Adjust scaling factor in `__init__`:
```python
# Increase for larger UI
self.ui_scale_factor = 2.0 if self.is_touchscreen else 1.0

# Decrease for smaller UI
self.ui_scale_factor = 1.3 if self.is_touchscreen else 1.0
```

## Testing

### Manual Testing Checklist

- [ ] Touchscreen detection works (run `test_touch_ui.py`)
- [ ] Window maximizes automatically in touch mode
- [ ] All buttons are easily tappable (48px height)
- [ ] Checkboxes easy to toggle with finger
- [ ] Spinboxes can be incremented with touch
- [ ] Sliders can be dragged smoothly
- [ ] Text is readable at larger sizes
- [ ] No UI clipping or overflow

### Automated Testing

```bash
# Test detection logic
python3 test_touch_ui.py

# Launch preferences to verify UI
python3 screensaver_preferences.py
```

## Future Enhancements

- [ ] Gesture support (swipe, pinch-to-zoom)
- [ ] Touch-friendly color picker
- [ ] Virtual keyboard auto-show for text inputs
- [ ] Haptic feedback (if supported)
- [ ] Orientation detection (portrait/landscape)
- [ ] Per-widget touch sensitivity tuning

## Files Modified

1. `screensaver_preferences.py` - Core preferences GUI
   - Added `detect_touchscreen()` method
   - Added `apply_touch_scaling()` method
   - Added `apply_touch_scaling_to_all_widgets()` method
   - Modified `__init__()` for conditional window sizing

2. `test_touch_ui.py` - New testing utility
   - Tests all 4 detection methods
   - Shows detailed detection results
   - Provides usage instructions

## References

- [Apple Human Interface Guidelines - Touch Targets](https://developer.apple.com/design/human-interface-guidelines/buttons)
- [Material Design - Touch Targets](https://material.io/design/usability/accessibility.html#layout-and-typography)
- [libinput Documentation](https://wayland.freedesktop.org/libinput/doc/latest/)
- [Linux Input Subsystem](https://www.kernel.org/doc/html/latest/input/input.html)
