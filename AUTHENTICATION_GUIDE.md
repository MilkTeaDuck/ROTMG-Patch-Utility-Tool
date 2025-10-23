# Authentication Options Guide

## 🔐 Multiple Authentication Methods

The ROTMG Patch Utility Tool now supports three different authentication methods:

1. **Local Authentication** - Store credentials locally with encryption
2. **Server Authentication** - Authenticate with a remote server
3. **Access Code** - Use access codes for authentication

## 🏠 Local Authentication

### How It Works
- Credentials are encrypted and stored locally on your machine
- Uses AES-256 encryption with PBKDF2 key derivation
- Session management with automatic timeout
- Works completely offline

### Setup
1. Launch the application
2. Select "Local Authentication" from the mode selector
3. Click "Register" to create a new account
4. Enter username, email (optional), and password
5. Complete registration and login

### Security Features
- Password hashing with SHA-256
- Salt-based encryption
- Session validation
- Account lockout after failed attempts

## 🌐 Server Authentication

### How It Works
- Authenticates with a remote server
- Supports both username/password and license key validation
- Session management with heartbeat
- Offline mode when server is unavailable

### Setup
1. Launch the application
2. Select "Server Authentication" from the mode selector
3. Choose authentication method:
   - **License Key**: Enter your license key
   - **Username/Password**: Enter your credentials
4. Configure server URL (default: `https://api.rotmg-patch-utility.com`)
5. Click "Authenticate"

### Server Requirements
Your authentication server must implement these endpoints:

#### License Validation
```
POST /api/v1/validate-license
Content-Type: application/json

{
  "license_key": "DEMO-2024-001",
  "machine_id": "unique-machine-id",
  "app_version": "1.0.0",
  "timestamp": 1234567890
}
```

#### User Authentication
```
POST /api/v1/authenticate
Content-Type: application/json

{
  "username": "admin",
  "password_hash": "sha256-hash",
  "machine_id": "unique-machine-id",
  "app_version": "1.0.0",
  "timestamp": 1234567890
}
```

#### Session Heartbeat
```
POST /api/v1/heartbeat
Content-Type: application/json

{
  "session_token": "session-token",
  "machine_id": "unique-machine-id",
  "timestamp": 1234567890
}
```

### Example Server
See `auth_server_example.py` for a complete Flask server implementation.

### Offline Mode
- Automatically enabled when server is unavailable
- Allows continued use for configurable days (default: 7)
- Validates with server when connection is restored

## 🎫 Access Code Authentication

### How It Works
- Simple access codes for authentication
- No user accounts required
- Codes can have expiration dates and usage limits
- Perfect for temporary access or demos

### Setup
1. Launch the application
2. Select "Access Code" from the mode selector
3. Enter your access code
4. Click "Validate Code"

### Default Access Codes
The application comes with these default codes:

- **DEMO-2024-001**: Demo access (100 uses, never expires)
- **BETA-2024-002**: Beta tester (10 uses, 30 days)

### Managing Access Codes
Access codes can be managed through the authentication settings:

1. Go to **Edit > Authentication Settings**
2. Click the **Access Codes** tab
3. Use the management tools:
   - **Generate New Access Code**: Create new codes
   - **List Access Codes**: View all codes and their status

### Code Format
Access codes follow this format: `XXXX-YYYY-ZZZZ`
- 4 characters, dash, 4 characters, dash, 4 characters
- Case insensitive
- Examples: `DEMO-2024-001`, `BETA-2024-002`

## ⚙️ Authentication Settings

### Accessing Settings
1. Go to **Edit > Authentication Settings**
2. Configure each authentication method

### General Settings
- **Current Mode**: Shows active authentication method
- **Available Methods**: Enable/disable authentication methods

### Local Authentication Settings
- **Auto-login**: Remember login state
- **Session Timeout**: How long sessions last

### Server Authentication Settings
- **Server URL**: Your authentication server
- **Offline Mode**: Allow offline use when server unavailable
- **Offline Duration**: How many days offline use is allowed

### Access Code Settings
- **Require Code on Startup**: Always prompt for code
- **Code Management**: Generate and manage codes

## 🔄 Switching Authentication Methods

### Method 1: Through Settings
1. Go to **Edit > Authentication Settings**
2. Enable/disable desired methods
3. Restart the application
4. Select new method from mode selector

### Method 2: Direct Selection
1. Logout from current method
2. Restart the application
3. Select new method from mode selector

## 🛡️ Security Considerations

### Local Authentication
- ✅ **Pros**: Works offline, fast, private
- ❌ **Cons**: No centralized control, single machine

### Server Authentication
- ✅ **Pros**: Centralized control, multi-machine, license management
- ❌ **Cons**: Requires internet, server maintenance

### Access Code
- ✅ **Pros**: Simple, no accounts, temporary access
- ❌ **Cons**: Limited features, manual management

## 🚀 Implementation Examples

### Setting Up Your Own Server

1. **Install Flask**:
   ```bash
   pip install flask
   ```

2. **Run the example server**:
   ```bash
   python auth_server_example.py
   ```

3. **Configure the client**:
   - Set server URL to `http://localhost:5000`
   - Use default credentials: `admin/password` or `demo/demo123`

### Creating Access Codes Programmatically

```python
from server_auth import AccessCodeManager

# Create code manager
code_manager = AccessCodeManager()

# Generate a new code
code = code_manager.generate_access_code(
    name="Temporary Access",
    features=["basic_patching"],
    expires_days=7,  # Expires in 7 days
    max_uses=5       # Can be used 5 times
)

print(f"Generated code: {code}")
```

### Custom Authentication Server

```python
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/api/v1/validate-license', methods=['POST'])
def validate_license():
    data = request.get_json()
    license_key = data.get('license_key')
    
    # Your validation logic here
    if license_key == "YOUR-LICENSE-KEY":
        return jsonify({
            'valid': True,
            'user_id': 'user_001',
            'username': 'licensed_user',
            'expires_at': int(time.time()) + (365 * 24 * 3600),  # 1 year
            'features': ['basic_patching', 'advanced_features']
        })
    
    return jsonify({'valid': False, 'message': 'Invalid license'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

## 🔧 Troubleshooting

### Common Issues

#### "Server Authentication Failed"
- Check server URL is correct
- Verify server is running and accessible
- Check firewall settings
- Try offline mode if available

#### "Access Code Invalid"
- Verify code format (XXXX-YYYY-ZZZZ)
- Check if code has expired
- Ensure code hasn't reached usage limit
- Contact administrator for new code

#### "Local Authentication Error"
- Check file permissions in config directory
- Verify encryption keys are valid
- Try re-registering account
- Clear config directory and restart

### Getting Help

1. **Check logs** in the application
2. **Review settings** in authentication configuration
3. **Test with example server** using `auth_server_example.py`
4. **Contact support** with specific error messages

## 📋 Best Practices

### For Administrators
- Use server authentication for production
- Implement proper license management
- Monitor usage and access patterns
- Keep access codes secure and rotated

### For Users
- Choose authentication method based on needs
- Keep credentials secure
- Use strong passwords for local auth
- Report suspicious activity

### For Developers
- Implement proper error handling
- Use HTTPS for server communication
- Validate all inputs
- Log authentication events

---

**Note**: This guide covers the authentication system implementation. For security best practices, see [SECURITY.md](SECURITY.md).
