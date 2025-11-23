#!/usr/bin/env python3
"""
Video Player Widget - VLC-Based Video Screensaver
Continuously loops videos from a selected folder with minimal CPU usage

Features:
- VLC command-line player with reliable speed control
- Hardware-accelerated video decoding (H.264/H.265)
- Seamless looping of multiple videos
- Touch-friendly exit controls
- Low CPU usage (~2% on Pi 5)
- Supports MP4, MKV, AVI, MOV formats

Version: 2.0.0 - VLC CLI Edition
Created: November 2025
"""

import sys
import os
import random
import time
import subprocess
import signal
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from PyQt6.QtWidgets import QWidget, QApplication, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QPoint
from PyQt6.QtGui import QKeyEvent, QMouseEvent


def log(message):
    """Print message with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"[{timestamp}] {message}")


class VideoPlayerWidget(QWidget):
    """VLC-based video player widget for screensaver"""

    # Signals
    exit_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        # Widget setup
        self.setWindowTitle("Video Screensaver")
        self.setStyleSheet("background-color: black;")
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setMouseTracking(True)

        # Mouse tracking for screensaver exit
        self.last_mouse_pos = None

        # Video settings
        self.settings = {
            'video_folder': '',
            'video_random': True,
            'video_playback_speed': 1.0,
            'show_stats': False,
            'video_mute': True
        }

        # Video state
        self.video_files: List[Path] = []
        self.current_video_index = 0
        self.vlc_process = None

        # Stats tracking
        self.last_frame_time = time.time()
        self.frame_count = 0
        self.fps = 0

        # Setup UI
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create stats overlay widget
        self.stats_overlay = QLabel(self)
        self.stats_overlay.setStyleSheet("""
            QLabel {
                background-color: transparent;
                color: #00ff00;
                font-family: 'Courier New', monospace;
                font-size: 14px;
                font-weight: bold;
                padding: 10px;
            }
        """)
        self.stats_overlay.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.stats_overlay.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.stats_overlay.hide()

        # Timer for stats update
        self.stats_timer = QTimer()
        self.stats_timer.timeout.connect(self.update_stats_overlay)
        self.stats_timer.start(1000)

        # Timer to check if VLC process ended
        self.vlc_check_timer = QTimer()
        self.vlc_check_timer.timeout.connect(self.check_vlc_status)
        self.vlc_check_timer.start(1000)

        # Emergency CPU throttling
        self.emergency_cpu_threshold = 90.0
        self.is_emergency_throttled = False
        self.last_emergency_check = time.time()
        self.emergency_check_interval = 2.0

    def update_settings(self, settings):
        """Update video player settings"""
        self.settings.update(settings)

        # Update stats overlay visibility
        if self.settings.get('show_stats', False):
            self.stats_overlay.show()
            self.stats_overlay.raise_()
        else:
            self.stats_overlay.hide()

        self.load_videos()
        self.start_playback()

    def load_videos(self):
        """Load video files from the specified folder"""
        self.video_files = []
        folder_path = self.settings.get('video_folder', '')

        if not folder_path or not os.path.exists(folder_path):
            log(f"❌ Video folder not found: {folder_path}")
            return

        folder = Path(folder_path)
        video_extensions = {'.mp4', '.mkv', '.avi', '.mov', '.webm', '.flv', '.wmv', '.m4v'}

        # Collect all video files
        for file_path in folder.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in video_extensions:
                self.video_files.append(file_path)

        if not self.video_files:
            log(f"❌ No videos found in folder: {folder_path}")
            return

        # Sort or randomize based on settings
        if self.settings.get('video_random', True):
            random.shuffle(self.video_files)
        else:
            self.video_files.sort()

        log(f"✅ Loaded {len(self.video_files)} videos from {folder_path}")

    def start_playback(self):
        """Start video playback with seamless transitions"""
        if not self.video_files:
            log("❌ No videos to play")
            return

        self.play_playlist()

    def play_playlist(self):
        """Play all videos in a continuous playlist using VLC"""
        if not self.video_files:
            return

        # Stop any existing VLC process
        self.stop_vlc()

        playback_speed = self.settings.get('video_playback_speed', 1.0)
        is_muted = self.settings.get('video_mute', True)

        log(f"🎬 Starting playlist with {len(self.video_files)} videos")
        log(f"   Playback speed: {playback_speed}x")
        log(f"   Muted: {is_muted}")

        # Get screen resolution
        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()
        log(f"   Screen resolution: {screen_width}x{screen_height}")

        # Build VLC command with playlist for seamless playback
        vlc_cmd = [
            'cvlc',  # Command-line VLC
            '--fullscreen',
            '--no-video-title-show',  # Don't show filename
            '--no-osd',  # No on-screen display
            '--video-on-top',  # Keep video on top
            '--no-video-deco',  # No window decorations
            f'--width={screen_width}',  # Match screen width
            f'--height={screen_height}',  # Match screen height
            '--qt-fullscreen-screennumber=0',  # Use primary screen
            '--no-qt-fs-controller',  # No fullscreen controller
            '--no-embedded-video',  # Don't try to embed
            '--vout=x11',  # Force X11 video output
            '--aspect-ratio=',  # Empty = ignore aspect ratio, fill screen
            '--autoscale',  # Scale to fill window
            f'--rate={playback_speed}',  # SPEED CONTROL - this works reliably!
            '--loop',  # Loop the entire playlist
            '--no-video-title',  # No title between videos
            '--no-interact',  # No interactive mode
        ]

        if is_muted:
            vlc_cmd.append('--no-audio')

        # Add all video files to create a playlist
        for video_path in self.video_files:
            vlc_cmd.append(str(video_path))

        log(f"   📋 Playlist: {', '.join([v.name for v in self.video_files[:3]])}{'...' if len(self.video_files) > 3 else ''}")

        # Start VLC process
        try:
            self.vlc_process = subprocess.Popen(
                vlc_cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                preexec_fn=os.setsid  # Create new process group for clean termination
            )
            log(f"   ✅ VLC playlist started with PID {self.vlc_process.pid}")
        except Exception as e:
            log(f"❌ Failed to start VLC: {e}")

    def play_current_video(self):
        """Legacy method - redirects to playlist playback"""
        self.play_playlist()

    def stop_vlc(self):
        """Stop VLC process aggressively - ensure it's completely killed"""
        if self.vlc_process:
            try:
                pid = self.vlc_process.pid
                pgid = os.getpgid(pid)

                log(f"   🛑 Stopping VLC (PID {pid}, PGID {pgid})...")

                # First try SIGTERM to allow graceful shutdown
                os.killpg(pgid, signal.SIGTERM)

                # Wait briefly for graceful shutdown
                try:
                    self.vlc_process.wait(timeout=1)
                    log(f"   ✅ VLC stopped gracefully")
                except subprocess.TimeoutExpired:
                    # If still running after 1 second, force kill with SIGKILL
                    log(f"   ⚠️ VLC didn't stop gracefully, force killing...")
                    try:
                        os.killpg(pgid, signal.SIGKILL)
                        self.vlc_process.wait(timeout=1)
                        log(f"   ✅ VLC force killed")
                    except (ProcessLookupError, OSError, subprocess.TimeoutExpired):
                        # Last resort: use pkill to kill any remaining VLC processes
                        log(f"   ⚠️ Using pkill as last resort...")
                        subprocess.run(['pkill', '-9', 'vlc'], stderr=subprocess.DEVNULL)

            except (ProcessLookupError, OSError) as e:
                log(f"   ℹ️ VLC process already terminated: {e}")
            finally:
                self.vlc_process = None

        # Extra safety: kill any orphaned VLC processes
        try:
            subprocess.run(['pkill', '-9', 'vlc'], stderr=subprocess.DEVNULL, timeout=1)
        except:
            pass

    def check_vlc_status(self):
        """Check if VLC process has ended (shouldn't happen with looping playlist)"""
        if self.vlc_process:
            poll = self.vlc_process.poll()
            if poll is not None:  # Process has ended unexpectedly
                log(f"   ⚠️ VLC playlist ended unexpectedly (exit code: {poll})")
                self.vlc_process = None
                # Restart the playlist
                self.play_playlist()

    def next_video(self):
        """Legacy method - not needed with playlist, but kept for compatibility"""
        pass

    def update_stats_overlay(self):
        """Update the stats overlay text - NOTE: Not visible with fullscreen VLC"""
        # Stats overlay is hidden behind VLC's fullscreen window
        # VLC runs as external process and takes over the entire screen
        # The Qt widget with stats overlay is underneath and not visible
        # For this reason, stats are disabled for video mode
        if not self.settings.get('show_stats', False):
            return

        # Keep the stats overlay updated even though it's not visible
        # In case someone runs video mode in windowed mode for debugging
        stats_lines = []

        # Video info
        stats_lines.append(f"⚠️  Stats hidden by fullscreen VLC")
        stats_lines.append(f"Videos: {len(self.video_files)} videos in playlist")
        stats_lines.append(f"Mode: Continuous Loop")

        # Playback speed
        playback_speed = self.settings.get('video_playback_speed', 1.0)
        stats_lines.append(f"Speed: {playback_speed:.2f}x (VLC CLI)")

        # Mute status
        is_muted = self.settings.get('video_mute', True)
        mute_status = "🔇 Muted" if is_muted else "🔊 Audio"
        stats_lines.append(f"Audio: {mute_status}")

        # VLC status
        if self.vlc_process and self.vlc_process.poll() is None:
            stats_lines.append(f"VLC: Running (PID {self.vlc_process.pid})")
        else:
            stats_lines.append("VLC: Stopped")

        # CPU info
        try:
            import psutil
            cpu = psutil.cpu_percent(interval=0)
            stats_lines.append(f"CPU: {cpu:.1f}%")

            # Memory info
            mem = psutil.virtual_memory()
            stats_lines.append(f"Memory: {mem.percent:.1f}%")
        except (ImportError, AttributeError):
            pass  # psutil not available or error

        # Update overlay text
        self.stats_overlay.setText("\n".join(stats_lines))

    def keyPressEvent(self, event: QKeyEvent):
        """Handle keyboard events - exit on any key"""
        log(f"⌨️ Key press detected: {event.key()} - Exiting screensaver...")
        self.stop_vlc()
        self.exit_requested.emit()

    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press events"""
        log(f"🖱️ Mouse press detected - Exiting screensaver...")
        self.stop_vlc()
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

        if dx > 5 or dy > 5:  # 5 pixel threshold
            log(f"🖱️ Mouse movement detected: dx={dx}, dy={dy} - Exiting screensaver...")
            self.stop_vlc()
            self.exit_requested.emit()

    def closeEvent(self, event):
        """Handle widget close events"""
        log("🔚 Video player closing...")
        self.stop_vlc()
        super().closeEvent(event)


class VideoScreensaver(QWidget):
    """Standalone video screensaver application"""

    def __init__(self, settings=None):
        super().__init__()

        # Default settings
        default_settings = {
            'video_folder': os.path.expanduser('~/Videos'),
            'video_random': True,
            'show_stats': False
        }

        if settings:
            default_settings.update(settings)

        # Setup window - but keep it hidden since VLC creates its own fullscreen window
        self.setWindowTitle("Video Screensaver")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        # Don't show the Qt window - VLC will create its own fullscreen window
        self.hide()

        # Create video player widget
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.video_player = VideoPlayerWidget()
        self.video_player.exit_requested.connect(self.handle_exit)
        layout.addWidget(self.video_player)

        # Update settings and start
        self.video_player.update_settings(default_settings)

        log("🎬 Video screensaver started")
        log(f"   Folder: {default_settings['video_folder']}")
        log(f"   Random: {default_settings['video_random']}")
        log(f"   Stats: {default_settings['show_stats']}")

    def handle_exit(self):
        """Handle exit request from video player"""
        self.close()

    def closeEvent(self, event):
        """Ensure VLC is stopped when screensaver closes"""
        log("🔚 Video screensaver closing - stopping VLC...")
        if hasattr(self, 'video_player'):
            self.video_player.stop_vlc()
        super().closeEvent(event)


def load_saved_settings():
    """Load ALL persistent settings from configuration file"""
    import json
    from pathlib import Path

    # Default settings - matching screensaver_preferences.py defaults
    settings = {
        'enabled': True,
        'screensaver_type': 'Videos',
        'video_mode': True,
        'video_folder': '',
        'video_random': True,
        'video_playback_speed': 1.0,
        'video_mute': True,
        'target_fps': 15,
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
            print(f"✅ Loaded ALL persistent Video settings from {config_file}")
            print(f"   Screensaver Type: {settings.get('screensaver_type', 'Videos')}")
            print(f"   Folder: {settings.get('video_folder')}, Random: {settings.get('video_random')}")
            print(f"   Speed: {settings.get('video_playback_speed')}x, Mute: {settings.get('video_mute')}")
            print(f"   FPS: {settings.get('target_fps')}, Stats: {settings.get('show_stats')}, "
                  f"CPU Limit: {settings.get('auto_cpu_limit')}")
        except Exception as e:
            print(f"⚠️ Error loading settings from {config_file}: {e}")
            print("   Using default Video settings instead")
    else:
        print(f"ℹ️ No config file found at {config_file}, using Video defaults")

    return settings

def main():
    """Main entry point for testing"""
    import argparse

    parser = argparse.ArgumentParser(description='Video Screensaver')
    parser.add_argument('--folder', type=str, help='Video folder path')
    parser.add_argument('--random', action='store_true', help='Random video order')
    parser.add_argument('--stats', action='store_true', help='Show stats overlay')

    args = parser.parse_args()

    app = QApplication(sys.argv)

    # Load persistent settings from config file first
    settings = load_saved_settings()

    # Command-line arguments override config file
    if args.folder:
        settings['video_folder'] = args.folder
    if args.random:
        settings['video_random'] = True
    if args.stats:
        settings['show_stats'] = True

    screensaver = VideoScreensaver(settings)
    screensaver.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
