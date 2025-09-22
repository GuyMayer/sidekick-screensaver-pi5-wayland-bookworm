#!/usr/bin/env python3
"""
Screensaver Preferences GUI - PyQt6 Version
A modern control panel for Wayland Matrix screensaver settings

Features:
- Modern PyQt6 interface with Matrix cyberpunk theme
- System tray integration with hide/show functionality
- Single instance enforcement to prevent multiple windows
- Native Python Matrix widget (no terminal dependencies)
- Autostart management with desktop entry integration
- Enhanced error handling and user feedback

Version: 3.0.0 - Pure Python Matrix Widget Edition
Updated: September 2025
"""

import sys
import os
import json
import subprocess
import datetime
import time
import atexit
from typing import Optional, Any, Union, List
from pathlib import Path

# Integrated Single Instance Protection
try:
    from filelock import Timeout, FileLock
    FILELOCK_AVAILABLE = True
except ImportError:
    FILELOCK_AVAILABLE = False

class SingleInstanceManager:
    """Professional single instance manager with file locking"""
    def __init__(self, app_name: str = "single_instance_app", lock_dir: Optional[str] = None):
        self.app_name = app_name
        self.lock_file = None
        self.lock = None
        self.is_locked = False
        if lock_dir:
            self.lock_dir = Path(lock_dir)
        else:
            if os.access("/tmp", os.W_OK):
                self.lock_dir = Path("/tmp")
            else:
                self.lock_dir = Path.cwd()
        self.lock_file_path = self.lock_dir / f"{self.app_name}.lock"
        if FILELOCK_AVAILABLE:
            self.lock = FileLock(str(self.lock_file_path))
        else:
            self.lock = None

    def acquire_lock(self, timeout: float = 0.0) -> bool:
        if not FILELOCK_AVAILABLE:
            return True  # Allow multiple instances if filelock unavailable
        if not self.lock:
            return False
        try:
            self.lock.acquire(timeout=timeout)
            self.is_locked = True
            atexit.register(self.release_lock)
            return True
        except Timeout:
            return False
        except Exception:
            return False

    def release_lock(self):
        if not self.is_locked or not self.lock:
            return
        try:
            self.lock.release()
            self.is_locked = False
        except Exception:
            pass

def ensure_single_instance(app_name: str = "single_instance_app", exit_on_conflict: bool = True, timeout: float = 0.0) -> SingleInstanceManager:
    """Ensure only one instance of the application runs"""
    manager = SingleInstanceManager(app_name)
    if manager.acquire_lock(timeout=timeout):
        return manager
    else:
        if exit_on_conflict:
            sys.exit(1)
        else:
            return manager
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                            QHBoxLayout, QGridLayout, QLabel, QPushButton,
                            QCheckBox, QComboBox, QSpinBox, QSlider, QGroupBox,
                            QStatusBar, QMessageBox, QFrame, QSystemTrayIcon, QMenu,
                            QFileDialog, QDoubleSpinBox)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon, QAction

# Import professional dark theme libraries
try:
    import qdarktheme
    QDARKTHEME_AVAILABLE = True
except Exception as e:
    QDARKTHEME_AVAILABLE = False
    print(f"ℹ️ qdarktheme not available ({e})")

try:
    import qdarkstyle
    QDARKSTYLE_AVAILABLE = True
    print("✅ qdarkstyle is available")
except Exception as e:
    QDARKSTYLE_AVAILABLE = False
    print(f"ℹ️ qdarkstyle not available ({e})")

DARK_THEME_AVAILABLE = QDARKTHEME_AVAILABLE or QDARKSTYLE_AVAILABLE

# Built-in dark theme stylesheet for fallback
DARK_THEME_STYLESHEET = """
QMainWindow {
    background-color: #2b2b2b;
    color: #ffffff;
}

QWidget {
    background-color: #2b2b2b;
    color: #ffffff;
}

QGroupBox {
    background-color: #3c3c3c;
    border: 2px solid #555555;
    border-radius: 8px;
    margin-top: 10px;
    padding-top: 15px;
    font-weight: bold;
    color: #ffffff;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px 0 5px;
    color: #00ff00;
}

QPushButton {
    background-color: #404040;
    border: 2px solid #666666;
    border-radius: 8px;
    color: #ffffff;
    font-weight: bold;
    padding: 8px 16px;
    min-height: 20px;
}

QPushButton:hover {
    background-color: #505050;
    border-color: #888888;
}

QPushButton:pressed {
    background-color: #353535;
    border-color: #999999;
}

QCheckBox {
    color: #ffffff;
    font-weight: bold;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
}

QCheckBox::indicator:unchecked {
    border: 2px solid #666666;
    background-color: #404040;
    border-radius: 3px;
}

QCheckBox::indicator:checked {
    border: 2px solid #00ff00;
    background-color: #00aa00;
    border-radius: 3px;
}

QComboBox {
    background-color: #404040;
    border: 2px solid #666666;
    border-radius: 5px;
    color: #ffffff;
    padding: 5px;
    min-height: 20px;
}

QComboBox:hover {
    border-color: #888888;
}

/* ComboBox drop-down button styling */
QComboBox::drop-down {
    background-color: #505050;
    border: 1px solid #666666;
    border-radius: 3px;
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 20px;
    margin-right: 2px;
}

QComboBox::drop-down:hover {
    background-color: #606060;
    border-color: #888888;
}

QComboBox::drop-down:pressed {
    background-color: #404040;
}

/* ComboBox down arrow styling - white arrow */
QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid #ffffff;
    width: 0px;
    height: 0px;
    margin-right: 5px;
}

QComboBox::down-arrow:on {
    border-top-color: #00ff00;
}

QComboBox::down-arrow:disabled {
    border-top-color: #666666;
}

/* ComboBox dropdown list styling */
QComboBox QAbstractItemView {
    background-color: #404040;
    border: 2px solid #666666;
    color: #ffffff;
    selection-background-color: #00aa00;
    selection-color: #ffffff;
    outline: none;
}

QSpinBox, QDoubleSpinBox {
    background-color: #404040;
    border: 2px solid #666666;
    border-radius: 5px;
    color: #ffffff;
    padding: 5px;
    min-height: 15px;
}

QSpinBox:hover, QDoubleSpinBox:hover {
    border-color: #888888;
}

/* SpinBox up button styling */
QSpinBox::up-button, QDoubleSpinBox::up-button {
    background-color: #505050;
    border: 1px solid #666666;
    border-radius: 3px;
    subcontrol-origin: border;
    subcontrol-position: top right;
    width: 16px;
    height: 14px;
}

QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover {
    background-color: #606060;
    border-color: #888888;
}

QSpinBox::up-button:pressed, QDoubleSpinBox::up-button:pressed {
    background-color: #404040;
}

/* SpinBox up arrow styling - white arrow */
QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-bottom: 4px solid #ffffff;
    width: 0px;
    height: 0px;
}

QSpinBox::up-arrow:disabled, QDoubleSpinBox::up-arrow:disabled {
    border-bottom-color: #666666;
}

/* SpinBox down button styling */
QSpinBox::down-button, QDoubleSpinBox::down-button {
    background-color: #505050;
    border: 1px solid #666666;
    border-radius: 3px;
    subcontrol-origin: border;
    subcontrol-position: bottom right;
    width: 16px;
    height: 14px;
}

QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {
    background-color: #606060;
    border-color: #888888;
}

QSpinBox::down-button:pressed, QDoubleSpinBox::down-button:pressed {
    background-color: #404040;
}

/* SpinBox down arrow styling - white arrow */
QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 4px solid #ffffff;
    width: 0px;
    height: 0px;
}

QSpinBox::down-arrow:disabled, QDoubleSpinBox::down-arrow:disabled {
    border-top-color: #666666;
}

QSlider::groove:horizontal {
    border: 1px solid #666666;
    height: 8px;
    background-color: #404040;
    border-radius: 4px;
}

QSlider::handle:horizontal {
    background-color: #00ff00;
    border: 2px solid #666666;
    width: 18px;
    margin: -2px 0;
    border-radius: 9px;
}

QSlider::handle:horizontal:hover {
    background-color: #00aa00;
    border-color: #888888;
}

QLabel {
    color: #ffffff;
    background-color: transparent;
}

QStatusBar {
    background-color: #2b2b2b;
    border-top: 1px solid #555555;
    color: #ffffff;
}

QFrame[objectName="separator"] {
    background-color: #555555;
    border: none;
    height: 2px;
    margin: 10px 0;
}
"""

LIGHT_THEME_STYLESHEET = """
/* Light theme - use default system styling */
"""

# Import our custom Sidekick widget
from sidekick_widget import MatrixScreensaver

# Version and build information
APP_VERSION = "3.0.0"
BUILD_DATE = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
COMPILE_TIME = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

