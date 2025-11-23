#!/usr/bin/env python3
# pyright: reportGeneralTypeIssues=false
"""
Screensaver Preferences GUI - v4.0 Modern UI Edition
A sophisticated 2025-aesthetic control panel for Wayland Matrix screensaver

NEW in v4.0:
- Modern sidebar navigation with clean layout
- iOS-style toggle switches replacing checkboxes
- Segmented controls for theme selection
- Smooth sliders with real-time value display
- Generous whitespace and elegant spacing
- Professional dark mode with vibrant blue accents (#3B82F6)

Preserved Features:
- All Matrix/Mystify/Slideshow settings
- System tray integration
- Single instance enforcement
- Autostart management
- Timer controls and auto-shutdown
- Update checker and diagnostics

Version: 4.0.0 - Modern 2025 UI Edition
Created: November 2025
"""

import sys
import os
import json
import subprocess
import datetime
import time
import atexit
import webbrowser
from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QSlider, QSpinBox, QFrame, QStackedWidget,
    QComboBox, QDoubleSpinBox, QFileDialog, QMessageBox, QStatusBar,
    QSystemTrayIcon, QMenu, QSplashScreen
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QPropertyAnimation, QEasingCurve, QPoint, QByteArray, QSize
from PyQt6.QtGui import QIcon, QPainter, QColor, QAction, QPixmap

# =============================================================================
# SINGLE INSTANCE PROTECTION
# =============================================================================

try:
    from filelock import Timeout, FileLock
    FILELOCK_AVAILABLE = True
except ImportError:
    FILELOCK_AVAILABLE = False

class SingleInstanceManager:
    """Professional single instance manager with file locking"""
    def __init__(self, app_name: str = "sidekick_screensaver_v4", lock_dir: Optional[str] = None):
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
        """Acquire file lock with optional timeout"""
        if not FILELOCK_AVAILABLE:
            return True
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
        """Release the file lock"""
        if not self.is_locked or not self.lock:
            return
        try:
            self.lock.release()
            self.is_locked = False
        except Exception:
            pass

# =============================================================================
# MODERN 2025 COLOR PALETTE
# =============================================================================

COLORS_DARK = {
    'bg_dark': '#18181B',           # Very dark gray background
    'bg_content': '#27272A',        # Slightly lighter content areas
    'bg_sidebar': '#27272A',        # Sidebar background
    'accent_blue': '#3B82F6',       # Vibrant blue for active elements
    'text_primary': '#FFFFFF',      # White text
    'text_secondary': '#E5E5E5',    # Light gray text
    'text_muted': '#71717A',        # Muted gray for labels
    'border': '#3F3F46',            # Subtle borders
    'hover': '#3F3F46',             # Hover state
}

COLORS_LIGHT = {
    'bg_dark': '#FFFFFF',           # White background
    'bg_content': '#F4F4F5',        # Light gray content areas
    'bg_sidebar': '#F9FAFB',        # Sidebar background
    'accent_blue': '#3B82F6',       # Vibrant blue for active elements
    'text_primary': '#18181B',      # Dark text
    'text_secondary': '#3F3F46',    # Medium gray text
    'text_muted': '#71717A',        # Muted gray for labels
    'border': '#E4E4E7',            # Light borders
    'hover': '#F4F4F5',             # Hover state
}

# Helper function for language injection (used by "Highlight f-strings" extension)
def css(stylesheet: str) -> str:
    """Language injection helper for CSS syntax highlighting"""
    return stylesheet

def get_stylesheet(theme: str = 'dark', touch_mode: bool = False) -> str:
    """Generate stylesheet based on theme and touch mode"""
    COLORS = COLORS_DARK if theme == 'dark' else COLORS_LIGHT

    # Touch-friendly sizing
    slider_height = "12px" if touch_mode else "6px"
    slider_handle_size = "28px" if touch_mode else "18px"
    slider_handle_margin = "-8px 0" if touch_mode else "-6px 0"
    combobox_height = "48px" if touch_mode else "20px"
    spinbox_height = "48px" if touch_mode else "auto"
    button_padding = "16px 28px" if touch_mode else "12px 24px"
    font_size = "16px" if touch_mode else "14px"

    return css(f"""
/* Main Window */
QMainWindow {{
    background-color: {COLORS['bg_dark']};
    color: {COLORS['text_primary']};
}}

/* Sidebar Navigation */
QFrame#sidebar {{
    background-color: {COLORS['bg_sidebar']};
    border-right: 1px solid {COLORS['border']};
}}

/* Content Area */
QFrame#contentArea {{
    background-color: {COLORS['bg_dark']};
}}

/* Navigation Buttons */
QPushButton#navButton {{
    background-color: transparent;
    color: {COLORS['text_secondary']};
    border: none;
    border-left: 3px solid transparent;
    text-align: left;
    padding: 16px 20px;
    font-size: 14px;
    font-weight: 500;
}}

QPushButton#navButton:hover {{
    background-color: {COLORS['hover']};
}}

QPushButton#navButton[active="true"] {{
    background-color: {COLORS['hover']};
    color: {COLORS['accent_blue']};
    border-left: 3px solid {COLORS['accent_blue']};
    font-weight: 600;
}}

/* Section Headers */
QLabel#sectionHeader {{
    color: {COLORS['text_primary']};
    font-size: 28px;
    font-weight: 600;
    padding: 0px 0px 24px 0px;
}}

/* Section Labels */
QLabel#sectionLabel {{
    color: {COLORS['text_secondary']};
    font-size: 16px;
    font-weight: 600;
    margin-top: 32px;
    margin-bottom: 16px;
}}

/* Regular Labels */
QLabel {{
    color: {COLORS['text_secondary']};
    font-size: {font_size};
}}

QLabel#valueLabel {{
    color: {COLORS['text_primary']};
    font-size: {font_size};
    font-weight: 500;
}}

/* Sliders */
QSlider::groove:horizontal {{
    background-color: {'#D1D5DB' if theme == 'light' else COLORS['bg_content']};
    height: {slider_height};
    border-radius: {'6px' if touch_mode else '3px'};
}}

QSlider::handle:horizontal {{
    background-color: {COLORS['accent_blue']};
    width: {slider_handle_size};
    height: {slider_handle_size};
    margin: {slider_handle_margin};
    border-radius: {'14px' if touch_mode else '9px'};
}}

QSlider::handle:horizontal:hover {{
    background-color: #60A5FA;
}}

/* SpinBoxes */
QSpinBox, QDoubleSpinBox {{
    background-color: {COLORS['bg_content']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    padding: {'12px 16px' if touch_mode else '8px 12px'};
    font-size: {font_size};
    min-width: {'120px' if touch_mode else '80px'};
    min-height: {spinbox_height};
}}

QSpinBox::up-button, QSpinBox::down-button,
QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {{
    background-color: transparent;
    border: none;
    width: {'32px' if touch_mode else '20px'};
}}

/* ComboBoxes */
QComboBox {{
    background-color: {COLORS['bg_content']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    padding: {'12px 16px' if touch_mode else '8px 12px'};
    font-size: {font_size};
    min-height: {combobox_height};
    min-width: {'200px' if touch_mode else '120px'};
}}

QComboBox:hover {{
    border-color: {COLORS['accent_blue']};
}}

QComboBox::drop-down {{
    border: none;
}}

QComboBox QAbstractItemView {{
    background-color: {COLORS['bg_content']};
    color: {COLORS['text_primary']};
    selection-background-color: {COLORS['accent_blue']};
    border: 1px solid {COLORS['border']};
    font-size: {font_size};
    padding: {'8px' if touch_mode else '4px'};
}}

QComboBox QAbstractItemView::item {{
    min-height: {'48px' if touch_mode else '24px'};
    padding: {'12px 16px' if touch_mode else '4px 8px'};
}}

/* Footer Buttons */
QPushButton#primaryButton {{
    background-color: {COLORS['accent_blue']};
    color: white;
    border: none;
    border-radius: 8px;
    padding: {button_padding};
    font-size: {font_size};
    font-weight: 600;
    min-height: {'52px' if touch_mode else '36px'};
}}

QPushButton#primaryButton:hover {{
    background-color: #2563EB;
}}

QPushButton#secondaryButton {{
    background-color: transparent;
    color: {COLORS['text_secondary']};
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    padding: {button_padding};
    font-size: {font_size};
    font-weight: 600;
    min-height: {'52px' if touch_mode else '36px'};
}}

QPushButton#secondaryButton:hover {{
    background-color: {COLORS['bg_content']};
}}

QPushButton#linkButton {{
    background-color: transparent;
    color: {COLORS['text_muted']};
    border: none;
    padding: 12px 24px;
    font-size: 14px;
    text-decoration: underline;
}}

QPushButton#linkButton:hover {{
    color: {COLORS['text_secondary']};
}}

/* Status Bar */
QStatusBar {{
    background-color: {COLORS['bg_content']};
    color: {COLORS['text_muted']};
    border-top: 1px solid {COLORS['border']};
    font-size: 12px;
}}
""")

# =============================================================================
# MODERN TOGGLE SWITCH WIDGET
# =============================================================================

