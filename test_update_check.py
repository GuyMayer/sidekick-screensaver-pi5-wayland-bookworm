#!/usr/bin/env python3
"""
Test script for update checking functionality
"""

import sys
import os
import json
import datetime
import urllib.request
import urllib.error
from pathlib import Path

# Add current directory to path to import from screensaver_preferences
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_version_comparison():
    """Test the version comparison logic"""
    print("🧪 Testing version comparison...")

    def is_newer_version(latest, current):
        """Compare version strings to determine if latest is newer than current"""
        try:
            # Simple version comparison (assumes semantic versioning like 3.0.0)
            latest_parts = [int(x) for x in latest.split('.')]
            current_parts = [int(x) for x in current.split('.')]

            # Pad shorter version with zeros
            max_len = max(len(latest_parts), len(current_parts))
            latest_parts.extend([0] * (max_len - len(latest_parts)))
            current_parts.extend([0] * (max_len - len(current_parts)))

            return latest_parts > current_parts
        except (ValueError, AttributeError):
            return False

    # Test cases
    test_cases = [
        ("3.1.0", "3.0.0", True),   # Newer minor version
        ("4.0.0", "3.0.0", True),   # Newer major version
        ("3.0.1", "3.0.0", True),   # Newer patch version
        ("3.0.0", "3.0.0", False),  # Same version
        ("2.9.9", "3.0.0", False),  # Older version
        ("3.0.0", "3.1.0", False),  # Current is newer
    ]

    for latest, current, expected in test_cases:
        result = is_newer_version(latest, current)
        status = "✅" if result == expected else "❌"
        print(f"  {status} {latest} > {current}: {result} (expected: {expected})")

    print()

def test_update_check_logic():
    """Test the update check timing logic"""
    print("🕒 Testing update check timing...")

    def should_check_for_updates(last_check, check_frequency):
        """Check if it's time to perform an update check"""
        if not last_check:
            return True  # Never checked before

        try:
            last_check_date = datetime.datetime.fromisoformat(last_check)
            days_since_check = (datetime.datetime.now() - last_check_date).days
            return days_since_check >= check_frequency
        except (ValueError, TypeError):
            return True  # Invalid date format, check anyway

    # Test cases
    now = datetime.datetime.now()
    yesterday = (now - datetime.timedelta(days=1)).isoformat()
    last_month = (now - datetime.timedelta(days=31)).isoformat()

    test_cases = [
        ("", 30, True, "Never checked"),
        (yesterday, 30, False, "Checked yesterday"),
        (last_month, 30, True, "Checked last month"),
        ("invalid", 30, True, "Invalid date"),
    ]

    for last_check, frequency, expected, description in test_cases:
        result = should_check_for_updates(last_check, frequency)
        status = "✅" if result == expected else "❌"
        print(f"  {status} {description}: {result} (expected: {expected})")

    print()

def test_github_api_access():
    """Test if we can access GitHub API"""
    print("🌐 Testing GitHub API access...")

    try:
        # Test repository URL - linked to actual git repository
        repo_url = "https://api.github.com/repos/GuyMayer/sidekick-screensaver-pi5-wayland-bookworm/releases/latest"

        # Create request with user agent
        request = urllib.request.Request(repo_url)
        request.add_header('User-Agent', 'Sidekick-Screensaver-UpdateChecker/1.0')

        # Try to access the API
        with urllib.request.urlopen(request, timeout=10) as response:
            if response.getcode() == 200:
                print("  ✅ GitHub API accessible")
                data = json.loads(response.read().decode())

                # Extract version info
                latest_version = data.get('tag_name', '').lstrip('v')
                release_name = data.get('name', '')
                release_url = data.get('html_url', '')

                print(f"  📦 Latest release: {latest_version}")
                print(f"  🏷️ Release name: {release_name}")
                print(f"  🔗 Release URL: {release_url}")

                return True
            else:
                print(f"  ❌ GitHub API returned: HTTP {response.getcode()}")
                return False

    except urllib.error.URLError as e:
        print(f"  ⚠️ Network error: {e}")
        print("  💡 This is normal if you don't have internet or the repository doesn't exist yet")
        return False
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def test_settings_file():
    """Test settings file creation and update"""
    print("📁 Testing settings file handling...")

    config_dir = Path.home() / '.config' / 'screensaver'
    config_file = config_dir / 'settings.json'

    # Create test settings
    test_settings = {
        'auto_update_check': True,
        'last_update_check': '',
        'update_check_frequency': 30,
        'update_notification': True
    }

    try:
        # Ensure directory exists
        config_dir.mkdir(exist_ok=True)
        print(f"  ✅ Config directory: {config_dir}")

        # Save test settings
        with open(config_file, 'w') as f:
            json.dump(test_settings, f, indent=2)
        print(f"  ✅ Settings saved to: {config_file}")

        # Read back settings
        with open(config_file, 'r') as f:
            loaded_settings = json.load(f)

        if loaded_settings == test_settings:
            print("  ✅ Settings loaded correctly")
        else:
            print("  ❌ Settings mismatch")

        # Update last check time
        test_settings['last_update_check'] = datetime.datetime.now().isoformat()
        with open(config_file, 'w') as f:
            json.dump(test_settings, f, indent=2)
        print("  ✅ Last check time updated")

        return True

    except Exception as e:
        print(f"  ❌ Settings file error: {e}")
        return False

def main():
    """Run all update check tests"""
    print("🚀 Sidekick Screensaver Update Check Test Suite")
    print("=" * 50)

    test_version_comparison()
    test_update_check_logic()
    test_github_api_access()
    test_settings_file()

    print("🎉 Update check test suite completed!")
    print("\n💡 To enable automatic updates in the GUI:")
    print("   1. Run: screensaver-prefs")
    print("   2. Check '🔄 Auto Update Check' in System Settings")
    print("   3. Click '🔍 Check Now' to test manual update check")

if __name__ == "__main__":
    main()
