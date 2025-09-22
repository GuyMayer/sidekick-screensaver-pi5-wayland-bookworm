#!/usr/bin/env python3
"""
Slideshow Widget for Matrix Screensaver
High-performance image slideshow with configurable timing and effects
"""

import os
import sys
import time
import random
from pathlib import Path
from typing import List, Optional

from PyQt6.QtWidgets import QWidget, QLabel
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QPixmap, QPainter, QKeyEvent, QMouseEvent, QPaintEvent

class SlideshowWidget(QWidget):
    """High-performance slideshow widget"""

    # Signals
    exit_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        # Widget setup
        self.setWindowTitle("Image Slideshow")
        self.setStyleSheet("background-color: black;")
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent)
        self.setMouseTracking(True)

        # Mouse tracking for screensaver exit
        self.last_mouse_pos = None

        # Slideshow settings (will be updated from preferences)
        self.settings = {
            'slideshow_folder': '',
            'slide_duration': 5.0,  # seconds
            'slideshow_random': True,
            'slideshow_fit_mode': 'contain',  # 'contain', 'cover', 'stretch'
            'show_stats': False
        }

        # Slideshow state
        self.image_files: List[Path] = []
        self.current_image_index = 0
        self.current_pixmap: Optional[QPixmap] = None
        self.last_frame_time = time.time()
        self.frame_count = 0
        self.fps = 0

        # Timer for slide transitions
        self.slide_timer = QTimer()
        self.slide_timer.timeout.connect(self.next_slide)

        # Timer for FPS calculation
        self.fps_timer = QTimer()
        self.fps_timer.timeout.connect(self.update_fps)
        self.fps_timer.start(1000)  # Update FPS every second

        # Stats position drift to prevent burn-in
        self.stats_drift_start_time = time.time()
        self.stats_base_x = 10  # Base position
        self.stats_base_y = 30  # Base position for first line
        self.stats_line_height = 20  # Height between stats lines
        self.drift_cycle_duration = 8 * 60  # 8 minutes total (2 min per edge)
        self.drift_margin = 50  # Stay this far from edges

    def update_settings(self, settings):
        """Update slideshow settings"""
        self.settings.update(settings)
        self.load_images()
        self.start_slideshow()

    def load_images(self):
        """Load image files from the specified folder"""
        self.image_files = []
        folder_path = self.settings.get('slideshow_folder', '')

        if not folder_path or not os.path.exists(folder_path):
            print(f"❌ Slideshow folder not found: {folder_path}")
            return

        folder = Path(folder_path)
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp'}

        # Collect all image files
        for file_path in folder.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in image_extensions:
                self.image_files.append(file_path)

        if not self.image_files:
            print(f"❌ No images found in folder: {folder_path}")
            return

        # Sort or randomize based on settings
        if self.settings.get('slideshow_random', True):
            random.shuffle(self.image_files)
        else:
            self.image_files.sort()

        print(f"✅ Loaded {len(self.image_files)} images from {folder_path}")

    def start_slideshow(self):
        """Start the slideshow"""
        if not self.image_files:
            print("❌ No images to display")
            return

        self.current_image_index = 0
        self.load_current_image()

        # Start slide timer
        interval = int(self.settings.get('slide_duration', 5.0) * 1000)
        self.slide_timer.start(interval)

    def load_current_image(self):
        """Load the current image"""
        if not self.image_files:
            return

        try:
            image_path = self.image_files[self.current_image_index]
            self.current_pixmap = QPixmap(str(image_path))

            if self.current_pixmap.isNull():
                print(f"❌ Failed to load image: {image_path}")
                self.next_slide()
                return

            print(f"📸 Loaded image: {image_path.name}")
            self.update()

        except Exception as e:
            print(f"❌ Error loading image: {e}")
            self.next_slide()

    def next_slide(self):
        """Move to the next slide"""
        if not self.image_files:
            return

        self.current_image_index = (self.current_image_index + 1) % len(self.image_files)
        self.load_current_image()

    def update_fps(self):
        """Update FPS counter"""
        current_time = time.time()
        time_diff = current_time - self.last_frame_time
        if time_diff > 0:
            self.fps = int(self.frame_count / time_diff)
        self.frame_count = 0
        self.last_frame_time = current_time

    def paintEvent(self, event: QPaintEvent):
        """Paint the current image"""
        painter = QPainter(self)
        painter.fillRect(self.rect(), Qt.GlobalColor.black)

        if self.current_pixmap and not self.current_pixmap.isNull():
            self.draw_image(painter)

        # Draw FPS if enabled
        if self.settings.get('show_stats', False):
            self.draw_stats(painter)

        self.frame_count += 1

    def draw_image(self, painter: QPainter):
        """Draw the current image with the specified fit mode"""
        if not self.current_pixmap:
            return

        widget_rect = self.rect()
        image_size = self.current_pixmap.size()

        fit_mode = self.settings.get('slideshow_fit_mode', 'contain')

        if fit_mode == 'stretch':
            # Stretch to fill entire screen
            target_rect = widget_rect
        elif fit_mode == 'cover':
            # Scale to fill screen, maintaining aspect ratio (may crop)
            scale_x = widget_rect.width() / image_size.width()
            scale_y = widget_rect.height() / image_size.height()
            scale = max(scale_x, scale_y)

            new_width = int(image_size.width() * scale)
            new_height = int(image_size.height() * scale)

            x = (widget_rect.width() - new_width) // 2
            y = (widget_rect.height() - new_height) // 2

            target_rect = painter.viewport().adjusted(x, y, x + new_width - widget_rect.width(), y + new_height - widget_rect.height())
        else:  # contain
            # Scale to fit within screen, maintaining aspect ratio
            scale_x = widget_rect.width() / image_size.width()
            scale_y = widget_rect.height() / image_size.height()
            scale = min(scale_x, scale_y)

            new_width = int(image_size.width() * scale)
            new_height = int(image_size.height() * scale)

            x = (widget_rect.width() - new_width) // 2
            y = (widget_rect.height() - new_height) // 2

            target_rect = painter.viewport().adjusted(x, y, x + new_width - widget_rect.width(), y + new_height - widget_rect.height())

        painter.drawPixmap(target_rect, self.current_pixmap)

    def draw_stats(self, painter: QPainter):
        """Draw slideshow statistics and info"""
        from PyQt6.QtGui import QPen, QColor

        painter.setPen(QPen(QColor(255, 255, 255)))

        # Calculate drifting position to prevent burn-in
        stats_x, stats_y = self.calculate_drift_position()

        # FPS and slideshow info
        if self.image_files:
            info_text = f"Slideshow: {self.current_image_index + 1}/{len(self.image_files)} | FPS: {self.fps}"
            painter.drawText(stats_x, stats_y, info_text)

            current_image = self.image_files[self.current_image_index]
            painter.drawText(stats_x, stats_y + self.stats_line_height, f"Image: {current_image.name}")

            duration = self.settings.get('slide_duration', 5.0)
            painter.drawText(stats_x, stats_y + 2 * self.stats_line_height, f"Duration: {duration}s | Mode: {self.settings.get('slideshow_fit_mode', 'contain')}")

    def calculate_drift_position(self):
        """Calculate current stats position based on slow drift around screen edges"""
        # Check if drift is enabled (default to True for backwards compatibility)
        if not hasattr(self, 'settings') or not self.settings.get('stats_drift', True):
            # Return fixed position if drift is disabled
            return 10, 30

        import time
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
            x = self.drift_margin + edge_progress * (screen_width - 2 * self.drift_margin - 400)  # Leave space for text
            y = self.drift_margin
        elif cycle_progress < 0.5:  # Right edge (top to bottom)
            edge_progress = (cycle_progress - 0.25) * 4
            x = screen_width - self.drift_margin - 400  # Fixed distance from right edge
            y = self.drift_margin + edge_progress * (screen_height - 2 * self.drift_margin - 80)  # Leave space for 3 lines
        elif cycle_progress < 0.75:  # Bottom edge (right to left)
            edge_progress = (cycle_progress - 0.5) * 4
            x = screen_width - self.drift_margin - 400 - edge_progress * (screen_width - 2 * self.drift_margin - 400)
            y = screen_height - self.drift_margin - 80  # Fixed distance from bottom
        else:  # Left edge (bottom to top)
            edge_progress = (cycle_progress - 0.75) * 4
            x = self.drift_margin
            y = screen_height - self.drift_margin - 80 - edge_progress * (screen_height - 2 * self.drift_margin - 80)

        return int(x), int(y)

    def keyPressEvent(self, event: QKeyEvent):
        """Handle key press events"""
        print(f"⌨️ Key press detected: {event.key()} - Exiting slideshow...")

        # Special keys for slideshow control
        if event.key() == Qt.Key.Key_Right or event.key() == Qt.Key.Key_Space:
            self.next_slide()
            return
        elif event.key() == Qt.Key.Key_Left:
            # Previous slide
            if self.image_files:
                self.current_image_index = (self.current_image_index - 1) % len(self.image_files)
                self.load_current_image()
            return

        # Any other key exits slideshow
        self.exit_requested.emit()

    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press events"""
        print(f"🖱️ Mouse click detected - Exiting slideshow...")
        self.exit_requested.emit()

    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle mouse movement"""
        if self.last_mouse_pos is None:
            self.last_mouse_pos = event.pos()
            return

        # Calculate movement distance using individual coordinates
        current_pos = event.pos()
        dx = current_pos.x() - self.last_mouse_pos.x()
        dy = current_pos.y() - self.last_mouse_pos.y()
        distance = (dx ** 2 + dy ** 2) ** 0.5

        # Exit if significant movement
        if distance > 10:
            print(f"🖱️ Mouse movement detected (distance: {distance:.1f}) - Exiting slideshow...")
            self.exit_requested.emit()

        self.last_mouse_pos = current_pos

    def closeEvent(self, event):
        """Clean up when closing"""
        self.slide_timer.stop()
        self.fps_timer.stop()
        event.accept()


class SlideshowScreensaver(QWidget):
    """Full-screen slideshow screensaver wrapper"""

    def __init__(self, settings=None):
        super().__init__()

        # Create slideshow widget
        self.slideshow_widget = SlideshowWidget()

        if settings:
            self.slideshow_widget.update_settings(settings)

        # Set up full-screen display
        self.slideshow_widget.showFullScreen()
        self.slideshow_widget.raise_()
        self.slideshow_widget.activateWindow()

    def close(self):
        """Close the slideshow"""
        if hasattr(self, 'slideshow_widget'):
            self.slideshow_widget.close()
        super().close()