class ScreensaverPreferences(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🎬 Screensaver Preferences")
        self.setGeometry(100, 100, 600, 800)
        self.setMaximumWidth(600)  # Limit window width to 600px

        # Instance manager for single instance enforcement
        self.instance_manager: Optional[SingleInstanceManager] = None  # Will be set by main()

        # Configuration file path
        self.config_dir = Path.home() / '.config' / 'screensaver'
        self.config_file = self.config_dir / 'settings.json'
        self.config_dir.mkdir(exist_ok=True)

        # Default settings
        self.settings = {
            'enabled': True,
            'effect': 'matrix',
            'matrix_mode': True,  # Use Matrix digital rain effect
            'color': 'green',
            'speed': 25,  # Default to middle speed (0-50 range)
            'lock_timeout': 300,  # 5 minutes
            'display_timeout': 600,  # 10 minutes
            'rainbow_mode': False,
            'bold_text': True,
            'async_scroll': True,
            'display_target': 'both',  # 'display0', 'display1', or 'both'
            'physical_only': True,  # Only run on physical screens, not remote
            'start_on_boot': False,  # Start Matrix screensaver on system boot
            'show_taskbar_icon': True,  # Show icon in taskbar when preferences are running
            'show_stats': False,  # Show system statistics overlay
            'target_fps': 15,  # Target frame rate (0 = unlimited) - changed to match user preference
            'auto_cpu_limit': False,  # Intelligent CPU management - prioritizes other programs
            'use_katakana': True,  # Use Japanese katakana characters
            'font_size': 14,  # Default font size
            'slideshow_mode': False,  # Use slideshow
            'slideshow_folder': '',  # Path to slideshow images folder
            'slide_duration': 5.0,  # Duration per slide in seconds
            'slideshow_random': True,  # Randomize slide order
            'slideshow_fit_mode': 'contain',  # 'contain', 'cover', 'stretch'
            'mystify_mode': False,  # Use Mystify curved patterns (Windows 10 style)
            'mystify_shapes': 3,  # Number of geometric shapes
            'mystify_trail_length': 50,  # Length of trailing effect
            'mystify_complexity': 6,  # Control points per curve (affects smoothness)
            'mystify_speed': 2,  # Movement speed
            'mystify_color_mode': 'rainbow',  # 'rainbow', 'single', 'duo'
            'mystify_fill': False,  # Fill shapes with color
            'mystify_color_hue': 240,  # Single mode hue (blue)
            'mystify_color_hue1': 240,  # Duo mode first hue (blue)
            'mystify_color_hue2': 60,  # Duo mode second hue (yellow)
            'dark_mode': True,  # Enable dark mode by default
            'auto_shutdown': False,  # Enable automatic shutdown timer
            'shutdown_timeout': 60  # Minutes until automatic shutdown (default 1 hour)
        }

        # Screensaver timer and progress tracking
        self.screensaver_timer = QTimer()
        self.progress_timer = QTimer()
        self.last_activity_time = 0
        self.screensaver_active = False
        self.is_test_mode = False  # Track if we're in test mode vs normal operation
        # Progress UI removed - timer display no longer needed

        self.load_settings()
        self.setup_icons()
        self.setup_dark_theme()
        self.create_widgets()
        self.create_status_bar()
        self.setup_system_tray()
        # Setup screensaver timer but DON'T start it when GUI is open
        self.setup_screensaver_timer()

        # GUI is open - timer should NOT be running
        self.stop_all_timers_for_gui()

        # Apply initial taskbar icon setting
        self.apply_initial_taskbar_setting()

        # Ensure system tray persists - critical for after interruption
        self.ensure_system_tray_persistence()

        # Initialize shutdown timer if auto-shutdown is enabled
        if self.settings.get('auto_shutdown', False):
            self.start_shutdown_timer()

    def safe_get_combo_value(self, combo_widget: Any, value_list: List[Any], default_value: Any) -> Any:
        """Safely get combo box value by index with fallback"""
        try:
            # Check if widget exists and is valid
            if combo_widget is not None and hasattr(combo_widget, 'currentIndex'):
                index = combo_widget.currentIndex()
                if 0 <= index < len(value_list):
                    return value_list[index]
            return default_value
        except (RuntimeError, AttributeError, IndexError) as e:
            # Widget was deleted or invalid access
            return default_value

    def safe_get_combo_text(self, combo_widget: Any, text_list: List[str], default_text: str) -> str:
        """Safely get combo box text with fallback"""
        try:
            if combo_widget is not None and hasattr(combo_widget, 'currentText'):
                current_text = combo_widget.currentText()
                # Map display text to internal values
                text_map = {
                    'Rainbow': 'rainbow',
                    'Single Color': 'single',
                    'Two Colors': 'duo'
                }
                return text_map.get(current_text, default_text)
            return default_text
        except (RuntimeError, AttributeError) as e:
            # Widget was deleted or invalid access
            return default_text

    def safe_get_combo_text_simple(self, combo_widget: Any, default_text: str) -> str:
        """Safely get combo box current text with fallback"""
        try:
            if combo_widget is not None and hasattr(combo_widget, 'currentText'):
                return combo_widget.currentText()
            return default_text
        except (RuntimeError, AttributeError) as e:
            # Widget was deleted or invalid access
            return default_text

    def safe_get_checkbox_value(self, checkbox_widget: Any, default_value: bool = False) -> bool:
        """Safely get checkbox value with fallback"""
        try:
            if checkbox_widget is not None and hasattr(checkbox_widget, 'isChecked'):
                return checkbox_widget.isChecked()
            return default_value
        except (RuntimeError, AttributeError) as e:
            # Widget was deleted or invalid access
            return default_value

    def safe_get_spinbox_value(self, spinbox_widget: Any, default_value: Union[int, float] = 0) -> Union[int, float]:
        """Safely get spinbox value with fallback (supports int and float)"""
        try:
            if spinbox_widget is not None and hasattr(spinbox_widget, 'value'):
                return spinbox_widget.value()
            return default_value
        except (RuntimeError, AttributeError) as e:
            # Widget was deleted or invalid access
            return default_value

    def safe_status_message(self, message):
        """Safely show status bar message with fallback"""
        try:
            if hasattr(self, 'status_bar') and self.status_bar:
                self.status_bar.showMessage(message)
        except (RuntimeError, AttributeError):
            # Widget was deleted or invalid access - fail silently
            pass

    def setup_icons(self):
        """Setup consistent icons for window and system tray"""
        # Try to get the same icon as used in the desktop launcher
        icon_found = False

        # List of icon names to try (in order of preference)
        icon_names = [
            "preferences-desktop-screensaver",
            "screensaver",
            "xscreensaver",
            "kscreensaver",
            "preferences-desktop",
            "applications-system",
            "preferences-system",
            "system-config-services"
        ]

        try:
            for icon_name in icon_names:
                icon = QIcon.fromTheme(icon_name)
                if not icon.isNull():
                    self.app_icon = icon
                    icon_found = True
                    break

            if not icon_found:
                # Try specific paths
                icon_paths = [
                    "/usr/share/icons/nuoveXT2/22x22/apps/preferences-desktop-screensaver.png",
                    "/usr/share/icons/hicolor/48x48/apps/preferences-desktop-screensaver.png",
                    "/usr/share/pixmaps/screensaver.png"
                ]

                for path in icon_paths:
                    if Path(path).exists():
                        icon = QIcon(path)
                        if not icon.isNull():
                            self.app_icon = icon
                            icon_found = True
                            break

            if not icon_found:
                # Final fallback to a standard icon
                self.app_icon = self.style().standardIcon(self.style().StandardPixmap.SP_ComputerIcon)

            # Set window icon
            self.setWindowIcon(self.app_icon)

        except Exception as e:
            # Ultimate fallback
            self.app_icon = self.style().standardIcon(self.style().StandardPixmap.SP_ComputerIcon)
            self.setWindowIcon(self.app_icon)

    def setup_dark_theme(self):
        """Setup professional dark mode - theme is applied at application level in main()"""
        # Theme is already applied at the QApplication level in main()
        # This method is kept for compatibility but does nothing
        pass

    def load_settings(self):
        """Load settings from JSON file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    saved_settings = json.load(f)
                    self.settings.update(saved_settings)
            except Exception as e:
                print(f"Error loading settings: {e}")

    def save_settings(self) -> bool:
        """Save settings to JSON file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
            return True
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save settings: {e}")
            return False

    def create_shared_widgets(self):
        """Create widgets that are used in multiple sections"""
        # FPS combo
        self.fps_combo = QComboBox()
        self.fps_combo.addItems(['15', '30', '45', '60', '75', '90', '120', 'Unlimited'])
        current_fps = self.settings.get('target_fps', 30)
        if current_fps == 0:
            self.fps_combo.setCurrentText('Unlimited')
        else:
            self.fps_combo.setCurrentText(str(current_fps))
        self.fps_combo.setToolTip("Set target frame rate (higher = smoother, more CPU usage)")
        self.fps_combo.currentTextChanged.connect(self.auto_save_settings)

        # Display combo
        self.display_combo = QComboBox()
        self.display_combo.addItems(['both', 'display0', 'display1'])
        self.display_combo.setCurrentText(self.settings.get('display_target', 'both'))
        self.display_combo.setToolTip("Select which display(s) to use for screensaver")
        self.display_combo.currentTextChanged.connect(self.auto_save_settings)

    def create_widgets(self):
        # Create the main GUI widgets
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Create widgets that are used in multiple sections
        self.create_shared_widgets()

        # === SYSTEM SETTINGS SECTION ===
        system_group = QGroupBox("🔧 System Settings")
        system_layout = QVBoxLayout(system_group)

        # System checkboxes row 1
        system_row1 = QHBoxLayout()

        # Show taskbar icon option
        self.show_taskbar_icon_checkbox = QCheckBox("� Show Taskbar Icon")
        self.show_taskbar_icon_checkbox.setChecked(self.settings.get('show_taskbar_icon', True))
        self.show_taskbar_icon_checkbox.setToolTip("Display icon in taskbar when screensaver preferences are running")
        self.show_taskbar_icon_checkbox.stateChanged.connect(self.on_taskbar_icon_changed)
        system_row1.addWidget(self.show_taskbar_icon_checkbox)

        # Autostart checkbox
        self.autostart_checkbox = QCheckBox("🚀 Start on Boot")
        self.autostart_checkbox.setChecked(self.settings['start_on_boot'])
        self.autostart_checkbox.setToolTip("Automatically start screensaver when system boots")
        self.autostart_checkbox.stateChanged.connect(self.auto_save_settings)
        system_row1.addWidget(self.autostart_checkbox)

        # Dark mode checkbox
        self.dark_mode_checkbox = QCheckBox("🌙 Dark Mode")
        self.dark_mode_checkbox.setChecked(self.settings.get('dark_mode', True))
        self.dark_mode_checkbox.setToolTip("Use dark theme for the preferences GUI")
        self.dark_mode_checkbox.stateChanged.connect(self.on_dark_mode_changed)
        system_row1.addWidget(self.dark_mode_checkbox)

        system_row1.addStretch()
        system_layout.addLayout(system_row1)

        layout.addWidget(system_group)

        # === SCREEN SETTINGS SECTION ===
        screen_group = QGroupBox("🖥️ Screen Settings")
        screen_layout = QVBoxLayout(screen_group)

        # Screen settings row 1 - Type and Performance
        screen_row1 = QHBoxLayout()

        # Screensaver Type Selection
        screen_row1.addWidget(QLabel("Screensaver Type:"))
        self.screensaver_type_combo = QComboBox()
        self.screensaver_type_combo.addItems(['None', 'Matrix', 'Mystify', 'Slideshow'])
        self.screensaver_type_combo.setToolTip("Select which screensaver to use")

        # Set initial value based on current settings
        if not self.settings.get('enabled', True):
            self.screensaver_type_combo.setCurrentText('None')
        elif self.settings.get('matrix_mode', True):
            self.screensaver_type_combo.setCurrentText('Matrix')
        elif self.settings.get('slideshow_mode', False):
            self.screensaver_type_combo.setCurrentText('Slideshow')
        elif self.settings.get('mystify_mode', False):
            self.screensaver_type_combo.setCurrentText('Mystify')
        else:
            self.screensaver_type_combo.setCurrentText('Matrix')

        self.screensaver_type_combo.currentTextChanged.connect(self.on_screensaver_type_changed)
        screen_row1.addWidget(self.screensaver_type_combo)

        screen_row1.addSpacing(20)

        # Target FPS
        screen_row1.addWidget(QLabel("🎯 Target FPS:"))
        screen_row1.addWidget(self.fps_combo)

        screen_row1.addStretch()
        screen_layout.addLayout(screen_row1)

        # Screen settings row 2 - Display Options
        screen_row2 = QHBoxLayout()

        # Display target
        screen_row2.addWidget(QLabel("🖥️ Display target:"))
        screen_row2.addWidget(self.display_combo)

        screen_row2.addSpacing(20)

        # Physical screens only
        self.physical_only_checkbox = QCheckBox("� Physical screens only")
        self.physical_only_checkbox.setChecked(self.settings.get('physical_only', True))
        self.physical_only_checkbox.setToolTip("Only use physical screens (not SSH/VNC connections)")
        self.physical_only_checkbox.stateChanged.connect(self.auto_save_settings)
        screen_row2.addWidget(self.physical_only_checkbox)

        screen_row2.addStretch()
        screen_layout.addLayout(screen_row2)

        # Screen settings row 3 - Performance Options
        screen_row3 = QHBoxLayout()

        # Show stats checkbox
        self.show_stats_checkbox = QCheckBox("📊 Show Stats")
        self.show_stats_checkbox.setChecked(self.settings.get('show_stats', False))
        self.show_stats_checkbox.setToolTip("Display performance statistics (FPS, memory usage) on screensaver")
        self.show_stats_checkbox.stateChanged.connect(self.auto_save_settings)
        screen_row3.addWidget(self.show_stats_checkbox)

        # Stats drift checkbox
        self.stats_drift_checkbox = QCheckBox("🌊 Drift")
        self.stats_drift_checkbox.setChecked(self.settings.get('stats_drift', True))
        self.stats_drift_checkbox.setToolTip("Make stats slowly drift around screen edges to prevent burn-in (2 min per edge)")
        self.stats_drift_checkbox.stateChanged.connect(self.auto_save_settings)
        screen_row3.addWidget(self.stats_drift_checkbox)

        screen_row3.addSpacing(20)

        # FPS Throttling (renamed from CPU management)
        self.auto_cpu_limit_checkbox = QCheckBox("🎯 FPS Throttling")
        self.auto_cpu_limit_checkbox.setChecked(self.settings.get('auto_cpu_limit', False))
        self.auto_cpu_limit_checkbox.setToolTip("Intelligent FPS limiting that uses Target FPS as maximum and reduces FPS when system is busy")
        self.auto_cpu_limit_checkbox.stateChanged.connect(self.auto_save_settings)
        screen_row3.addWidget(self.auto_cpu_limit_checkbox)

        screen_row3.addStretch()
        screen_layout.addLayout(screen_row3)

        layout.addWidget(screen_group)

        # === TIMER SETTINGS SECTION ===
        timer_group = QGroupBox("⏰ Timer Settings")
        timer_layout = QVBoxLayout(timer_group)

        # Timer row 1 - Screensaver and Display timers
        timer_row1 = QHBoxLayout()

        timer_row1.addWidget(QLabel("⏰ Start screensaver after:"))
        self.lock_spinbox = QSpinBox()
        self.lock_spinbox.setRange(1, 60)
        self.lock_spinbox.setValue(self.settings['lock_timeout'] // 60)
        self.lock_spinbox.setToolTip("Minutes of inactivity before screensaver starts")
        self.lock_spinbox.valueChanged.connect(self.auto_save_settings)
        timer_row1.addWidget(self.lock_spinbox)
        timer_row1.addWidget(QLabel("min"))

        timer_row1.addSpacing(20)

        timer_row1.addWidget(QLabel("📺 Turn off display after:"))
        self.display_spinbox = QSpinBox()
        self.display_spinbox.setRange(5, 120)
        self.display_spinbox.setValue(self.settings['display_timeout'] // 60)
        self.display_spinbox.setToolTip("Minutes before display turns off for power saving")
        self.display_spinbox.valueChanged.connect(self.auto_save_settings)
        timer_row1.addWidget(self.display_spinbox)
        timer_row1.addWidget(QLabel("min"))

        timer_row1.addStretch()
        timer_layout.addLayout(timer_row1)

        # Timer row 2 - Auto-shutdown timer
        timer_row2 = QHBoxLayout()

        # Auto-shutdown checkbox and spinbox
        self.auto_shutdown_checkbox = QCheckBox("🔴 Auto-shutdown after:")
        self.auto_shutdown_checkbox.setChecked(self.settings.get('auto_shutdown', False))
        self.auto_shutdown_checkbox.setToolTip("Automatically shutdown the system after specified time")
        self.auto_shutdown_checkbox.stateChanged.connect(self.on_auto_shutdown_changed)
        timer_row2.addWidget(self.auto_shutdown_checkbox)

        self.shutdown_spinbox = QSpinBox()
        self.shutdown_spinbox.setRange(5, 480)  # 5 minutes to 8 hours
        self.shutdown_spinbox.setValue(self.settings.get('shutdown_timeout', 60))
        self.shutdown_spinbox.setToolTip("Minutes until automatic system shutdown")
        self.shutdown_spinbox.valueChanged.connect(self.auto_save_settings)
        self.shutdown_spinbox.setEnabled(self.settings.get('auto_shutdown', False))
        timer_row2.addWidget(self.shutdown_spinbox)
        timer_row2.addWidget(QLabel("min"))

        timer_row2.addStretch()
        timer_layout.addLayout(timer_row2)

        layout.addWidget(timer_group)

        # Separator
        separator = QFrame()
        separator.setObjectName("separator")
        separator.setFrameShape(QFrame.Shape.HLine)
        layout.addWidget(separator)

        # Dynamic Settings Section - shows settings relevant to selected screensaver type
        self.settings_group = QGroupBox("🎛️ Screensaver Settings")
        self.settings_layout = QVBoxLayout(self.settings_group)
        layout.addWidget(self.settings_group)

        # Create all setting widgets (but don't add them to layout yet)
        self.create_all_setting_widgets()

        # Update the settings display based on current selection
        self.update_settings_display()

        # Control Buttons
        control_layout = QHBoxLayout()

        self.test_button = QPushButton("🎬 Test Screensaver")
        self.test_button.setObjectName("matrixButton")
        self.test_button.clicked.connect(self.test_matrix)
        control_layout.addWidget(self.test_button)

        # About button
        self.about_button = QPushButton("ℹ️ About")
        self.about_button.setObjectName("matrixButton")
        self.about_button.clicked.connect(self.show_about)
        control_layout.addWidget(self.about_button)

        # Diagnostics button
        self.diagnostics_button = QPushButton("🔧 Diagnostics")
        self.diagnostics_button.setObjectName("matrixButton")
        self.diagnostics_button.clicked.connect(self.run_diagnostics)
        control_layout.addWidget(self.diagnostics_button)

        layout.addLayout(control_layout)

        # Action Buttons
        action_layout = QHBoxLayout()

        self.reset_button = QPushButton("🔄 Reset Defaults")
        self.reset_button.setObjectName("actionButton")
        self.reset_button.clicked.connect(self.reset_defaults)
        action_layout.addWidget(self.reset_button)

        self.close_button = QPushButton("❌ Close")
        self.close_button.setObjectName("actionButton")
        self.close_button.clicked.connect(self.handle_close)
        action_layout.addWidget(self.close_button)

        layout.addLayout(action_layout)

        # Stretch to push everything up
        layout.addStretch()

        # Diagnostics button
        self.diagnostics_button = QPushButton("🔧 Diagnostics")
        self.diagnostics_button.setObjectName("matrixButton")
        self.diagnostics_button.clicked.connect(self.run_diagnostics)
        control_layout.addWidget(self.diagnostics_button)

        layout.addLayout(control_layout)

        # Action Buttons
        action_layout = QHBoxLayout()

        self.reset_button = QPushButton("🔄 Reset Defaults")
        self.reset_button.setObjectName("actionButton")
        self.reset_button.clicked.connect(self.reset_defaults)
        action_layout.addWidget(self.reset_button)

        self.close_button = QPushButton("❌ Close")
        self.close_button.setObjectName("actionButton")
        self.close_button.clicked.connect(self.handle_close)
        action_layout.addWidget(self.close_button)

        layout.addLayout(action_layout)

        # Stretch to push everything up
        layout.addStretch()

    def create_all_setting_widgets(self):
        """Create all setting widgets but don't add them to layouts yet"""

        # Matrix Settings
        self.color_combo = QComboBox()
        self.color_combo.addItems(['green', 'red', 'blue', 'cyan', 'magenta', 'yellow', 'white', 'rainbow'])
        if self.settings.get('rainbow_mode', False):
            self.color_combo.setCurrentText('rainbow')
        else:
            self.color_combo.setCurrentText(self.settings['color'])
        self.color_combo.currentTextChanged.connect(self.auto_save_settings)

        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(0, 50)
        self.speed_slider.setValue(self.settings['speed'])
        self.speed_slider.valueChanged.connect(self.update_speed_label)
        self.speed_slider.valueChanged.connect(self.auto_save_settings)

        initial_speed = self.settings['speed']
        if initial_speed == 0:
            speed_text = "Slowest"
        elif initial_speed == 50:
            speed_text = "Fastest"
        elif initial_speed <= 10:
            speed_text = f"Very Slow ({initial_speed})"
        elif initial_speed <= 20:
            speed_text = f"Slow ({initial_speed})"
        elif initial_speed <= 30:
            speed_text = f"Medium ({initial_speed})"
        elif initial_speed <= 40:
            speed_text = f"Fast ({initial_speed})"
        else:
            speed_text = f"Very Fast ({initial_speed})"
        self.speed_label = QLabel(f"({speed_text})")

        self.bold_checkbox = QCheckBox("Bold characters")
        self.bold_checkbox.setChecked(self.settings['bold_text'])
        self.bold_checkbox.stateChanged.connect(self.auto_save_settings)

        self.katakana_checkbox = QCheckBox("Use Japanese katakana characters")
        self.katakana_checkbox.setChecked(self.settings.get('use_katakana', True))
        self.katakana_checkbox.setToolTip("Use authentic Japanese katakana characters (disable for ASCII only)")
        self.katakana_checkbox.stateChanged.connect(self.auto_save_settings)

        # Slideshow Settings
        self.slideshow_folder_button = QPushButton("📁 Browse...")
        self.slideshow_folder_button.clicked.connect(self.browse_slideshow_folder)

        self.slideshow_folder_label = QLabel(self.settings.get('slideshow_folder', 'No folder selected'))
        self.slideshow_folder_label.setStyleSheet("color: #888888; font-style: italic;")

        self.slide_duration_spinbox = QDoubleSpinBox()
        self.slide_duration_spinbox.setRange(0.5, 60.0)
        self.slide_duration_spinbox.setSingleStep(0.5)
        self.slide_duration_spinbox.setValue(self.settings.get('slide_duration', 5.0))
        self.slide_duration_spinbox.setToolTip("How long each image is displayed")
        self.slide_duration_spinbox.valueChanged.connect(self.auto_save_settings)

        self.slideshow_random_checkbox = QCheckBox("Randomize slide order")
        self.slideshow_random_checkbox.setChecked(self.settings.get('slideshow_random', True))
        self.slideshow_random_checkbox.setToolTip("Display images in random order instead of alphabetical")
        self.slideshow_random_checkbox.stateChanged.connect(self.auto_save_settings)

        self.slideshow_fit_combo = QComboBox()
        self.slideshow_fit_combo.addItems(['Contain (fit within screen)', 'Cover (fill screen)', 'Stretch (exact fit)'])
        fit_mode = self.settings.get('slideshow_fit_mode', 'contain')
        fit_index = {'contain': 0, 'cover': 1, 'stretch': 2}.get(fit_mode, 0)
        self.slideshow_fit_combo.setCurrentIndex(fit_index)
        self.slideshow_fit_combo.currentTextChanged.connect(self.auto_save_settings)

        # Mystify Settings
        self.mystify_shapes_spinbox = QSpinBox()
        self.mystify_shapes_spinbox.setRange(1, 8)
        self.mystify_shapes_spinbox.setValue(self.settings.get('mystify_shapes', 3))
        self.mystify_shapes_spinbox.setToolTip("Number of geometric shapes moving on screen")
        self.mystify_shapes_spinbox.valueChanged.connect(self.auto_save_settings)

        self.mystify_complexity_spinbox = QSpinBox()
        self.mystify_complexity_spinbox.setRange(3, 12)
        self.mystify_complexity_spinbox.setValue(self.settings.get('mystify_complexity', 6))
        self.mystify_complexity_spinbox.setToolTip("Number of points per shape (3=triangle, 6=hexagon, etc.)")
        self.mystify_complexity_spinbox.valueChanged.connect(self.auto_save_settings)

        self.mystify_trail_spinbox = QSpinBox()
        self.mystify_trail_spinbox.setRange(10, 200)
        self.mystify_trail_spinbox.setValue(self.settings.get('mystify_trail_length', 50))
        self.mystify_trail_spinbox.setToolTip("Length of the trailing effect behind shapes")
        self.mystify_trail_spinbox.valueChanged.connect(self.auto_save_settings)

        self.mystify_speed_spinbox = QSpinBox()
        self.mystify_speed_spinbox.setRange(1, 10)
        self.mystify_speed_spinbox.setValue(self.settings.get('mystify_speed', 2))
        self.mystify_speed_spinbox.setToolTip("Movement speed of the shapes")
        self.mystify_speed_spinbox.valueChanged.connect(self.auto_save_settings)

        self.mystify_color_combo = QComboBox()
        self.mystify_color_combo.addItems(["Rainbow", "Single Color", "Two Colors"])
        color_mode = self.settings.get('mystify_color_mode', 'rainbow')
        color_index = {'rainbow': 0, 'single': 1, 'duo': 2}.get(color_mode, 0)
        self.mystify_color_combo.setCurrentIndex(color_index)
        self.mystify_color_combo.setToolTip("Color scheme for the geometric patterns")
        self.mystify_color_combo.currentTextChanged.connect(self.auto_save_settings)

        self.mystify_fill_checkbox = QCheckBox("Fill shapes")
        self.mystify_fill_checkbox.setChecked(self.settings.get('mystify_fill', False))
        self.mystify_fill_checkbox.setToolTip("Fill geometric shapes with semi-transparent color")
        self.mystify_fill_checkbox.stateChanged.connect(self.auto_save_settings)

    def update_settings_display(self):
        """Update the settings display based on currently selected screensaver type"""
        # Clear existing widgets from settings layout
        while self.settings_layout.count():
            child = self.settings_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Process pending events to ensure widgets are properly deleted
        QApplication.processEvents()

        # Safety check - ensure screensaver_type_combo still exists
        if not hasattr(self, 'screensaver_type_combo') or not self.screensaver_type_combo:
            return

        screensaver_type = self.safe_get_combo_text_simple(self.screensaver_type_combo, 'Matrix')

        if screensaver_type == "None":
            # Show message that screensaver is disabled
            disabled_label = QLabel("Screensaver is disabled. Select a screensaver type to configure settings.")
            disabled_label.setStyleSheet("color: #888888; font-style: italic; text-align: center;")
            self.settings_layout.addWidget(disabled_label)

        elif screensaver_type == "Matrix":
            self.create_matrix_settings()

        elif screensaver_type == "Slideshow":
            self.create_slideshow_settings()

        elif screensaver_type == "Mystify":
            self.create_mystify_settings()

    def create_matrix_settings(self):
        """Create Matrix-specific settings layout"""
        grid_layout = QGridLayout()

        # Color selection
        grid_layout.addWidget(QLabel("Color:"), 0, 0)
        grid_layout.addWidget(self.color_combo, 0, 1)

        # Speed setting
        grid_layout.addWidget(QLabel("Speed (0-50):"), 1, 0)
        speed_layout = QHBoxLayout()
        speed_layout.addWidget(self.speed_slider)
        speed_layout.addWidget(self.speed_label)
        speed_widget = QWidget()
        speed_widget.setLayout(speed_layout)
        grid_layout.addWidget(speed_widget, 1, 1)

        # Bold text
        grid_layout.addWidget(self.bold_checkbox, 2, 0, 1, 2)

        # Katakana characters
        grid_layout.addWidget(self.katakana_checkbox, 3, 0, 1, 2)

        # Add to main settings layout
        grid_widget = QWidget()
        grid_widget.setLayout(grid_layout)
        self.settings_layout.addWidget(grid_widget)

    def create_slideshow_settings(self):
        """Create Slideshow-specific settings layout"""
        grid_layout = QGridLayout()

        # Folder selection
        grid_layout.addWidget(QLabel("Images folder:"), 0, 0)
        grid_layout.addWidget(self.slideshow_folder_button, 0, 1)
        grid_layout.addWidget(self.slideshow_folder_label, 0, 2)

        # Slide duration
        grid_layout.addWidget(QLabel("Slide duration (seconds):"), 1, 0)
        grid_layout.addWidget(self.slide_duration_spinbox, 1, 1)

        # Randomize order
        grid_layout.addWidget(self.slideshow_random_checkbox, 2, 0, 1, 2)

        # Fit mode
        grid_layout.addWidget(QLabel("Image fit mode:"), 3, 0)
        grid_layout.addWidget(self.slideshow_fit_combo, 3, 1, 1, 2)

        # Add to main settings layout
        grid_widget = QWidget()
        grid_widget.setLayout(grid_layout)
        self.settings_layout.addWidget(grid_widget)

    def create_mystify_settings(self):
        """Create Mystify-specific settings layout"""
        grid_layout = QGridLayout()

        # Number of shapes
        grid_layout.addWidget(QLabel("Number of shapes:"), 0, 0)
        grid_layout.addWidget(self.mystify_shapes_spinbox, 0, 1)

        # Shape complexity
        grid_layout.addWidget(QLabel("Shape complexity:"), 0, 2)
        grid_layout.addWidget(self.mystify_complexity_spinbox, 0, 3)

        # Trail length
        grid_layout.addWidget(QLabel("Trail length:"), 1, 0)
        grid_layout.addWidget(self.mystify_trail_spinbox, 1, 1)

        # Movement speed
        grid_layout.addWidget(QLabel("Speed:"), 1, 2)
        grid_layout.addWidget(self.mystify_speed_spinbox, 1, 3)

        # Color mode
        grid_layout.addWidget(QLabel("Color mode:"), 2, 0)
        grid_layout.addWidget(self.mystify_color_combo, 2, 1)

        # Fill shapes checkbox
        grid_layout.addWidget(self.mystify_fill_checkbox, 2, 2, 1, 2)

        # Add to main settings layout
        grid_widget = QWidget()
        grid_widget.setLayout(grid_layout)
        self.settings_layout.addWidget(grid_widget)

    def handle_close(self):
        """Handle close button click"""
        self.close()

    def create_status_bar(self):
        """Create status bar with version and build information"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Add permanent version info to the right side
        version_label = QLabel(f"v{APP_VERSION} | Build: {COMPILE_TIME}")
        version_label.setStyleSheet("color: #00ff00; font-size: 10px; padding: 2px;")
        self.status_bar.addPermanentWidget(version_label)

        # Set initial message
        self.status_bar.showMessage(f"Ready - Screensaver Preferences v{APP_VERSION}")

    def setup_system_tray(self):
        """Setup system tray icon and menu"""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            print("⚠️ System tray not available")
            return

        # Create system tray icon
        self.tray_icon = QSystemTrayIcon(self)

        # Use the same icon as the window/launcher
        if hasattr(self, 'app_icon'):
            self.tray_icon.setIcon(self.app_icon)
        else:
            # Fallback if setup_icons wasn't called
            icon = QIcon.fromTheme("preferences-desktop-screensaver")
            if icon.isNull():
                icon = self.style().standardIcon(self.style().StandardPixmap.SP_ComputerIcon)
            self.tray_icon.setIcon(icon)

        # Create tray menu
        tray_menu = QMenu()

        # Show/Hide action
        show_action = QAction("🟢 Screensaver Settings", self)
        show_action.triggered.connect(self.show_and_raise)
        tray_menu.addAction(show_action)

        tray_menu.addSeparator()

        # Test Screensaver action
        test_action = QAction("🧪 Test Screensaver", self)
        test_action.triggered.connect(self.test_matrix)
        tray_menu.addAction(test_action)

        tray_menu.addSeparator()

        # Quit action
        quit_action = QAction("❌ Quit Settings", self)
        quit_action.triggered.connect(self.quit_application)
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)

        # Handle tray icon clicks
        self.tray_icon.activated.connect(self.tray_icon_activated)

        # Show tray icon and ensure it persists
        self.tray_icon.show()

        # Set tooltip
        self.tray_icon.setToolTip("Screensaver Settings")

        print("✅ System tray icon setup complete and visible")

    def ensure_system_tray_persistence(self):
        """Ensure system tray icon remains visible and accessible after screensaver interruptions"""
        if hasattr(self, 'tray_icon') and self.tray_icon:
            # Create a timer to periodically check tray icon visibility
            self.tray_persistence_timer = QTimer()
            self.tray_persistence_timer.timeout.connect(self.check_tray_icon_visibility)
            self.tray_persistence_timer.start(5000)  # Check every 5 seconds
            print("🔒 System tray persistence monitor started")

    def check_tray_icon_visibility(self):
        """Periodically check and restore system tray icon if needed"""
        if hasattr(self, 'tray_icon') and self.tray_icon:
            if not self.tray_icon.isVisible():
                self.tray_icon.show()
                print("🔧 System tray icon restored (was hidden)")

            # Update tooltip based on current state
            if self.screensaver_active:
                self.tray_icon.setToolTip("Screensaver Settings - Screensaver Active")
            elif hasattr(self, 'activity_timer') and self.activity_timer.isActive():
                self.tray_icon.setToolTip("Screensaver Settings - Monitoring Active")
            else:
                self.tray_icon.setToolTip("Screensaver Settings")

    def show_and_raise(self):
        """Show and raise the main window"""
        self.show()
        self.raise_()
        self.activateWindow()

        # Stop screensaver timer when GUI becomes visible
        self.stop_all_timers_for_gui()

    def tray_icon_activated(self, reason):
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.ActivationReason.Trigger:  # Left click
            self.show_and_raise()

    def quit_application(self):
        """Quit the application - save settings before exit"""
        try:
            # Save all current settings before quitting
            if hasattr(self, 'fps_combo') and self.fps_combo:
                fps_text = self.safe_get_combo_text_simple(self.fps_combo, '15')
                target_fps = 0 if fps_text == "Unlimited" else int(fps_text)
            else:
                target_fps = 15  # Default

            # Safe widget access with existence checks
            screensaver_type = self.safe_get_combo_text_simple(self.screensaver_type_combo, 'Matrix') if hasattr(self, 'screensaver_type_combo') and self.screensaver_type_combo else 'Matrix'
            color_text = self.safe_get_combo_text_simple(self.color_combo, 'green')

            self.settings.update({
                'enabled': self.settings['enabled'],  # Use current settings value
                'start_on_boot': self.autostart_checkbox.isChecked() if hasattr(self, 'autostart_checkbox') and self.autostart_checkbox else False,
                'show_taskbar_icon': self.show_taskbar_icon_checkbox.isChecked() if hasattr(self, 'show_taskbar_icon_checkbox') and self.show_taskbar_icon_checkbox else True,
                'matrix_mode': screensaver_type == 'Matrix',
                'color': color_text if color_text != 'rainbow' else 'green',
                'speed': self.speed_slider.value() if hasattr(self, 'speed_slider') and self.speed_slider else 25,
                'lock_timeout': (self.lock_spinbox.value() if hasattr(self, 'lock_spinbox') and self.lock_spinbox else 5) * 60,
                'display_timeout': (self.display_spinbox.value() if hasattr(self, 'display_spinbox') and self.display_spinbox else 10) * 60,
                'rainbow_mode': color_text == 'rainbow',
                'bold_text': self.bold_checkbox.isChecked() if hasattr(self, 'bold_checkbox') and self.bold_checkbox else True,
                'async_scroll': True,
                'display_target': self.safe_get_combo_text_simple(self.display_combo, 'both'),
                'physical_only': self.physical_only_checkbox.isChecked() if hasattr(self, 'physical_only_checkbox') and self.physical_only_checkbox else True,
                'show_stats': self.show_stats_checkbox.isChecked() if hasattr(self, 'show_stats_checkbox') and self.show_stats_checkbox else False,
                'show_stats': self.show_stats_checkbox.isChecked() if hasattr(self, 'show_stats_checkbox') and self.show_stats_checkbox else False,
                'use_katakana': self.katakana_checkbox.isChecked() if hasattr(self, 'katakana_checkbox') and self.katakana_checkbox else True,
                'auto_cpu_limit': self.auto_cpu_limit_checkbox.isChecked() if hasattr(self, 'auto_cpu_limit_checkbox') and self.auto_cpu_limit_checkbox else False,
                'target_fps': target_fps,
                'slideshow_mode': screensaver_type == 'Slideshow',
                'slideshow_folder': self.settings.get('slideshow_folder', ''),
                'slide_duration': self.slide_duration_spinbox.value() if hasattr(self, 'slide_duration_spinbox') and self.slide_duration_spinbox else 5.0,
                'slideshow_random': self.slideshow_random_checkbox.isChecked() if hasattr(self, 'slideshow_random_checkbox') and self.slideshow_random_checkbox else True,
                'slideshow_fit_mode': self.safe_get_combo_value(self.slideshow_fit_combo, ['contain', 'cover', 'stretch'], 'contain'),
                'mystify_mode': screensaver_type == 'Mystify',
                'mystify_shapes': self.mystify_shapes_spinbox.value() if hasattr(self, 'mystify_shapes_spinbox') and self.mystify_shapes_spinbox else 3,
                'mystify_trail_length': self.mystify_trail_spinbox.value() if hasattr(self, 'mystify_trail_spinbox') and self.mystify_trail_spinbox else 50,
                'mystify_complexity': self.mystify_complexity_spinbox.value() if hasattr(self, 'mystify_complexity_spinbox') and self.mystify_complexity_spinbox else 6,
                'mystify_speed': self.mystify_speed_spinbox.value() if hasattr(self, 'mystify_speed_spinbox') and self.mystify_speed_spinbox else 2,
                'mystify_color_mode': self.safe_get_combo_value(self.mystify_color_combo, ['rainbow', 'single', 'duo'], 'rainbow'),
                'mystify_fill': self.mystify_fill_checkbox.isChecked() if hasattr(self, 'mystify_fill_checkbox') and self.mystify_fill_checkbox else False,
                'auto_shutdown': self.auto_shutdown_checkbox.isChecked() if hasattr(self, 'auto_shutdown_checkbox') and self.auto_shutdown_checkbox else False,
                'shutdown_timeout': self.shutdown_spinbox.value() if hasattr(self, 'shutdown_spinbox') and self.shutdown_spinbox else 60
            })

            # Save settings silently
            self.save_settings()
        except Exception as e:
            print(f"Warning: Could not save settings on quit: {e}")

        if hasattr(self, 'instance_manager') and self.instance_manager:
            self.instance_manager.release_lock()

        # Stop persistence timer if it exists
        if hasattr(self, 'tray_persistence_timer'):
            self.tray_persistence_timer.stop()

        # Stop shutdown timer if it exists
        self.stop_shutdown_timer()

        self.tray_icon.hide()
        print("🚪 Application explicitly quit by user - system tray hidden")
        QApplication.quit()

    def closeEvent(self, event):
        """Handle close event - save settings and minimize to tray instead of quitting"""
        # Save all current settings before closing/minimizing
        try:
            # Update settings from GUI (same as apply_settings but without notifications)
            if hasattr(self, 'fps_combo') and self.fps_combo:
                fps_text = self.safe_get_combo_text_simple(self.fps_combo, '15')
                target_fps = 0 if fps_text == "Unlimited" else int(fps_text)
            else:
                target_fps = 15  # Default

            # Safe widget access with existence checks
            screensaver_type = self.safe_get_combo_text_simple(self.screensaver_type_combo, 'Matrix') if hasattr(self, 'screensaver_type_combo') and self.screensaver_type_combo else 'Matrix'
            color_text = self.safe_get_combo_text_simple(self.color_combo, 'green')

            self.settings.update({
                'enabled': self.settings['enabled'],
                'start_on_boot': self.safe_get_checkbox_value(self.autostart_checkbox, False),
                'show_taskbar_icon': self.safe_get_checkbox_value(self.show_taskbar_icon_checkbox, True),
                'matrix_mode': screensaver_type == 'Matrix',
                'color': color_text if color_text != 'rainbow' else 'green',
                'speed': self.safe_get_spinbox_value(self.speed_slider, 25),
                'lock_timeout': self.safe_get_spinbox_value(self.lock_spinbox, 5) * 60,
                'display_timeout': self.safe_get_spinbox_value(self.display_spinbox, 10) * 60,
                'rainbow_mode': color_text == 'rainbow',
                'bold_text': self.safe_get_checkbox_value(self.bold_checkbox, True),
                'async_scroll': True,
                'display_target': self.safe_get_combo_text_simple(self.display_combo, 'both'),
                'physical_only': self.safe_get_checkbox_value(self.physical_only_checkbox, True),
                'show_stats': self.safe_get_checkbox_value(self.show_stats_checkbox, False),
                'use_katakana': self.safe_get_checkbox_value(self.katakana_checkbox, True),
                'auto_cpu_limit': self.safe_get_checkbox_value(self.auto_cpu_limit_checkbox, False),
                'target_fps': target_fps,
                'slideshow_mode': screensaver_type == 'Slideshow',
                'slideshow_folder': self.settings.get('slideshow_folder', ''),
                'slide_duration': self.safe_get_spinbox_value(self.slide_duration_spinbox, 5),
                'slideshow_random': self.safe_get_checkbox_value(self.slideshow_random_checkbox, True),
                'slideshow_fit_mode': self.safe_get_combo_value(self.slideshow_fit_combo, ['contain', 'cover', 'stretch'], 'contain'),
                'mystify_mode': screensaver_type == 'Mystify',
                'mystify_shapes': self.safe_get_spinbox_value(self.mystify_shapes_spinbox, 3),
                'mystify_trail_length': self.safe_get_spinbox_value(self.mystify_trail_spinbox, 50),
                'mystify_complexity': self.safe_get_spinbox_value(self.mystify_complexity_spinbox, 6),
                'mystify_speed': self.safe_get_spinbox_value(self.mystify_speed_spinbox, 2),
                'mystify_color_mode': self.safe_get_combo_value(self.mystify_color_combo, ['rainbow', 'single', 'duo'], 'rainbow'),
                'mystify_fill': self.safe_get_checkbox_value(self.mystify_fill_checkbox, False),
                'auto_shutdown': self.safe_get_checkbox_value(self.auto_shutdown_checkbox, False),
                'shutdown_timeout': self.safe_get_spinbox_value(self.shutdown_spinbox, 60)
            })

            # Save settings silently
            self.save_settings()
        except Exception as e:
            print(f"Warning: Could not save settings on close: {e}")

        # Restart screensaver timer when GUI is closed/minimized
        if self.settings.get('enabled', True):
            print("🔄 GUI closing - restarting automatic monitoring")
            self.start_automatic_monitoring()
        else:
            print("🛑 Screensaver disabled - monitoring not started")

        if hasattr(self, 'tray_icon') and self.tray_icon.isVisible():
            self.hide()
            self.tray_icon.showMessage(
                "Matrix Screensaver Settings",
                "Application minimized to tray. Click the tray icon to restore.",
                QSystemTrayIcon.MessageIcon.Information,
                2000
            )
            event.ignore()
        else:
            event.accept()

    def update_speed_label(self, value):
        """Update speed label when slider changes"""
        if value == 0:
            speed_text = "Slowest"
        elif value == 50:
            speed_text = "Fastest"
        elif value <= 10:
            speed_text = f"Very Slow ({value})"
        elif value <= 20:
            speed_text = f"Slow ({value})"
        elif value <= 30:
            speed_text = f"Medium ({value})"
        elif value <= 40:
            speed_text = f"Fast ({value})"
        else:
            speed_text = f"Very Fast ({value})"
        self.speed_label.setText(f"({speed_text})")

    def on_enabled_changed(self, state):
        """Handle enable/disable checkbox"""
        if state == Qt.CheckState.Checked:
            self.status_bar.showMessage("Matrix screensaver enabled")
            # Start automatic monitoring
            self.start_automatic_monitoring()
            # Update timer button states
            self.update_timer_buttons()
        else:
            self.status_bar.showMessage("Matrix screensaver disabled")
            # Stop all timers
            self.reset_screensaver_timer()
            if hasattr(self, 'activity_timer'):
                self.activity_timer.stop()

    def on_taskbar_icon_changed(self, state):
        """Handle taskbar icon display checkbox"""
        show_icon = (state == Qt.CheckState.Checked)
        self.settings['show_taskbar_icon'] = show_icon

        if show_icon:
            self.status_bar.showMessage("Taskbar icon enabled")
            # Show the window in taskbar
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.Tool)
            self.show()
        else:
            self.status_bar.showMessage("Taskbar icon disabled")
            # Hide the window from taskbar (make it a tool window)
            self.setWindowFlags(self.windowFlags() | Qt.WindowType.Tool)
            self.show()

        # Auto-save the setting
        self.auto_save_settings()

    def restart_gui_for_theme_change(self):
        """Restart the GUI to apply theme changes"""
        try:
            import sys
            import subprocess

            # Save current settings before restart
            self.save_settings()

            # Get the current script path
            script_path = sys.argv[0]
            if not os.path.isabs(script_path):
                script_path = os.path.abspath(script_path)

            # Clean up current instance
            if hasattr(self, 'instance_manager') and self.instance_manager:
                self.instance_manager.release_lock()

            if hasattr(self, 'tray_icon'):
                self.tray_icon.hide()

            # Start new instance
            subprocess.Popen([sys.executable, script_path],
                           cwd=os.path.dirname(script_path),
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL)

            # Exit current instance
            QApplication.quit()

        except Exception as e:
            # Fallback to simple quit if restart fails
            QMessageBox.warning(self, "Restart Failed",
                              f"Could not restart automatically: {e}\nPlease restart manually.")
            self.quit_application()

    def on_dark_mode_changed(self, state):
        """Handle dark mode checkbox change"""
        dark_mode = (state == Qt.CheckState.Checked)
        self.settings['dark_mode'] = dark_mode

        if dark_mode:
            self.status_bar.showMessage("Dark mode enabled - restarting GUI...")
        else:
            self.status_bar.showMessage("Dark mode disabled - restarting GUI...")

        # Auto-save the setting
        self.auto_save_settings()

        # Close and restart the GUI to apply theme change
        self.restart_gui_for_theme_change()

    def on_screensaver_type_changed(self, text):
        """Handle screensaver type dropdown change"""
        # Enable/disable screensaver based on selection
        enabled = text != "None"
        self.settings['enabled'] = enabled
        self.settings['screensaver_type'] = text

        # Update the settings display to show relevant settings
        self.update_settings_display()

        # Update status message
        if enabled:
            self.status_bar.showMessage(f"Screensaver type changed to {text}")
        else:
            self.status_bar.showMessage("Screensaver disabled")

        self.auto_save_settings()

    def on_auto_shutdown_changed(self, state):
        """Handle auto-shutdown checkbox change"""
        enabled = (state == Qt.CheckState.Checked)
        self.settings['auto_shutdown'] = enabled

        # Enable/disable the spinbox based on checkbox state
        if hasattr(self, 'shutdown_spinbox'):
            self.shutdown_spinbox.setEnabled(enabled)

        if enabled:
            timeout_mins = self.settings.get('shutdown_timeout', 60)
            self.status_bar.showMessage(f"Auto-shutdown enabled - system will shutdown after {timeout_mins} minutes")
            # Start the shutdown timer
            self.start_shutdown_timer()
        else:
            self.status_bar.showMessage("Auto-shutdown disabled")
            # Stop the shutdown timer
            self.stop_shutdown_timer()

        # Auto-save the setting
        self.auto_save_settings()

    def stop_all_timers_for_gui(self):
        """Stop all timers when GUI is open - timer should not run with GUI visible"""
        print("🛑 GUI open - stopping all screensaver timers")
        self.screensaver_timer.stop()
        self.progress_timer.stop()
        if hasattr(self, 'activity_timer'):
            self.activity_timer.stop()
        self.status_bar.showMessage("GUI open - timers stopped")

    def restart_timers_after_test(self):
        """Restart timers after a test completes"""
        if self.settings['enabled'] and not self.is_test_mode:
            print("🔄 Restarting screensaver timers after test")
            self.last_activity_time = time.time()  # Reset activity time
            self.start_automatic_monitoring()
            self.status_bar.showMessage("Timers restarted after test")

    def apply_initial_taskbar_setting(self):
        """Apply the initial taskbar icon setting when GUI starts"""
        show_icon = self.settings.get('show_taskbar_icon', True)

        if not show_icon:
            # Hide the window from taskbar (make it a tool window)
            self.setWindowFlags(self.windowFlags() | Qt.WindowType.Tool)

    def update_autostart_desktop_entry(self):
        """Update autostart desktop entry based on start_on_boot setting"""
        try:
            autostart_dir = Path.home() / '.config' / 'autostart'
            autostart_dir.mkdir(parents=True, exist_ok=True)

            autostart_file = autostart_dir / 'matrix-screensaver.desktop'

            if self.settings.get('start_on_boot', False):
                # Create autostart desktop entry
                desktop_content = f"""[Desktop Entry]
Version=1.0
Type=Application
Name=Matrix Screensaver
Comment=Auto-start Matrix screensaver
Exec={Path.home() / '.local' / 'bin' / 'wayland_sidekick_autolock.sh'}
Icon=preferences-desktop-screensaver
Terminal=false
StartupNotify=false
Hidden=false
NoDisplay=false
Categories=System;
X-GNOME-Autostart-enabled=true
"""
                autostart_file.write_text(desktop_content)
                self.safe_status_message("Autostart enabled")
            else:
                # Remove autostart desktop entry
                if autostart_file.exists():
                    autostart_file.unlink()
                    self.safe_status_message("Autostart disabled")
        except Exception as e:
            QMessageBox.warning(self, "Warning", f"Failed to update autostart: {e}")

    def show_about(self):
        """Show about dialog with version and feature information"""
        about_text = """
<h3>🎬 Sidekick Screensaver</h3>
<p><b>Version:</b> 2.1.0</p>
<p><b>Updated:</b> September 2025</p>
<p><b>Developer:</b> Guy Mayer</p>

<h4>✨ Features:</h4>
<ul>
<li>🎨 Multiple screensaver modes: Matrix, Mystify, Slideshow</li>
<li>� Real-time performance stats with anti-burn-in drift</li>
<li>�️ Professional PyQt6 interface with dark/light themes</li>
<li>� System tray integration with persistent operation</li>
<li>� USB activity detection with instant exit</li>
<li>⏰ Smart timer management and auto-shutdown</li>
<li>🚀 Autostart support and desktop integration</li>
<li>� Intelligent FPS throttling and performance monitoring</li>
<li>📱 Multi-display support and power management</li>
<li>⚡ Robust error handling and recovery</li>
</ul>

<h4>🛠️ Requirements:</h4>
<p><b>Platform:</b> Linux (X11/Wayland)</p>
<p><b>Dependencies:</b> PyQt6, psutil, qdarkstyle</p>
<p><b>Desktop:</b> GNOME, KDE, XFCE, LXDE compatible</p>

<h4>💝 Support Development:</h4>
<p>If you find this software useful, consider supporting its development:</p>
<p>• <a href="https://github.com/sponsors/GuyMayer">GitHub Sponsors</a></p>
<p>• <a href="https://ko-fi.com/guymayer">Ko-fi</a></p>
<p>• <a href="https://www.paypal.me/guymayer">PayPal</a></p>
<p>• <a href="https://buymeacoffee.com/guymayer">Buy Me a Coffee</a></p>

<h4>🌐 Open Source:</h4>
<p>This project is open source under the MIT License.</p>
<p>Contributions welcome on <a href="https://github.com/GuyMayer/sidekick-screensaver">GitHub</a></p>
        """

        QMessageBox.about(self, "About Sidekick Screensaver", about_text)

    def run_diagnostics(self):
        """Run system diagnostics to help troubleshoot issues"""
        diagnostics = []

        # Check PyQt6
        try:
            from PyQt6.QtCore import Qt  # Use existing import instead of duplicate
            diagnostics.append("✅ PyQt6: Available")
        except ImportError:
            diagnostics.append("❌ PyQt6: Not found")

        # Check required binaries
        required_bins = [
            ('wmctrl', 'Window management'),
            ('xdotool', 'Window manipulation'),
            ('swayidle', 'Wayland idle detection'),
            ('lxterminal', 'Terminal emulator'),
            ('x-terminal-emulator', 'Alternative terminal')
        ]

        for binary, description in required_bins:
            if subprocess.run(['which', binary], capture_output=True).returncode == 0:
                diagnostics.append(f"✅ {binary}: Available ({description})")
            else:
                diagnostics.append(f"❌ {binary}: Not found ({description})")

        # Check environment
        display = os.environ.get('DISPLAY', 'Not set')
        wayland = os.environ.get('WAYLAND_DISPLAY', 'Not set')
        diagnostics.append(f"🖥️ DISPLAY: {display}")
        diagnostics.append(f"🖥️ WAYLAND_DISPLAY: {wayland}")

        # Check desktop environment
        desktop = os.environ.get('XDG_CURRENT_DESKTOP', 'Unknown')
        session = os.environ.get('XDG_SESSION_TYPE', 'Unknown')
        diagnostics.append(f"🖥️ Desktop: {desktop}")
        diagnostics.append(f"🖥️ Session: {session}")

        # Show results
        result_text = "\n".join(diagnostics)
        QMessageBox.information(self, "System Diagnostics",
                               f"<h3>🔧 System Diagnostics Report</h3><pre>{result_text}</pre>")

    def test_matrix(self):
        """Test the currently selected screensaver mode (Matrix, Mystify, or Slideshow)"""
        try:
            self.is_test_mode = True  # Mark as test mode

            # Stop the screensaver timer to prevent interference
            print("🛑 Stopping screensaver timer for test mode")
            self.screensaver_timer.stop()
            self.progress_timer.stop()
            if hasattr(self, 'activity_timer'):
                self.activity_timer.stop()

            # Check which screensaver mode is enabled and test accordingly
            screensaver_type = self.safe_get_combo_text_simple(self.screensaver_type_combo, 'Matrix')
            if screensaver_type == 'Slideshow':
                self.status_bar.showMessage("Starting slideshow test...")
                self.test_slideshow()
            elif screensaver_type == 'Mystify':
                self.status_bar.showMessage("Starting Mystify test...")
                self.test_mystify_effect()
            elif screensaver_type == 'Matrix':
                self.status_bar.showMessage("Starting Matrix test...")
                self.test_matrix_effect()
            else:
                self.status_bar.showMessage("No screensaver selected - please choose from dropdown")
                return

        except Exception as e:
            self.show()  # Restore GUI on error
            QMessageBox.critical(self, "Error", f"Failed to start test: {e}")
            self.status_bar.showMessage("Test failed")
            # Restart timers after test failure
            self.restart_timers_after_test()

    def test_matrix_effect(self):
        """Test the Matrix digital rain effect"""
        QApplication.processEvents()

        # Gather current settings
        settings = {
            'color': self.safe_get_combo_text_simple(self.color_combo, 'green') if self.safe_get_combo_text_simple(self.color_combo, 'green') != 'rainbow' else 'green',
            'speed': self.safe_get_spinbox_value(self.speed_slider, 25),
            'bold': self.safe_get_checkbox_value(self.bold_checkbox, True),
            'rainbow': self.safe_get_combo_text_simple(self.color_combo, 'green') == 'rainbow',
            'font_size': self.settings.get('font_size', 14),
            'show_stats': self.safe_get_checkbox_value(self.show_stats_checkbox, False),
            'use_katakana': self.safe_get_checkbox_value(self.katakana_checkbox, True),
            'target_fps': 0 if self.safe_get_combo_text_simple(self.fps_combo, '15') == 'Unlimited' else int(self.safe_get_combo_text_simple(self.fps_combo, '15')),
            'auto_cpu_limit': self.safe_get_checkbox_value(self.auto_cpu_limit_checkbox, False)
        }

        # Create and launch Sidekick screensaver
        from sidekick_widget import MatrixScreensaver
        self.sidekick_screensaver = MatrixScreensaver(settings)
        self.sidekick_screensaver.show()

        # Connect to close event to restore GUI
        self.sidekick_screensaver.matrix_widget.exit_requested.connect(self.on_sidekick_test_finished)
        print("🔗 Matrix screensaver exit signal connected")

        self.status_bar.showMessage("Matrix test running - press any key or click to exit")

    def test_slideshow(self):
        """Test the slideshow functionality"""
        # Check if folder is selected
        slideshow_folder = self.settings.get('slideshow_folder', '')
        if not slideshow_folder:
            QMessageBox.warning(self, "No Folder Selected",
                              "Please select an images folder for the slideshow first.")
            self.is_test_mode = False
            return

        QApplication.processEvents()

        # Gather slideshow settings
        settings = {
            'slideshow_folder': slideshow_folder,
            'slide_duration': self.safe_get_spinbox_value(self.slide_duration_spinbox, 5),
            'slideshow_random': self.safe_get_checkbox_value(self.slideshow_random_checkbox, True),
            'slideshow_fit_mode': self.safe_get_combo_value(self.slideshow_fit_combo, ['contain', 'cover', 'stretch'], 'contain'),
            'show_stats': self.safe_get_checkbox_value(self.show_stats_checkbox, False)
        }

        # Create and launch slideshow
        from slideshow_widget import SlideshowScreensaver
        self.slideshow_screensaver = SlideshowScreensaver(settings)

        # Connect to close event to restore GUI
        self.slideshow_screensaver.slideshow_widget.exit_requested.connect(self.on_slideshow_test_finished)
        print("🔗 Slideshow exit signal connected")

        self.status_bar.showMessage("Slideshow test running - press any key, click, or use arrow keys")

    def test_mystify_effect(self):
        """Test the Mystify geometric patterns effect"""
        QApplication.processEvents()

        # Gather current Mystify settings
        settings = {
            'mystify_shapes': self.settings.get('mystify_shapes', 3),
            'mystify_trail_length': self.settings.get('mystify_trail_length', 50),
            'mystify_complexity': self.settings.get('mystify_complexity', 6),
            'mystify_speed': self.settings.get('mystify_speed', 2),
            'mystify_color_mode': self.settings.get('mystify_color_mode', 'rainbow'),
            'mystify_fill': self.settings.get('mystify_fill', False),
            'mystify_color_hue': self.settings.get('mystify_color_hue', 240),
            'mystify_color_hue1': self.settings.get('mystify_color_hue1', 240),
            'mystify_color_hue2': self.settings.get('mystify_color_hue2', 60),
            'show_stats': self.safe_get_checkbox_value(self.show_stats_checkbox, False),
            'target_fps': 0 if self.safe_get_combo_text_simple(self.fps_combo, '15') == 'Unlimited' else int(self.safe_get_combo_text_simple(self.fps_combo, '15')),
            'auto_cpu_limit': self.safe_get_checkbox_value(self.auto_cpu_limit_checkbox, False)
        }

        # Create and launch Mystify screensaver
        from mystify_widget import MystifyScreensaver
        self.mystify_screensaver = MystifyScreensaver(settings)
        mystify_widget = self.mystify_screensaver.show()

        # Connect to close event to restore GUI
        if mystify_widget:
            mystify_widget.exit_requested.connect(self.on_mystify_test_finished)
            print("🔗 Mystify screensaver exit signal connected")
        else:
            print("⚠️ Failed to create mystify widget")

        self.status_bar.showMessage("Mystify test running - press any key or click to exit")

    def on_sidekick_test_finished(self):
        """Handle Matrix test completion"""
        print("🛑 Matrix test finished signal received")
        self.is_test_mode = False  # Reset test mode flag

        if hasattr(self, 'sidekick_screensaver'):
            self.sidekick_screensaver.close()
            delattr(self, 'sidekick_screensaver')

        # Restart timers after test
        self.restart_timers_after_test()

        # Exit the entire application when screensaver test closes
        QApplication.quit()

    def on_slideshow_test_finished(self):
        """Handle slideshow test completion"""
        print("🛑 Slideshow test finished signal received")
        self.is_test_mode = False  # Reset test mode flag

        if hasattr(self, 'slideshow_screensaver'):
            self.slideshow_screensaver.close()
            delattr(self, 'slideshow_screensaver')

        # Restart timers after test
        self.restart_timers_after_test()

        # Exit the entire application when slideshow test closes
        QApplication.quit()

    def on_mystify_test_finished(self):
        """Handle Mystify test completion"""
        print("🛑 Mystify test finished signal received")
        self.is_test_mode = False  # Reset test mode flag

        if hasattr(self, 'mystify_screensaver'):
            self.mystify_screensaver.close()
            delattr(self, 'mystify_screensaver')

        # Restart timers after test
        self.restart_timers_after_test()

        # Exit the entire application when screensaver test closes
        QApplication.quit()

    def stop_matrix(self):
        """Stop any running screensaver processes (Matrix, Mystify, or Slideshow)"""
        try:
            # Stop Matrix processes
            subprocess.run(['pkill', '-f', 'matrix_'], check=False)
            subprocess.run(['pkill', '-f', 'lxterminal.*matrix'], check=False)

            # Stop Python screensaver widgets
            subprocess.run(['pkill', '-f', 'sidekick_widget.py'], check=False)
            subprocess.run(['pkill', '-f', 'mystify_widget.py'], check=False)
            subprocess.run(['pkill', '-f', 'slideshow_widget.py'], check=False)

            # Stop any running test screensavers
            if hasattr(self, 'sidekick_screensaver'):
                self.sidekick_screensaver.close()
                delattr(self, 'sidekick_screensaver')

            if hasattr(self, 'mystify_screensaver'):
                self.mystify_screensaver.close()
                delattr(self, 'mystify_screensaver')

            if hasattr(self, 'slideshow_screensaver'):
                self.slideshow_screensaver.close()
                delattr(self, 'slideshow_screensaver')

            self.status_bar.showMessage("All screensaver processes stopped")
        except Exception as e:
            self.status_bar.showMessage(f"Error stopping screensaver: {e}")

    def kill_screensaver_immediately(self):
        """Immediately kill any running screensaver terminals (silent, no confirmation)"""
        try:
            # Kill all Matrix-related processes silently
            subprocess.run(['pkill', '-f', 'matrix_'], check=False,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(['pkill', '-f', 'lxterminal.*matrix'], check=False,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            # Kill all Python screensaver widgets
            subprocess.run(['pkill', '-f', 'sidekick_widget.py'], check=False,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(['pkill', '-f', 'mystify_widget.py'], check=False,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(['pkill', '-f', 'slideshow_widget.py'], check=False,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            # Kill specific screensaver terminal windows with new titles
            subprocess.run(['pkill', '-f', 'lxterminal.*Screensaver'], check=False,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            # Also kill any fullscreen terminal windows that might be running screensaver
            subprocess.run(['pkill', '-f', 'lxterminal.*fullscreen'], check=False,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            # Use wmctrl to close windows by title (if available)
            try:
                subprocess.run(['wmctrl', '-c', 'Matrix Screensaver'], check=False,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                subprocess.run(['wmctrl', '-c', 'Mystify Screensaver'], check=False,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                subprocess.run(['wmctrl', '-c', 'Slideshow Screensaver'], check=False,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except:
                pass

            # Stop any Python screensaver instances that are running in this application
            if hasattr(self, 'sidekick_screensaver') and self.sidekick_screensaver:
                try:
                    self.sidekick_screensaver.close()
                    delattr(self, 'sidekick_screensaver')
                except:
                    pass

            if hasattr(self, 'mystify_screensaver') and self.mystify_screensaver:
                try:
                    self.mystify_screensaver.close()
                    delattr(self, 'mystify_screensaver')
                except:
                    pass

            if hasattr(self, 'slideshow_screensaver') and self.slideshow_screensaver:
                try:
                    self.slideshow_screensaver.close()
                    delattr(self, 'slideshow_screensaver')
                except:
                    pass

        except Exception as e:
            # Silent failure - don't show errors during automatic activity detection
            pass

    def _safe_cleanup(self, file_path):
        """Safely cleanup temporary files"""
        try:
            if os.path.exists(file_path):
                os.unlink(file_path)
        except Exception:
            pass  # Silent cleanup failure

    def setup_screensaver_timer(self):
        """Setup screensaver countdown timer with PHYSICAL input monitoring only"""
        self.last_activity_time = time.time()

        # Timer to check for inactivity and monitor PHYSICAL activity only
        self.screensaver_timer.timeout.connect(self.check_screensaver_timeout)

        # Timer to update progress bar (updates every second)
        self.progress_timer.timeout.connect(self.update_progress_bar)

        # PHYSICAL activity monitoring timer (checks every 10 seconds for keyboard/mouse/touchpad input)
        self.activity_timer = QTimer()
        self.activity_timer.timeout.connect(self.check_user_activity)

        # Debug message
        timeout_mins = self.settings['lock_timeout'] // 60
        self.status_bar.showMessage(f"🔧 PHYSICAL input monitor setup - timeout: {timeout_mins}m")

        # Start automatic monitoring if screensaver is enabled
        if self.settings['enabled']:
            self.start_automatic_monitoring()
        else:
            # Timer display removed - no longer needed
            pass

    def start_screensaver_countdown(self):
        """Start the screensaver countdown timer"""
        if not self.settings['enabled']:
            QMessageBox.information(self, "Screensaver Disabled",
                                  "Please enable the Matrix screensaver first.")
            return

        self.last_activity_time = time.time()
        self.screensaver_active = False

        # Setup progress bar
        timeout_seconds = self.settings['lock_timeout']

        # Start timers
        self.screensaver_timer.start(1000)  # Check every second
        self.progress_timer.start(1000)     # Update progress every second

        self.status_bar.showMessage(f"Screensaver countdown started - {timeout_seconds} seconds")
        self.update_timer_buttons()

    def reset_screensaver_timer(self):
        """Reset the screensaver timer"""
        self.last_activity_time = time.time()
        self.screensaver_active = False

        # Stop all timers
        self.screensaver_timer.stop()
        self.progress_timer.stop()
        if hasattr(self, 'activity_timer'):
            self.activity_timer.stop()

        # Reset progress bar

        self.status_bar.showMessage("Screensaver timer reset")
        self.update_timer_buttons()

    def reset_activity_timer(self):
        """Manually reset the activity timer (for testing)"""
        old_time = self.last_activity_time
        self.last_activity_time = time.time()

        elapsed_before = time.time() - old_time
        self.status_bar.showMessage(f"🖱️ Activity timer manually reset (was {elapsed_before:.0f}s elapsed)")

    def start_shutdown_timer(self):
        """Start the auto-shutdown countdown timer"""
        if not self.settings.get('auto_shutdown', False):
            return

        # Stop any existing shutdown timer
        self.stop_shutdown_timer()

        # Get shutdown timeout in minutes
        timeout_minutes = self.settings.get('shutdown_timeout', 60)
        timeout_seconds = timeout_minutes * 60

        # Create shutdown timer
        self.shutdown_timer = QTimer()
        self.shutdown_timer.timeout.connect(self.execute_shutdown)
        self.shutdown_timer.setSingleShot(True)  # Single shot timer
        self.shutdown_timer.start(timeout_seconds * 1000)  # Convert to milliseconds

        print(f"🔴 Auto-shutdown timer started - system will shutdown in {timeout_minutes} minutes")
        self.status_bar.showMessage(f"🔴 Auto-shutdown timer active - {timeout_minutes} minutes remaining")

    def stop_shutdown_timer(self):
        """Stop the auto-shutdown timer"""
        if hasattr(self, 'shutdown_timer') and self.shutdown_timer:
            self.shutdown_timer.stop()
            self.shutdown_timer = None
            print("🛑 Auto-shutdown timer stopped")

    def execute_shutdown(self):
        """Execute system shutdown"""
        try:
            import subprocess
            print("🔴 EXECUTING SYSTEM SHUTDOWN - Auto-shutdown timer expired")

            # Show warning message to user before shutdown
            if hasattr(self, 'tray_icon') and self.tray_icon:
                self.tray_icon.showMessage(
                    "System Shutdown",
                    "System is shutting down due to auto-shutdown timer.",
                    QSystemTrayIcon.MessageIcon.Warning,
                    5000
                )

            # Wait a moment for the message to display
            QTimer.singleShot(3000, self.perform_shutdown)

        except Exception as e:
            print(f"❌ Error initiating shutdown: {e}")

    def perform_shutdown(self):
        """Perform the actual system shutdown"""
        try:
            import subprocess

            # Save settings before shutdown
            self.save_settings()

            # Execute shutdown command
            subprocess.run(['shutdown', '-h', 'now'], check=False)

        except Exception as e:
            print(f"❌ Error executing shutdown: {e}")
            # Fallback shutdown methods
            try:
                subprocess.run(['systemctl', 'poweroff'], check=False)
            except:
                try:
                    subprocess.run(['poweroff'], check=False)
                except:
                    print("❌ All shutdown methods failed")

    def check_screensaver_timeout(self):
        """Check if screensaver should activate"""
        # Don't activate screensaver if we're in test mode
        if hasattr(self, 'is_test_mode') and self.is_test_mode:
            return

        current_time = time.time()
        elapsed_time = current_time - self.last_activity_time
        timeout_seconds = self.settings['lock_timeout']

        # Enhanced Debug: Show what's happening with more detail
        if elapsed_time >= timeout_seconds and not self.screensaver_active:
            print(f"🚀 SCREENSAVER TIMEOUT REACHED! elapsed={elapsed_time:.1f}s, timeout={timeout_seconds}s, active={self.screensaver_active}")
            self.status_bar.showMessage(f"🚀 ACTIVATING SCREENSAVER - {elapsed_time:.0f}s >= {timeout_seconds}s")
            self.activate_screensaver()
        elif self.screensaver_active:
            # Already active, don't spam activation
            pass
        else:
            # Show debug info more frequently for testing
            if int(elapsed_time) % 10 == 0:  # Every 10 seconds instead of 30
                remaining = timeout_seconds - elapsed_time
                print(f"🕐 Timer check: {elapsed_time:.0f}s/{timeout_seconds}s - {remaining:.0f}s remaining - active={self.screensaver_active}")
                self.status_bar.showMessage(f"⏳ Timer: {elapsed_time:.0f}s/{timeout_seconds}s - {remaining:.0f}s remaining")

    def update_progress_bar(self):
        """Update the progress bar showing time until screensaver"""
        current_time = time.time()
        elapsed_time = int(current_time - self.last_activity_time)
        timeout_seconds = self.settings['lock_timeout']

        remaining_time = max(0, timeout_seconds - elapsed_time)

            # Make sure progress bar is visible and properly configured
            # Add format to show current/total

        if remaining_time > 0:
            minutes = remaining_time // 60
            seconds = remaining_time % 60
            # Update status bar with debug info
            # self.status_bar.showMessage(f"Timer active: {elapsed_time}s elapsed, {remaining_time}s remaining")
        else:
            if not self.screensaver_active:
                self.status_bar.showMessage(f"⚠️ TIMEOUT REACHED - elapsed: {elapsed_time}s, timeout: {timeout_seconds}s")

    def activate_screensaver(self):
        """Activate the selected screensaver mode"""
        print("🚀 ACTIVATING SCREENSAVER!")  # Debug print
        print(f"🔧 Settings check - enabled: {self.settings.get('enabled', False)}")  # Debug

        self.screensaver_active = True
        self.is_test_mode = False  # This is normal operation, not a test
        self.progress_timer.stop()
        self.screensaver_timer.stop()

        # Determine screensaver type from saved settings (not GUI widgets)
        # This ensures it works both in GUI mode and autostart/background mode
        screensaver_type = None
        
        if not self.settings.get('enabled', True):
            screensaver_type = 'None'
        elif self.settings.get('slideshow_mode', False):
            screensaver_type = 'Slideshow'
        elif self.settings.get('mystify_mode', False):
            screensaver_type = 'Mystify'
        elif self.settings.get('matrix_mode', True):
            screensaver_type = 'Matrix'
        else:
            # Fallback to Matrix if no mode is set
            screensaver_type = 'Matrix'
        
        print(f"🎯 Determined screensaver type from settings: {screensaver_type}")
        print(f"🔧 Settings state - matrix_mode: {self.settings.get('matrix_mode')}, mystify_mode: {self.settings.get('mystify_mode')}, slideshow_mode: {self.settings.get('slideshow_mode')}")

        if screensaver_type == 'Slideshow':
            self.status_bar.showMessage("🚀 Slideshow screensaver LAUNCHING...")
            self.activate_slideshow_screensaver()
        elif screensaver_type == 'Mystify':
            self.status_bar.showMessage("🚀 Mystify screensaver LAUNCHING...")
            self.activate_mystify_screensaver()
        elif screensaver_type == 'Matrix':
            self.status_bar.showMessage("🚀 Matrix screensaver LAUNCHING...")
            self.activate_sidekick_screensaver()
        elif screensaver_type == 'None':
            self.status_bar.showMessage("⚠️ Screensaver disabled - not launching")
            return
        else:
            self.status_bar.showMessage("❌ No screensaver configured - defaulting to Matrix")
            self.activate_sidekick_screensaver()

        self.update_timer_buttons()

    def activate_sidekick_screensaver(self):
        """Activate the Matrix screensaver using native Python widget"""

        try:
            print("📱 Using native Python Matrix widget for screensaver...")  # Debug print

            # CLOSE ALL GUI APPLICATIONS BEFORE SCREENSAVER STARTS
            print("🗄️ Closing all GUI applications before screensaver...")
            self.close_all_gui_applications()

            # Gather current settings - use saved settings instead of GUI widgets for autostart compatibility
            settings = {
                'color': self.settings.get('color', 'green') if not self.settings.get('rainbow_mode', False) else 'green',
                'speed': self.settings.get('speed', 25),
                'bold': self.settings.get('bold_text', True),
                'rainbow': self.settings.get('rainbow_mode', False),
                'font_size': self.settings.get('font_size', 14),
                'show_stats': self.settings.get('show_stats', False),
                'use_katakana': self.settings.get('use_katakana', True),
                'target_fps': self.settings.get('target_fps', 15),
                'auto_cpu_limit': self.settings.get('auto_cpu_limit', False)
            }

            print(f"🔧 Matrix screensaver settings: {settings}")  # Debug

            # Hide the settings window after closing other GUIs (only if GUI exists)
            if self.isVisible():
                print("🗄️ Hiding settings window before screensaver launch...")
                self.hide()

            # Create and launch Matrix screensaver
            self.active_screensaver = MatrixScreensaver(settings)
            self.active_screensaver.show()

            # Connect to close event to handle screensaver exit
            self.active_screensaver.matrix_widget.exit_requested.connect(self.on_screensaver_exit)

            print("✅ Native Python Matrix screensaver launched successfully!")  # Debug

        except Exception as e:
            print(f"❌ Matrix screensaver error: {e}")  # Debug print
            import traceback
            print(f"❌ Full traceback: {traceback.format_exc()}")  # Full error details
            self.status_bar.showMessage(f"❌ Matrix screensaver failed: {e}")
            # Restore GUI on error (only if it was visible)
            if hasattr(self, 'isVisible') and not self.isVisible():
                self.show()

    def activate_slideshow_screensaver(self):
        """Activate the slideshow screensaver"""
        try:
            print("📸 Using slideshow screensaver...")

            # CLOSE ALL GUI APPLICATIONS BEFORE SCREENSAVER STARTS
            self.close_all_gui_applications()

            # Gather slideshow settings - use saved settings for autostart compatibility
            settings = {
                'slideshow_folder': self.settings.get('slideshow_folder', ''),
                'slide_duration': self.settings.get('slide_duration', 5.0),
                'slideshow_random': self.settings.get('slideshow_random', True),
                'slideshow_fit_mode': self.settings.get('slideshow_fit_mode', 'contain'),
                'show_stats': self.settings.get('show_stats', False),
                'target_fps': self.settings.get('target_fps', 15),
            }

            print(f"🔧 Slideshow screensaver settings: {settings}")

            # Hide the settings window (only if GUI exists)
            if self.isVisible():
                self.hide()

            # Create and launch slideshow screensaver
            from slideshow_widget import SlideshowScreensaver
            self.active_screensaver = SlideshowScreensaver(settings)
            self.active_screensaver.show()

            # Connect to close event
            self.active_screensaver.slideshow_widget.exit_requested.connect(self.on_screensaver_exit)

            print("✅ Slideshow screensaver launched successfully!")

        except Exception as e:
            print(f"❌ Slideshow screensaver error: {e}")
            import traceback
            print(f"❌ Full traceback: {traceback.format_exc()}")
            self.status_bar.showMessage(f"❌ Slideshow screensaver failed: {e}")
            if hasattr(self, 'isVisible') and not self.isVisible():
                self.show()

    def activate_mystify_screensaver(self):
        """Activate the Mystify screensaver"""
        try:
            print("🔶 Using Mystify screensaver...")
            print(f"🔍 Debug - Timer states before mystify: screensaver_timer.isActive()={self.screensaver_timer.isActive()}, progress_timer.isActive()={self.progress_timer.isActive()}")
            if hasattr(self, 'activity_timer'):
                print(f"🔍 Debug - activity_timer.isActive()={self.activity_timer.isActive()}")

            # STOP ALL TIMERS BEFORE SCREENSAVER - This might be the key fix!
            print("🛑 Stopping all GUI timers before mystify launch")
            self.screensaver_timer.stop()
            self.progress_timer.stop()
            if hasattr(self, 'activity_timer'):
                self.activity_timer.stop()

            # CLOSE ALL GUI APPLICATIONS BEFORE SCREENSAVER STARTS
            self.close_all_gui_applications()

            # Gather mystify settings - use saved settings for autostart compatibility
            settings = {
                'mystify_shapes': self.settings.get('mystify_shapes', 3),
                'mystify_trail_length': self.settings.get('mystify_trail_length', 50),
                'mystify_complexity': self.settings.get('mystify_complexity', 6),
                'mystify_speed': self.settings.get('mystify_speed', 2),
                'mystify_color_mode': self.settings.get('mystify_color_mode', 'rainbow'),
                'mystify_fill': self.settings.get('mystify_fill', False),
                'mystify_color_hue': self.settings.get('mystify_color_hue', 240),
                'mystify_color_hue1': self.settings.get('mystify_color_hue1', 240),
                'mystify_color_hue2': self.settings.get('mystify_color_hue2', 60),
                'show_stats': self.settings.get('show_stats', False),
                'target_fps': self.settings.get('target_fps', 15),
                'auto_cpu_limit': self.settings.get('auto_cpu_limit', False)
            }

            print(f"🔧 Mystify screensaver settings: {settings}")

            # Hide the settings window (only if GUI exists)
            if self.isVisible():
                self.hide()

            # Create and launch mystify screensaver
            from mystify_widget import MystifyScreensaver
            self.active_screensaver = MystifyScreensaver(settings)
            self.active_screensaver.show()

            # Connect to close event if mystify_widget was created successfully
            if self.active_screensaver.mystify_widget is not None:
                self.active_screensaver.mystify_widget.exit_requested.connect(self.on_screensaver_exit)

            print("✅ Mystify screensaver launched successfully!")

        except Exception as e:
            print(f"❌ Mystify screensaver error: {e}")
            import traceback
            print(f"❌ Full traceback: {traceback.format_exc()}")
            self.status_bar.showMessage(f"❌ Mystify screensaver failed: {e}")
            if hasattr(self, 'isVisible') and not self.isVisible():
                self.show()

    def close_all_gui_applications(self):
        """Close only the screensaver settings GUI window before screensaver starts"""
        print("🗄️ Closing screensaver settings window...")

        try:
            # Method 1: Close screensaver settings windows using wmctrl
            try:
                # Get list of all windows
                result = subprocess.run(['wmctrl', '-l'],
                                      capture_output=True,
                                      text=True,
                                      timeout=5)

                if result.returncode == 0:
                    windows = result.stdout.strip().split('\n')
                    settings_window_keywords = [
                        'screensaver preferences',
                        'screensaver',
                        'preferences'
                    ]

                    for window_line in windows:
                        if window_line.strip():
                            # Extract window title (last part after multiple spaces)
                            parts = window_line.split()
                            if len(parts) >= 4:
                                window_title = ' '.join(parts[3:]).lower()

                                # Check if this is a screensaver settings window
                                for keyword in settings_window_keywords:
                                    if keyword in window_title:
                                        window_id = parts[0]
                                        try:
                                            # Close the settings window
                                            subprocess.run(['wmctrl', '-i', '-c', window_id],
                                                         check=False,
                                                         stdout=subprocess.DEVNULL,
                                                         stderr=subprocess.DEVNULL,
                                                         timeout=2)
                                            print(f"   🔸 Closed settings window: {window_title}")
                                        except Exception:
                                            pass
                                        break

            except Exception as e:
                print(f"   ⚠️ wmctrl method failed: {e}")

            # Method 2: Kill only screensaver preferences processes
            screensaver_apps_to_close = [
                'screensaver_preferences.py',
                'screensaver_preferences_qt6.py'
            ]

            for app in screensaver_apps_to_close:
                try:
                    # Kill by process name (but not ourselves)
                    current_pid = os.getpid()

                    # Get processes matching the app name
                    result = subprocess.run(['pgrep', '-f', app],
                                          capture_output=True,
                                          text=True,
                                          timeout=3)

                    if result.returncode == 0:
                        pids = result.stdout.strip().split('\n')
                        for pid_str in pids:
                            if pid_str.strip():
                                try:
                                    pid = int(pid_str.strip())
                                    # Don't kill our own process
                                    if pid != current_pid:
                                        subprocess.run(['kill', str(pid)],
                                                     check=False,
                                                     stdout=subprocess.DEVNULL,
                                                     stderr=subprocess.DEVNULL,
                                                     timeout=2)
                                        print(f"   🔸 Closed duplicate settings process: PID {pid}")
                                except (ValueError, subprocess.TimeoutExpired):
                                    continue

                except Exception:
                    pass  # Continue if kill fails

            print("✅ Settings window cleanup completed")

        except Exception as e:
            print(f"❌ Error closing settings window: {e}")

    def on_screensaver_exit(self):
        """Handle screensaver exit and restart monitoring"""
        print("🚪 Screensaver exited by user input")  # Debug print

        if hasattr(self, 'active_screensaver'):
            self.active_screensaver.close()
            delattr(self, 'active_screensaver')

        # Mark screensaver as inactive
        self.screensaver_active = False

        # Restart activity monitoring
        self.last_activity_time = time.time()
        if self.settings['enabled']:
            print("🔄 Restarting activity monitoring...")  # Debug print
            self.start_automatic_monitoring()

        # ENSURE SYSTEM TRAY REMAINS VISIBLE AND ACCESSIBLE
        if hasattr(self, 'tray_icon') and self.tray_icon:
            # Force show the system tray icon
            self.tray_icon.show()

            # Update tray tooltip to show monitoring is active
            self.tray_icon.setToolTip("Screensaver Settings - Monitoring Active")

            # Force a tray message to confirm it's working
            if self.tray_icon.isVisible():
                self.tray_icon.showMessage(
                    "Screensaver Monitoring",
                    "Screensaver deactivated. Monitoring resumed.",
                    QSystemTrayIcon.MessageIcon.Information,
                    3000
                )
                print("🔧 System tray icon confirmed visible and active")
            else:
                print("⚠️ System tray icon not visible - attempting to restore")
                # Try to recreate tray icon if needed
                self.setup_system_tray()
        else:
            print("⚠️ System tray icon missing - recreating")
            self.setup_system_tray()

        # For normal operation, stay hidden (GUI should not pop up)
        # Only show GUI briefly if this was a test
        if self.is_test_mode:
            # Show GUI briefly for test mode only
            self.show()
            if self.settings['enabled'] and hasattr(self, 'tray_icon') and self.tray_icon.isVisible():
                # Auto-hide after a short delay
                QTimer.singleShot(2000, self.hide)
        else:
            # Normal operation - ensure GUI stays hidden but app keeps running
            self.hide()
            print("🔒 GUI hidden, continuing background monitoring with system tray")

        self.is_test_mode = False  # Reset test mode flag

        self.status_bar.showMessage("Screensaver deactivated - monitoring resumed")
        print("✅ Activity monitoring resumed, system tray persistent")  # Debug print

    def aggressive_maximize(self, window_title):
        """AGGRESSIVELY maximize terminal using ALL available methods"""
        try:
            # Set display environment
            display_env = os.environ.copy()
            if not display_env.get('DISPLAY'):
                display_env['DISPLAY'] = ':0'

            # Method 1: wmctrl maximize
            subprocess.run(['wmctrl', '-r', window_title, '-b', 'add,maximized_vert,maximized_horz'],
                         env=display_env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=2)

            # Method 2: wmctrl fullscreen
            subprocess.run(['wmctrl', '-r', window_title, '-b', 'add,fullscreen'],
                         env=display_env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=2)

            # Method 3: wmctrl move to front and resize
            subprocess.run(['wmctrl', '-r', window_title, '-e', '0,0,0,-1,-1'],
                         env=display_env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=2)

            # Method 4: xdotool maximize
            try:
                subprocess.run(['xdotool', 'search', '--name', window_title, 'windowstate', '--add', 'MAXIMIZED_VERT', 'MAXIMIZED_HORZ'],
                             env=display_env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=2)
            except:
                pass

            # Method 5: xdotool fullscreen
            try:
                subprocess.run(['xdotool', 'search', '--name', window_title, 'windowstate', '--add', 'FULLSCREEN'],
                             env=display_env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=2)
            except:
                pass

        except Exception as e:
            # Silent failure - maximization is best effort
            pass

    def update_timer_buttons(self):
        """Timer buttons removed - this method does nothing now"""
        pass  # Buttons removed per user request

    def start_automatic_monitoring(self):
        """Start automatic activity monitoring for real screensaver behavior"""
        if not self.settings['enabled']:
            return

        self.last_activity_time = time.time()
        self.screensaver_active = False

        # Start the activity monitoring timer - MUCH MORE SENSITIVE! (checks every 2 seconds for USB activity)
        self.activity_timer.start(2000)  # Changed from 10000ms to 2000ms for faster USB detection

        # Start the main screensaver timer (checks every second)
        self.screensaver_timer.start(1000)

        # Start progress updates
        self.progress_timer.start(1000)

        # Setup progress bar for automatic mode
        timeout_seconds = self.settings['lock_timeout']

        self.status_bar.showMessage(f"🟢 PHYSICAL INPUT MONITOR - timeout: {timeout_seconds//60}m{timeout_seconds%60}s")

    def check_user_activity(self):
        """Check for PHYSICAL user activity ONLY (keyboard/mouse/touchpad input)"""
        try:
            import subprocess

            current_time = time.time()

            # Set up display environment for xprintidle
            display_env = os.environ.copy()
            if not display_env.get('DISPLAY'):
                display_env['DISPLAY'] = ':0'
            if not display_env.get('WAYLAND_DISPLAY'):
                display_env['WAYLAND_DISPLAY'] = 'wayland-0'

            # Method 1: Try xprintidle (physical input only)
            activity_detected = False
            try:
                result = subprocess.run(['xprintidle'], capture_output=True, text=True,
                                      timeout=2, env=display_env)
                if result.returncode == 0:
                    idle_ms = int(result.stdout.strip())
                    idle_seconds = idle_ms / 1000

                    # Recent physical input detected
                    if idle_seconds < 3:  # Less than 3 seconds = recent PHYSICAL input
                        activity_detected = True

                        # Show current idle status
                        elapsed = current_time - getattr(self, '_last_status_msg', 0)
                        if elapsed > 30:  # Show status every 30 seconds
                            self.status_bar.showMessage(f"✅ xprintidle working - idle: {idle_seconds:.1f}s")
                            self._last_status_msg = current_time
                    else:
                        # Show current idle time occasionally for debugging
                        elapsed = current_time - getattr(self, '_last_idle_msg', 0)
                        if elapsed > 30:  # Show idle status every 30 seconds
                            mins = int(idle_seconds // 60)
                            secs = int(idle_seconds % 60)
                            self.status_bar.showMessage(f"⏰ xprintidle: no input for {mins}m{secs}s")
                            self._last_idle_msg = current_time
                else:
                    # xprintidle failed, try fallback methods
                    elapsed = current_time - getattr(self, '_last_error_msg', 0)
                    if elapsed > 30:  # Show error every 30 seconds
                        self.status_bar.showMessage(f"⚠️ xprintidle failed (code {result.returncode}) - using fallback")
                        self._last_error_msg = current_time

                    # Fallback: Check for recent mouse/keyboard processes or file modifications
                    activity_detected = self.check_activity_fallback()

            except Exception as e:
                # xprintidle error, use fallback
                elapsed = current_time - getattr(self, '_last_error_msg', 0)
                if elapsed > 30:  # Show error every 30 seconds
                    self.status_bar.showMessage(f"⚠️ xprintidle error: {str(e)[:20]} - using fallback")
                    self._last_error_msg = current_time

                # Fallback: Check for recent activity
                activity_detected = self.check_activity_fallback()

                # Enhanced: Check specifically for USB mouse activity
                mouse_activity = self.check_usb_mouse_activity()

                # If either activity type detected, reset timer
                if activity_detected or mouse_activity:
                    # RESET EVERYTHING - full timer reset
                    self.last_activity_time = current_time
                self.screensaver_active = False  # Allow screensaver to activate again

                # IMMEDIATELY KILL any running screensaver terminals (no confirmation)
                self.kill_screensaver_immediately()

                # Show message (but not too frequently)
                elapsed = current_time - getattr(self, '_last_input_msg', 0)
                if elapsed > 5:  # Show message every 5 seconds for better feedback
                    self.status_bar.showMessage(f"⌨️🖱️ PHYSICAL input DETECTED - TIMER RESET")
                    self._last_input_msg = current_time

        except Exception as e:
            # General error
            elapsed = current_time - getattr(self, '_last_general_error', 0)
            if elapsed > 60:  # Show error every minute
                self.status_bar.showMessage(f"⚠️ Activity detection error: {str(e)[:30]}")
                self._last_general_error = current_time

    def check_activity_fallback(self) -> bool:
        """USB interrupt monitoring (ULTRA SENSITIVE - immediate response)"""
        try:
            current_time = time.time()

            # ULTRA SENSITIVE USB interrupt monitoring - detect ANY change immediately
            try:
                with open('/proc/interrupts', 'r') as f:
                    content = f.read()

                usb_interrupts = 0
                hid_interrupts = 0

                # Look for ALL USB/HID related interrupts - be more inclusive
                for line in content.split('\n'):
                    line_lower = line.lower()
                    if any(keyword in line_lower for keyword in ['usb', 'ehci', 'ohci', 'xhci', 'hid', 'input', 'mouse', 'keyboard']):
                        parts = line.split()
                        if len(parts) > 1:
                            # Sum all CPU columns (skip first column which is IRQ number)
                            for i in range(1, len(parts)):
                                if parts[i].isdigit():
                                    if 'usb' in line_lower or 'ehci' in line_lower or 'ohci' in line_lower or 'xhci' in line_lower:
                                        usb_interrupts += int(parts[i])
                                    else:
                                        hid_interrupts += int(parts[i])
                                else:
                                    break

                total_interrupts = usb_interrupts + hid_interrupts

                # Initialize baseline on first run
                if not hasattr(self, '_interrupt_baseline'):
                    self._interrupt_baseline = total_interrupts
                    self.status_bar.showMessage(f"🔌 ULTRA SENSITIVE USB/HID monitoring - baseline: {total_interrupts}")
                    return False

                # ULTRA SENSITIVE: Detect even the smallest change
                interrupt_diff = total_interrupts - self._interrupt_baseline

                if interrupt_diff > 0:  # ANY activity detected - immediate response
                    # Update baseline immediately
                    self._interrupt_baseline = total_interrupts

                    # Show activity message immediately (no throttling for ultra sensitivity)
                    elapsed = current_time - getattr(self, '_last_activity_msg', 0)
                    if elapsed > 1:  # Show message every 1 second (very frequent feedback)
                        self.status_bar.showMessage(f"� ULTRA SENSITIVE! USB/HID +{interrupt_diff} interrupts - IMMEDIATE TIMER RESET")
                        self._last_activity_msg = current_time
                    return True
                else:
                    # Update baseline (no activity)
                    self._interrupt_baseline = total_interrupts

                    # Show monitoring status occasionally
                    elapsed = current_time - getattr(self, '_last_status_msg', 0)
                    if elapsed > 15:  # Show status every 15 seconds
                        self.status_bar.showMessage(f"🔌 Ultra sensitive monitoring active - total interrupts: {total_interrupts}")
                        self._last_status_msg = current_time
                    return False

            except Exception as e:
                # USB monitoring failed
                elapsed = current_time - getattr(self, '_last_usb_error', 0)
                if elapsed > 30:  # Show errors more frequently for debugging
                    self.status_bar.showMessage(f"⚠️ USB monitoring error: {str(e)[:25]}")
                    self._last_usb_error = current_time
                return False

        except Exception as e:
            return False

    def check_usb_mouse_activity(self) -> bool:
        """Enhanced USB mouse movement detection"""
        try:
            import glob
            import os
            current_time = time.time()

            # Method 1: Check USB mouse device files for recent access
            mouse_devices = glob.glob('/dev/input/mouse*') + glob.glob('/dev/input/event*')

            for device_path in mouse_devices:
                try:
                    # Check device access time
                    stat_info = os.stat(device_path)
                    access_time = stat_info.st_atime

                    # Initialize baseline for this device
                    baseline_attr = f'_mouse_access_{device_path.replace("/", "_").replace(".", "_")}'
                    if not hasattr(self, baseline_attr):
                        setattr(self, baseline_attr, access_time)
                        continue

                    last_access = getattr(self, baseline_attr)

                    # Check if accessed within last 3 seconds (mouse movement)
                    if access_time > last_access:
                        setattr(self, baseline_attr, access_time)
                        self.status_bar.showMessage(f"🖱️ USB mouse movement detected on {device_path}")
                        return True

                except (OSError, IOError):
                    # Device might not be accessible, skip
                    continue

            # Method 2: Check /proc/bus/input/devices for USB mouse info
            try:
                with open('/proc/bus/input/devices', 'r') as f:
                    devices_content = f.read()

                # Look for USB mouse devices
                if 'mouse' in devices_content.lower() and 'usb' in devices_content.lower():
                    # Get current content hash to detect changes
                    import hashlib
                    content_hash = hashlib.md5(devices_content.encode()).hexdigest()

                    if not hasattr(self, '_devices_hash'):
                        self._devices_hash = content_hash
                        return False

                    if content_hash != self._devices_hash:
                        self._devices_hash = content_hash
                        self.status_bar.showMessage(f"🔌 USB input device change detected")
                        return True

            except Exception:
                pass

            # Method 3: Check xinput for USB mouse activity (if available)
            try:
                import subprocess
                result = subprocess.run(['xinput', 'list'], capture_output=True, text=True, timeout=2)
                if result.returncode == 0:
                    xinput_output = result.stdout.lower()
                    if 'mouse' in xinput_output and 'usb' in xinput_output:
                        # Simple change detection
                        import hashlib
                        xinput_hash = hashlib.md5(xinput_output.encode()).hexdigest()

                        if not hasattr(self, '_xinput_hash'):
                            self._xinput_hash = xinput_hash
                            return False

                        if xinput_hash != self._xinput_hash:
                            self._xinput_hash = xinput_hash
                            self.status_bar.showMessage(f"🖱️ X11 mouse state change detected")
                            return True

            except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
                pass

            return False

        except Exception as e:
            return False

    def force_maximize_terminal(self, window_title_part):
        """Force maximize terminal window using multiple methods with proper display environment"""
        # Set up display environment for maximization tools
        display_env = os.environ.copy()
        if 'DISPLAY' not in display_env:
            display_env['DISPLAY'] = ':0'
        if 'WAYLAND_DISPLAY' not in display_env:
            display_env['WAYLAND_DISPLAY'] = 'wayland-0'

        # Wait a moment for terminal window to appear
        QTimer.singleShot(1000, lambda: self._do_maximize(window_title_part, display_env))

    def _do_maximize(self, window_title_part, display_env):
        """Perform AGGRESSIVE maximization with multiple title attempts"""
        try:
            print(f"🔧 Attempting to maximize window with title containing: '{window_title_part}'")

            # Get list of all windows first to see what's available
            try:
                result = subprocess.run(['wmctrl', '-l'], capture_output=True, text=True, timeout=5, env=display_env)
                if result.returncode == 0 and result.stdout.strip():
                    print("🔧 Available windows (wmctrl):")
                    for line in result.stdout.split('\n'):
                        if line.strip():
                            print(f"   📋 {line}")
                else:
                    print("🔧 wmctrl found no windows, trying xdotool...")
                    # Try xdotool as alternative
                    result = subprocess.run(['xdotool', 'search', '--name', '.*'],
                                          capture_output=True, text=True, timeout=5, env=display_env)
                    if result.returncode == 0:
                        window_ids = result.stdout.strip().split('\n')
                        print("🔧 Available windows (xdotool):")
                        for wid in window_ids:
                            if wid.strip():
                                try:
                                    name_result = subprocess.run(['xdotool', 'getwindowname', wid.strip()],
                                                               capture_output=True, text=True, timeout=2, env=display_env)
                                    if name_result.returncode == 0:
                                        print(f"   📋 {wid}: {name_result.stdout.strip()}")
                                except:
                                    pass
            except Exception as e:
                print(f"🔧 Window detection error: {e}")

            # Try multiple title variations for screensaver window (CASE INSENSITIVE)
            title_variations = [
                window_title_part.lower(),
                "matrix",
                "sidekick",
                "mystify",
                "slideshow",
                "lxterminal",
                "terminal",
                "bash"
            ]

            # Method 1: wmctrl with case insensitive matching
            for title in title_variations:
                try:
                    print(f"🔧 Trying to maximize window with title: '{title}' (wmctrl)")

                    # Try both exact match and partial match, case insensitive
                    for match_type in [title, f".*{title}.*"]:
                        # Remove window decorations (title bar)
                        subprocess.run(['wmctrl', '-r', match_type, '-b', 'remove,decorations'],
                                     check=False, capture_output=True, timeout=3, env=display_env)

                        # Maximize window
                        result1 = subprocess.run(['wmctrl', '-r', match_type, '-b', 'add,maximized_vert,maximized_horz'],
                                  check=False, capture_output=True, timeout=3, env=display_env)
                        result2 = subprocess.run(['wmctrl', '-r', match_type, '-b', 'add,fullscreen'],
                                  check=False, capture_output=True, timeout=3, env=display_env)

                        if result1.returncode == 0 or result2.returncode == 0:
                            print(f"✅ Successfully maximized and removed decorations for window: '{match_type}'")
                            return

                except Exception as e:
                    print(f"❌ wmctrl error with title '{title}': {e}")
                    continue

            # Method 2: xdotool with case insensitive search
            try:
                print("🔧 Trying xdotool maximization...")
                for title in title_variations:
                    # Search for windows containing the title (case insensitive)
                    search_patterns = [
                        f".*{title}.*",
                        title,
                        title.upper(),
                        title.capitalize()
                    ]

                    for pattern in search_patterns:
                        try:
                            # Find windows matching pattern
                            result = subprocess.run(['xdotool', 'search', '--name', pattern],
                                                  capture_output=True, text=True, timeout=3, env=display_env)
                            if result.returncode == 0 and result.stdout.strip():
                                window_ids = result.stdout.strip().split('\n')
                                for wid in window_ids:
                                    if wid.strip():
                                        try:
                                            # Remove window decorations (title bar) with xdotool
                                            subprocess.run(['xdotool', 'windowstate', wid.strip(), '--remove', 'DECORATIONS'],
                                                         check=False, timeout=2, env=display_env)

                                            # Maximize window
                                            subprocess.run(['xdotool', 'windowsize', wid.strip(), '100%', '100%'],
                                                         check=False, timeout=2, env=display_env)
                                            subprocess.run(['xdotool', 'windowmove', wid.strip(), '0', '0'],
                                                         check=False, timeout=2, env=display_env)
                                            print(f"✅ Successfully maximized and removed decorations for window {wid} with pattern: '{pattern}'")
                                            return
                                        except Exception as e:
                                            print(f"❌ Failed to maximize window {wid}: {e}")
                        except Exception as e:
                            continue
            except Exception as e:
                print(f"❌ xdotool error: {e}")

            # Method 3: Brute force - try to maximize any terminal-like process
            try:
                print("🔧 Trying brute force maximization of any terminal...")
                # Get all window IDs
                result = subprocess.run(['xdotool', 'search', '--name', '.*'],
                                      capture_output=True, text=True, timeout=5, env=display_env)
                if result.returncode == 0:
                    window_ids = result.stdout.strip().split('\n')
                    for wid in window_ids[:10]:  # Limit to first 10 windows
                        if wid.strip():
                            try:
                                # Get window name
                                name_result = subprocess.run(['xdotool', 'getwindowname', wid.strip()],
                                                           capture_output=True, text=True, timeout=2, env=display_env)
                                if name_result.returncode == 0:
                                    window_name = name_result.stdout.strip().lower()
                                    # Check if this looks like a terminal or screensaver window
                                    if any(term in window_name for term in ['terminal', 'bash', 'matrix', 'sidekick', 'mystify', 'slideshow']):
                                        # Remove decorations first
                                        subprocess.run(['xdotool', 'windowstate', wid.strip(), '--remove', 'DECORATIONS'],
                                                     check=False, timeout=2, env=display_env)
                                        # Then maximize
                                        subprocess.run(['xdotool', 'windowsize', wid.strip(), '100%', '100%'],
                                                     check=False, timeout=2, env=display_env)
                                        subprocess.run(['xdotool', 'windowmove', wid.strip(), '0', '0'],
                                                     check=False, timeout=2, env=display_env)
                                        print(f"✅ Brute force maximized and removed decorations for window: {window_name}")
                                        return
                            except:
                                continue
            except Exception as e:
                print(f"❌ Brute force error: {e}")

            print("❌ All maximization methods failed")

        except Exception as e:
            print(f"❌ Maximization error: {e}")

        except:
            try:
                # Method 3: Use xdotool
                subprocess.run(['xdotool', 'search', '--name', window_title_part, 'windowstate', '--add', 'MAXIMIZED_VERT', 'MAXIMIZED_HORZ'],
                              check=False, capture_output=True, timeout=5, env=display_env)

                # Method 4: Try fullscreen with xdotool
                subprocess.run(['xdotool', 'search', '--name', window_title_part, 'windowstate', '--add', 'FULLSCREEN'],
                              check=False, capture_output=True, timeout=5, env=display_env)
            except:
                pass  # If all methods fail, continue

    def cleanup_temp_file(self, file_path):
        """Clean up temporary files"""
        try:
            os.unlink(file_path)
        except:
            pass  # Ignore cleanup errors

    def browse_slideshow_folder(self):
        """Open folder browser for slideshow images"""
        current_folder = self.settings.get('slideshow_folder', '')
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Images Folder for Slideshow",
            current_folder,
            QFileDialog.Option.ShowDirsOnly
        )

        if folder:
            self.settings['slideshow_folder'] = folder
            self.slideshow_folder_label.setText(folder)
            self.slideshow_folder_label.setStyleSheet("color: #00ff00;")

            # Count images in the folder
            image_count = self.count_images_in_folder(folder)
            if image_count > 0:
                self.slideshow_folder_label.setToolTip(f"{image_count} images found")
            else:
                self.slideshow_folder_label.setToolTip("No images found in this folder")
                self.slideshow_folder_label.setStyleSheet("color: #ff8800;")

            # Auto-save the settings
            self.auto_save_settings()

    def count_images_in_folder(self, folder_path) -> int:
        """Count supported image files in the folder"""
        try:
            from pathlib import Path
            folder = Path(folder_path)
            image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp'}

            count = 0
            for file_path in folder.glob('*'):
                if file_path.is_file() and file_path.suffix.lower() in image_extensions:
                    count += 1
            return count
        except Exception:
            return 0

    def toggle_slideshow_controls(self, enabled):
        """Enable/disable slideshow controls based on mode"""
        self.slideshow_folder_button.setEnabled(enabled)
        self.slide_duration_spinbox.setEnabled(enabled)
        self.slideshow_random_checkbox.setEnabled(enabled)
        self.slideshow_fit_combo.setEnabled(enabled)

        # Update label styling
        if enabled:
            self.slideshow_folder_label.setStyleSheet("color: #00ff00;" if self.settings.get('slideshow_folder') else "color: #888888; font-style: italic;")
        else:
            self.slideshow_folder_label.setStyleSheet("color: #666666; font-style: italic;")

    def toggle_matrix_controls(self, enabled):
        """Enable/disable matrix controls based on mode"""
        self.color_combo.setEnabled(enabled)
        self.speed_slider.setEnabled(enabled)
        self.bold_checkbox.setEnabled(enabled)
        self.fps_combo.setEnabled(enabled)
        self.show_stats_checkbox.setEnabled(enabled)
        self.auto_cpu_limit_checkbox.setEnabled(enabled)
        self.katakana_checkbox.setEnabled(enabled)
        self.display_combo.setEnabled(enabled)
        self.physical_only_checkbox.setEnabled(enabled)

    def toggle_mystify_controls(self, enabled):
        """Enable/disable mystify controls based on mode"""
        self.mystify_shapes_spinbox.setEnabled(enabled)
        self.mystify_complexity_spinbox.setEnabled(enabled)
        self.mystify_trail_spinbox.setEnabled(enabled)
        self.mystify_speed_spinbox.setEnabled(enabled)
        self.mystify_color_combo.setEnabled(enabled)
        self.mystify_fill_checkbox.setEnabled(enabled)

    def handle_mode_exclusion(self, activated_mode, checked):
        """Handle mutual exclusion between screensaver modes - now handled by dropdown"""
        # This function is no longer needed since the dropdown handles exclusivity
        pass

    def auto_save_settings(self):
        """Automatically save settings when any control is changed"""
        try:
            # Check if widgets exist before accessing them
            if not hasattr(self, 'fps_combo') or not self.fps_combo:
                return  # Don't save if widgets aren't ready

            # Get target FPS value from combo box
            fps_text = self.safe_get_combo_text_simple(self.fps_combo, '15')
            target_fps = 0 if fps_text == "Unlimited" else int(fps_text)

            # Safe widget access with existence checks
            screensaver_type = self.safe_get_combo_text_simple(self.screensaver_type_combo, 'Matrix') if hasattr(self, 'screensaver_type_combo') and self.screensaver_type_combo else 'Matrix'
            color_text = self.safe_get_combo_text_simple(self.color_combo, 'green')

            # Update settings from GUI using safe widget access methods
            self.settings.update({
                'enabled': screensaver_type != "None",  # Enabled if not "None"
                'start_on_boot': self.safe_get_checkbox_value(self.autostart_checkbox, False),
                'show_taskbar_icon': self.safe_get_checkbox_value(self.show_taskbar_icon_checkbox, True),
                'dark_mode': self.safe_get_checkbox_value(self.dark_mode_checkbox, True),
                'matrix_mode': screensaver_type == 'Matrix',
                'color': color_text if color_text != 'rainbow' else 'green',
                'speed': self.safe_get_spinbox_value(self.speed_slider, 25),
                'lock_timeout': self.safe_get_spinbox_value(self.lock_spinbox, 5) * 60,
                'display_timeout': self.safe_get_spinbox_value(self.display_spinbox, 10) * 60,
                'rainbow_mode': color_text == 'rainbow',
                'bold_text': self.safe_get_checkbox_value(self.bold_checkbox, True),
                'async_scroll': True,  # Always enabled for better effect
                'display_target': self.safe_get_combo_text_simple(self.display_combo, 'both'),
                'physical_only': self.safe_get_checkbox_value(self.physical_only_checkbox, True),
                'show_stats': self.safe_get_checkbox_value(self.show_stats_checkbox, False),
                'use_katakana': self.safe_get_checkbox_value(self.katakana_checkbox, True),
                'auto_cpu_limit': self.safe_get_checkbox_value(self.auto_cpu_limit_checkbox, False),
                'target_fps': target_fps,
                # Slideshow settings
                'slideshow_mode': screensaver_type == 'Slideshow',
                'slideshow_folder': self.settings.get('slideshow_folder', ''),
                'slide_duration': self.safe_get_spinbox_value(self.slide_duration_spinbox, 5),
                'slideshow_random': self.safe_get_checkbox_value(self.slideshow_random_checkbox, True),
                'slideshow_fit_mode': self.safe_get_combo_value(self.slideshow_fit_combo, ['contain', 'cover', 'stretch'], 'contain'),
                # Mystify settings
                'mystify_mode': screensaver_type == 'Mystify',
                'mystify_shapes': self.safe_get_spinbox_value(self.mystify_shapes_spinbox, 3),
                'mystify_trail_length': self.safe_get_spinbox_value(self.mystify_trail_spinbox, 50),
                'mystify_complexity': self.safe_get_spinbox_value(self.mystify_complexity_spinbox, 6),
                'mystify_speed': self.safe_get_spinbox_value(self.mystify_speed_spinbox, 2),
                'mystify_color_mode': self.safe_get_combo_text(self.mystify_color_combo, ['rainbow', 'single', 'duo'], 'rainbow'),
                'mystify_fill': self.safe_get_checkbox_value(self.mystify_fill_checkbox, False),
                # Shutdown timer settings
                'auto_shutdown': self.safe_get_checkbox_value(self.auto_shutdown_checkbox, False),
                'shutdown_timeout': self.safe_get_spinbox_value(self.shutdown_spinbox, 60)
            })

            # Restart shutdown timer if settings changed
            if self.settings.get('auto_shutdown', False):
                self.start_shutdown_timer()
            else:
                self.stop_shutdown_timer()

            # Save to file silently (no status messages to avoid spam)
            if self.save_settings():
                # Handle autostart changes
                if hasattr(self, 'autostart_checkbox') and self.autostart_checkbox:
                    self.update_autostart_desktop_entry()

        except Exception as e:
            # Silent failure for auto-save - don't interrupt user
            pass

    def apply_settings(self):
        """Apply current settings"""
        try:
            # Check if widgets exist before accessing them
            if not hasattr(self, 'fps_combo') or not self.fps_combo:
                QMessageBox.warning(self, "Error", "GUI widgets not ready. Please try again.")
                return

            # Get target FPS value from combo box
            fps_text = self.safe_get_combo_text_simple(self.fps_combo, '15')
            target_fps = 0 if fps_text == "Unlimited" else int(fps_text)

            # Safe widget access with existence checks
            screensaver_type = self.safe_get_combo_text_simple(self.screensaver_type_combo, 'Matrix') if hasattr(self, 'screensaver_type_combo') and self.screensaver_type_combo else 'Matrix'
            color_text = self.safe_get_combo_text_simple(self.color_combo, 'green')

            # Update settings from GUI using safe widget access methods
            self.settings.update({
                'enabled': self.settings['enabled'],
                'start_on_boot': self.safe_get_checkbox_value(self.autostart_checkbox, False),
                'show_taskbar_icon': self.safe_get_checkbox_value(self.show_taskbar_icon_checkbox, True),
                'matrix_mode': screensaver_type == 'Matrix',
                'color': color_text if color_text != 'rainbow' else 'green',
                'speed': self.safe_get_spinbox_value(self.speed_slider, 25),
                'lock_timeout': self.safe_get_spinbox_value(self.lock_spinbox, 5) * 60,
                'display_timeout': self.safe_get_spinbox_value(self.display_spinbox, 10) * 60,
                'rainbow_mode': color_text == 'rainbow',
                'bold_text': self.safe_get_checkbox_value(self.bold_checkbox, True),
                'async_scroll': True,  # Always enabled for better effect
                'display_target': self.safe_get_combo_text_simple(self.display_combo, 'both'),
                'physical_only': self.safe_get_checkbox_value(self.physical_only_checkbox, True),
                'show_stats': self.safe_get_checkbox_value(self.show_stats_checkbox, False),
                'use_katakana': self.safe_get_checkbox_value(self.katakana_checkbox, True),
                'auto_cpu_limit': self.safe_get_checkbox_value(self.auto_cpu_limit_checkbox, False),
                'target_fps': target_fps,
                # Slideshow settings
                'slideshow_mode': screensaver_type == 'Slideshow',
                'slideshow_folder': self.settings.get('slideshow_folder', ''),
                'slide_duration': self.safe_get_spinbox_value(self.slide_duration_spinbox, 5),
                'slideshow_random': self.safe_get_checkbox_value(self.slideshow_random_checkbox, True),
                'slideshow_fit_mode': self.safe_get_combo_value(self.slideshow_fit_combo, ['contain', 'cover', 'stretch'], 'contain'),
                # Mystify settings
                'mystify_mode': screensaver_type == 'Mystify',
                'mystify_shapes': self.safe_get_spinbox_value(self.mystify_shapes_spinbox, 3),
                'mystify_trail_length': self.safe_get_spinbox_value(self.mystify_trail_spinbox, 50),
                'mystify_complexity': self.safe_get_spinbox_value(self.mystify_complexity_spinbox, 6),
                'mystify_speed': self.safe_get_spinbox_value(self.mystify_speed_spinbox, 2),
                'mystify_color_mode': self.safe_get_combo_value(self.mystify_color_combo, ['rainbow', 'single', 'duo'], 'rainbow'),
                'mystify_fill': self.safe_get_checkbox_value(self.mystify_fill_checkbox, False)
            })

            # Save settings
            if self.save_settings():
                # Update autostart script
                self.update_autostart_script()
                # Update autostart desktop entry
                self.update_autostart_desktop_entry()
                self.safe_status_message("Settings applied successfully!")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to apply settings: {e}")
            self.safe_status_message("Failed to apply settings")

    def update_autostart_script(self):
        """Update the autostart script with new settings"""
        script_path = Path.home() / '.local' / 'bin' / 'wayland_sidekick_autolock.sh'

        # Determine display management commands based on target
        display_target = self.settings.get('display_target', 'both')

        if display_target == 'display0':
            display_off_cmd = "wlopm --off HDMI-A-1 2>/dev/null || xset -display :0 dpms force off"
            display_on_cmd = "wlopm --on HDMI-A-1 2>/dev/null || xset -display :0 dpms force on"
            display_desc = "Display 0 (HDMI-A-1)"
        elif display_target == 'display1':
            display_off_cmd = "wlopm --off HDMI-A-2 2>/dev/null || xset -display :1 dpms force off"
            display_on_cmd = "wlopm --on HDMI-A-2 2>/dev/null || xset -display :1 dpms force on"
            display_desc = "Display 1 (HDMI-A-2)"
        else:  # both
            display_off_cmd = "wlopm --off '*' 2>/dev/null || xset dpms force off"
            display_on_cmd = "wlopm --on '*' 2>/dev/null || xset dpms force on"
            display_desc = "All displays"

        # Create the script content with enhanced touchpad activity detection
        script_content = f"""#!/bin/bash
# Auto-generated Wayland Matrix screensaver script
# Generated by PyQt6 Screensaver Preferences GUI

SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
MATRIX_SCRIPT="$SCRIPT_DIR/sidekick_screensaver.sh"

# Make sure the matrix script is executable
chmod +x "$MATRIX_SCRIPT"

echo "🟢 Starting Wayland Matrix Screensaver System..."
echo "Settings: {self.settings['color']} color, speed {self.settings['speed']}"
echo "Target: {display_desc}"
echo "Timeline:"
echo "  0-{self.settings['lock_timeout']//60} min:  Normal desktop"
echo "  {self.settings['lock_timeout']//60}-{self.settings['display_timeout']//60} min: Matrix digital rain"
echo "  {self.settings['display_timeout']//60}+ min:  Screen off (power saving)"
echo ""

# The complete recipe with user settings and enhanced activity detection
swayidle -w \\
    timeout {self.settings['lock_timeout']} "echo 'Entering the Matrix...' && $MATRIX_SCRIPT" \\
    timeout {self.settings['display_timeout']} "echo 'Powering down {display_desc.lower()}...' && pkill -f sidekick_widget; pkill -f mystify_widget; pkill -f slideshow_widget; {display_off_cmd}" \\
    resume "echo 'Exiting the Matrix...' && pkill -f sidekick_widget; pkill -f mystify_widget; pkill -f slideshow_widget; {display_on_cmd}" \\
    before-sleep "echo 'System sleeping - killing Matrix...' && pkill -f sidekick_widget; pkill -f mystify_widget; pkill -f slideshow_widget; {display_off_cmd}"
"""

        # Write the script
        script_path.parent.mkdir(exist_ok=True)
        with open(script_path, 'w') as f:
            f.write(script_content)

        # Make executable
        script_path.chmod(0o755)

        # Also update the sidekick_screensaver.sh to handle touchpad activity
        self.update_matrix_script()

    def update_matrix_script(self):
        """Update the sidekick_screensaver.sh script with enhanced activity detection"""
        script_path = Path.home() / '.local' / 'bin' / 'sidekick_screensaver.sh'

        # Build the cmatrix command with current settings
        cmd_parts = ['cmatrix']

        # Add flags based on settings
        if self.settings.get('async_scroll', True):
            cmd_parts.append('-a')
        if self.settings.get('bold_text', True):
            cmd_parts.append('-b')

        cmd_parts.extend(['-f', '-s'])  # Force Linux mode, screensaver mode

        # Add color (or rainbow mode)
        if self.settings.get('rainbow_mode', False):
            cmd_parts.append('-r')  # Rainbow mode
        else:
            cmd_parts.extend(['-C', self.settings.get('color', 'green')])

        # Add speed (reverse for cmatrix: stored value 0=slowest, 50=fastest becomes high delay to low delay for cmatrix -u)
        reversed_speed = 50 - self.settings.get('speed', 25)  # Default to middle speed
        cmd_parts.extend(['-u', str(reversed_speed)])

        # Create the matrix script content with enhanced activity detection
        display_target = self.settings.get('display_target', 'both')

        if display_target == 'display0':
            display_env = "DISPLAY=:0"
            display_desc = "Display 0"
        elif display_target == 'display1':
            display_env = "DISPLAY=:1"
            display_desc = "Display 1"
        else:  # both
            display_env = ""
            display_desc = "All displays"

        script_content = f"""#!/bin/bash
# Matrix screensaver script with enhanced activity detection including touchpad
# Auto-generated by PyQt6 Screensaver Preferences GUI

echo "🟢💚 Starting Matrix Digital Rain on {display_desc}..."

# Check if we should only run on physical screens
PHYSICAL_ONLY={str(self.settings.get('physical_only', True)).lower()}

if [ "$PHYSICAL_ONLY" = "true" ]; then
    # Check if this is a physical session (not SSH/VNC)
    if [ -n "$SSH_CLIENT" ] || [ -n "$SSH_TTY" ] || [ -n "$VNC_DESKTOP" ] || [ "$XDG_SESSION_TYPE" = "tty" ]; then
        echo "🚫 Skipping Matrix - not running on physical display"
        exit 0
    fi

    # Additional check for local display
    if [ -z "$DISPLAY" ] && [ -z "$WAYLAND_DISPLAY" ]; then
        echo "🚫 Skipping Matrix - no local display detected"
        exit 0
    fi

    echo "✅ Physical display confirmed - proceeding with Matrix..."
fi

# Function to cleanup on exit
cleanup() {{
    pkill -f "cmatrix" 2>/dev/null
    exit 0
}}

# Set up signal handlers for cleanup
trap cleanup SIGTERM SIGINT SIGQUIT

# Create a temporary script for the matrix effect with enhanced activity detection
TEMP_SCRIPT="/tmp/matrix_$$"
cat > "$TEMP_SCRIPT" << 'MATRIX_EOF'
#!/bin/bash
# Maximized matrix terminal script with enhanced activity detection

# Enhanced function to detect ALL input activity including touchpad
activity_monitor() {{
    while true; do
        # Method 1: Check /proc/interrupts for hardware activity
        if [ -f /proc/interrupts ]; then
            INITIAL_ACTIVITY=$(grep -E "(keyboard|mouse|i8042|usb|input|touchpad|synaptics)" /proc/interrupts 2>/dev/null | awk '{{sum+=$2}} END {{print sum+0}}')
            sleep 0.5
            CURRENT_ACTIVITY=$(grep -E "(keyboard|mouse|i8042|usb|input|touchpad|synaptics)" /proc/interrupts 2>/dev/null | awk '{{sum+=$2}} END {{print sum+0}}')

            if [ "$CURRENT_ACTIVITY" -gt "$INITIAL_ACTIVITY" ] 2>/dev/null; then
                # Activity detected - exit immediately
                pkill -f cmatrix 2>/dev/null
                sleep 0.1
                exit 0
            fi
        fi

        # Method 2: Monitor input devices directly (includes touchpad events)
        for input_dev in /dev/input/event*; do
            if [ -c "$input_dev" ]; then
                # Check device name to include touchpad devices
                DEVICE_NAME=$(cat "/sys/class/input/$(basename $input_dev)/device/name" 2>/dev/null || echo "")

                # Check for any input activity (keyboard, mouse, touchpad, touch)
                if echo "$DEVICE_NAME" | grep -qiE "(keyboard|mouse|touchpad|touch|synaptics|alps|elan)"; then
                    if timeout 0.1s cat "$input_dev" >/dev/null 2>&1; then
                        # Input detected - exit immediately
                        pkill -f cmatrix 2>/dev/null
                        sleep 0.1
                        exit 0
                    fi
                fi
            fi
        done

        # Method 3: Check for mouse position changes
        if command -v xdotool >/dev/null 2>&1; then
            MOUSE_POS=$(xdotool getmouselocation 2>/dev/null | cut -d' ' -f1-2)
            if [ -n "$PREV_MOUSE_POS" ] && [ "$MOUSE_POS" != "$PREV_MOUSE_POS" ]; then
                # Mouse moved - exit immediately
                pkill -f cmatrix 2>/dev/null
                sleep 0.1
                exit 0
            fi
            PREV_MOUSE_POS="$MOUSE_POS"
        fi

        # Method 4: Check xinput for touchpad/pointer events (if available)
        if command -v xinput >/dev/null 2>&1; then
            # Get list of pointer devices (includes touchpads)
            POINTER_DEVICES=$(xinput list --short | grep -i "pointer" | grep -iE "(touchpad|mouse|synaptics)" | cut -d'=' -f2 | cut -d'[' -f1)
            for device_id in $POINTER_DEVICES; do
                if [ -n "$device_id" ]; then
                    # Test device activity (this will return immediately if no activity)
                    if timeout 0.1s xinput test "$device_id" >/dev/null 2>&1; then
                        pkill -f cmatrix 2>/dev/null
                        sleep 0.1
                        exit 0
                    fi
                fi
            done
        fi

        sleep 0.3  # Check frequently for responsive exit
    done
}}

# Start activity monitor in background
activity_monitor &
MONITOR_PID=$!

# Cleanup function for the terminal
cleanup_terminal() {{
    kill $MONITOR_PID 2>/dev/null
    pkill -f cmatrix 2>/dev/null
    # Auto-close terminal without prompting
    sleep 0.2
    exit 0
}}

trap cleanup_terminal SIGTERM SIGINT SIGQUIT

# Run matrix effect
{' '.join(cmd_parts)}

# If cmatrix exits normally, cleanup and close terminal immediately
cleanup_terminal
MATRIX_EOF

chmod +x "$TEMP_SCRIPT"

# Find a suitable terminal and run fullscreen/maximized
TERMINAL_FOUND=false

# Try different terminals with fullscreen/maximized flags
for term_cmd in \\
    "lxterminal --command" \\
    "xterm -fullscreen -e" \\
    "gnome-terminal --full-screen -- bash" \\
    "konsole --fullscreen -e bash" \\
    "x-terminal-emulator -e bash"; do

    TERM_NAME=$(echo "$term_cmd" | awk '{{print $1}}')
    if command -v "$TERM_NAME" >/dev/null 2>&1; then
        echo "🖥️ Using $TERM_NAME for Matrix screensaver..."

        if [[ "$term_cmd" == *"lxterminal"* ]]; then
            # Special handling for lxterminal to get true fullscreen without title bar
            {display_env} lxterminal --geometry=999x999+0+0 --command="bash $TEMP_SCRIPT" --title="cmatrix Terminal" &
            TERMINAL_PID=$!

            # Wait for terminal to open then maximize it
            sleep 1
            if command -v wmctrl >/dev/null 2>&1; then
                wmctrl -r "Matrix Screensaver" -b add,fullscreen 2>/dev/null || \\
                wmctrl -r "Matrix Screensaver" -b add,maximized_vert,maximized_horz 2>/dev/null
            elif command -v xdotool >/dev/null 2>&1; then
                xdotool search --name "Matrix Screensaver" windowstate --add FULLSCREEN 2>/dev/null || \\
                xdotool search --name "Matrix Screensaver" windowstate --add MAXIMIZED_VERT MAXIMIZED_HORZ 2>/dev/null
            fi
        else
            {display_env} $term_cmd "$TEMP_SCRIPT" &
            TERMINAL_PID=$!
        fi

        TERMINAL_FOUND=true
        break
    fi
done

if [ "$TERMINAL_FOUND" = false ]; then
    echo "⚠️ No suitable terminal found, running Matrix in current session..."
    {display_env} bash "$TEMP_SCRIPT" &
    TERMINAL_PID=$!
fi

# Wait for the terminal to finish
wait $TERMINAL_PID 2>/dev/null

# Cleanup temp script
rm -f "$TEMP_SCRIPT"

# Silent exit - no end message
"""

        # Write the script
        script_path.parent.mkdir(exist_ok=True)
        with open(script_path, 'w') as f:
            f.write(script_content)

        # Make executable
        script_path.chmod(0o755)

    def reset_defaults(self):
        """Reset all settings to defaults"""
        reply = QMessageBox.question(self, "Reset Settings", "Reset all settings to defaults?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            # Reset to defaults
            self.settings = {
                'enabled': True,
                'effect': 'matrix',
                'color': 'green',
                'speed': 25,  # Default to middle speed (0-50 range)
                'lock_timeout': 300,
                'display_timeout': 600,
                'rainbow_mode': False,
                'bold_text': True,
                'async_scroll': True,
                'display_target': 'both',
                'physical_only': True,
                'start_on_boot': False,
                'auto_shutdown': False,  # Default to disabled
                'shutdown_timeout': 60  # Default to 1 hour
            }

            # Update GUI
            self.autostart_checkbox.setChecked(self.settings['start_on_boot'])
            # Set rainbow in dropdown if rainbow_mode was enabled
            if self.settings.get('rainbow_mode', False):
                self.color_combo.setCurrentText('rainbow')
            else:
                self.color_combo.setCurrentText(self.settings['color'])
            self.speed_slider.setValue(self.settings['speed'])
            self.lock_spinbox.setValue(self.settings['lock_timeout'] // 60)
            self.display_spinbox.setValue(self.settings['display_timeout'] // 60)
            # Rainbow checkbox removed - now handled in color dropdown
            self.bold_checkbox.setChecked(self.settings['bold_text'])
            self.display_combo.setCurrentText(self.settings['display_target'])
            self.physical_only_checkbox.setChecked(self.settings['physical_only'])

            # Reset shutdown timer settings
            self.auto_shutdown_checkbox.setChecked(self.settings['auto_shutdown'])
            self.shutdown_spinbox.setValue(self.settings['shutdown_timeout'])
            self.shutdown_spinbox.setEnabled(self.settings['auto_shutdown'])

            # Stop any running shutdown timer since we reset to disabled
            self.stop_shutdown_timer()

            self.status_bar.showMessage("Settings reset to defaults")

def main():
    """Main entry point"""
    import argparse
    import json
    from pathlib import Path

    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Matrix Screensaver Preferences')
    parser.add_argument('--autostart', action='store_true',
                       help='Start in background mode for autostart (no GUI)')
    parser.add_argument('--test', action='store_true',
                       help='Test mode for development')
    args = parser.parse_args()

    # Check for single instance using the professional SingleInstance manager
    # Use a unique name for screensaver preferences
    try:
        instance_manager = ensure_single_instance("screensaver_preferences_gui", exit_on_conflict=False)
        if not instance_manager.is_locked:
            if not args.autostart:  # Only show message if not autostart
                print("Screensaver Preferences is already running!")
                # Try to bring existing window to front
                try:
                    subprocess.run(['wmctrl', '-a', 'Screensaver Preferences'],
                                  check=False, capture_output=True, timeout=2)
                except:
                    pass
            sys.exit(0)
    except Exception as e:
        print(f"⚠️ Single instance check failed: {e}")
        print("ℹ️ Continuing with potential multiple instances")

    app = QApplication(sys.argv)

    # CRITICAL: Prevent application from quitting when last window closes
    # This ensures the system tray remains active even when all windows are hidden
    app.setQuitOnLastWindowClosed(False)

    # Load settings to check dark mode preference
    config_dir = Path.home() / '.config' / 'screensaver'
    config_file = config_dir / 'settings.json'
    dark_mode_enabled = True  # Default to dark mode

    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                saved_settings = json.load(f)
                dark_mode_enabled = saved_settings.get('dark_mode', True)
        except Exception as e:
            print(f"Warning: Could not load dark mode setting: {e}")

    # Apply theme based on user preference
    try:
        if QDARKTHEME_AVAILABLE:
            try:
                if dark_mode_enabled:
                    # Apply qdarktheme professional dark theme
                    qdarktheme.setup_theme("dark")
                    print("✅ QDarkTheme professional dark theme applied")
                else:
                    # Apply qdarktheme light theme
                    qdarktheme.setup_theme("light")
                    print("✅ QDarkTheme professional light theme applied")
            except Exception as e:
                print(f"⚠️ qdarktheme failed ({e}), trying qdarkstyle")
                # Try qdarkstyle as fallback
                if QDARKSTYLE_AVAILABLE and dark_mode_enabled:
                    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt6())
                    print("✅ QDarkStyle professional dark theme applied")
                elif dark_mode_enabled:
                    app.setStyleSheet(DARK_THEME_STYLESHEET)
                    print("✅ Built-in dark theme applied")
                else:
                    app.setStyleSheet(LIGHT_THEME_STYLESHEET)
                    print("✅ Built-in light theme applied")
        elif QDARKSTYLE_AVAILABLE:
            # Use qdarkstyle professional theme
            if dark_mode_enabled:
                app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt6())
                print("✅ QDarkStyle professional dark theme applied")
            else:
                app.setStyleSheet("")  # Default light theme
                print("✅ Default light theme applied")
        else:
            # Use built-in themes as last resort
            if dark_mode_enabled:
                app.setStyleSheet(DARK_THEME_STYLESHEET)
                print("✅ Built-in dark theme applied")
            else:
                app.setStyleSheet(LIGHT_THEME_STYLESHEET)
                print("✅ Built-in light theme applied")
    except Exception as e:
        print(f"⚠️ Failed to apply theme: {e}")
        print("ℹ️ Continuing with system default theme")

    # Set application properties
    app.setApplicationName("Screensaver Preferences")
    app.setApplicationVersion("2.1.0")
    app.setOrganizationName("Matrix Screensaver")

    # Set application icon if available
    try:
        app.setWindowIcon(QIcon.fromTheme("preferences-desktop-screensaver"))
    except:
        pass  # Ignore if icon theme not available

    # Cleanup on exit - the SingleInstance manager will auto-cleanup via atexit
    def cleanup_on_exit():
        """Clean up instance manager when application exits"""
        if hasattr(instance_manager, 'release_lock'):
            instance_manager.release_lock()

    app.aboutToQuit.connect(cleanup_on_exit)

    # Create and show the main window
    window = ScreensaverPreferences()

    # Store instance manager in window for reference
    window.instance_manager = instance_manager

    # Handle autostart mode
    if args.autostart:
        print("🚀 Starting in autostart mode (background monitoring)")
        # Don't show the GUI, just start background monitoring
        if window.settings.get('enabled', True):
            window.start_automatic_monitoring()
            print("✅ Background monitoring started")
        else:
            print("⚠️ Screensaver disabled - no monitoring started")
    else:
        # Normal mode - show the GUI
        window.show()

    # Run the application
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
