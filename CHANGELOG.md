# Changelog

All notable changes to Sidekick Screensaver will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Contribution guidelines and development documentation
- Security policy and responsible disclosure process
- Comprehensive project structure for open source publishing

## [2.1.0] - 2025-09-08

### Added
- **GUI Layout Reorganization**: Professional 3-section layout (System, Screen, Timer)
- **Stats Drift Feature**: Anti-burn-in stats movement (8-minute cycle, 2 min per edge)
- **Drift Control Checkbox**: User-controllable stats drift (default enabled)
- **Enhanced System Tray Persistence**: Robust persistence after screensaver interruptions
- **FPS Throttling**: Renamed and moved from "Intelligent CPU Management" to Screen Settings
- **Show Stats Enhancement**: Moved to Screen Settings for logical grouping

### Changed
- **GUI Organization**: Show Stats and FPS Throttling moved to Screen Settings section
- **System Tray Behavior**: Enhanced restoration and confirmation messages
- **Settings Layout**: Cleaner organization with QGroupBox containers
- **Performance**: Improved stats display with drift prevention

### Fixed
- **Critical Qt Fix**: `app.setQuitOnLastWindowClosed(False)` prevents app quit on screensaver exit
- **System Tray Persistence**: Icon remains visible and accessible after keystroke interruptions
- **Verification Scripts**: Corrected file references from `matrix_widget.py` to `sidekick_widget.py`
- **Background Monitoring**: Continues properly after screensaver interruption

### Technical
- Enhanced error handling for system tray operations
- Improved drift calculation algorithms
- Better widget initialization and cleanup
- Comprehensive verification system updates

## [2.0.0] - 2025-09-05

### Added
- **Multi-Mode Support**: Matrix, Mystify, and Slideshow screensaver modes
- **Professional GUI**: Complete PyQt6 rewrite with dark/light themes
- **Show Stats Feature**: Real-time FPS, CPU, and memory monitoring
- **USB Activity Detection**: Hardware-level interrupt monitoring
- **Mystify Mode**: Windows-style geometric pattern screensaver
- **Slideshow Mode**: Directory-based image slideshow with transitions
- **Performance Monitoring**: Comprehensive system statistics overlay
- **Dark Theme Integration**: QDarkStyle and QDarkTheme support
- **Auto-shutdown Timer**: Configurable system shutdown functionality

### Changed
- **Complete Rewrite**: Migrated from basic script to full PyQt6 application
- **Settings System**: JSON-based configuration with auto-save
- **Installation Process**: Comprehensive installer with verification
- **User Interface**: Professional GUI with organized settings sections
- **Performance**: Optimized rendering and resource management

### Improved
- **System Integration**: Better desktop environment compatibility
- **Error Handling**: Robust error handling and recovery
- **Documentation**: Comprehensive guides and verification tools
- **Compatibility**: Support for multiple Linux distributions and desktop environments

## [1.0.0] - 2025-08-01

### Added
- **Initial Release**: Basic Matrix digital rain screensaver
- **Core Functionality**: Simple screensaver with basic customization
- **Installation Script**: Basic setup and configuration
- **System Tray**: Simple tray integration
- **Configuration**: Basic settings management

### Features
- Matrix digital rain effect
- Color customization (green, red, blue, etc.)
- Speed adjustment
- Basic system tray integration
- Simple installation process

---

## Version Naming Convention

- **Major** (X.0.0): Breaking changes, major feature additions, architectural changes
- **Minor** (x.Y.0): New features, significant improvements, backward-compatible changes
- **Patch** (x.y.Z): Bug fixes, small improvements, security patches

## Release Process

1. **Development**: Feature development on feature branches
2. **Testing**: Comprehensive testing on multiple platforms
3. **Documentation**: Update README, CHANGELOG, and documentation
4. **Version Bump**: Update version numbers in relevant files
5. **Tag Release**: Create git tag with version number
6. **GitHub Release**: Create GitHub release with detailed notes
7. **Distribution**: Update package managers and distribution channels

## Support Timeline

- **Current Version (2.1.x)**: Full support with new features and bug fixes
- **Previous Major (2.0.x)**: Security and critical bug fixes only
- **Legacy (1.x.x)**: No longer supported, upgrade recommended

## Migration Guide

### From 1.x to 2.x
- Backup existing settings
- Uninstall old version
- Install new version with installer
- Reconfigure settings in new GUI
- Test functionality thoroughly

### From 2.0 to 2.1
- Automatic settings migration
- New features available immediately
- Enhanced GUI organization
- Improved system tray behavior

## Contributors

Special thanks to all contributors who have helped improve Sidekick Screensaver:

- **Core Development**: Initial development and maintenance
- **Feature Contributions**: GUI improvements, new screensaver modes
- **Testing**: Cross-platform testing and bug reports
- **Documentation**: README improvements and user guides
- **Community**: Feedback, suggestions, and support

## Future Roadmap

### Planned for 2.2.0
- [ ] Plugin system for custom screensavers
- [ ] Network activity monitoring
- [ ] Clock and system info overlays
- [ ] Enhanced slideshow transitions
- [ ] Remote control capabilities

### Planned for 3.0.0
- [ ] Wayland-native implementation
- [ ] Modern UI framework migration
- [ ] Mobile companion app
- [ ] Cloud synchronization
- [ ] Advanced customization system

---

For detailed information about any release, see the corresponding [GitHub Release](https://github.com/yourusername/sidekick-screensaver/releases) page.
