# Security Guide for ROTMG Patch Utility Tool

## 🔐 Authentication System

The ROTMG Patch Utility Tool includes a comprehensive authentication system to protect your patches and settings.

### User Registration and Login

#### First Time Setup
1. **Launch the application** - You'll be prompted to login
2. **Click "Register"** to create a new account
3. **Enter your credentials**:
   - Username (required)
   - Email (optional)
   - Password (must meet security requirements)
4. **Complete registration** and login

#### Password Requirements
- **Minimum length**: 8 characters (configurable)
- **Must contain**: Uppercase letters, lowercase letters, numbers
- **Optional**: Special characters (configurable)
- **No common passwords**: Avoid dictionary words

### Security Features

#### 🔒 Encrypted Storage
- **All credentials are encrypted** using AES-256 encryption
- **Passwords are hashed** with SHA-256 before storage
- **Salt is used** to prevent rainbow table attacks
- **PBKDF2 key derivation** with 100,000 iterations

#### 🕒 Session Management
- **Automatic session timeout** (default: 1 hour)
- **Session validation** on application startup
- **Secure logout** clears all session data
- **Configurable timeout** in settings

#### 🚫 Account Protection
- **Login attempt limiting** (default: 3 attempts)
- **Account lockout** after failed attempts (default: 5 minutes)
- **Progressive lockout** for repeated failures
- **Automatic unlock** after timeout period

## 🛡️ Security Best Practices

### For Users

#### Password Security
- ✅ **Use strong, unique passwords**
- ✅ **Don't reuse passwords** from other accounts
- ✅ **Consider using a password manager**
- ❌ **Never share your credentials**
- ❌ **Don't write passwords down**

#### Application Security
- ✅ **Keep the application updated**
- ✅ **Use the logout function** when finished
- ✅ **Don't leave the application running** unattended
- ✅ **Regularly backup your patches**
- ❌ **Don't run on shared computers** without logging out

#### File Security
- ✅ **Keep your resources.assets file secure**
- ✅ **Use the built-in backup system**
- ✅ **Store backups in a safe location**
- ❌ **Don't share your assets files** with others

### For Developers

#### Credential Storage
```python
# ✅ DO: Use encrypted storage
encrypted_data, salt = self._encrypt_data(user_data, password)

# ❌ DON'T: Store passwords in plain text
user_data["password"] = password  # NEVER DO THIS
```

#### Session Management
```python
# ✅ DO: Validate sessions
if not self.auth_manager.is_session_valid():
    self.show_login()

# ❌ DON'T: Skip session validation
# Always validate before allowing access
```

#### Error Handling
```python
# ✅ DO: Handle errors securely
try:
    result = authenticate_user(username, password)
except Exception as e:
    log_error("Authentication failed", e)
    return False

# ❌ DON'T: Expose sensitive information
except Exception as e:
    messagebox.showerror("Error", f"Password: {password}")  # NEVER
```

## 🔧 Configuration Security

### Settings Location
- **Windows**: `%USERPROFILE%\.rotmg_patch_utility\`
- **Linux/macOS**: `~/.rotmg_patch_utility/`

### Files Created
- `credentials.enc` - Encrypted user credentials
- `session.json` - Current session data
- `config.json` - Application configuration
- `user_config.json` - User preferences

### File Permissions
- **Credentials file**: Read/write for user only (600)
- **Session file**: Read/write for user only (600)
- **Config files**: Read/write for user only (644)

## 🚨 Security Warnings

### ⚠️ Important Notes
1. **This is NOT a server application** - authentication is local only
2. **Credentials are stored locally** on your machine
3. **No network authentication** - works offline
4. **Backup your credentials** if you need to reinstall

### 🔍 What's Protected
- ✅ User credentials (encrypted)
- ✅ Session data (temporary)
- ✅ Application settings
- ✅ User preferences

### 🔓 What's NOT Protected
- ❌ Your resources.assets file (you must protect this)
- ❌ Patch files (stored in plain text)
- ❌ Log files (may contain sensitive info)
- ❌ Backup files (unencrypted)

## 🛠️ Troubleshooting Security Issues

### Common Problems

#### "Invalid username or password"
- Check your credentials
- Ensure caps lock is off
- Try resetting your password (re-register)

#### "Account locked"
- Wait for the lockout period to expire
- Check your login attempts
- Contact support if persistent

#### "Session expired"
- This is normal behavior
- Simply login again
- Adjust timeout in settings if needed

#### "Cannot access settings"
- Ensure you're logged in
- Check file permissions
- Restart the application

### Security Checklist

#### Before First Use
- [ ] Create a strong password
- [ ] Note down your credentials safely
- [ ] Review security settings
- [ ] Enable automatic backup

#### Regular Maintenance
- [ ] Update the application
- [ ] Review recent login activity
- [ ] Backup your patches
- [ ] Check file permissions

#### If Compromised
- [ ] Change your password immediately
- [ ] Logout from all sessions
- [ ] Review your patches for changes
- [ ] Report any suspicious activity

## 📞 Support and Reporting

### Security Issues
If you discover a security vulnerability:
1. **DO NOT** post publicly
2. **Contact the developers** privately
3. **Provide detailed information**
4. **Wait for confirmation** before disclosure

### Getting Help
- Check this documentation first
- Review the README.md file
- Use the built-in help system
- Contact support for critical issues

## 🔄 Updates and Maintenance

### Keeping Secure
- **Regular updates** include security patches
- **Check for updates** in the help menu
- **Backup before updating**
- **Test after updates**

### Version History
- **v1.0.0**: Initial release with authentication
- **Future versions**: Enhanced security features

---

**Remember**: Security is a shared responsibility. Use strong passwords, keep your software updated, and follow these best practices to keep your patches and data secure.