class ModernToggleSwitch(QWidget):
    """Modern iOS-style toggle switch widget (replaces checkboxes)"""

    toggled = pyqtSignal(bool)

    def __init__(self, checked=False, parent=None):
        super().__init__(parent)
        self.setFixedSize(48, 28)
        self._checked = checked
        self.setStyleSheet("background: transparent;")

    def paintEvent(self, event):
        """Paint the toggle switch UI"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw track
        track_color = QColor(COLORS_DARK['accent_blue']) if self._checked else QColor(COLORS_DARK['bg_content'])
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(track_color)
        painter.drawRoundedRect(0, 0, 48, 28, 14, 14)

        # Draw handle
        handle_x = 22 if self._checked else 2
        painter.setBrush(QColor('white'))
        painter.drawEllipse(handle_x, 2, 24, 24)

    def mousePressEvent(self, event):
        """Handle mouse click to toggle switch"""
        self._checked = not self._checked
        self.toggled.emit(self._checked)  # type: ignore[attr-defined]
        self.update()

    def isChecked(self) -> bool:
        """Return current checked state"""
        return self._checked

    def setChecked(self, checked: bool) -> None:
        """Set checked state"""
        self._checked = checked
        self.update()

# =============================================================================
# SEGMENTED CONTROL WIDGET
# =============================================================================

class SegmentedControl(QWidget):
    """Modern segmented control for option selection"""

    selectionChanged = pyqtSignal(int)

    def __init__(self, options, parent=None):
        super().__init__(parent)
        self.options = options
        self.selected = 0
        self.buttons = []

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        for i, option in enumerate(options):
            btn = QPushButton(option)
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, idx=i: self.select(idx))
            btn.setStyleSheet(self._get_button_style(i == 0))
            layout.addWidget(btn)
            self.buttons.append(btn)

        self.buttons[0].setChecked(True)

    def _get_button_style(self, is_selected):
        base_style = f"""
            QPushButton {{
                {'background-color: ' + COLORS_DARK['accent_blue'] + '; color: white;' if is_selected else 'background-color: ' + COLORS_DARK['bg_content'] + '; color: ' + COLORS_DARK['text_secondary'] + ';'}
                border: none;
                padding: 8px 16px;
                font-size: 13px;
                font-weight: 600;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: {'#2563EB' if is_selected else COLORS_DARK['hover']};
            }}
        """
        return base_style

    def select(self, index):
        """Select a segment by index"""
        self.selected = index
        for i, btn in enumerate(self.buttons):
            btn.setChecked(i == index)
            btn.setStyleSheet(self._get_button_style(i == index))
        self.selectionChanged.emit(index)  # type: ignore[attr-defined]

    def currentIndex(self) -> int:
        """Return currently selected index"""
        return self.selected

    def setCurrentIndex(self, index: int) -> None:
        """Set current selection by index"""
        if 0 <= index < len(self.buttons):
            self.select(index)

# =============================================================================
# MAIN PREFERENCES WINDOW
# =============================================================================

class ScreensaverPreferencesV4(QMainWindow):
    """Modern screensaver preferences with 2025 aesthetic"""

    def __init__(self):
        super().__init__()

        # Version info
        self.app_version = "4.0.0"
        self.build_date = datetime.datetime.now().strftime("%Y-%m-%d")

        # Instance checker
        self.instance_manager: Optional[SingleInstanceManager] = None

        # Configuration
        self.config_dir = Path.home() / '.config' / 'screensaver'
        self.config_file = self.config_dir / 'settings.json'
        self.config_dir.mkdir(exist_ok=True)

        # Default settings (same as original)
        self.settings = {
            'enabled': True,
            'effect': 'matrix',
            'matrix_mode': True,
            'color': 'green',
            'speed': 25,
            'lock_timeout': 300,
            'display_timeout': 600,
            'rainbow_mode': False,
            'bold_text': True,
            'async_scroll': True,
            'display_target': 'both',
            'physical_only': True,
            'start_on_boot': False,
            'show_taskbar_icon': True,
            'start_maximized': False,
            'show_stats': False,
            'target_fps': 15,
            'auto_cpu_limit': False,
            'use_katakana': True,
            'font_size': 14,
            'slideshow_mode': False,
            'slideshow_folder': str(Path.home() / 'screensaver-media' / 'images'),
            'slide_duration': 5.0,
            'slideshow_random': True,
            'slideshow_fit_mode': 'contain',
            'mystify_mode': False,
            'mystify_shapes': 3,
            'mystify_trail_length': 50,
            'mystify_complexity': 6,
            'mystify_speed': 2,
            'mystify_color_mode': 'rainbow',
            'mystify_fill': False,
            'mystify_color_hue': 240,
            'mystify_color_hue1': 240,
            'mystify_color_hue2': 60,
            'dark_mode': True,
            'auto_shutdown': False,
            'shutdown_timeout': 60,
            'auto_update_check': True,
            'last_update_check': '',
            'update_check_frequency': 30,
            'update_notification': True,
            'stats_drift': True,
            'video_mode': False,
            'video_folder': str(Path.home() / 'screensaver-media' / 'videos'),
            'video_random': True,
            'video_playback_speed': 1.0,
            'video_mute': True,
            'enable_touch_ui': False,  # Manual touch UI override
            'display_shutdown': False,
            'display_shutdown_timeout': 30,
        }

        # Load saved settings
        self.load_settings()

        # Detect touchscreen and apply UI scaling
        self.is_touchscreen = self.detect_touchscreen()
        self.ui_scale_factor = 1.5 if (self.is_touchscreen or self.settings.get('enable_touch_ui', False)) else 1.0

        # Setup window
        self.setWindowTitle("Screensaver Settings")

        # Adjust window size based on touch UI
        if self.ui_scale_factor > 1.0:
            self.setGeometry(100, 100, 1200, 900)  # Larger for touch
        else:
            self.setGeometry(100, 100, 950, 750)  # Normal desktop size

        # Apply theme
        current_theme = 'dark' if self.settings.get('dark_mode', True) else 'light'
        self.setStyleSheet(get_stylesheet(current_theme, self.ui_scale_factor > 1.0))        # Setup UI
        self.setup_icons()
        self.create_ui()
        self.create_status_bar()
        self.setup_system_tray()

        # Timers
        self.screensaver_timer = QTimer()
        self.screensaver_timer.timeout.connect(self.on_screensaver_timeout)  # type: ignore
        self.progress_timer = QTimer()
        self.last_activity_time = 0
        self.screensaver_active = False
        self.is_test_mode = False

        # Show systray immediately if available (no delay for Wayland compatibility testing)
        # Note: Wayland often lacks systray support - this will show debug info
        QTimer.singleShot(100, self.activate_systray_icon)  # Show after 100ms (allow window to initialize)

        # Check for updates on startup (non-blocking)
        QTimer.singleShot(2000, lambda: self.check_for_updates(manual=False))

        # Shutdown timer
        if self.settings.get('auto_shutdown', False):
            self.start_shutdown_timer()

        # Display shutdown timer
        if self.settings.get('display_shutdown', False):
            self.setup_display_shutdown()

    def setup_icons(self):
        """Setup window and tray icons using custom favicon"""
        # Try to use custom favicon from media/Logo folder (development) or same directory (installed)
        dark_mode = self.settings.get('dark_mode', True)

        # Use optimized 22x22 for system tray, 600x600 for window
        favicon_22_filename = "SideKick_Logo_2025_Favicon_22.png" if dark_mode else "SideKick_Logo_2025_Favicon_light_22.png"
        favicon_filename = "SideKick_Logo_2025_Favicon.png" if dark_mode else "SideKick_Logo_2025_Favicon_light.png"

        # First try installed location (same directory as script)
        favicon_22_path = Path(__file__).parent / favicon_22_filename
        favicon_path = Path(__file__).parent / favicon_filename

        # If not found, try development location (media/Logo/)
        if not favicon_22_path.exists():
            favicon_22_path = Path(__file__).parent.parent / "media" / "Logo" / favicon_22_filename
        if not favicon_path.exists():
            favicon_path = Path(__file__).parent.parent / "media" / "Logo" / favicon_filename

        # Create QIcon with multiple sizes for best rendering
        if favicon_22_path.exists() and favicon_path.exists():
            self.app_icon = QIcon()
            self.app_icon.addFile(str(favicon_22_path), QSize(22, 22))  # System tray size
            self.app_icon.addFile(str(favicon_path), QSize(600, 600))   # Window icon size
            self.setWindowIcon(self.app_icon)
            print(f"✅ Using custom favicon with optimized sizes (22x22 for tray, 600x600 for window)")
            return
        elif favicon_path.exists():
            # Fallback to single size if 22x22 not available
            self.app_icon = QIcon(str(favicon_path))
            self.setWindowIcon(self.app_icon)
            print(f"✅ Using custom favicon: {favicon_filename}")
            return

        # Fallback to system theme icons
        icon_names = [
            "preferences-desktop-screensaver",
            "xscreensaver",
            "screensaver",
            "preferences-desktop",
            "video-display"
        ]

        for icon_name in icon_names:
            icon = QIcon.fromTheme(icon_name)
            if not icon.isNull():
                self.app_icon = icon
                self.setWindowIcon(icon)
                print(f"✅ Using icon: {icon_name}")
                return

        # Final fallback
        print("⚠️  Using fallback computer icon")
        self.app_icon = self.style().standardIcon(self.style().StandardPixmap.SP_ComputerIcon)
        self.setWindowIcon(self.app_icon)

    def load_settings(self):
        """Load settings from JSON"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    saved = json.load(f)
                    self.settings.update(saved)
            except Exception as e:
                print(f"Error loading settings: {e}")

    def save_settings(self) -> bool:
        """Save settings to JSON"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2)
            return True
        except Exception as e:
            msg = self.create_styled_messagebox("Error", f"Failed to save: {e}", QMessageBox.Icon.Critical)
            msg.exec()
            return False

    def create_ui(self):
        """Create the main UI with sidebar navigation"""
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)  # Changed to VBoxLayout to stack content and footer
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Top section with sidebar and content
        top_section = QWidget()
        top_layout = QHBoxLayout(top_section)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(0)

        # Sidebar
        sidebar = self.create_sidebar()
        top_layout.addWidget(sidebar)

        # Content area
        self.content_stack = QStackedWidget()
        self.content_stack.setObjectName("contentArea")
        self.content_stack.addWidget(self.create_general_page())
        self.content_stack.addWidget(self.create_display_page())
        self.content_stack.addWidget(self.create_matrix_page())
        self.content_stack.addWidget(self.create_mystify_page())
        self.content_stack.addWidget(self.create_slideshow_page())
        self.content_stack.addWidget(self.create_video_page())

        top_layout.addWidget(self.content_stack)

        # Add top section and footer to main layout
        main_layout.addWidget(top_section)

        # Add centralized footer buttons
        footer_container = QWidget()
        footer_container.setStyleSheet(f"background-color: {COLORS_DARK['bg_content']}; border-top: 1px solid {COLORS_DARK['border']};")
        footer_layout = QHBoxLayout(footer_container)
        footer_layout.setContentsMargins(48, 16, 48, 16)
        footer_layout.addLayout(self.create_footer())
        main_layout.addWidget(footer_container)

    def create_sidebar(self) -> QFrame:
        """Create navigation sidebar"""
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(260)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 20, 0, 20)
        layout.setSpacing(4)

        # Header
        header = QLabel("Screensaver Hub")
        header.setStyleSheet(f"""
            color: {COLORS_DARK['text_primary']};
            font-size: 18px;
            font-weight: 700;
            padding: 20px;
        """)
        layout.addWidget(header)

        # Navigation
        nav_items = [
            ("⚙️  General", 0),
            ("🖥️  Display & Performance", 1),
            ("🎬  Matrix Settings", 2),
            ("🌈  Mystify Settings", 3),
            ("🖼️  Slideshow Settings", 4),
            ("📹  Video Settings", 5),
        ]

        self.nav_buttons = []
        for text, index in nav_items:
            btn = QPushButton(text)
            btn.setObjectName("navButton")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, idx=index: self.switch_page(idx))
            layout.addWidget(btn)
            self.nav_buttons.append(btn)

        self.nav_buttons[0].setProperty("active", "true")
        self.nav_buttons[0].style().unpolish(self.nav_buttons[0])
        self.nav_buttons[0].style().polish(self.nav_buttons[0])

        layout.addStretch()

        # Add logo at bottom of sidebar
        logo_label = QLabel()
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Load logo based on current theme
        dark_mode = self.settings.get('dark_mode', True)
        logo_filename = "sidekick_logo_dark.png" if dark_mode else "sidekick_logo_light.png"

        # Try installed location first (same directory), then development location
        logo_path = Path(__file__).parent / logo_filename
        if not logo_path.exists():
            logo_path = Path(__file__).parent.parent / "media" / "Logo" / logo_filename

        if logo_path.exists():
            pixmap = QPixmap(str(logo_path))
            # Scale to fit sidebar width (260px) with some padding
            scaled_pixmap = pixmap.scaled(220, 140, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
        else:
            # Fallback text if logo not found
            logo_label.setText("SideKick")
            logo_label.setStyleSheet(f"""
                color: {COLORS_DARK['text_muted']};
                font-size: 16px;
                font-weight: 700;
                padding: 20px;
            """)

        layout.addWidget(logo_label)
        layout.addSpacing(20)

        return sidebar

    def switch_page(self, index):
        """Switch pages and update nav buttons"""
        self.content_stack.setCurrentIndex(index)
        for i, btn in enumerate(self.nav_buttons):
            btn.setProperty("active", "true" if i == index else "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def create_general_page(self) -> QWidget:
        """Create General settings page"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(48, 40, 48, 40)
        layout.setSpacing(0)

        # Header
        header = QLabel("⚙️ General Settings")
        header.setObjectName("sectionHeader")
        layout.addWidget(header)

        # Behavior Section
        behavior_label = QLabel("Behavior")
        behavior_label.setObjectName("sectionLabel")
        layout.addWidget(behavior_label)

        self.boot_toggle = self.create_toggle_row("Start on Boot", self.settings.get('start_on_boot', False))
        layout.addLayout(self.boot_toggle[0])
        layout.addSpacing(12)

        self.taskbar_toggle = self.create_toggle_row("Show Taskbar Icon", self.settings.get('show_taskbar_icon', True))
        layout.addLayout(self.taskbar_toggle[0])

        layout.addSpacing(12)

        self.maximized_toggle = self.create_toggle_row("Start GUI Maximized", self.settings.get('start_maximized', False))
        layout.addLayout(self.maximized_toggle[0])

        layout.addSpacing(12)

        self.touch_ui_toggle = self.create_toggle_row("Enable Touch UI Mode", self.settings.get('enable_touch_ui', False))
        layout.addLayout(self.touch_ui_toggle[0])

        # Appearance Section
        appearance_label = QLabel("Appearance")
        appearance_label.setObjectName("sectionLabel")
        layout.addWidget(appearance_label)

        theme_row = QHBoxLayout()
        theme_row.addWidget(QLabel("Theme"))
        theme_row.addSpacing(20)

        self.theme_control = SegmentedControl(["Dark", "Light"])
        current_theme_index = 0 if self.settings.get('dark_mode', True) else 1
        self.theme_control.setCurrentIndex(current_theme_index)
        self.theme_control.selectionChanged.connect(self.on_theme_changed)
        theme_row.addWidget(self.theme_control)
        theme_row.addStretch()
        layout.addLayout(theme_row)        # Screensaver Type Section
        type_label = QLabel("Screensaver")
        type_label.setObjectName("sectionLabel")
        layout.addWidget(type_label)

        type_row = QHBoxLayout()
        type_row.addWidget(QLabel("Type:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(['Matrix', 'Mystify', 'Slideshow', 'Videos', 'None'])

        if not self.settings.get('enabled', True):
            self.type_combo.setCurrentText('None')
        elif self.settings.get('matrix_mode', True):
            self.type_combo.setCurrentText('Matrix')
        elif self.settings.get('slideshow_mode', False):
            self.type_combo.setCurrentText('Slideshow')
        elif self.settings.get('mystify_mode', False):
            self.type_combo.setCurrentText('Mystify')
        elif self.settings.get('video_mode', False):
            self.type_combo.setCurrentText('Videos')

        self.type_combo.currentTextChanged.connect(self.on_type_changed)
        type_row.addWidget(self.type_combo)
        type_row.addStretch()
        layout.addLayout(type_row)        # Timers Section
        timers_label = QLabel("Timers")
        timers_label.setObjectName("sectionLabel")
        layout.addWidget(timers_label)

        self.screensaver_slider = self.create_slider_row(
            "Start screensaver after:",
            self.settings['lock_timeout'] // 60, 1, 60, "min"
        )
        layout.addLayout(self.screensaver_slider[0])
        layout.addSpacing(20)

        # Auto-shutdown toggle
        self.auto_shutdown_toggle = self.create_toggle_row("Enable Auto-Shutdown", self.settings.get('auto_shutdown', False))
        layout.addLayout(self.auto_shutdown_toggle[0])
        layout.addSpacing(12)

        self.shutdown_row = self.create_slider_row(
            "Auto-shutdown after:",
            self.settings.get('shutdown_timeout', 60), 5, 480, "min"
        )
        layout.addLayout(self.shutdown_row[0])

        note = QLabel("• Saves power after extended inactivity.")
        note.setStyleSheet(f"color: {COLORS_DARK['text_muted']}; font-size: 12px; margin-top: 8px;")
        layout.addWidget(note)

        # Update Check Section
        update_label = QLabel("Updates")
        update_label.setObjectName("sectionLabel")
        layout.addWidget(update_label)

        self.auto_update_toggle = self.create_toggle_row("Check for Updates Automatically", self.settings.get('auto_update_check', True))
        layout.addLayout(self.auto_update_toggle[0])

        layout.addSpacing(12)

        self.update_notification_toggle = self.create_toggle_row("Show Update Notifications", self.settings.get('update_notification', True))
        layout.addLayout(self.update_notification_toggle[0])

        layout.addSpacing(12)

        self.update_frequency_slider = self.create_slider_row(
            "Check frequency:",
            self.settings.get('update_check_frequency', 30), 1, 90, "days"
        )
        layout.addLayout(self.update_frequency_slider[0])

        layout.addStretch()

        return page

    def create_display_page(self) -> QWidget:
        """Create Display & Performance page"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(48, 40, 48, 40)

        header = QLabel("🖥️ Display & Performance")
        header.setObjectName("sectionHeader")
        layout.addWidget(header)

        # FPS Settings
        perf_label = QLabel("Performance")
        perf_label.setObjectName("sectionLabel")
        layout.addWidget(perf_label)

        fps_row = QHBoxLayout()
        fps_row.addWidget(QLabel("Target FPS:"))
        self.fps_combo = QComboBox()
        self.fps_combo.addItems(['15', '30', '45', '60', '75', '90', '120', 'Unlimited'])
        current_fps = self.settings.get('target_fps', 15)
        self.fps_combo.setCurrentText('Unlimited' if current_fps == 0 else str(current_fps))
        fps_row.addWidget(self.fps_combo)
        fps_row.addStretch()
        layout.addLayout(fps_row)

        layout.addSpacing(12)

        self.cpu_toggle = self.create_toggle_row("FPS Throttling", self.settings.get('auto_cpu_limit', False))
        layout.addLayout(self.cpu_toggle[0])

        # Display Settings
        display_label = QLabel("Display")
        display_label.setObjectName("sectionLabel")
        layout.addWidget(display_label)

        target_row = QHBoxLayout()
        target_row.addWidget(QLabel("Display Target:"))
        self.display_combo = QComboBox()
        self.display_combo.addItems(['both', 'display0', 'display1'])
        self.display_combo.setCurrentText(self.settings.get('display_target', 'both'))
        target_row.addWidget(self.display_combo)
        target_row.addStretch()
        layout.addLayout(target_row)

        layout.addSpacing(12)

        self.physical_toggle = self.create_toggle_row("Physical screens only", self.settings.get('physical_only', True))
        layout.addLayout(self.physical_toggle[0])

        layout.addSpacing(12)

        self.stats_toggle = self.create_toggle_row("Show Stats Overlay", self.settings.get('show_stats', False))
        layout.addLayout(self.stats_toggle[0])

        # Note about stats compatibility
        stats_note = QLabel("• Stats overlay works with Matrix, Mystify, and Slideshow modes.\n• Not available for Video mode (VLC runs fullscreen externally).")
        stats_note.setStyleSheet(f"color: {COLORS_DARK['text_muted']}; font-size: 12px; margin-top: 8px;")
        layout.addWidget(stats_note)

        # Display Power Management
        power_label = QLabel("Power Management")
        power_label.setObjectName("sectionLabel")
        layout.addWidget(power_label)

        self.display_shutdown_toggle = self.create_toggle_row("Enable Display Shutdown", self.settings.get('display_shutdown', False))
        layout.addLayout(self.display_shutdown_toggle[0])
        layout.addSpacing(12)

        self.display_shutdown_slider = self.create_slider_row(
            "Shutdown display after:",
            self.settings.get('display_shutdown_timeout', 30), 5, 120, "min"
        )
        layout.addLayout(self.display_shutdown_slider[0])

        note = QLabel("• Turns off display after inactivity to save power.")
        note.setStyleSheet(f"color: {COLORS_DARK['text_muted']}; font-size: 12px; margin-top: 8px;")
        layout.addWidget(note)

        layout.addStretch()
        return page

    def create_matrix_page(self) -> QWidget:
        """Create Matrix screensaver settings page"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(48, 40, 48, 40)

        header = QLabel("🎬 Matrix Screensaver")
        header.setObjectName("sectionHeader")
        layout.addWidget(header)

        # Color Settings
        color_label = QLabel("Color Settings")
        color_label.setObjectName("sectionLabel")
        layout.addWidget(color_label)

        color_row = QHBoxLayout()
        color_row.addWidget(QLabel("Color:"))
        self.color_combo = QComboBox()
        self.color_combo.addItems(['green', 'red', 'blue', 'cyan', 'magenta', 'yellow', 'white', 'rainbow'])
        color = 'rainbow' if self.settings.get('rainbow_mode', False) else self.settings.get('color', 'green')
        self.color_combo.setCurrentText(color)
        color_row.addWidget(self.color_combo)
        color_row.addStretch()
        layout.addLayout(color_row)

        # Animation Settings
        anim_label = QLabel("Animation")
        anim_label.setObjectName("sectionLabel")
        layout.addWidget(anim_label)

        self.speed_slider = self.create_slider_row(
            "Speed:",
            self.settings.get('speed', 25), 0, 50, ""
        )
        layout.addLayout(self.speed_slider[0])

        # Character Settings
        char_label = QLabel("Characters")
        char_label.setObjectName("sectionLabel")
        layout.addWidget(char_label)

        self.katakana_toggle = self.create_toggle_row("Use Japanese Katakana", self.settings.get('use_katakana', True))
        layout.addLayout(self.katakana_toggle[0])

        layout.addSpacing(12)

        self.bold_toggle = self.create_toggle_row("Bold Characters", self.settings.get('bold_text', True))
        layout.addLayout(self.bold_toggle[0])

        layout.addSpacing(12)

        self.font_size_slider = self.create_slider_row(
            "Font Size:",
            self.settings.get('font_size', 14), 10, 20, "px"
        )
        layout.addLayout(self.font_size_slider[0])

        layout.addStretch()
        return page

    def create_mystify_page(self) -> QWidget:
        """Create Mystify screensaver settings page"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(48, 40, 48, 40)

        header = QLabel("🌈 Mystify Screensaver")
        header.setObjectName("sectionHeader")
        layout.addWidget(header)

        # Shape Settings
        shape_label = QLabel("Shape Settings")
        shape_label.setObjectName("sectionLabel")
        layout.addWidget(shape_label)

        shapes_row = QHBoxLayout()
        shapes_row.addWidget(QLabel("Number of Shapes:"))
        self.shapes_spin = QSpinBox()
        self.shapes_spin.setRange(1, 8)
        self.shapes_spin.setValue(self.settings.get('mystify_shapes', 3))
        shapes_row.addWidget(self.shapes_spin)
        shapes_row.addStretch()
        layout.addLayout(shapes_row)

        layout.addSpacing(20)

        complexity_row = QHBoxLayout()
        complexity_row.addWidget(QLabel("Complexity (Vertices):"))
        self.complexity_spin = QSpinBox()
        self.complexity_spin.setRange(3, 12)
        self.complexity_spin.setValue(self.settings.get('mystify_complexity', 6))
        complexity_row.addWidget(self.complexity_spin)
        complexity_row.addStretch()
        layout.addLayout(complexity_row)

        # Animation Settings
        anim_label = QLabel("Animation")
        anim_label.setObjectName("sectionLabel")
        layout.addWidget(anim_label)

        speed_row = QHBoxLayout()
        speed_row.addWidget(QLabel("Speed:"))
        self.mystify_speed_spin = QSpinBox()
        self.mystify_speed_spin.setRange(1, 10)
        self.mystify_speed_spin.setValue(self.settings.get('mystify_speed', 2))
        speed_row.addWidget(self.mystify_speed_spin)
        speed_row.addStretch()
        layout.addLayout(speed_row)

        layout.addSpacing(20)

        trail_row = QHBoxLayout()
        trail_row.addWidget(QLabel("Trail Length:"))
        self.trail_spin = QSpinBox()
        self.trail_spin.setRange(10, 100)
        self.trail_spin.setValue(self.settings.get('mystify_trail_length', 50))
        trail_row.addWidget(self.trail_spin)
        trail_row.addStretch()
        layout.addLayout(trail_row)

        # Rendering
        render_label = QLabel("Rendering")
        render_label.setObjectName("sectionLabel")
        layout.addWidget(render_label)

        self.fill_toggle = self.create_toggle_row("Fill Shapes", self.settings.get('mystify_fill', False))
        layout.addLayout(self.fill_toggle[0])

        # Color Settings
        color_label = QLabel("Colors")
        color_label.setObjectName("sectionLabel")
        layout.addWidget(color_label)

        color_mode_row = QHBoxLayout()
        color_mode_row.addWidget(QLabel("Color Mode:"))
        self.mystify_color_combo = QComboBox()
        self.mystify_color_combo.addItems(['Rainbow', 'Single', 'Duo'])
        current_mode = self.settings.get('mystify_color_mode', 'rainbow')
        mode_index = {'rainbow': 0, 'single': 1, 'duo': 2}.get(current_mode, 0)
        self.mystify_color_combo.setCurrentIndex(mode_index)
        self.mystify_color_combo.currentIndexChanged.connect(self.on_mystify_color_mode_changed)
        color_mode_row.addWidget(self.mystify_color_combo)
        color_mode_row.addStretch()
        layout.addLayout(color_mode_row)

        layout.addSpacing(12)

        # Single color hue slider
        self.mystify_hue_slider = self.create_slider_row(
            "Single Color Hue:",
            self.settings.get('mystify_color_hue', 240), 0, 360, "°"
        )
        layout.addLayout(self.mystify_hue_slider[0])

        layout.addSpacing(12)

        # Duo color hue sliders
        self.mystify_hue1_slider = self.create_slider_row(
            "Duo Color 1 Hue:",
            self.settings.get('mystify_color_hue1', 240), 0, 360, "°"
        )
        layout.addLayout(self.mystify_hue1_slider[0])

        layout.addSpacing(12)

        self.mystify_hue2_slider = self.create_slider_row(
            "Duo Color 2 Hue:",
            self.settings.get('mystify_color_hue2', 60), 0, 360, "°"
        )
        layout.addLayout(self.mystify_hue2_slider[0])

        # Initially show/hide color sliders based on mode
        self.on_mystify_color_mode_changed(mode_index)

        layout.addStretch()
        return page

    def create_slideshow_page(self) -> QWidget:
        """Create Slideshow settings page"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(48, 40, 48, 40)

        header = QLabel("🖼️ Slideshow Settings")
        header.setObjectName("sectionHeader")
        layout.addWidget(header)

        # Folder Settings
        folder_label = QLabel("Source")
        folder_label.setObjectName("sectionLabel")
        layout.addWidget(folder_label)

        folder_row = QHBoxLayout()
        folder_row.addWidget(QLabel("Image Folder:"))
        self.folder_button = QPushButton("📁 Browse...")
        self.folder_button.setObjectName("secondaryButton")
        self.folder_button.clicked.connect(self.browse_folder)
        folder_row.addWidget(self.folder_button)

        # Display current folder path
        self.slideshow_folder_label = QLabel()
        current_folder = self.settings.get('slideshow_folder', '')
        if current_folder:
            self.slideshow_folder_label.setText(f"📂 {current_folder}")
        else:
            self.slideshow_folder_label.setText("(No folder selected)")
        self.slideshow_folder_label.setStyleSheet(f"color: {COLORS_DARK['text_muted']}; font-size: 12px;")
        folder_row.addWidget(self.slideshow_folder_label)

        folder_row.addStretch()
        layout.addLayout(folder_row)

        # Timing Settings
        timing_label = QLabel("Timing")
        timing_label.setObjectName("sectionLabel")
        layout.addWidget(timing_label)

        duration_row = QHBoxLayout()
        duration_row.addWidget(QLabel("Slide Duration (seconds):"))
        self.duration_spin = QDoubleSpinBox()
        self.duration_spin.setRange(1.0, 60.0)
        self.duration_spin.setValue(self.settings.get('slide_duration', 5.0))
        duration_row.addWidget(self.duration_spin)
        duration_row.addStretch()
        layout.addLayout(duration_row)

        # Playback Settings
        playback_label = QLabel("Playback")
        playback_label.setObjectName("sectionLabel")
        layout.addWidget(playback_label)

        self.slideshow_random_toggle = self.create_toggle_row("Randomize Order", self.settings.get('slideshow_random', True))
        layout.addLayout(self.slideshow_random_toggle[0])

        layout.addSpacing(12)

        fit_row = QHBoxLayout()
        fit_row.addWidget(QLabel("Fit Mode:"))
        self.fit_combo = QComboBox()
        self.fit_combo.addItems(['contain', 'cover', 'fill', 'scale-down'])
        self.fit_combo.setCurrentText(self.settings.get('slideshow_fit_mode', 'contain'))
        fit_row.addWidget(self.fit_combo)
        fit_row.addStretch()
        layout.addLayout(fit_row)

        layout.addStretch()
        return page

    def create_video_page(self) -> QWidget:
        """Create Video player settings page"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(48, 40, 48, 40)

        header = QLabel("📹 Video Player Settings")
        header.setObjectName("sectionHeader")
        layout.addWidget(header)

        # Source Settings
        source_label = QLabel("Source")
        source_label.setObjectName("sectionLabel")
        layout.addWidget(source_label)

        video_folder_row = QHBoxLayout()
        video_folder_row.addWidget(QLabel("Video Folder:"))
        self.video_folder_button = QPushButton("📁 Browse...")
        self.video_folder_button.setObjectName("secondaryButton")
        self.video_folder_button.clicked.connect(self.browse_video_folder)
        video_folder_row.addWidget(self.video_folder_button)

        # Display current folder path
        self.video_folder_label = QLabel()
        current_folder = self.settings.get('video_folder', '')
        if current_folder:
            self.video_folder_label.setText(f"📂 {current_folder}")
        else:
            self.video_folder_label.setText("(No folder selected)")
        self.video_folder_label.setStyleSheet(f"color: {COLORS_DARK['text_muted']}; font-size: 12px;")
        video_folder_row.addWidget(self.video_folder_label)

        video_folder_row.addStretch()
        layout.addLayout(video_folder_row)

        # Playback Settings
        playback_label = QLabel("Playback")
        playback_label.setObjectName("sectionLabel")
        layout.addWidget(playback_label)

        self.video_random_toggle = self.create_toggle_row("Randomize Video Order", self.settings.get('video_random', True))
        layout.addLayout(self.video_random_toggle[0])

        layout.addSpacing(12)

        self.video_mute_toggle = self.create_toggle_row("Mute Video Audio", self.settings.get('video_mute', True))
        layout.addLayout(self.video_mute_toggle[0])

        layout.addSpacing(12)

        # Playback speed slider (0.25x to 2.0x, step 0.25)
        speed_value = int(self.settings.get('video_playback_speed', 1.0) * 4)  # Convert to 1-8 range
        self.video_speed_slider = self.create_slider_row(
            "Playback Speed:",
            speed_value, 1, 8, "x"
        )
        # Custom value label formatting for speed
        speed_slider = self.video_speed_slider[1]
        speed_label = self.video_speed_slider[2]
        speed_label.setText(f"{speed_value/4:.2f}x")
        speed_slider.valueChanged.connect(lambda v: speed_label.setText(f"{v/4:.2f}x"))
        layout.addLayout(self.video_speed_slider[0])

        layout.addStretch()
        return page
        """Create Source (Videos) page"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(48, 40, 48, 40)

        header = QLabel("◀️ Source Settings")
        header.setObjectName("sectionHeader")
        layout.addWidget(header)

        # Matrix Settings
        matrix_label = QLabel("Matrix Settings")
        matrix_label.setObjectName("sectionLabel")
        layout.addWidget(matrix_label)

        color_row = QHBoxLayout()
        color_row.addWidget(QLabel("Color:"))
        self.color_combo = QComboBox()
        self.color_combo.addItems(['green', 'red', 'blue', 'cyan', 'magenta', 'yellow', 'white', 'rainbow'])
        color = 'rainbow' if self.settings.get('rainbow_mode', False) else self.settings.get('color', 'green')
        self.color_combo.setCurrentText(color)
        color_row.addWidget(self.color_combo)
        color_row.addStretch()
        layout.addLayout(color_row)

        layout.addSpacing(20)

        self.speed_slider = self.create_slider_row(
            "Speed:",
            self.settings.get('speed', 25), 0, 50, ""
        )
        layout.addLayout(self.speed_slider[0])

        layout.addSpacing(20)

        self.katakana_toggle = self.create_toggle_row("Use Japanese Katakana", self.settings.get('use_katakana', True))
        layout.addLayout(self.katakana_toggle[0])

        layout.addSpacing(12)

        self.bold_toggle = self.create_toggle_row("Bold Characters", self.settings.get('bold_text', True))
        layout.addLayout(self.bold_toggle[0])

        # Slideshow Settings
        slideshow_label = QLabel("Slideshow Settings")
        slideshow_label.setObjectName("sectionLabel")
        layout.addWidget(slideshow_label)

        folder_row = QHBoxLayout()
        folder_row.addWidget(QLabel("Folder:"))
        self.folder_button = QPushButton("📁 Browse...")
        self.folder_button.setObjectName("secondaryButton")
        self.folder_button.clicked.connect(self.browse_folder)
        folder_row.addWidget(self.folder_button)
        folder_row.addStretch()
        layout.addLayout(folder_row)

        # Mystify Settings
        mystify_label = QLabel("Mystify Settings")
        mystify_label.setObjectName("sectionLabel")
        layout.addWidget(mystify_label)

        shapes_row = QHBoxLayout()
        shapes_row.addWidget(QLabel("Shapes:"))
        self.shapes_spin = QSpinBox()
        self.shapes_spin.setRange(1, 8)
        self.shapes_spin.setValue(self.settings.get('mystify_shapes', 3))
        shapes_row.addWidget(self.shapes_spin)
        shapes_row.addStretch()
        layout.addLayout(shapes_row)

        # Video Settings
        video_label = QLabel("Video Player Settings")
        video_label.setObjectName("sectionLabel")
        layout.addWidget(video_label)

        video_folder_row = QHBoxLayout()
        video_folder_row.addWidget(QLabel("Video Folder:"))
        self.video_folder_button = QPushButton("📁 Browse...")
        self.video_folder_button.setObjectName("secondaryButton")
        self.video_folder_button.clicked.connect(self.browse_video_folder)
        video_folder_row.addWidget(self.video_folder_button)
        video_folder_row.addStretch()
        layout.addLayout(video_folder_row)

        layout.addSpacing(12)

        self.video_random_toggle = self.create_toggle_row("Randomize Video Order", self.settings.get('video_random', True))
        layout.addLayout(self.video_random_toggle[0])

        layout.addSpacing(12)

        self.video_mute_toggle = self.create_toggle_row("Mute Video Audio", self.settings.get('video_mute', True))
        layout.addLayout(self.video_mute_toggle[0])

        layout.addStretch()
        return page

    def create_toggle_row(self, label_text: str, checked: bool = False) -> tuple[QHBoxLayout, ModernToggleSwitch]:
        """Create row with label and toggle"""
        row = QHBoxLayout()
        row.setSpacing(0)

        label = QLabel(label_text)
        toggle = ModernToggleSwitch(checked)

        row.addWidget(label)
        row.addStretch()
        row.addWidget(toggle)

        return (row, toggle)

    def create_slider_row(self, label_text: str, value: int, min_val: int, max_val: int, unit: str) -> tuple[QVBoxLayout, QSlider, QLabel]:
        """Create row with slider and value display"""
        container = QVBoxLayout()
        container.setSpacing(8)

        label_row = QHBoxLayout()
        label = QLabel(label_text)
        value_label = QLabel(f"{value} {unit}")
        value_label.setObjectName("valueLabel")

        label_row.addWidget(label)
        label_row.addStretch()
        label_row.addWidget(value_label)
        container.addLayout(label_row)

        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setMinimum(min_val)
        slider.setMaximum(max_val)
        slider.setValue(value)
        slider.valueChanged.connect(lambda v: value_label.setText(f"{v} {unit}"))

        container.addWidget(slider)

        return (container, slider, value_label)

    def create_footer(self) -> QHBoxLayout:
        """Create centralized footer buttons"""
        footer = QHBoxLayout()
        footer.setContentsMargins(0, 0, 0, 0)
        footer.setSpacing(12)

        # Left side buttons
        test_btn = QPushButton("Test Screensaver")
        test_btn.setObjectName("secondaryButton")
        test_btn.clicked.connect(self.test_screensaver)

        about_btn = QPushButton("About")
        about_btn.setObjectName("secondaryButton")
        about_btn.clicked.connect(self.show_about)

        diag_btn = QPushButton("Diagnostics")
        diag_btn.setObjectName("secondaryButton")
        diag_btn.clicked.connect(self.run_diagnostics)

        # Right side buttons
        apply_btn = QPushButton("Apply")
        apply_btn.setObjectName("primaryButton")
        apply_btn.clicked.connect(self.apply_settings)

        quit_btn = QPushButton("Quit")
        quit_btn.setObjectName("secondaryButton")
        quit_btn.clicked.connect(self.quit_application)  # Actually quit, don't minimize

        # Center: Buy Me a Coffee button (bold and obvious)
        coffee_btn = QPushButton("☕ Buy Me a Coffee")
        coffee_btn.setObjectName("coffeeButton")
        coffee_btn.setStyleSheet(f"""
            QPushButton#coffeeButton {{
                background-color: #FFDD00;
                color: #000000;
                border: none;
                border-radius: 8px;
                padding: {'16px 32px' if self.ui_scale_factor > 1.0 else '12px 28px'};
                font-size: {'18px' if self.ui_scale_factor > 1.0 else '15px'};
                font-weight: 700;
                min-height: {'52px' if self.ui_scale_factor > 1.0 else '40px'};
            }}
            QPushButton#coffeeButton:hover {{
                background-color: #FFEA00;
                transform: scale(1.05);
            }}
        """)
        coffee_btn.clicked.connect(self.open_coffee_link)

        # Store reference for animation
        self.coffee_btn = coffee_btn

        # Start bounce animation timer (every 15 seconds)
        self.bounce_timer = QTimer()
        self.bounce_timer.timeout.connect(self.bounce_coffee_button)
        self.bounce_timer.start(15000)  # 15 seconds

        # Center all buttons in footer with coffee button in middle
        footer.addStretch()  # Left stretch
        footer.addWidget(test_btn)
        footer.addWidget(about_btn)
        footer.addWidget(diag_btn)
        footer.addSpacing(40)  # Space before coffee button
        footer.addWidget(coffee_btn)  # Center coffee button
        footer.addSpacing(40)  # Space after coffee button
        footer.addWidget(apply_btn)
        footer.addWidget(quit_btn)
        footer.addStretch()  # Right stretch

        return footer

    def create_status_bar(self):
        """Create status bar"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage(f"Ready - v{self.app_version}")

    def setup_system_tray(self):
        """Setup system tray icon (but don't show it yet - delayed activation)"""
        print(f"🔍 System tray available: {QSystemTrayIcon.isSystemTrayAvailable()}")

        if not QSystemTrayIcon.isSystemTrayAvailable():
            print("⚠️  System tray not available - skipping tray icon setup")
            return

        print("✅ Creating system tray icon...")
        self.tray_icon = QSystemTrayIcon(self)

        # Ensure we use the same icon as the window
        if hasattr(self, 'app_icon') and not self.app_icon.isNull():
            self.tray_icon.setIcon(self.app_icon)
            print(f"   ✅ Systray icon set (using app_icon)")
        else:
            print(f"   ⚠️  App icon not available, using fallback")
            self.tray_icon.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_ComputerIcon))

        print(f"   Icon null: {self.app_icon.isNull() if hasattr(self, 'app_icon') else 'N/A'}")

        # Create tray menu
        tray_menu = QMenu()

        show_action = QAction("Show Settings", self)
        show_action.triggered.connect(self.show_from_tray)
        tray_menu.addAction(show_action)

        tray_menu.addSeparator()

        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.quit_application)
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)

        # Click tray icon to show window (using activated signal)
        self.tray_icon.activated.connect(self.tray_icon_activated)

        print("✅ System tray icon configured (will show after 100ms)")

    def tray_icon_activated(self, reason):
        """Handle tray icon activation (clicks)"""
        # Trigger is single-click, DoubleClick is double-click
        from PyQt6.QtWidgets import QSystemTrayIcon
        if reason in (QSystemTrayIcon.ActivationReason.Trigger,
                      QSystemTrayIcon.ActivationReason.DoubleClick):
            print(f"🖱️  Tray icon clicked (reason: {reason}) - showing window")
            self.show_from_tray()

    def show_from_tray(self):
        """Show window from system tray"""
        self.show()
        self.raise_()
        self.activateWindow()

    def activate_systray_icon(self):
        """Activate systray icon after delay (called by timer)"""
        if not hasattr(self, 'tray_icon'):
            print("❌ No tray icon object - system tray not available")
            return

        if self.settings.get('show_taskbar_icon', True):
            self.tray_icon.show()
            print(f"✅ Systray icon activated after 30-second delay")
            print(f"   Visible: {self.tray_icon.isVisible()}")
        else:
            print("ℹ️  Systray icon not shown (disabled in settings)")


    def on_type_changed(self, text):
        """Handle screensaver type change"""
        self.settings['enabled'] = (text != 'None')
        self.settings['matrix_mode'] = (text == 'Matrix')
        self.settings['slideshow_mode'] = (text == 'Slideshow')
        self.settings['mystify_mode'] = (text == 'Mystify')
        self.settings['video_mode'] = (text == 'Videos')
        self.status_bar.showMessage(f"Screensaver type: {text}")

    def browse_folder(self):
        """Browse for slideshow folder"""
        folder = QFileDialog.getExistingDirectory(self, "Select Slideshow Folder")
        if folder:
            self.settings['slideshow_folder'] = folder
            self.slideshow_folder_label.setText(f"📂 {folder}")
            self.status_bar.showMessage(f"Slideshow folder: {folder}")

    def browse_video_folder(self):
        """Browse for video folder"""
        folder = QFileDialog.getExistingDirectory(self, "Select Video Folder")
        if folder:
            self.settings['video_folder'] = folder
            self.video_folder_label.setText(f"📂 {folder}")
            self.status_bar.showMessage(f"Video folder: {folder}")

    def detect_touchscreen(self) -> bool:
        """Detect if a touchscreen is connected for UI optimization"""
        try:
            # Method 1: Check xinput
            try:
                result = subprocess.run(['xinput', 'list'],
                                      capture_output=True, text=True, timeout=2)
                if 'touch' in result.stdout.lower() or 'touchscreen' in result.stdout.lower():
                    return True
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass

            # Method 2: Check libinput
            try:
                result = subprocess.run(['libinput', 'list-devices'],
                                      capture_output=True, text=True, timeout=2)
                if 'touchscreen' in result.stdout.lower():
                    return True
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass

            # Method 3: Check /proc/bus/input/devices
            try:
                with open('/proc/bus/input/devices', 'r', encoding='utf-8') as f:
                    content = f.read().lower()
                    if 'touchscreen' in content or 'touch screen' in content:
                        return True
            except (IOError, PermissionError):
                pass

            return False

        except Exception as e:
            print(f"⚠️ Touchscreen detection error: {e}")
            return False

    def create_styled_messagebox(self, title: str, text: str, icon: QMessageBox.Icon = QMessageBox.Icon.Information) -> QMessageBox:
        """Create a themed message box matching v4 design"""
        COLORS = COLORS_DARK if self.settings.get('dark_mode', True) else COLORS_LIGHT

        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setIcon(icon)

        # Apply v4 theme styling
        msg.setStyleSheet(f"""
            QMessageBox {{
                background-color: {COLORS['bg_content']};
                color: {COLORS['text_primary']};
            }}
            QMessageBox QLabel {{
                color: {COLORS['text_primary']};
                font-size: 14px;
            }}
            QMessageBox QPushButton {{
                background-color: {COLORS['accent_blue']};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 20px;
                font-size: 14px;
                font-weight: 500;
                min-width: 80px;
            }}
            QMessageBox QPushButton:hover {{
                background-color: #2563EB;
            }}
            QMessageBox QPushButton:pressed {{
                background-color: #1D4ED8;
            }}
        """)

        return msg

    def on_theme_changed(self, index):
        """Handle theme change"""
        is_dark = (index == 0)
        self.settings['dark_mode'] = is_dark
        theme_name = 'dark' if is_dark else 'light'

        # Apply new theme with touch mode
        self.setStyleSheet(get_stylesheet(theme_name, self.ui_scale_factor > 1.0))

        # Update toggle switch colors for the new theme
        self.update_toggle_colors()

        self.status_bar.showMessage(f"Theme changed to {theme_name} mode")

    def on_mystify_color_mode_changed(self, index):
        """Show/hide color sliders based on mystify color mode"""
        # 0 = Rainbow (hide all), 1 = Single (show hue), 2 = Duo (show hue1/hue2)
        show_single = (index == 1)
        show_duo = (index == 2)

        # Show/hide single hue slider - iterate through layout items
        layout = self.mystify_hue_slider[0]
        for i in range(layout.count()):
            item = layout.itemAt(i)
            if item and item.widget():
                item.widget().setVisible(show_single)
            elif item and item.layout():
                for j in range(item.layout().count()):
                    sub_item = item.layout().itemAt(j)
                    if sub_item and sub_item.widget():
                        sub_item.widget().setVisible(show_single)

        # Show/hide duo hue sliders
        for slider_layout in [self.mystify_hue1_slider[0], self.mystify_hue2_slider[0]]:
            for i in range(slider_layout.count()):
                item = slider_layout.itemAt(i)
                if item and item.widget():
                    item.widget().setVisible(show_duo)
                elif item and item.layout():
                    for j in range(item.layout().count()):
                        sub_item = item.layout().itemAt(j)
                        if sub_item and sub_item.widget():
                            sub_item.widget().setVisible(show_duo)

    def update_toggle_colors(self):
        """Update toggle switch colors after theme change"""
        # Toggle switches paint themselves, so we just need to trigger repaints
        for widget in self.findChildren(ModernToggleSwitch):
            widget.update()

    def apply_settings(self):
        """Apply and save all settings"""
        # Gather all settings from UI
        self.settings['start_on_boot'] = self.boot_toggle[1].isChecked()
        self.settings['show_taskbar_icon'] = self.taskbar_toggle[1].isChecked()
        self.settings['start_maximized'] = self.maximized_toggle[1].isChecked()
        self.settings['enable_touch_ui'] = self.touch_ui_toggle[1].isChecked()
        self.settings['dark_mode'] = (self.theme_control.currentIndex() == 0)
        self.settings['lock_timeout'] = self.screensaver_slider[1].value() * 60
        self.settings['auto_shutdown'] = self.auto_shutdown_toggle[1].isChecked()
        self.settings['shutdown_timeout'] = self.shutdown_row[1].value()
        self.settings['auto_update_check'] = self.auto_update_toggle[1].isChecked()
        self.settings['update_notification'] = self.update_notification_toggle[1].isChecked()
        self.settings['update_check_frequency'] = self.update_frequency_slider[1].value()

        # Display & Performance
        self.settings['target_fps'] = 0 if self.fps_combo.currentText() == 'Unlimited' else int(self.fps_combo.currentText())
        self.settings['auto_cpu_limit'] = self.cpu_toggle[1].isChecked()
        self.settings['display_target'] = self.display_combo.currentText()
        self.settings['physical_only'] = self.physical_toggle[1].isChecked()
        self.settings['show_stats'] = self.stats_toggle[1].isChecked()
        self.settings['display_shutdown'] = self.display_shutdown_toggle[1].isChecked()
        self.settings['display_shutdown_timeout'] = self.display_shutdown_slider[1].value()

        # Matrix settings
        self.settings['color'] = self.color_combo.currentText()
        self.settings['rainbow_mode'] = (self.color_combo.currentText() == 'rainbow')
        self.settings['speed'] = self.speed_slider[1].value()
        self.settings['use_katakana'] = self.katakana_toggle[1].isChecked()
        self.settings['bold_text'] = self.bold_toggle[1].isChecked()
        self.settings['font_size'] = self.font_size_slider[1].value()

        # Mystify settings
        self.settings['mystify_shapes'] = self.shapes_spin.value()
        self.settings['mystify_complexity'] = self.complexity_spin.value()
        self.settings['mystify_speed'] = self.mystify_speed_spin.value()
        self.settings['mystify_trail_length'] = self.trail_spin.value()
        self.settings['mystify_fill'] = self.fill_toggle[1].isChecked()
        color_mode_map = {0: 'rainbow', 1: 'single', 2: 'duo'}
        self.settings['mystify_color_mode'] = color_mode_map[self.mystify_color_combo.currentIndex()]
        self.settings['mystify_color_hue'] = self.mystify_hue_slider[1].value()
        self.settings['mystify_color_hue1'] = self.mystify_hue1_slider[1].value()
        self.settings['mystify_color_hue2'] = self.mystify_hue2_slider[1].value()

        # Slideshow settings
        self.settings['slide_duration'] = self.duration_spin.value()
        self.settings['slideshow_random'] = self.slideshow_random_toggle[1].isChecked()
        self.settings['slideshow_fit_mode'] = self.fit_combo.currentText()

        # Video settings
        self.settings['video_random'] = self.video_random_toggle[1].isChecked()
        self.settings['video_mute'] = self.video_mute_toggle[1].isChecked()
        self.settings['video_playback_speed'] = self.video_speed_slider[1].value() / 4.0  # Convert from 1-8 to 0.25-2.0

        if self.save_settings():
            # Update autostart configuration
            self.setup_autostart(self.settings['start_on_boot'])

            self.status_bar.showMessage("✅ Settings saved - minimizing to tray")

            # Update systray visibility based on settings
            if hasattr(self, 'tray_icon'):
                if self.settings['show_taskbar_icon']:
                    self.tray_icon.show()
                else:
                    self.tray_icon.hide()

            # Show restart message if touch UI was changed
            if self.settings['enable_touch_ui'] != (self.ui_scale_factor > 1.0):
                msg = self.create_styled_messagebox(
                    "Settings Applied",
                    "Touch UI mode changed. Please restart the application for changes to take effect.\n\nMinimizing to tray now (timers still running).",
                    QMessageBox.Icon.Information
                )
                msg.exec()

            # Minimize to tray after applying settings (timers keep running)
            self.close()  # This will minimize to tray via closeEvent
        else:
            self.status_bar.showMessage("❌ Failed to save settings")
            msg = self.create_styled_messagebox("Error", "Failed to save settings. Please try again.", QMessageBox.Icon.Critical)
            msg.exec()

    def setup_autostart(self, enable: bool) -> None:
        """Configure application to start on boot"""
        autostart_dir = Path.home() / '.config' / 'autostart'
        autostart_file = autostart_dir / 'screensaver-preferences-v4.desktop'

        try:
            autostart_dir.mkdir(parents=True, exist_ok=True)

            if enable:
                # Get the path to the installed script
                script_path = Path.home() / '.local' / 'bin' / 'screensaver_preferences_v4.py'
                if not script_path.exists():
                    script_path = Path(__file__).resolve()

                desktop_entry = f"""[Desktop Entry]
Type=Application
Name=Screensaver Preferences v4
Comment=Modern screensaver control panel
Exec={script_path}
Icon=preferences-desktop-screensaver
Terminal=false
Categories=Settings;System;
X-GNOME-Autostart-enabled=true
StartupNotify=false
"""
                with open(autostart_file, 'w', encoding='utf-8') as f:
                    f.write(desktop_entry)
                autostart_file.chmod(0o755)
                self.status_bar.showMessage("✅ Autostart enabled")
            else:
                # Remove autostart file
                if autostart_file.exists():
                    autostart_file.unlink()
                self.status_bar.showMessage("✅ Autostart disabled")
        except Exception as e:
            self.status_bar.showMessage(f"❌ Autostart configuration failed: {e}")

    def show_boot_notification(self) -> None:
        """Show a brief notification popup on boot if physical display detected"""
        try:
            # Check if there's a physical display
            result = subprocess.run(['xrandr'], capture_output=True, text=True, timeout=2)
            has_physical_display = ' connected' in result.stdout

            if has_physical_display:
                # Create a simple notification
                msg = QMessageBox(self)
                msg.setWindowTitle("Screensaver Active")
                msg.setText("🎬 Screensaver Preferences v4 is running")
                msg.setInformativeText("Find the icon in your system tray")
                msg.setIcon(QMessageBox.Icon.Information)
                msg.setStandardButtons(QMessageBox.StandardButton.Ok)
                msg.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint)

                # Auto-close after 3 seconds
                close_timer = QTimer()
                close_timer.setSingleShot(True)
                close_timer.timeout.connect(msg.accept)  # type: ignore
                close_timer.start(3000)

                # Show non-blocking
                msg.show()
        except Exception:
            pass  # Silently fail if display detection doesn't work

    def check_for_updates(self, manual: bool = False) -> None:
        """Check for updates from GitHub releases"""
        import urllib.request
        import urllib.error

        if not manual and not self.settings.get('auto_update_check', True):
            return

        # Check if it's time to check for updates (unless manual)
        if not manual and not self.should_check_for_updates():
            return

        try:
            # GitHub API URL for latest release
            repo_url = "https://api.github.com/repos/GuyMayer/sidekick-screensaver-pi5-wayland-bookworm/releases/latest"

            request = urllib.request.Request(repo_url)
            request.add_header('User-Agent', 'Sidekick-Screensaver-UpdateChecker/1.0')

            with urllib.request.urlopen(request, timeout=10) as response:
                if response.getcode() == 200:
                    data = json.load(response)
                    latest_version = data.get('tag_name', '').lstrip('v')
                    release_url = data.get('html_url', '')

                    # Update last check time
                    self.settings['last_update_check'] = datetime.datetime.now().isoformat()
                    self.save_settings()

                    # Compare versions
                    if self.is_newer_version(latest_version, self.app_version):
                        if self.settings.get('update_notification', True) or manual:
                            msg = self.create_styled_messagebox(
                                "Update Available",
                                f"New version {latest_version} is available!\n\nYou have: {self.app_version}\n\nVisit GitHub to download the update.",
                                QMessageBox.Icon.Information
                            )
                            msg.exec()
                            import webbrowser
                            webbrowser.open(release_url)
                    elif manual:
                        msg = self.create_styled_messagebox(
                            "Up to Date",
                            f"You have the latest version ({self.app_version})",
                            QMessageBox.Icon.Information
                        )
                        msg.exec()

        except urllib.error.URLError:
            if manual:
                msg = self.create_styled_messagebox(
                    "Update Check Failed",
                    "Could not connect to GitHub.\nCheck your internet connection.",
                    QMessageBox.Icon.Warning
                )
                msg.exec()
        except Exception as e:
            if manual:
                msg = self.create_styled_messagebox(
                    "Update Check Error",
                    f"Error checking for updates: {e}",
                    QMessageBox.Icon.Warning
                )
                msg.exec()

    def should_check_for_updates(self) -> bool:
        """Check if it's time to perform an update check"""
        last_check = self.settings.get('last_update_check', '')
        if not last_check:
            return True

        try:
            last_check_date = datetime.datetime.fromisoformat(last_check)
            days_since_check = (datetime.datetime.now() - last_check_date).days
            frequency = self.settings.get('update_check_frequency', 30)
            return days_since_check >= frequency
        except (ValueError, TypeError):
            return True

    def is_newer_version(self, latest: str, current: str) -> bool:
        """Compare version strings to determine if latest is newer than current"""
        try:
            latest_parts = [int(x) for x in latest.split('.')]
            current_parts = [int(x) for x in current.split('.')]

            max_len = max(len(latest_parts), len(current_parts))
            latest_parts.extend([0] * (max_len - len(latest_parts)))
            current_parts.extend([0] * (max_len - len(current_parts)))

            return latest_parts > current_parts
        except (ValueError, AttributeError):
            return False

    def test_screensaver(self):
        """Test the screensaver"""
        screensaver_type = self.type_combo.currentText()
        self.status_bar.showMessage(f"Testing {screensaver_type} screensaver...")

        try:
            if screensaver_type == 'Matrix':
                from sidekick_widget import MatrixScreensaver
                settings = {
                    'color': self.color_combo.currentText(),
                    'speed': self.speed_slider[1].value(),
                    'bold': self.bold_toggle[1].isChecked(),
                    'rainbow': (self.color_combo.currentText() == 'rainbow'),
                    'use_katakana': self.katakana_toggle[1].isChecked(),
                    'font_size': self.font_size_slider[1].value(),
                    'show_stats': self.settings.get('show_stats', False),
                }
                self.test_window = MatrixScreensaver(settings)
                self.test_window.show()

            elif screensaver_type == 'Mystify':
                from mystify_widget import MystifyScreensaver
                color_mode_map = {0: 'rainbow', 1: 'single', 2: 'duo'}
                settings = {
                    'mystify_shapes': self.shapes_spin.value(),
                    'mystify_complexity': self.complexity_spin.value(),
                    'mystify_speed': self.mystify_speed_spin.value(),
                    'mystify_trail_length': self.trail_spin.value(),
                    'mystify_fill': self.fill_toggle[1].isChecked(),
                    'mystify_color_mode': color_mode_map[self.mystify_color_combo.currentIndex()],
                    'mystify_color_hue': self.mystify_hue_slider[1].value(),
                    'mystify_color_hue1': self.mystify_hue1_slider[1].value(),
                    'mystify_color_hue2': self.mystify_hue2_slider[1].value(),
                    'show_stats': self.settings.get('show_stats', False),
                }
                self.test_window = MystifyScreensaver(settings)
                self.test_window.show()

            elif screensaver_type == 'Slideshow':
                if not self.settings.get('slideshow_folder'):
                    msg = self.create_styled_messagebox("No Folder", "Please select a slideshow folder first in the Slideshow page", QMessageBox.Icon.Warning)
                    msg.exec()
                else:
                    from slideshow_widget import SlideshowScreensaver
                    settings = {
                        'slideshow_folder': self.settings.get('slideshow_folder'),
                        'slide_duration': self.duration_spin.value(),
                        'slideshow_random': self.slideshow_random_toggle[1].isChecked(),
                        'slideshow_fit_mode': self.fit_combo.currentText(),
                        'show_stats': self.settings.get('show_stats', False),
                    }
                    self.test_window = SlideshowScreensaver(settings)
                    self.test_window.slideshow_widget.show()

            elif screensaver_type == 'Videos':
                if not self.settings.get('video_folder'):
                    msg = self.create_styled_messagebox("No Folder", "Please select a video folder first in the Videos page", QMessageBox.Icon.Warning)
                    msg.exec()
                else:
                    from video_widget import VideoScreensaver
                    settings = {
                        'video_folder': self.settings.get('video_folder'),
                        'video_random': self.video_random_toggle[1].isChecked(),
                        'video_mute': self.video_mute_toggle[1].isChecked(),
                        'video_playback_speed': self.video_speed_slider[1].value() / 4.0,
                        'show_stats': self.settings.get('show_stats', False),
                    }
                    # VideoScreensaver shows itself in fullscreen during __init__
                    self.test_window = VideoScreensaver(settings)
                    self.status_bar.showMessage("Video test running - press any key or click to exit")

            else:
                msg = self.create_styled_messagebox("No Screensaver", "Please select a screensaver type first", QMessageBox.Icon.Warning)
                msg.exec()
        except Exception as e:
            msg = self.create_styled_messagebox("Error", f"Failed to test: {e}", QMessageBox.Icon.Critical)
            msg.exec()

    def show_about(self):
        """Show about dialog with logo and bio"""
        # Create custom dialog with logo
        dialog = QMessageBox(self)
        dialog.setWindowTitle("About Sidekick Screensaver")

        # Load and set logo
        dark_mode = self.settings.get('dark_mode', True)
        logo_filename = "sidekick_logo_dark.png" if dark_mode else "sidekick_logo_light.png"

        # Try installed location first, then development location
        logo_path = Path(__file__).parent / logo_filename
        if not logo_path.exists():
            logo_path = Path(__file__).parent.parent / "media" / "Logo" / logo_filename

        if logo_path.exists():
            pixmap = QPixmap(str(logo_path))
            scaled_pixmap = pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            dialog.setIconPixmap(scaled_pixmap)

        about_text = f"""<h3>🎬 Sidekick Screensaver</h3>
<p><b>Version:</b> {self.app_version} (Modern UI Edition)</p>
<p><b>Updated:</b> {self.build_date}</p>
<p><b>Developer:</b> Guy Mayer</p>

<h4>👋 About the Developer:</h4>
<p>Hello! I'm a professional photographer and tango teacher, but my other full-time passion is coding.</p>

<p>I'm currently stuck on a major 'bug': The resources I need to level up (pro courses, new software, hosting) cost money. It's the one 'refactor' I can't do alone.</p>

<p><b>You can be the hero who helps me resolve this ticket.</b></p>

<p>Every coffee you send is a direct contribution to my coding 'stack.' You're not just donating; you're actively helping me debug my finances so I can get back to building.</p>

<p>I can't wait to see what we build. Thank you for your support!</p>

<h4>🛠️ Features:</h4>
<ul>
<li>Multiple screensaver modes (Matrix, Mystify, Slideshow)</li>
<li>System tray integration</li>
<li>Auto-shutdown timer</li>
<li>Performance monitoring</li>
<li>Multi-display support</li>
</ul>"""

        dialog.setText(about_text)
        dialog.setStandardButtons(QMessageBox.StandardButton.Ok)

        # Apply theme-aware styling
        theme = 'dark' if dark_mode else 'light'
        COLORS = COLORS_DARK if theme == 'dark' else COLORS_LIGHT
        dialog.setStyleSheet(f"""
            QMessageBox {{
                background-color: {COLORS['bg_content']};
                color: {COLORS['text_primary']};
            }}
            QLabel {{
                color: {COLORS['text_primary']};
            }}
            QPushButton {{
                background-color: {COLORS['accent_blue']};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 24px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: #2563EB;
            }}
        """)

        dialog.exec()

    def open_coffee_link(self):
        """Open Buy Me a Coffee link in browser"""
        import webbrowser
        coffee_url = "https://buymeacoffee.com/studiomailt"  # User-provided Buy Me a Coffee link
        try:
            webbrowser.open(coffee_url)
            self.status_bar.showMessage("☕ Opening Buy Me a Coffee page... Thank you for your support!")
        except Exception as e:
            msg = self.create_styled_messagebox(
                "Info",
                f"Please visit: {coffee_url}\n\nThank you for supporting this project! ☕",
                QMessageBox.Icon.Information
            )
            msg.exec()

    def bounce_coffee_button(self):
        """Make the coffee button bounce to attract attention"""
        if not hasattr(self, 'coffee_btn'):
            return

        # Get original position
        original_pos = self.coffee_btn.pos()

        # Create bounce animation (up and down)
        self.bounce_animation = QPropertyAnimation(self.coffee_btn, b"pos")  # type: ignore
        self.bounce_animation.setDuration(600)  # 600ms total animation
        self.bounce_animation.setEasingCurve(QEasingCurve.Type.OutBounce)

        # Bounce up by 10 pixels and back
        self.bounce_animation.setStartValue(original_pos)
        self.bounce_animation.setKeyValueAt(0.5, QPoint(original_pos.x(), original_pos.y() - 15))
        self.bounce_animation.setEndValue(original_pos)

        # Start the animation
        self.bounce_animation.start()

    def run_diagnostics(self):
        """Run system diagnostics to help troubleshoot issues"""
        import subprocess

        diagnostics = []

        # Check PyQt6
        try:
            from PyQt6.QtCore import PYQT_VERSION_STR
            diagnostics.append(f"PyQt6: {PYQT_VERSION_STR}")
        except (ImportError, AttributeError):
            diagnostics.append("PyQt6: Available")

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
                diagnostics.append(f"{binary}: Available ({description})")
            else:
                diagnostics.append(f"❌ {binary}: Not found ({description})")

        # Check environment
        display = os.environ.get('DISPLAY', 'Not set')
        wayland = os.environ.get('WAYLAND_DISPLAY', 'Not set')
        diagnostics.append(f"DISPLAY: {display}")
        diagnostics.append(f"WAYLAND_DISPLAY: {wayland}")

        # Check desktop environment
        desktop = os.environ.get('XDG_CURRENT_DESKTOP', 'Unknown')
        session = os.environ.get('XDG_SESSION_TYPE', 'Unknown')
        diagnostics.append(f"Desktop: {desktop}")
        diagnostics.append(f"Session: {session}")

        # Show results
        result_text = "\n".join(diagnostics)
        msg = self.create_styled_messagebox("System Diagnostics", f"<h3>System Diagnostics Report</h3><pre>{result_text}</pre>")
        msg.exec()

    def on_screensaver_timeout(self) -> None:
        """Handle screensaver timer timeout - launch the screensaver"""
        if not self.settings.get('enabled', True):
            return

        print("⏰ Screensaver timer triggered - launching screensaver")

        # Determine which screensaver type to launch
        screensaver_type = self.type_combo.currentText() if hasattr(self, 'type_combo') else 'Matrix'

        try:
            # Launch the sidekick screensaver with appropriate parameters
            script_path = Path.home() / '.local' / 'bin' / 'sidekick_screensaver.sh'
            if not script_path.exists():
                script_path = Path(__file__).parent / 'sidekick_screensaver.sh'

            if script_path.exists():
                subprocess.Popen([str(script_path)], start_new_session=True)
                self.screensaver_active = True
                print(f"✅ Launched {screensaver_type} screensaver")
            else:
                print(f"⚠️  Screensaver script not found: {script_path}")

        except Exception as e:
            print(f"❌ Failed to launch screensaver: {e}")

    def start_shutdown_timer(self):
        """Start auto-shutdown timer"""
        timeout_minutes = self.settings.get('shutdown_timeout', 60)
        timeout_ms = timeout_minutes * 60 * 1000

        self.shutdown_timer = QTimer()
        self.shutdown_timer.timeout.connect(self.on_shutdown_timeout)  # type: ignore
        self.shutdown_timer.setSingleShot(True)
        self.shutdown_timer.start(timeout_ms)

        print(f"🕒 Auto-shutdown timer started: {timeout_minutes} minutes")

    def on_shutdown_timeout(self) -> None:
        """Handle auto-shutdown timeout"""
        print("⏰ Auto-shutdown timer triggered")
        try:
            subprocess.run(['shutdown', '-h', 'now'], check=False)
        except Exception as e:
            print(f"❌ Shutdown failed: {e}")

    def setup_display_shutdown(self) -> None:
        """Setup display shutdown timer if enabled"""
        if not self.settings.get('display_shutdown', False):
            return

        timeout_minutes = self.settings.get('display_shutdown_timeout', 30)
        timeout_ms = timeout_minutes * 60 * 1000

        self.display_shutdown_timer = QTimer()
        self.display_shutdown_timer.timeout.connect(self.turn_off_displays)  # type: ignore
        self.display_shutdown_timer.setSingleShot(True)
        self.display_shutdown_timer.start(timeout_ms)

        print(f"🖥️ Display shutdown timer started: {timeout_minutes} minutes")

    def turn_off_displays(self) -> None:
        """Turn off displays using xset dpms"""
        print("🖥️ Turning off displays...")
        try:
            # Force displays off immediately
            subprocess.run(['xset', 'dpms', 'force', 'off'], check=False)
            print("✅ Displays turned off")
        except Exception as e:
            print(f"❌ Failed to turn off displays: {e}")

    def showEvent(self, event):
        """Handle window show - pause timers"""
        super().showEvent(event)
        # Stop timers when GUI is visible
        if hasattr(self, 'screensaver_timer'):
            self.screensaver_timer.stop()
        if hasattr(self, 'progress_timer'):
            self.progress_timer.stop()
        # Update status bar
        if hasattr(self, 'status_bar'):
            self.status_bar.showMessage(f"Ready - v{self.app_version} (Timers paused while GUI shown)")

    def hideEvent(self, event):
        """Handle window hide - resume timers"""
        super().hideEvent(event)
        # Restart timers when GUI is hidden
        if hasattr(self, 'screensaver_timer') and self.settings.get('enabled', True):
            timeout_secs = self.settings.get('lock_timeout', 300)
            self.screensaver_timer.start(timeout_secs * 1000)
        if hasattr(self, 'progress_timer'):
            self.progress_timer.start(1000)
        # Update status bar
        if hasattr(self, 'status_bar'):
            self.status_bar.showMessage(f"Timers resumed - screensaver will start after {self.settings.get('lock_timeout', 300) // 60} minutes")

    def closeEvent(self, event):
        """Handle window close - minimize to tray if enabled, otherwise quit"""
        # If systray is enabled and available, minimize to tray instead of closing
        if (hasattr(self, 'tray_icon') and
            self.tray_icon.isVisible() and
            self.settings.get('show_taskbar_icon', True)):

            print("ℹ️  Minimizing to system tray (window hidden, timers still running)")
            event.ignore()  # Don't close the window
            self.hide()     # Just hide it - timers keep running!

            # Show a notification that we're still running
            if hasattr(self, 'tray_icon'):
                self.tray_icon.showMessage(
                    "Screensaver Settings",
                    "Running in background. Timers active. Click icon to restore.",
                    QSystemTrayIcon.MessageIcon.Information,
                    2000
                )
        else:
            # No systray - actually quit
            self.quit_application()
            event.accept()

    def quit_application(self):
        """Actually quit the application"""
        print("🛑 Quitting application...")

        # Stop any running test screensavers
        if hasattr(self, 'test_window') and self.test_window:
            try:
                # If it's a VideoScreensaver, make sure VLC is killed
                from video_widget import VideoScreensaver
                if isinstance(self.test_window, VideoScreensaver) and hasattr(self.test_window, 'video_player'):
                    self.test_window.video_player.stop_vlc()
                self.test_window.close()
            except Exception as e:
                print(f"Error closing test window: {e}")

        self.save_settings()
        if hasattr(self, 'tray_icon'):
            self.tray_icon.hide()

        QApplication.quit()


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

