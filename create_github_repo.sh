#!/bin/bash
# GitHub Repository Creation Script for Sidekick Screensaver - Pi5 Wayland Bookworm
# This script creates a new GitHub repository and pushes the local code

set -e  # Exit on any error

# Repository Configuration
REPO_NAME="sidekick-screensaver-pi5-wayland-bookworm"
REPO_DESCRIPTION="Modern screensaver system optimized for Raspberry Pi 5 with Wayland on Bookworm - Matrix digital rain, Mystify patterns, hardware-accelerated USB detection, and PyQt6 GUI"
GITHUB_USERNAME="GuyMayer"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [[ ! -f "screensaver_preferences.py" ]]; then
    print_error "Not in the Sidekick Screensaver directory. Please cd to the correct directory."
    exit 1
fi

print_status "Creating GitHub repository: ${REPO_NAME}"
print_status "Description: ${REPO_DESCRIPTION}"

# Check if GitHub CLI is installed
if ! command -v gh &> /dev/null; then
    print_error "GitHub CLI (gh) is not installed. Please install it:"
    echo "  sudo apt update && sudo apt install gh"
    echo "  Then run: gh auth login"
    exit 1
fi

# Check if user is authenticated
if ! gh auth status &> /dev/null; then
    print_error "Not authenticated with GitHub CLI. Please run:"
    echo "  gh auth login"
    exit 1
fi

# Initialize git repository if not already done
if [[ ! -d ".git" ]]; then
    print_status "Initializing Git repository..."
    git init
    print_success "Git repository initialized"
else
    print_status "Git repository already exists"
fi

# Add all files to git
print_status "Adding files to Git..."
git add .

# Check if there are any changes to commit
if git diff --staged --quiet; then
    print_warning "No changes to commit. Repository might already be up to date."
else
    # Commit with Pi5-Wayland-Bookworm focused message
    print_status "Committing changes..."
    git commit -m "feat: Pi5-Wayland-Bookworm optimized screensaver system

- Hardware-accelerated Matrix and Mystify screensavers for Pi 5 GPU
- Native Wayland compositor integration (Wayfire, wlroots, Sway)
- USB4 and USB-A instant wake detection with hardware interrupts
- PyQt6 GUI with dark mode and system tray integration
- Dual 4K HDMI display support for Pi 5
- Real-time GPU temperature and system monitoring
- SingleInstance protection with robust file locking
- Professional MIT-licensed open source package
- Comprehensive documentation and installation system

Optimized for:
- Raspberry Pi 5 (4GB/8GB models)
- Raspberry Pi OS Bookworm 64-bit
- Wayland display server (not X11)
- VideoCore VII GPU acceleration
- PCIe NVMe SSD compatibility"
    print_success "Changes committed"
fi

# Create GitHub repository
print_status "Creating GitHub repository..."
if gh repo create "${GITHUB_USERNAME}/${REPO_NAME}" \
    --public \
    --description "${REPO_DESCRIPTION}" \
    --clone=false; then
    print_success "GitHub repository created successfully"
else
    print_error "Failed to create GitHub repository"
    exit 1
fi

# Add remote origin
print_status "Adding remote origin..."
git remote add origin "https://github.com/${GITHUB_USERNAME}/${REPO_NAME}.git" 2>/dev/null || {
    print_warning "Remote origin already exists, updating..."
    git remote set-url origin "https://github.com/${GITHUB_USERNAME}/${REPO_NAME}.git"
}

# Push to GitHub
print_status "Pushing to GitHub..."
git branch -M main
git push -u origin main

print_success "Repository successfully published!"
echo ""
print_status "Repository URL: https://github.com/${GITHUB_USERNAME}/${REPO_NAME}"
print_status "Clone command: git clone https://github.com/${GITHUB_USERNAME}/${REPO_NAME}.git"
echo ""
print_success "✅ Sidekick Screensaver - Pi5 Wayland Bookworm is now live on GitHub!"
echo ""
print_status "Next steps:"
echo "  1. Visit the repository URL to verify all files uploaded correctly"
echo "  2. Consider enabling GitHub Pages for documentation"
echo "  3. Add topics/tags for better discoverability:"
echo "     - raspberry-pi-5"
echo "     - wayland"
echo "     - bookworm"
echo "     - screensaver"
echo "     - pyqt6"
echo "     - hardware-acceleration"
echo "  4. Create first release with version tag"