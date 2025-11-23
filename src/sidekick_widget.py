#!/usr/bin/env python3
"""
Matrix Widget - Pure Python PyQt6 Matrix Screensaver
High-performance Matrix digital rain effect with customizable settings

Features:
- Hardware-accelerated rendering with PyQt6
- Customizable colors, speed, and effects
- True fullscreen without terminal dependencies
- Direct input handling for responsive exit
- Smooth animations with optimized performance
- Built-in maximization and fullscreen support

Version: 1.0.0
Created: September 2025
"""

import sys
import random
import time
from typing import List, Optional
from PyQt6.QtWidgets import QWidget, QApplication, QMainWindow
from PyQt6.QtCore import QTimer, Qt, QPoint, pyqtSignal, QEvent
from PyQt6.QtGui import QPainter, QFont, QColor, QPen, QFontMetrics, QPaintEvent, QKeyEvent, QMouseEvent

class MatrixColumn:
    """Represents a single column of Matrix characters"""

    def __init__(self, x: int, screen_height: int, char_height: int, use_katakana: bool = True):
        self.x = x
        self.screen_height = screen_height
        self.char_height = char_height
        self.max_chars = screen_height // char_height + 5
        self.use_katakana = use_katakana

        # Column properties
        self.characters: List[str] = []
        self.char_positions: List[float] = []  # Changed to float for smooth movement
        self.char_ages: List[int] = []
        self.head_position = -50
        self.speed = random.uniform(0.3, 1.5)  # REDUCED speed range (was 0.5-3.0)
        self.length = random.randint(3, 15)  # REDUCED max length (was 5-25)
        self.last_update = 0

        # Performance optimization - INCREASED update interval
        self.update_interval = random.randint(100, 250)  # ms (was 50-150)

        self.reset_column()

    def get_character_set(self) -> str:
        """Get the appropriate character set based on settings"""
        if self.use_katakana:
            return "ｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜｦﾝ0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        else:
            return "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()_+-=[]{}|;:,.<>?"

    def reset_column(self):
        """Reset column to start from top"""
        self.head_position = random.randint(-100, -20)
        self.speed = random.uniform(0.3, 1.5)  # REDUCED speed (was 0.5-3.0)
        self.length = random.randint(3, 15)  # REDUCED length (was 5-25)
        self.characters = []
        self.char_positions = []
        self.char_ages = []

        # Pre-generate characters for this drop
        matrix_chars = self.get_character_set()

        for i in range(self.length):
            char = random.choice(matrix_chars)
            pos = self.head_position - (i * self.char_height)
            age = i

            self.characters.append(char)
            self.char_positions.append(float(pos))  # Ensure float type
            self.char_ages.append(age)

    def update(self, delta_time: float) -> bool:
        """Update column animation. Returns True if column needs reset"""
        current_time = time.time() * 1000

        # Throttle updates for performance
        if current_time - self.last_update < self.update_interval:
            return False

        self.last_update = current_time

        # Move all characters down - REDUCED movement speed
        movement = self.speed * delta_time * 60  # REDUCED multiplier (was 100)
        self.head_position += movement

        for i in range(len(self.char_positions)):
            self.char_positions[i] += movement
            self.char_ages[i] += 1

            # REDUCED character change frequency for less CPU
            if random.random() < 0.02:  # REDUCED from 0.05
                matrix_chars = self.get_character_set()
                self.characters[i] = random.choice(matrix_chars)

        # Check if column is off screen
        if self.head_position > self.screen_height + 100:
            return True

        return False

