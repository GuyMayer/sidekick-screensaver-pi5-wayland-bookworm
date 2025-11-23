# Security Policy

## Supported Versions

We provide security updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 2.1.x   | :white_check_mark: |
| 2.0.x   | :white_check_mark: |
| < 2.0   | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability in Sidekick Screensaver, please report it responsibly:

### 🔒 Private Reporting (Preferred)
- **Email**: [maintainer-email@example.com]
- **Subject**: "Security Vulnerability in Sidekick Screensaver"
- **Include**: Detailed description and steps to reproduce

### 🐛 GitHub Security Advisories
- Use [GitHub's security advisory feature](https://github.com/yourusername/sidekick-screensaver/security/advisories)
- This allows private disclosure and coordinated response

### ⚡ Response Timeline
- **Initial Response**: Within 48 hours
- **Investigation**: Within 1 week
- **Fix Development**: Within 2 weeks for critical issues
- **Public Disclosure**: After fix is available and users have had time to update

## 🛡️ Security Considerations

### System Access
Sidekick Screensaver requires certain system permissions:
- **Display Access**: To create screensaver windows
- **System Tray**: For background operation
- **USB Monitoring**: For activity detection
- **File System**: For settings and image storage

### Data Handling
- **Settings**: Stored locally in `~/.config/screensaver/`
- **No Network**: Application does not connect to external services
- **No Telemetry**: No usage data is collected or transmitted
- **Local Only**: All operations are performed locally

### Installation Security
- **Installer Script**: Reviews recommended before running with sudo
- **File Permissions**: Proper permissions set during installation
- **System Integration**: Minimal system modification required

## 🔍 Security Best Practices

### For Users
1. **Download from trusted sources** only
2. **Review installer script** before running with sudo privileges
3. **Keep system updated** with latest security patches
4. **Use latest version** of Sidekick Screensaver
5. **Report suspicious behavior** immediately

### For Developers
1. **Input Validation**: Validate all user inputs
2. **Error Handling**: Fail securely without exposing information
3. **Dependency Management**: Keep dependencies updated
4. **Code Review**: All changes reviewed for security implications
5. **Testing**: Include security testing in development process

## 🚨 Known Security Considerations

### System Permissions
- Installer requires sudo for system-wide installation
- USB monitoring requires access to system device information
- Screen capture capabilities for screensaver operation

### Mitigation Strategies
- Minimal privilege principle applied
- No unnecessary system access requested
- Clear documentation of required permissions
- Optional features can be disabled if not needed

## 📋 Security Checklist for Contributors

When contributing code, ensure:
- [ ] No hardcoded secrets or credentials
- [ ] Input validation for all user-provided data
- [ ] Proper error handling without information leakage
- [ ] Dependencies are up-to-date and secure
- [ ] No shell injection vulnerabilities
- [ ] File operations use proper path validation
- [ ] System calls are properly sanitized

## 🛠️ Security Tools

We recommend using these tools for security testing:
- **Bandit**: Python security linter
- **Safety**: Dependency vulnerability scanner
- **CodeQL**: Static analysis for security issues

```bash
# Install security tools
pip install bandit safety

# Run security scans
bandit -r .
safety check

# Check for known vulnerabilities
pip-audit
```

## 📞 Contact

For security-related questions or concerns:
- **Security Email**: [security@example.com]
- **Maintainer**: [maintainer@example.com]
- **GitHub**: [@maintainer-username]

## 🏆 Responsible Disclosure Hall of Fame

We appreciate security researchers who help keep Sidekick Screensaver secure:

- *[Your name could be here!]*

## 🔄 Updates to this Policy

This security policy may be updated as the project evolves. Users will be notified of significant changes through:
- GitHub releases
- Security advisories
- Project announcements

Last updated: September 2025