def create_splash_screen(dark_mode: bool = True) -> Optional[QSplashScreen]:
    """Create splash screen with appropriate logo based on theme"""
    # Determine logo path based on theme
    logo_filename = "sidekick_logo_dark.png" if dark_mode else "sidekick_logo_light.png"

    # Try installed location first (same directory), then development location
    logo_path = Path(__file__).parent / logo_filename
    if not logo_path.exists():
        logo_path = Path(__file__).parent.parent / "media" / "Logo" / logo_filename

    # Fallback to current working directory
    if not logo_path.exists():
        logo_path = Path.cwd() / "media" / "Logo" / logo_filename

    # Create splash screen
    if logo_path.exists():
        pixmap = QPixmap(str(logo_path))
        # Scale down if too large (max 800x600)
        if pixmap.width() > 800 or pixmap.height() > 600:
            pixmap = pixmap.scaled(800, 600, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        splash = QSplashScreen(pixmap)
        splash.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint)
        return splash
    else:
        print(f"⚠️  Logo not found: {logo_path}")
        return None

def main() -> int:
    """Main entry point for the screensaver preferences application"""
    # Check for command-line arguments
    start_minimized = '--start-minimized' in sys.argv

    # Single instance check
    instance_manager = SingleInstanceManager("sidekick_screensaver_v4")
    if not instance_manager.acquire_lock():
        print("❌ Another instance is already running!")
        return 1

    app = QApplication(sys.argv)
    app.setApplicationName("Sidekick Screensaver v4")

    # Show splash screen (only if not starting minimized)
    splash = None
    if not start_minimized:
        # Load settings to determine dark mode
        config_dir = Path.home() / '.config' / 'screensaver'
        config_file = config_dir / 'settings.json'
        dark_mode = True  # Default

        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    dark_mode = settings.get('dark_mode', True)
            except Exception:
                pass

        splash = create_splash_screen(dark_mode)
        if splash:
            splash.show()
            app.processEvents()

    # Modern font
    app.setStyleSheet("""
        QWidget {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI",
                         Roboto, "Helvetica Neue", Arial, sans-serif;
        }
    """)

    window = ScreensaverPreferencesV4()
    window.instance_manager = instance_manager

    # Close splash screen after window is ready
    if splash:
        splash_timer = QTimer()
        splash_timer.setSingleShot(True)
        splash_timer.timeout.connect(splash.close)  # type: ignore
        splash_timer.start(1500)  # Show for 1.5 seconds

    # Handle boot startup (minimized to tray)
    if start_minimized:
        # Show systray icon immediately
        if hasattr(window, 'tray_icon'):
            window.tray_icon.show()

        # Show boot notification if physical display detected
        QTimer.singleShot(500, window.show_boot_notification)

        # Don't show the main window, just run in tray
        window.hide()
    else:
        # Normal startup - show window
        if window.settings.get('start_maximized', False):
            # Show normal first, then maximize after a delay to avoid rendering glitches
            window.show()
            QTimer.singleShot(100, window.showMaximized)
        else:
            window.show()

    return app.exec()


if __name__ == '__main__':
    sys.exit(main())