class MatrixWidget(QWidget):
    """High-performance Matrix digital rain widget"""

    # Signals
    exit_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        # Widget setup
        self.setWindowTitle("Matrix Digital Rain")
        self.setStyleSheet("background-color: black;")
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent)
        self.setMouseTracking(True)  # Enable mouse movement tracking

        # Explicitly enable keyboard input and tab focus
        self.setAttribute(Qt.WidgetAttribute.WA_KeyCompression, False)
        self.setTabletTracking(True)

        # Set minimum size to ensure proper sizing
        self.setMinimumSize(800, 600)

        # Set size policy to expand
        from PyQt6.QtWidgets import QSizePolicy
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Mouse tracking for screensaver exit
        self.last_mouse_pos = None

        # Matrix settings (will be updated from preferences)
        self.settings = {
            'color': 'green',
            'speed': 25,  # 0-50 scale
            'bold': True,
            'rainbow': False,
            'font_size': 14,
            'show_stats': True,  # Enable stats by default
            'use_katakana': True,
            'target_fps': 10,  # Default FPS - REDUCED for CPU efficiency (was 15)
            'auto_cpu_limit': True,  # Enable auto CPU limiting by default
            'stats_drift': True  # Enable stats drift to prevent burn-in
        }

        # Animation state
        self.columns: List[MatrixColumn] = []
        self.last_frame_time = time.time()
        self.frame_count = 0
        self.fps = 0

        # CPU monitoring for auto limit
        self.cpu_samples: List[float] = []
        self.last_cpu_check = time.time()
        self.current_target_fps = self.settings.get('target_fps', 10)  # REDUCED default
        self.min_fps = 8  # REDUCED minimum (was 15)
        self.max_fps = 20  # REDUCED maximum (was 30)
        self.cpu_threshold = 30.0  # REDUCED threshold - throttle earlier (was 40%)

        # Emergency CPU throttling (NEW)
        self.emergency_cpu_threshold = 90.0  # If system CPU > 90%, throttle to 1 FPS
        self.is_emergency_throttled = False
        self.last_emergency_check = time.time()
        self.emergency_check_interval = 2.0  # Check every 2 seconds

        # Stats display averaging and timing
        self.stats_cpu_samples: List[float] = []
        self.last_stats_update = time.time()

        # Create persistent process object for CPU monitoring (CRITICAL FIX)
        # Creating new Process() each time causes cpu_percent() to return 0.0
        try:
            import psutil
            import os
            self.current_process = psutil.Process(os.getpid())
            self.current_process.cpu_percent()  # Baseline call (first call returns 0.0)
        except ImportError:
            self.current_process = None

        # Create persistent process object for CPU monitoring (CRITICAL FIX)
        # Creating new Process() each time causes cpu_percent() to return 0.0
        try:
            import psutil
            import os
            self.current_process = psutil.Process(os.getpid())
            self.current_process.cpu_percent()  # Baseline call (first call returns 0.0)
        except ImportError:
            self.current_process = None
        self.displayed_cpu = 0.0  # Initialize as float for 2 decimal precision
        self.displayed_memory = 0
        self.displayed_process_cpu = 0.0  # Initialize as float for 2 decimal precision
        self.displayed_process_memory = 0.0

        # Memory monitoring for the screensaver itself
        self.own_memory_samples: List[float] = []
        self.last_memory_check = time.time()
        self.memory_warning_threshold = 200  # MB - warn if screensaver uses > 200MB
        self.memory_critical_threshold = 500  # MB - critical if screensaver uses > 500MB

        # Color cycling for stats to prevent burn-in
        self.last_color_change = time.time()
        self.current_color_index = 0
        self.stats_colors = [
            QColor(255, 255, 255),  # White
            QColor(220, 220, 220),  # Light gray
            QColor(200, 255, 200),  # Light green
            QColor(255, 220, 200),  # Light peach
            QColor(200, 220, 255),  # Light blue
            QColor(255, 200, 255),  # Light magenta
            QColor(255, 255, 200),  # Light yellow
            QColor(200, 255, 255),  # Light cyan
        ]

        # Stats position drift to prevent burn-in
        self.stats_drift_start_time = time.time()
        self.stats_base_x = 10  # Base position
        self.stats_base_y = 30  # Base position for first line
        self.stats_line_height = 20  # Height between stats lines
        self.drift_cycle_duration = 8 * 60  # 8 minutes total (2 min per edge)
        self.drift_margin = 50  # Stay this far from edges
        # Drift positions will be calculated dynamically based on screen size

        # Colors
        self.setup_colors()

        # Font setup
        self.matrix_font = QFont("Consolas", self.settings['font_size'])
        self.matrix_font.setBold(self.settings['bold'])
        self.matrix_font.setStyleHint(QFont.StyleHint.Monospace)

        # Animation timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_animation)

        # USB Activity Monitoring Timer for physical input detection
        self.usb_monitor_timer = QTimer()
        self.usb_monitor_timer.timeout.connect(self.check_usb_activity)
        self.usb_interrupt_baseline = None
        self.last_usb_check = time.time()

        # Start USB monitoring every 500ms for responsive USB device detection
        self.usb_monitor_timer.start(500)

        # Set initial FPS based on target_fps setting
        target_fps = self.settings.get('target_fps', 60)
        if target_fps > 0:
            interval = int(1000 / target_fps)  # Convert FPS to milliseconds
        else:
            interval = 1  # Unlimited FPS (as fast as possible)
        self.timer.start(interval)

        # Setup columns when widget is shown
        self.columns_initialized = False

    def setup_colors(self):
        """Setup color scheme based on settings"""
        base_colors = {
            'green': QColor(0, 255, 0),
            'red': QColor(255, 0, 0),
            'blue': QColor(0, 0, 255),
            'cyan': QColor(0, 255, 255),
            'magenta': QColor(255, 0, 255),
            'yellow': QColor(255, 255, 0),
            'white': QColor(255, 255, 255)
        }

        self.primary_color = base_colors.get(self.settings['color'], base_colors['green'])

        # Create color variations for depth effect
        self.head_color = QColor(255, 255, 255)  # Bright white for head
        self.fade_colors = []

        # Generate fade colors
        for i in range(20):
            alpha = max(50, 255 - (i * 12))
            color = QColor(self.primary_color)
            color.setAlpha(alpha)
            self.fade_colors.append(color)

    def update_settings(self, settings: dict):
        """Update Matrix settings from preferences"""
        self.settings.update(settings)
        self.setup_colors()

        # Update font
        self.matrix_font.setPointSize(self.settings['font_size'])
        self.matrix_font.setBold(self.settings['bold'])

        # Update timer interval based on target FPS
        target_fps = self.settings.get('target_fps', 60)
        if target_fps > 0:
            interval = int(1000 / target_fps)  # Convert FPS to milliseconds
        else:
            interval = 1  # Unlimited FPS (as fast as possible)

        self.timer.stop()
        self.timer.start(interval)

        # Update column speeds
        speed_factor = self.settings['speed'] / 25.0  # Normalize to 1.0
        for column in self.columns:
            column.speed *= speed_factor

    def setup_columns(self):
        """Initialize Matrix columns based on widget size"""
        if self.width() <= 0 or self.height() <= 0:
            return

        # Calculate character dimensions
        font_metrics = QFontMetrics(self.matrix_font)
        char_width = font_metrics.horizontalAdvance('M')
        char_height = font_metrics.height()

        # Calculate number of columns - REDUCED by 50% for CPU efficiency
        max_columns = self.width() // char_width
        num_columns = max(20, max_columns // 2)  # Use only half the columns, minimum 20

        # Create columns with wider spacing
        column_spacing = self.width() / num_columns

        self.columns = []
        for i in range(num_columns):
            x = int(i * column_spacing)
            column = MatrixColumn(x, self.height(), char_height, self.settings.get('use_katakana', True))
            # Stagger start times
            column.head_position -= random.randint(0, self.height())
            self.columns.append(column)

        self.columns_initialized = True
        print(f"🎬 Matrix: Created {num_columns} columns (max: {max_columns}, reduced for CPU efficiency)")

    def showEvent(self, event):
        """Setup columns when widget is first shown"""
        super().showEvent(event)
        if not self.columns_initialized:
            self.setup_columns()

    def resizeEvent(self, event):
        """Reinitialize columns on resize"""
        super().resizeEvent(event)
        self.setup_columns()

    def check_and_adjust_fps(self):
        """Simple FPS management without blocking calls"""
        # Skip expensive operations that could cause system instability
        return

    def update_animation(self):
        """Update animation frame with performance optimizations"""
        current_time = time.time()
        delta_time = current_time - self.last_frame_time
        self.last_frame_time = current_time

        # EMERGENCY CPU THROTTLING: Check system CPU every 2 seconds
        if current_time - self.last_emergency_check >= self.emergency_check_interval:
            self.last_emergency_check = current_time
            self.check_emergency_cpu_throttle()

        # OPTIMIZATION: Update FPS counter less frequently (every 2 seconds)
        self.frame_count += 1
        if self.frame_count % 60 == 0:  # Every ~2 seconds at 30 FPS
            self.fps = int(1.0 / delta_time) if delta_time > 0 else 0

        # OPTIMIZATION: Batch update all columns (more cache-friendly)
        for column in self.columns:
            if column.update(delta_time):
                column.reset_column()

        # OPTIMIZATION: Use single update() call instead of repaint()
        self.update()

    def check_emergency_cpu_throttle(self):
        """Check system CPU and throttle to 1 FPS if over 90%"""
        try:
            import psutil

            # Get current system CPU usage
            cpu_percent = psutil.cpu_percent(interval=0)

            # Ensure it's a number
            if not isinstance(cpu_percent, (int, float)):
                return

            # Check if we need emergency throttling
            if cpu_percent > self.emergency_cpu_threshold:
                if not self.is_emergency_throttled:
                    # Enable emergency throttling
                    self.is_emergency_throttled = True
                    self.timer.setInterval(1000)  # 1 FPS = 1000ms interval
                    print(f"🚨 EMERGENCY THROTTLE: System CPU at {cpu_percent:.1f}% - reducing to 1 FPS")
            else:
                if self.is_emergency_throttled:
                    # Restore normal FPS
                    self.is_emergency_throttled = False
                    target_fps = self.settings.get('target_fps', 15)
                    if target_fps > 0:
                        interval = int(1000 / target_fps)
                    else:
                        interval = 1
                    self.timer.setInterval(interval)
                    print(f"✅ THROTTLE RELEASED: System CPU at {cpu_percent:.1f}% - restoring to {target_fps} FPS")

        except ImportError:
            # psutil not available, skip throttling
            pass
        except Exception as e:
            print(f"⚠️ Emergency throttle check error: {e}")

    def paintEvent(self, event: QPaintEvent):
        """Render Matrix effect with MAXIMUM CPU efficiency"""
        painter = QPainter(self)
        # DISABLED anti-aliasing for better performance
        # painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        painter.setFont(self.matrix_font)

        # Clear screen
        painter.fillRect(self.rect(), QColor(0, 0, 0))

        # Draw columns
        for column in self.columns:
            self.draw_column(painter, column)

        # Draw FPS and Stats if enabled
        if self.settings.get('show_stats', False):
            self.draw_fps(painter)

    def draw_column(self, painter: QPainter, column: MatrixColumn):
        """Draw a single Matrix column with MAXIMUM performance optimizations"""
        screen_height = self.height()

        # Pre-calculate time-based values once per column
        current_time = time.time()
        if self.settings['rainbow']:
            base_hue = (current_time * 100 + column.x) % 360

        # OPTIMIZATION: Further reduced max trail length (was 15, now 10)
        max_chars_to_draw = 10

        for i, (char, pos, age) in enumerate(zip(column.characters, column.char_positions, column.char_ages)):
            # OPTIMIZATION: Skip characters that are completely off-screen (expanded margin)
            if pos < -50 or pos > screen_height + 50:
                continue

            # OPTIMIZATION: Limit trail length for performance (max 10 characters)
            if i > max_chars_to_draw:
                break

            # Determine color based on position in trail
            if i == 0:  # Head character
                if self.settings['rainbow']:
                    # OPTIMIZATION: Use pre-calculated base hue
                    color = QColor.fromHsv(int(base_hue), 255, 255)
                else:
                    color = self.head_color
            else:
                # Trailing characters with fade
                if self.settings['rainbow']:
                    # OPTIMIZATION: Reduce HSV calculations - faster fade, fewer colors
                    hue = int((base_hue + i * 30) % 360)  # Larger hue steps
                    brightness = max(30, 255 - i * 25)  # Faster fade (was 12)
                    color = QColor.fromHsv(hue, 255, brightness)
                else:
                    fade_index = min(i, len(self.fade_colors) - 1)
                    color = self.fade_colors[fade_index]

            painter.setPen(color)  # OPTIMIZATION: Removed QPen wrapper
            painter.drawText(int(column.x), int(pos), char)  # OPTIMIZATION: Use ints

    def draw_fps(self, painter: QPainter):
        """Draw comprehensive system statistics including FPS, CPU, and memory metrics"""
        current_time = time.time()

        # Change stats color every 5 seconds to prevent burn-in
        if current_time - self.last_color_change >= 5.0:
            self.current_color_index = (self.current_color_index + 1) % len(self.stats_colors)
            self.last_color_change = current_time

        stats_color = self.stats_colors[self.current_color_index]

        # Calculate drifting position to prevent burn-in
        stats_x, stats_y = self.calculate_drift_position()

        painter.setPen(QPen(stats_color))
        painter.drawText(QPoint(stats_x, stats_y), f"FPS {self.fps} (Target {self.current_target_fps})")

        # Show CPU intelligence metrics if auto CPU limiting is enabled OR always show comprehensive stats
        if self.settings.get('auto_cpu_limit', False) or self.settings.get('show_stats', False):
            try:
                import psutil
                import os

                # Update stats every second
                if current_time - self.last_stats_update >= 1.0:
                    # Get current system metrics
                    cpu_percent = psutil.cpu_percent(interval=0)
                    memory = psutil.virtual_memory()

                    # Get screensaver process stats
                    process_cpu = self.current_process.cpu_percent() / psutil.cpu_count() if self.current_process else 0.0
                    process_memory_info = self.current_process.memory_info() if self.current_process else None
                    process_memory_mb = (process_memory_info.rss / 1024 / 1024) if process_memory_info else 0.0  # Convert to MB

                    # Calculate process memory percentage of total system memory
                    total_memory_gb = memory.total / 1024 / 1024 / 1024
                    process_memory_percent = (process_memory_mb / 1024) / total_memory_gb * 100

                    # Ensure cpu_percent is a number
                    if not isinstance(cpu_percent, (int, float)):
                        cpu_percent = 0.0

                    # Add to CPU samples for averaging
                    self.stats_cpu_samples.append(float(cpu_percent))

                    # Keep only last 10 samples for averaging
                    if len(self.stats_cpu_samples) > 10:
                        self.stats_cpu_samples = self.stats_cpu_samples[-10:]

                    # Calculate average CPU and store as floats for precise display
                    if self.stats_cpu_samples:
                        avg_cpu = sum(self.stats_cpu_samples) / len(self.stats_cpu_samples)
                        self.displayed_cpu = avg_cpu  # Keep as float for 2 decimal precision

                    self.displayed_memory = int(memory.percent)
                    self.displayed_process_cpu = process_cpu  # Keep as float for 2 decimal precision
                    self.displayed_process_memory = process_memory_mb
                    self.last_stats_update = current_time

                # Use the cycling color for all stats text
                painter.setPen(QPen(stats_color))

                # Format CPU percentages with 2 decimal places, show "<1%" if 0.00
                total_cpu_text = f"{self.displayed_cpu:.1f}%"
                screensaver_cpu_text = f"{self.displayed_process_cpu:.1f}%"

                painter.drawText(QPoint(stats_x, stats_y + self.stats_line_height), f"CPU Total {total_cpu_text} Screensaver {screensaver_cpu_text}")
                painter.drawText(QPoint(stats_x, stats_y + 2 * self.stats_line_height), f"Memory Total {self.displayed_memory}% Screensaver {self.displayed_process_memory:.1f}MB")

            except ImportError:
                painter.setPen(QPen(stats_color))
                painter.drawText(QPoint(stats_x, stats_y + self.stats_line_height), "CPU Intelligence psutil not available")

    def calculate_drift_position(self):
        """Calculate current stats position based on slow drift around screen edges"""
        # Check if drift is enabled (default to True for backwards compatibility)
        if not hasattr(self, 'settings') or not self.settings.get('stats_drift', True):
            # Return fixed position if drift is disabled
            return 10, 30

        current_time = time.time()
        elapsed = current_time - self.stats_drift_start_time

        # Get screen dimensions
        screen_width = self.width()
        screen_height = self.height()

        # Calculate progress through the drift cycle (0.0 to 1.0)
        cycle_progress = (elapsed % self.drift_cycle_duration) / self.drift_cycle_duration

        # Calculate which edge and progress along that edge (each edge takes 25% of cycle)
        if cycle_progress < 0.25:  # Top edge (left to right)
            edge_progress = cycle_progress * 4  # 0.0 to 1.0
            x = self.drift_margin + edge_progress * (screen_width - 2 * self.drift_margin - 300)  # Leave space for text
            y = self.drift_margin
        elif cycle_progress < 0.5:  # Right edge (top to bottom)
            edge_progress = (cycle_progress - 0.25) * 4
            x = screen_width - self.drift_margin - 300  # Fixed distance from right edge
            y = self.drift_margin + edge_progress * (screen_height - 2 * self.drift_margin - 80)  # Leave space for 3 lines
        elif cycle_progress < 0.75:  # Bottom edge (right to left)
            edge_progress = (cycle_progress - 0.5) * 4
            x = screen_width - self.drift_margin - 300 - edge_progress * (screen_width - 2 * self.drift_margin - 300)
            y = screen_height - self.drift_margin - 80  # Fixed distance from bottom
        else:  # Left edge (bottom to top)
            edge_progress = (cycle_progress - 0.75) * 4
            x = self.drift_margin
            y = screen_height - self.drift_margin - 80 - edge_progress * (screen_height - 2 * self.drift_margin - 80)

        return int(x), int(y)

    def keyPressEvent(self, event: QKeyEvent):
        """Handle key press events"""
        print(f"⌨️ Key press detected: {event.key()} - Exiting screensaver...")
        # Any key exits screensaver
        if event.key() == Qt.Key.Key_F:
            # Toggle stats display
            current_stats = self.settings.get('show_stats', False)
            self.settings['show_stats'] = not current_stats
        elif event.key() == Qt.Key.Key_Escape or event.key() == Qt.Key.Key_Q:
            self.exit_requested.emit()
        else:
            # Any other key exits screensaver
            self.exit_requested.emit()

    def event(self, event: QEvent) -> bool:
        """Override event handler to ensure all keyboard events are captured"""
        if event.type() == QEvent.Type.KeyPress:
            # Cast to QKeyEvent properly
            if isinstance(event, QKeyEvent):
                print(f"🎯 Intercepted KeyPress via event(): {event.key()}")
                self.keyPressEvent(event)
                return True
        elif event.type() == QEvent.Type.KeyRelease:
            # Also handle key release to be thorough
            if isinstance(event, QKeyEvent):
                print(f"⌨️ Key release detected via event(): {event.key()}")
                return True
        elif event.type() == QEvent.Type.FocusIn:
            print("🎯 Matrix widget gained focus via event()")
        elif event.type() == QEvent.Type.FocusOut:
            print("🎯 Matrix widget lost focus via event()")

        # Call parent event handler for all other events
        return super().event(event)

    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press events"""
        print(f"🖱️ Mouse press detected: {event.button()} - Exiting screensaver...")
        self.exit_requested.emit()

    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle mouse movement events"""
        if self.last_mouse_pos is None:
            self.last_mouse_pos = event.position().toPoint()
            return

        # Check if mouse moved significantly
        current_pos = event.position().toPoint()
        dx = abs(current_pos.x() - self.last_mouse_pos.x())
        dy = abs(current_pos.y() - self.last_mouse_pos.y())

        if dx > 5 or dy > 5:  # 5 pixel threshold to avoid minor jitter
            print(f"🖱️ Mouse movement detected: dx={dx}, dy={dy} - Exiting screensaver...")
            self.exit_requested.emit()

    def focusInEvent(self, event):
        """Handle focus gained events"""
        print("🎯 Matrix widget gained focus")
        super().focusInEvent(event)

    def focusOutEvent(self, event):
        """Handle focus lost events"""
        print("🎯 Matrix widget lost focus")
        super().focusOutEvent(event)

    def closeEvent(self, event):
        """Handle widget close events - restore desktop environment"""
        print("🔚 Matrix widget closing - restoring desktop...")
        self.restore_desktop_environment()
        super().closeEvent(event)

    def restore_desktop_environment(self):
        """Restore taskbar and desktop environment after screensaver"""
        try:
            import subprocess
            import os
            print("🖥️ Restoring desktop environment...")

            # Detect display server type
            is_wayland = os.environ.get('WAYLAND_DISPLAY') is not None
            is_x11 = os.environ.get('DISPLAY') is not None

            if is_wayland:
                print("🌊 Detected Wayland display server")
            elif is_x11:
                print("🖼️ Detected X11 display server")

            # Try using quiet taskbar restoration first
            quiet_script_path = os.path.join(os.path.dirname(__file__), 'restore_taskbar_quiet.sh')
            if os.path.exists(quiet_script_path):
                try:
                    subprocess.run([quiet_script_path], timeout=3, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    print("✅ Taskbar restored quietly")
                    return
                except (subprocess.TimeoutExpired, subprocess.SubprocessError):
                    pass

            # Fallback: Try dedicated restoration script
            script_path = os.path.join(os.path.dirname(__file__), 'restore_desktop.sh')
            if os.path.exists(script_path):
                try:
                    subprocess.run([script_path], timeout=5, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    print("✅ Desktop restored using restoration script")
                    return
                except (subprocess.TimeoutExpired, subprocess.SubprocessError):
                    pass

            # Final fallback: Manual restoration with warning suppression
            try:
                # Kill existing panel
                subprocess.run(["pkill", "-f", "lxpanel"], timeout=2, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                # Start panel quietly
                env = os.environ.copy()
                if is_wayland:
                    env['GDK_BACKEND'] = 'wayland'

                # Use nohup to suppress all output and warnings
                subprocess.Popen(["nohup", "lxpanel"], env=env,
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                print("✅ Panel restarted quietly")
            except (subprocess.TimeoutExpired, subprocess.SubprocessError) as e:
                print(f"⚠️ Panel restart warning: {e}")

            # Check if desktop manager is running before starting it
            try:
                result = subprocess.run(["pgrep", "-f", "pcmanfm.*desktop"],
                                      capture_output=True, timeout=2)
                if result.returncode != 0:  # Not running
                    env = os.environ.copy()
                    if is_wayland:
                        env['GDK_BACKEND'] = 'wayland'

                    subprocess.Popen(["nohup", "pcmanfm", "--desktop"], env=env,
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    print("✅ Desktop manager started quietly")
                else:
                    print("✅ Desktop manager already running - background preserved")
            except (subprocess.TimeoutExpired, subprocess.SubprocessError):
                pass

            print("✅ Desktop environment restoration completed")

        except Exception as e:
            print(f"⚠️ Desktop restoration warning: {e}")
            # Don't fail the screensaver exit if desktop restoration fails

    def check_usb_activity(self):
        """Monitor USB interrupts for physical device activity (mouse/keyboard)"""
        try:
            current_time = time.time()

            # Read USB/HID interrupt data from /proc/interrupts
            with open('/proc/interrupts', 'r', encoding='utf-8') as f:
                content = f.read()

            usb_interrupts = 0
            hid_interrupts = 0

            # Look for ALL USB/HID related interrupts
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
            if self.usb_interrupt_baseline is None:
                self.usb_interrupt_baseline = total_interrupts
                print(f"🔌 USB activity monitoring started - baseline: {total_interrupts}")
                return

            # Detect ANY change in interrupts (USB device activity)
            interrupt_diff = total_interrupts - self.usb_interrupt_baseline

            if interrupt_diff > 0:  # USB activity detected!
                print(f"🔌 USB activity detected! +{interrupt_diff} interrupts - Exiting screensaver...")
                # Update baseline
                self.usb_interrupt_baseline = total_interrupts
                # Exit screensaver immediately
                self.exit_requested.emit()
            else:
                # Update baseline for next check
                self.usb_interrupt_baseline = total_interrupts

        except Exception as e:
            # If we can't read interrupts, fall back to timer-based check
            elapsed = current_time - self.last_usb_check
            if elapsed > 5:  # Show error every 5 seconds
                print(f"⚠️ USB monitoring error: {e}")
                self.last_usb_check = current_time

class MatrixScreensaver(QMainWindow):
    """Fullscreen Matrix screensaver window"""

    def __init__(self, settings: Optional[dict] = None, standalone_mode: bool = False):
        super().__init__()

        # Store standalone mode flag
        self.standalone_mode = standalone_mode

        # Get screen geometry for proper sizing
        from PyQt6.QtWidgets import QApplication
        screen = QApplication.primaryScreen()
        if screen:
            screen_geometry = screen.geometry()
            self.setGeometry(screen_geometry)

        # Window setup - ensure it covers taskbar and stays on top
        self.setWindowTitle("Matrix Digital Rain Screensaver")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint |
                           Qt.WindowType.WindowStaysOnTopHint |
                           Qt.WindowType.Tool |
                           Qt.WindowType.BypassWindowManagerHint)

        # Set window state to fullscreen and maximize
        self.setWindowState(Qt.WindowState.WindowFullScreen | Qt.WindowState.WindowMaximized)

        # Set window attributes to ensure it covers everything
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, False)
        self.setAttribute(Qt.WidgetAttribute.WA_X11NetWmWindowTypeDesktop, True)

        # Create Matrix widget
        self.matrix_widget = MatrixWidget()
        if settings:
            self.matrix_widget.update_settings(settings)

        # Connect exit signal
        self.matrix_widget.exit_requested.connect(self.close_screensaver)

        # Set as central widget
        self.setCentralWidget(self.matrix_widget)

        # Make fullscreen and ensure it's maximized
        self.showFullScreen()
        self.showMaximized()

        # Ensure the Matrix widget grabs mouse and keyboard input
        # Set focus first, then grab input
        self.matrix_widget.setFocus(Qt.FocusReason.OtherFocusReason)

        # Use a small delay to ensure focus is properly set before grabbing
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(50, self.grab_input)

        # Force window to fill screen properly after a short delay
        QTimer.singleShot(100, self.ensure_fullscreen)

    def grab_input(self):
        """Grab keyboard and mouse input after focus is established"""
        try:
            self.matrix_widget.grabKeyboard()
            self.matrix_widget.grabMouse()
            print("Input grabbing successful")
        except Exception as e:
            print(f"Warning: Could not grab input: {e}")

    def ensure_fullscreen(self):
        """Ensure the window is properly fullscreen and covers taskbar"""

        # Force window to take full screen including taskbar area
        screen = QApplication.primaryScreen()
        if screen:
            # Get the full screen geometry (not available geometry)
            screen_geometry = screen.geometry()
            print(f"Screen geometry: {screen_geometry.width()}x{screen_geometry.height()}")

            # Force geometry to cover entire screen including taskbar
            self.setGeometry(0, 0, screen_geometry.width(), screen_geometry.height())

            # Also try using availableGeometry to compare
            available_geometry = screen.availableGeometry()
            print(f"Available geometry: {available_geometry.width()}x{available_geometry.height()}")

            # Use the larger of the two to ensure we cover everything
            max_width = max(screen_geometry.width(), available_geometry.width())
            max_height = max(screen_geometry.height(), available_geometry.height())
            self.setGeometry(0, 0, max_width, max_height)

        # Multiple approaches to ensure fullscreen over taskbar
        self.setWindowState(Qt.WindowState.WindowFullScreen | Qt.WindowState.WindowMaximized)

        # Force the window to stay on top and cover everything
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        self.showFullScreen()
        self.showMaximized()
        self.activateWindow()
        self.raise_()

        # Additional system-level approaches to ensure taskbar coverage
        self.hide_taskbar_and_maximize()

        # Ensure the matrix widget also takes full size
        self.matrix_widget.resize(self.size())

        # Set focus first, then grab input with proper timing
        self.matrix_widget.setFocus(Qt.FocusReason.OtherFocusReason)

        # Use a small delay to ensure focus is properly set before grabbing
        QTimer.singleShot(50, self.grab_input_delayed)

        print(f"Window size after fullscreen: {self.width()}x{self.height()}")
        print(f"Matrix widget size: {self.matrix_widget.width()}x{self.matrix_widget.height()}")
        print("🎯 Input grab scheduled - mouse and keyboard events should be captured")

    def grab_input_delayed(self):
        """Delayed input grabbing for the secondary fullscreen setup"""
        try:
            self.matrix_widget.grabKeyboard()
            self.matrix_widget.grabMouse()
            print("🎯 Delayed input grabbing successful")
        except Exception as e:
            print(f"Warning: Could not grab input (delayed): {e}")
        print("📺 Window should now cover taskbar completely")

    def hide_taskbar_and_maximize(self):
        """Use system-specific methods to ensure taskbar is covered"""
        import subprocess
        import os

        try:
            # Method 1: Try to set window properties using xprop (X11)
            window_id = int(self.winId())
            subprocess.run(['xprop', '-id', str(window_id), '-set', '_NET_WM_STATE',
                          '_NET_WM_STATE_FULLSCREEN'],
                          check=False, capture_output=True, timeout=2)

            # Method 2: Try wmctrl to maximize and remove decorations
            subprocess.run(['wmctrl', '-r', 'Matrix Digital Rain Screensaver', '-b', 'add,fullscreen'],
                          check=False, capture_output=True, timeout=2)

            # Method 3: Try xdotool approach
            subprocess.run(['xdotool', 'search', '--name', 'Matrix Digital Rain Screensaver',
                          'windowstate', '--add', 'FULLSCREEN'],
                          check=False, capture_output=True, timeout=2)

            print("🔧 Applied system-level fullscreen hints")

        except Exception as e:
            print(f"⚠️ System-level fullscreen setup failed (this is usually fine): {e}")

    def close_screensaver(self):
        """Close the screensaver window"""
        # Stop USB monitoring timer
        if hasattr(self.matrix_widget, 'usb_monitor_timer'):
            self.matrix_widget.usb_monitor_timer.stop()
            print("🔌 USB monitoring stopped")

        # Release keyboard and mouse grabs before closing
        if hasattr(self.matrix_widget, 'grabKeyboard'):
            try:
                self.matrix_widget.releaseKeyboard()
                self.matrix_widget.releaseMouse()
            except Exception as e:
                print(f"Warning: Could not release input grabs: {e}")

        # Restore desktop environment and taskbar (handled by widget's closeEvent)
        print("🖥️ Initiating desktop restoration...")

        if self.standalone_mode:
            # In standalone mode, exit the entire application
            from PyQt6.QtWidgets import QApplication
            QApplication.quit()
        else:
            # In test mode, just close the window
            self.close()

def load_saved_settings():
    """Load ALL persistent settings from configuration file"""
    import json
    from pathlib import Path

    # Default settings - matching screensaver_preferences.py defaults
    settings = {
        'enabled': True,
        'effect': 'matrix',
        'matrix_mode': True,
        'color': 'green',
        'speed': 25,
        'bold_text': True,
        'bold': True,  # Alias for backward compatibility
        'rainbow_mode': False,
        'rainbow': False,  # Alias for backward compatibility
        'font_size': 14,
        'show_fps': False,
        'show_stats': False,
        'stats_drift': True,
        'use_katakana': True,
        'target_fps': 15,
        'auto_cpu_limit': False,
        'async_scroll': True,
        'display_target': 'both',
        'physical_only': True,
        'lock_timeout': 300,
        'display_timeout': 600,
        'start_on_boot': False,
        'show_taskbar_icon': True,
        'start_maximized': False,
        'dark_mode': True,
        'auto_shutdown': False,
        'shutdown_timeout': 60,
        'auto_update_check': True,
        'screensaver_type': 'Matrix',
        'mystify_mode': False,
        'slideshow_mode': False,
        'video_mode': False
    }

    # Try to load from config file
    config_dir = Path.home() / '.config' / 'screensaver'
    config_file = config_dir / 'settings.json'

    if config_file.exists():
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                saved_settings = json.load(f)
                # Merge saved settings with defaults (saved settings take priority)
                settings.update(saved_settings)
            print(f"✅ Loaded ALL persistent settings from {config_file}")
            print(f"   Screensaver Type: {settings.get('screensaver_type', 'Matrix')}")
            print(f"   Color: {settings.get('color')}, Speed: {settings.get('speed')}, "
                  f"FPS: {settings.get('target_fps')}, Stats: {settings.get('show_stats')}")
            print(f"   Rainbow: {settings.get('rainbow_mode')}, Bold: {settings.get('bold_text')}, "
                  f"Katakana: {settings.get('use_katakana')}")
            print(f"   CPU Limit: {settings.get('auto_cpu_limit')}, Stats Drift: {settings.get('stats_drift')}")
        except Exception as e:
            print(f"⚠️ Error loading settings from {config_file}: {e}")
            print("   Using default settings instead")
    else:
        print(f"ℹ️ No config file found at {config_file}, using defaults")

    return settings

def main():
    """Run Matrix screensaver in standalone mode"""
    app = QApplication(sys.argv)

    # Load persistent settings from config file
    settings = load_saved_settings()

    # Create and show screensaver in standalone mode
    screensaver = MatrixScreensaver(settings, standalone_mode=True)
    screensaver.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
