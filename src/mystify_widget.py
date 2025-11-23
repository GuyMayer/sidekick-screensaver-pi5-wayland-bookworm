#!/usr/bin/env python3
"""
Windows Mystify Screensaver - Geometric Patterns with Trails
A PyQt6 implementation of the classic Windows Mystify screensaver
featuring flowing geometric shapes with customizable trails and colors.
"""

import random
import sys
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import QTimer, Qt, pyqtSignal, QPointF
from PyQt6.QtGui import QPainter, QPen, QColor, QPainterPath

import time

# Setup debug logging
def setup_debug_logging() -> logging.Logger:
    """Setup debug logging to mystify_debug.log"""
    log_file = Path.home() / "mystify_debug.log"

    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler(log_file, mode='w'),  # Overwrite each run
            logging.StreamHandler(sys.stdout)  # Also print to console
        ]
    )

    logger = logging.getLogger('mystify')
    logger.info(f"=== MYSTIFY DEBUG SESSION STARTED ===")
    logger.info(f"Log file: {log_file}")
    return logger

# Initialize debug logger
debug_logger = setup_debug_logging()

class MystifyWidget(QWidget):
    """Mystify screensaver with flowing geometric patterns and trails"""

    exit_requested = pyqtSignal()

    def __init__(self, settings=None):
        super().__init__()
        self.settings = settings or {}

        # Debug logging
        debug_logger.info("=== MYSTIFY WIDGET INITIALIZATION ===")
        debug_logger.info(f"Settings received: {self.settings}")

        # Mystify-specific settings
        self.num_shapes = self.settings.get('mystify_shapes', 3)  # Number of geometric shapes
        self.trail_length = self.settings.get('mystify_trail_length', 50)  # Length of trailing effect
        self.shape_complexity = self.settings.get('mystify_complexity', 6)  # Points per shape (3-12)
        self.speed = self.settings.get('mystify_speed', 2)  # Movement speed
        self.color_mode = self.settings.get('mystify_color_mode', 'rainbow')  # 'rainbow', 'single', 'duo'

        debug_logger.info(f"Mystify config - shapes: {self.num_shapes}, trail: {self.trail_length}, complexity: {self.shape_complexity}, speed: {self.speed}, color_mode: {self.color_mode}")

        # Stats display settings
        self.show_stats = self.settings.get('show_stats', False)

        debug_logger.info(f"Display settings - show_stats: {self.show_stats}")        # Color settings
        self.primary_color = QColor(120, 200, 255)  # Default blue
        self.secondary_color = QColor(255, 120, 200)  # Default pink

        # Shape data storage
        self.shapes = []
        self.shape_trails = []  # Store previous positions for trailing effect

        # Initialize shapes
        self.init_shapes()

        # Setup window
        self.setup_window()

        # Animation timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_animation)

        # Get FPS from settings - check both 'fps' and 'target_fps' for compatibility
        fps = self.settings.get('fps', self.settings.get('target_fps', 30))
        if fps == 0:  # Unlimited FPS
            fps = 60  # Cap at 60 for performance
        self.timer.start(1000 // fps)

        debug_logger.info(f"Animation timer started - FPS: {fps}, interval: {1000 // fps}ms")

        # USB Activity Monitoring Timer for physical input detection
        self.usb_monitor_timer = QTimer()
        self.usb_monitor_timer.timeout.connect(self.check_usb_activity)
        self.usb_interrupt_baseline = None
        self.last_usb_check = time.time()
        self.screensaver_start_time = time.time()  # Track when screensaver started

        # Start USB monitoring every 2 seconds (less frequent to avoid false positives)
        # and only after the screensaver has been running for at least 5 seconds
        # Disable USB monitoring if show_stats is enabled (likely test mode)
        if not self.show_stats:
            self.usb_monitor_timer.start(2000)
            debug_logger.info("USB monitoring timer started (2000ms interval)")
        else:
            debug_logger.info("USB monitoring disabled in test mode (show_stats=True)")
            print("🔌 USB monitoring disabled in test mode (show_stats=True)")

        # Performance tracking
        self.last_update = time.time()
        self.frame_count = 0
        self.fps = 0
        self.last_fps_update = time.time()

        # Stats display
        self.displayed_cpu = 0.0  # Initialize as float for 2 decimal precision
        self.displayed_memory = 0
        self.displayed_process_cpu = 0.0  # Initialize as float for 2 decimal precision
        self.displayed_process_memory = 0.0
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
        self.stats_cpu_samples = []

        # Performance optimization settings
        self.max_fps = 60  # Cap at 60 FPS for efficiency
        self.min_fps = 15  # Never go below 15 FPS
        self.frame_times: List[float] = []
        self.performance_check_interval = 5.0  # Check every 5 seconds
        self.last_performance_check = time.time()
        self.cpu_threshold = 40.0  # If CPU > 40%, reduce FPS
        self.memory_threshold = 70.0  # If Memory > 70%, reduce quality

        # Emergency CPU throttling (NEW)
        self.emergency_cpu_threshold = 90.0  # If system CPU > 90%, throttle to 1 FPS
        self.is_emergency_throttled = False
        self.last_emergency_check = time.time()
        self.emergency_check_interval = 2.0  # Check every 2 seconds

        # Quality settings for performance scaling
        self.quality_level = 1.0  # 1.0 = full quality, 0.5 = half quality
        self.adaptive_quality = True

        # Rendering optimizations
        self.skip_frame_counter = 0
        self.frame_skip_ratio = 1  # Skip every Nth frame when needed
        self.shape_update_batch_size = 1  # Update shapes in batches

        # Color cycling for stats to prevent burn-in
        self.current_color_index = 0
        self.last_color_change = time.time()
        self.stats_colors = [
            QColor(0, 255, 0),    # Green
            QColor(0, 255, 255),  # Cyan
            QColor(255, 255, 0),  # Yellow
            QColor(255, 128, 0),  # Orange
            QColor(255, 0, 255),  # Magenta
            QColor(128, 255, 128) # Light green
        ]

        # Stats position drift to prevent burn-in
        self.stats_drift_start_time = time.time()
        self.stats_base_x = 10  # Base position
        self.stats_base_y = 30  # Base position for first line
        self.stats_line_height = 20  # Height between stats lines
        self.drift_cycle_duration = 8 * 60  # 8 minutes total (2 min per edge)
        self.drift_margin = 50  # Stay this far from edges

    def setup_window(self):
        """Setup the mystify window"""
        self.setWindowTitle("Mystify Screensaver")
        self.setStyleSheet("background-color: black;")

        # Fullscreen setup
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.showFullScreen()
        self.setCursor(Qt.CursorShape.BlankCursor)

    def init_shapes(self):
        """Initialize geometric shapes with random properties - using curves instead of polygons"""
        screen_geometry = QApplication.primaryScreen().geometry()
        width = screen_geometry.width()
        height = screen_geometry.height()

        self.shapes = []
        self.shape_trails = []

        for i in range(self.num_shapes):
            shape = {
                'control_points': [],      # Main control points for the curve
                'velocities': [],          # Velocities for each control point
                'control_velocities': [],  # Velocities for curve control handles
                'color_hue': random.randint(0, 360),
                'color_shift': random.uniform(0.5, 2.0),
                'size_factor': random.uniform(0.1, 0.3),
                'curve_tension': random.uniform(0.3, 0.8)  # How "curvy" the shape is
            }

            # Create control points for smooth curves (reduced number for smoother curves)
            num_control_points = max(3, self.shape_complexity // 2)  # Fewer points = smoother curves
            for j in range(num_control_points):
                # Random starting position
                x = random.randint(100, width - 100)
                y = random.randint(100, height - 100)
                shape['control_points'].append(QPointF(x, y))

                # Random velocity for each control point
                vx = random.uniform(-self.speed, self.speed)
                vy = random.uniform(-self.speed, self.speed)
                shape['velocities'].append(QPointF(vx, vy))

                # Control handle velocities for curve deformation
                cvx = random.uniform(-self.speed * 0.5, self.speed * 0.5)
                cvy = random.uniform(-self.speed * 0.5, self.speed * 0.5)
                shape['control_velocities'].append(QPointF(cvx, cvy))

            self.shapes.append(shape)
            self.shape_trails.append([])  # Initialize empty trail

    def create_smooth_curve(self, control_points: List[QPointF], tension: float) -> QPainterPath:
        """Create a smooth closed curve using cubic Bézier curves"""
        if len(control_points) < 3:
            # Fallback to simple path for too few points
            path = QPainterPath()
            if control_points:
                path.moveTo(control_points[0])
                for point in control_points[1:]:
                    path.lineTo(point)
                path.closeSubpath()
            return path

        path = QPainterPath()

        # Start at the first control point
        path.moveTo(control_points[0])

        # Create smooth curves between control points
        for i in range(len(control_points)):
            current = control_points[i]
            next_point = control_points[(i + 1) % len(control_points)]

            # Calculate control handles for smooth curves
            prev_point = control_points[i - 1] if i > 0 else control_points[-1]
            next_next = control_points[(i + 2) % len(control_points)]

            # Create control handles using tension
            handle1_x = current.x() + (next_point.x() - prev_point.x()) * tension * 0.25
            handle1_y = current.y() + (next_point.y() - prev_point.y()) * tension * 0.25

            handle2_x = next_point.x() - (next_next.x() - current.x()) * tension * 0.25
            handle2_y = next_point.y() - (next_next.y() - current.y()) * tension * 0.25

            # Add cubic Bézier curve
            path.cubicTo(
                QPointF(handle1_x, handle1_y),
                QPointF(handle2_x, handle2_y),
                next_point
            )

        path.closeSubpath()
        return path

    def _update_debug_info(self, current_time: float, delta_time: float) -> None:
        """Handle debug printing and logging"""
        # Debug: Print every 5 seconds to check if animation is still running
        if hasattr(self, '_last_debug_print'):
            if current_time - self._last_debug_print >= 5.0:
                debug_msg = f"🎯 Mystify animation running - Frame {self.frame_count}, Quality: {self.quality_level:.2f}, Shapes: {len(self.shapes)}"
                print(debug_msg)
                debug_logger.info(debug_msg)
                debug_logger.info(f"Timer status - animation timer active: {self.timer.isActive()}, USB timer active: {self.usb_monitor_timer.isActive()}")
                debug_logger.info(f"Performance - delta_time: {delta_time:.4f}s, skip_ratio: {self.frame_skip_ratio}")
                self._last_debug_print = current_time
        else:
            self._last_debug_print = current_time
            debug_logger.info("First animation update - debug printing initialized")

    def _apply_performance_optimizations(self, current_time: float) -> bool:
        """Apply performance optimizations and return True if frame should be skipped"""
        # POWER SAVING: Apply aggressive optimizations for efficiency
        power_saving = self.settings.get('power_saving_mode', False)
        if power_saving:
            # Reduce update frequency by 50%
            if self.frame_count % 2 != 0:
                return True
            # Force lower quality
            self.quality_level = min(0.6, self.quality_level)

        # ENERGY EFFICIENT: Apply general efficiency optimizations
        energy_efficient = self.settings.get('energy_efficient', True)
        if energy_efficient:
            # Reduce unnecessary updates when not much is changing
            if self.frame_count % 5 == 0:  # Every 5th frame, check if we can skip updates
                if hasattr(self, '_last_activity_check'):
                    time_since_activity = current_time - self._last_activity_check
                    if time_since_activity > 30:  # After 30 seconds of no activity, reduce further
                        self.quality_level = min(0.7, self.quality_level)
                else:
                    self._last_activity_check = current_time
        return False

    def _update_stats_display(self, current_time: float) -> None:
        """Update performance statistics if enabled"""
        if not self.show_stats:
            return

        try:
            import psutil
            import os

            # Update stats every second
            if current_time - self.last_stats_update >= 1.0:
                # Get current system metrics
                cpu_percent = psutil.cpu_percent(interval=0)
                memory = psutil.virtual_memory()

                # Get process-specific stats
                try:
                    process_cpu = self.current_process.cpu_percent() / psutil.cpu_count() if self.current_process else 0.0
                    process_memory_info = self.current_process.memory_info() if self.current_process else None
                    process_memory_mb = (process_memory_info.rss / (1024 * 1024)) if process_memory_info else 0.0  # Convert to MB
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    process_cpu = 0.0
                    process_memory_mb = 0.0

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

        except ImportError:
            pass  # psutil not available

    def _update_shape_animations(self, current_time: float) -> None:
        """Update all shape positions and trails"""
        screen_geometry = QApplication.primaryScreen().geometry()
        width = screen_geometry.width()
        height = screen_geometry.height()

        # PERFORMANCE: Update shapes in batches based on quality level (but ensure all get updated)
        shapes_per_frame = len(self.shapes)  # Always update all shapes to prevent vanishing
        start_idx = self.frame_count % len(self.shapes)

        # Debug: Check if shapes are being processed
        if self.frame_count % 150 == 0:  # Every 5 seconds at 30fps
            print(f"🔍 Mystify details - Shapes per frame: {shapes_per_frame}, Quality: {self.quality_level:.3f}, Total shapes: {len(self.shapes)}")

        for idx in range(shapes_per_frame):
            i = (start_idx + idx) % len(self.shapes)
            shape = self.shapes[i]

            # Store current curve in trail (reduced frequency at low quality)
            if self.quality_level > 0.7 or self.frame_count % 2 == 0:
                current_curve = self.create_smooth_curve(shape['control_points'], shape['curve_tension'])
                self.shape_trails[i].append(current_curve)

                # Limit trail length (maintain minimum trail to prevent vanishing)
                min_trail = max(5, self.trail_length // 4)  # Always keep at least 25% of trail
                max_trail = max(min_trail, int(self.trail_length * self.quality_level))
                if len(self.shape_trails[i]) > max_trail:
                    self.shape_trails[i].pop(0)

            # Update each control point position (with performance scaling)
            speed_multiplier = self.quality_level if self.quality_level > 0.5 else 0.5

            for j, point in enumerate(shape['control_points']):
                velocity = shape['velocities'][j]

                # Update position with speed scaling
                new_x = point.x() + velocity.x() * speed_multiplier
                new_y = point.y() + velocity.y() * speed_multiplier

                # Bounce off screen edges
                if new_x <= 0 or new_x >= width:
                    velocity.setX(-velocity.x())
                    new_x = max(0, min(width, new_x))

                if new_y <= 0 or new_y >= height:
                    velocity.setY(-velocity.y())
                    new_y = max(0, min(height, new_y))

                shape['control_points'][j] = QPointF(new_x, new_y)
                shape['velocities'][j] = velocity

            # Gradually evolve curve tension for organic movement
            shape['curve_tension'] += random.uniform(-0.01, 0.01)
            shape['curve_tension'] = max(0.2, min(1.0, shape['curve_tension']))

            # Update color (less frequently at low quality)
            if self.quality_level > 0.7 or self.frame_count % 3 == 0:
                shape['color_hue'] = (shape['color_hue'] + shape['color_shift']) % 360

    def _update_performance_tracking(self, current_time: float) -> None:
        """Update FPS and performance tracking"""
        # Performance tracking
        self.frame_count += 1

        # Calculate FPS every second
        if current_time - self.last_fps_update >= 1.0:
            self.fps = self.frame_count
            self.frame_count = 0
            self.last_fps_update = current_time

    def update_animation(self):
        """Update shape positions and trails with performance optimizations"""
        current_time = time.time()
        delta_time = current_time - self.last_update
        self.last_update = current_time

        # EMERGENCY CPU THROTTLING: Check system CPU every 2 seconds
        if current_time - self.last_emergency_check >= self.emergency_check_interval:
            self.last_emergency_check = current_time
            self.check_emergency_cpu_throttle()

        # Handle debug information
        self._update_debug_info(current_time, delta_time)

        # PERFORMANCE: Frame skipping DISABLED for smooth animation
        self.skip_frame_counter += 1
        # Frame skipping disabled - always render every frame

        # PERFORMANCE: Track frame timing for adaptive quality
        self.frame_times.append(delta_time)
        if len(self.frame_times) > 60:  # Keep last 60 frames
            self.frame_times.pop(0)

        # PERFORMANCE: Adaptive quality and FPS monitoring
        if current_time - self.last_performance_check >= self.performance_check_interval:
            self.adaptive_performance_adjustment()
            self.last_performance_check = current_time

        # Apply performance optimizations and check if frame should be skipped
        if self._apply_performance_optimizations(current_time):
            return

        # Update stats display
        self._update_stats_display(current_time)

        # Update shape animations
        self._update_shape_animations(current_time)

        # Update display
        self.update()

        # Update performance tracking
        self._update_performance_tracking(current_time)

    def check_emergency_cpu_throttle(self):
        """Check system CPU and throttle to 1 FPS if over 90%"""
        try:
            import psutil

            # Get current system CPU usage
            cpu_percent = psutil.cpu_percent(interval=0)

            # Ensure it's a number
            if isinstance(cpu_percent, list):
                cpu_percent = sum(cpu_percent) / len(cpu_percent) if cpu_percent else 0.0
            elif not isinstance(cpu_percent, (int, float)):
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
                    fps = self.settings.get('fps', self.settings.get('target_fps', 30))
                    if fps == 0:
                        fps = 60
                    interval = 1000 // fps
                    self.timer.setInterval(interval)
                    print(f"✅ THROTTLE RELEASED: System CPU at {cpu_percent:.1f}% - restoring to {fps} FPS")

        except ImportError:
            # psutil not available, skip throttling
            pass
        except Exception as e:
            print(f"⚠️ Emergency throttle check error: {e}")

    def adaptive_performance_adjustment(self):
        """Adjust performance settings based on system load"""
        print(f"🔧 Performance check - Current quality: {self.quality_level:.3f}")

        try:
            import psutil

            # Get current system metrics with non-blocking call
            cpu_percent = psutil.cpu_percent(interval=0)  # Non-blocking call
            memory_percent = psutil.virtual_memory().percent

            print(f"📊 System metrics - CPU: {cpu_percent}%, Memory: {memory_percent}%")

            # Ensure cpu_percent is a number
            if isinstance(cpu_percent, list):
                cpu_percent = sum(cpu_percent) / len(cpu_percent) if cpu_percent else 0.0
            elif not isinstance(cpu_percent, (int, float)):
                cpu_percent = 0.0

            # Calculate average frame time
            if self.frame_times:
                avg_frame_time = sum(self.frame_times) / len(self.frame_times)
                target_frame_time = 1.0 / 30.0  # Target 30 FPS

                # If frames are taking too long, reduce quality more gently
                if avg_frame_time > target_frame_time * 2.0:  # More lenient threshold
                    old_quality = self.quality_level
                    self.quality_level = max(0.5, self.quality_level - 0.05)  # Smaller reduction
                    # FRAME SKIPPING DISABLED - keep ratio at 1
                    # self.frame_skip_ratio = min(2, self.frame_skip_ratio + 1)
                    debug_logger.warning(f"⬇️ Reducing quality from {old_quality:.3f} to {self.quality_level:.3f} (slow frames, NO frame skip)")
                    print(f"⬇️ Reducing quality from {old_quality:.3f} to {self.quality_level:.3f} (slow frames, NO frame skip)")
                elif avg_frame_time < target_frame_time * 0.8:
                    old_quality = self.quality_level
                    self.quality_level = min(1.0, self.quality_level + 0.05)
                    # FRAME SKIPPING DISABLED - keep ratio at 1
                    # self.frame_skip_ratio = max(1, self.frame_skip_ratio - 1)
                    print(f"⬆️ Increasing quality from {old_quality:.3f} to {self.quality_level:.3f} (fast frames, NO frame skip)")

            # Adjust based on CPU usage
            if float(cpu_percent) > self.cpu_threshold:
                old_quality = self.quality_level
                self.quality_level = max(0.3, self.quality_level - 0.1)
                # FRAME SKIPPING DISABLED - keep ratio at 1
                # self.frame_skip_ratio = min(3, self.frame_skip_ratio + 1)
                print(f"🔥 CPU high ({cpu_percent}%) - reducing quality from {old_quality:.3f} to {self.quality_level:.3f} (NO frame skip)")
                # Instead of removing shapes, reduce trail frequency and complexity
                if float(cpu_percent) > 70:
                    # Reduce trail update frequency instead of removing shapes
                    self.frame_skip_ratio = min(4, self.frame_skip_ratio + 1)
                    print(f"🔥 CPU very high - increasing frame skip to {self.frame_skip_ratio} (shapes preserved)")

            # Adjust based on memory usage
            if memory_percent > self.memory_threshold:
                old_quality = self.quality_level
                self.quality_level = max(0.3, self.quality_level - 0.1)
                print(f"💾 Memory high ({memory_percent}%) - reducing quality from {old_quality:.3f} to {self.quality_level:.3f}")
                # Reduce trail length if memory is high
                if memory_percent > 85:
                    old_trail = self.trail_length
                    self.trail_length = max(10, int(self.trail_length * 0.8))
                    print(f"💾 Memory very high - reduced trail from {old_trail} to {self.trail_length}")

        except ImportError:
            print("⚠️ psutil not available - skipping performance monitoring")
            pass  # psutil not available

    def paintEvent(self, event):
        """Paint the mystify patterns with performance optimizations"""
        painter = QPainter(self)

        # PERFORMANCE: Only enable antialiasing at high quality
        if self.quality_level > 0.7:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Clear with black background
        painter.fillRect(self.rect(), QColor(0, 0, 0))

        # PERFORMANCE: Draw shapes with quality scaling (but always draw all shapes)
        shapes_to_draw = len(self.shapes)  # Always draw all shapes to prevent vanishing

        # Draw each shape's trail
        for i in range(shapes_to_draw):
            if i >= len(self.shapes):
                break

            shape = self.shapes[i]
            trail = self.shape_trails[i]

            if len(trail) < 2:
                continue

            # PERFORMANCE: Reduce trail segments at low quality (but maintain visibility)
            min_segments = max(3, len(trail) // 4)  # Always keep at least 25% of trail segments
            trail_segments = max(min_segments, int(len(trail) * self.quality_level))

            # Draw trail with fading effect
            for j in range(trail_segments):
                if j >= len(trail):
                    break

                curve_path = trail[j]
                if curve_path.isEmpty():
                    continue

                # Calculate fade factor (newer = more opaque)
                fade_factor = j / len(trail)

                # Get color based on mode
                color = self.get_shape_color(shape, fade_factor)

                # Set pen for outline
                pen_width = max(1, int(3 * fade_factor))
                pen = QPen(color, pen_width)
                pen.setCapStyle(Qt.PenCapStyle.RoundCap)
                pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
                painter.setPen(pen)

                # Draw the smooth curve
                painter.drawPath(curve_path)

                # Optional: Fill with semi-transparent color
                if self.settings.get('mystify_fill', False):
                    fill_color = QColor(color)
                    fill_color.setAlphaF(fade_factor * 0.2)  # More subtle fill for curves
                    painter.fillPath(curve_path, fill_color)

        # Display all stats together when show_stats is enabled (like matrix widget)
        if self.show_stats:
            current_time = time.time()

            # Color cycling for stats to prevent burn-in
            if current_time - self.last_color_change >= 3.0:  # Change color every 3 seconds
                self.current_color_index = (self.current_color_index + 1) % len(self.stats_colors)
                self.last_color_change = current_time

            stats_color = self.stats_colors[self.current_color_index]
            painter.setPen(QPen(stats_color))

            # Calculate drifting position to prevent burn-in
            stats_x, stats_y = self.calculate_drift_position()

            # Draw all stats together in same format as matrix widget
            target_fps = self.settings.get('target_fps', 0)
            if target_fps == 0:
                painter.drawText(stats_x, stats_y, f"FPS {self.fps:.0f} (Target Unlimited)")
            else:
                painter.drawText(stats_x, stats_y, f"FPS {self.fps:.0f} (Target {target_fps})")

            # Format CPU percentages with 2 decimal places, show "<1%" if 0.00
            total_cpu_text = f"{self.displayed_cpu:.1f}%"
            screensaver_cpu_text = f"{self.displayed_process_cpu:.1f}%"

            painter.drawText(stats_x, stats_y + self.stats_line_height, f"CPU Total {total_cpu_text} Screensaver {screensaver_cpu_text}")
            painter.drawText(stats_x, stats_y + 2 * self.stats_line_height, f"Memory Total {self.displayed_memory}% Screensaver {self.displayed_process_memory:.1f}MB")

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

    def get_shape_color(self, shape: Dict[str, Any], age_factor: float) -> QColor:
        """Get color for a shape based on mode and age."""
        base_alpha = max(50, min(255, int(255 * (1 - age_factor))))

        if self.color_mode == 'rainbow':
            color = QColor.fromHsv(int(shape['color_hue']), 255, 255, base_alpha)
        elif self.color_mode == 'single':
            # Single color with hue variation
            base_hue = int(self.primary_color.hue())
            color = QColor.fromHsv(base_hue, 255, 255, base_alpha)
        else:  # duo
            # Alternate between two colors
            if shape['color_hue'] % 60 < 30:
                color = QColor(self.primary_color)
                color.setAlpha(base_alpha)
            else:
                color = QColor(self.secondary_color)
                color.setAlpha(base_alpha)

        return color

    def keyPressEvent(self, event):
        """Handle key press events"""
        debug_logger.warning(f"Key press detected: {event.key()} - exiting screensaver")
        # Any key press exits
        self.exit_requested.emit()
        self.close()

    def mousePressEvent(self, event):
        """Handle mouse press events"""
        debug_logger.warning(f"Mouse press detected: button {event.button()} - exiting screensaver")
        # Any mouse click exits
        self.exit_requested.emit()
        self.close()

    def mouseMoveEvent(self, event):
        """Handle mouse movement"""
        debug_logger.warning(f"Mouse movement detected: ({event.position().x()}, {event.position().y()}) - exiting screensaver")
        # Mouse movement exits
        self.exit_requested.emit()
        self.close()

    def check_usb_activity(self):
        """Monitor USB interrupts for physical device activity (mouse/keyboard) - with sensitivity control"""
        try:
            current_time = time.time()

            debug_logger.debug(f"USB check triggered at {current_time:.2f}")

            # Don't monitor USB activity for the first 10 seconds to avoid false positives during startup
            time_since_start = current_time - self.screensaver_start_time
            if time_since_start < 10.0:
                debug_logger.debug(f"USB monitoring skipped - startup grace period ({time_since_start:.1f}s < 10s)")
                return

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
            debug_logger.debug(f"Interrupt counts - USB: {usb_interrupts}, HID: {hid_interrupts}, Total: {total_interrupts}")

            # Initialize baseline on first run
            if self.usb_interrupt_baseline is None:
                self.usb_interrupt_baseline = total_interrupts
                baseline_msg = f"🔌 Mystify USB activity monitoring started - baseline: {total_interrupts}"
                print(baseline_msg)
                debug_logger.info(baseline_msg)
                return

            # Use a higher threshold to avoid false positives from system activity
            # Only exit if there's significant interrupt activity (more than 50 interrupts)
            interrupt_diff = total_interrupts - self.usb_interrupt_baseline
            debug_logger.debug(f"Interrupt diff: {interrupt_diff} (threshold: 50)")

            if interrupt_diff > 50:  # Higher threshold to reduce false positives
                exit_msg = f"🔌 Mystify significant USB activity detected! +{interrupt_diff} interrupts - Exiting screensaver..."
                print(exit_msg)
                debug_logger.warning(exit_msg)
                debug_logger.info("Emitting exit_requested signal...")
                # Update baseline
                self.usb_interrupt_baseline = total_interrupts
                # Exit screensaver immediately
                self.exit_requested.emit()
            else:
                # Update baseline for next check (gradual adjustment to avoid drift)
                self.usb_interrupt_baseline = total_interrupts
                debug_logger.debug(f"USB activity below threshold - baseline updated to {total_interrupts}")

        except Exception as e:
            # If we can't read interrupts, fall back to timer-based check
            debug_logger.error(f"USB monitoring error: {e}")
            pass

class MystifyScreensaver:
    """Main mystify screensaver class"""

    def __init__(self, settings=None):
        self.settings = settings or {}
        self.mystify_widget: Optional['MystifyWidget'] = None
        self.app = None

        debug_logger.info("=== MYSTIFY SCREENSAVER CLASS INITIALIZED ===")
        debug_logger.info(f"Screensaver settings: {self.settings}")

    def show(self) -> 'MystifyWidget':
        """Show the mystify screensaver (compatible with GUI interface)"""
        debug_logger.info("MystifyScreensaver.show() called")

        if not QApplication.instance():
            self.app = QApplication(sys.argv)
            debug_logger.info("Created new QApplication instance")
        else:
            self.app = QApplication.instance()
            debug_logger.info("Using existing QApplication instance")

        debug_logger.info("Creating MystifyWidget...")
        self.mystify_widget = MystifyWidget(self.settings)
        debug_logger.info("Showing MystifyWidget...")
        self.mystify_widget.show()
        debug_logger.info("MystifyWidget shown successfully")

        return self.mystify_widget

    def close(self):
        """Close the mystify screensaver (compatible with GUI interface)"""
        debug_logger.info("MystifyScreensaver.close() called")
        if self.mystify_widget:
            self.mystify_widget.close()
            self.mystify_widget = None

    def start(self) -> Optional['MystifyWidget']:
        """Start the mystify screensaver"""
        return self.show()

    def stop(self):
        """Stop the mystify screensaver"""
        self.close()

def load_saved_settings():
    """Load ALL persistent settings from configuration file"""
    import json
    from pathlib import Path

    # Default settings for mystify - matching screensaver_preferences.py defaults
    settings = {
        'enabled': True,
        'screensaver_type': 'Mystify',
        'mystify_mode': True,
        'mystify_shapes': 3,
        'mystify_trail_length': 50,
        'mystify_trails': 8,  # Alias
        'mystify_complexity': 6,
        'mystify_speed': 2,
        'mystify_color_mode': 'rainbow',
        'mystify_fill': False,
        'mystify_color_hue': 240,
        'mystify_color_hue1': 240,
        'mystify_color_hue2': 60,
        'target_fps': 15,
        'fps': 60,  # Alias
        'show_stats': False,
        'stats_drift': True,
        'auto_cpu_limit': False,
        'display_target': 'both',
        'physical_only': True,
        'start_on_boot': False,
        'dark_mode': True
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
            print(f"✅ Loaded ALL persistent Mystify settings from {config_file}")
            print(f"   Screensaver Type: {settings.get('screensaver_type', 'Mystify')}")
            print(f"   Shapes: {settings.get('mystify_shapes')}, Trail: {settings.get('mystify_trail_length')}, "
                  f"Complexity: {settings.get('mystify_complexity')}")
            print(f"   Speed: {settings.get('mystify_speed')}, Fill: {settings.get('mystify_fill')}, "
                  f"Color Mode: {settings.get('mystify_color_mode')}")
            print(f"   FPS: {settings.get('target_fps')}, Stats: {settings.get('show_stats')}, "
                  f"CPU Limit: {settings.get('auto_cpu_limit')}")
        except Exception as e:
            print(f"⚠️ Error loading settings from {config_file}: {e}")
            print("   Using default Mystify settings instead")
    else:
        print(f"ℹ️ No config file found at {config_file}, using Mystify defaults")

    return settings

def main():
    """Main function for testing"""
    app = QApplication(sys.argv)

    # Load persistent settings from config file
    test_settings = load_saved_settings()

    screensaver = MystifyScreensaver(test_settings)
    widget = screensaver.start()

    # Run continuously until input detected - no test timer
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
