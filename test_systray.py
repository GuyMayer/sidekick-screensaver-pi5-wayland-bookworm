#!/usr/bin/env python3
"""
Test system tray availability and functionality
"""
import sys
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QAction

def test_systray():
    app = QApplication(sys.argv)

    print("=" * 60)
    print("System Tray Test")
    print("=" * 60)

    # Check if system tray is available
    available = QSystemTrayIcon.isSystemTrayAvailable()
    print(f"\n1. System Tray Available: {available}")

    if not available:
        print("\n❌ System tray not available on this system!")
        print("   This is common on Wayland without proper tray support.")
        return 1

    # Try to create a tray icon
    try:
        tray = QSystemTrayIcon(app)
        print("✅ QSystemTrayIcon created successfully")

        # Try to set an icon
        icon = app.style().standardIcon(app.style().StandardPixmap.SP_ComputerIcon)
        tray.setIcon(icon)
        print("✅ Icon set successfully")

        # Create menu
        menu = QMenu()
        test_action = QAction("Test Action", app)
        menu.addAction(test_action)
        tray.setContextMenu(menu)
        print("✅ Context menu set successfully")

        # Try to show the tray
        tray.show()
        print("✅ Tray icon shown successfully")

        # Check if it's visible
        if tray.isVisible():
            print("\n✅ SUCCESS: System tray icon is visible!")
        else:
            print("\n⚠️  WARNING: Tray icon created but not visible")
            print("   This may be due to desktop environment settings")

        print("\nℹ️  The tray icon should now be visible in your system tray.")
        print("   Right-click it to see the 'Test Action' menu item.")
        print("   Press Ctrl+C to quit.")

        # Keep app running to show tray
        sys.exit(app.exec())

    except Exception as e:
        print(f"\n❌ Error creating system tray: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(test_systray())
