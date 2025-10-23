"""
Example Server for ROTMG Patch Utility Tool Authentication
This is a simple Flask server that demonstrates how to implement server-side authentication
"""

from flask import Flask, request, jsonify
import hashlib
import time
import json
from datetime import datetime, timedelta

app = Flask(__name__)

# In-memory storage (use a database in production)
users_db = {
    "admin": {
        "password_hash": "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8",  # "password"
        "user_id": "admin_001",
        "features": ["basic_patching", "advanced_features", "admin_tools"],
        "expires_at": None  # Never expires
    },
    "demo": {
        "password_hash": "ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f",  # "demo123"
        "user_id": "demo_001", 
        "features": ["basic_patching"],
        "expires_at": int(time.time()) + (30 * 24 * 3600)  # 30 days
    }
}

licenses_db = {
    "DEMO-2024-001": {
        "user_id": "demo_001",
        "username": "demo_user",
        "features": ["basic_patching"],
        "expires_at": int(time.time()) + (30 * 24 * 3600),  # 30 days
        "machine_id": None,  # Allow any machine
        "max_machines": 1
    },
    "BETA-2024-002": {
        "user_id": "beta_001",
        "username": "beta_tester",
        "features": ["basic_patching", "advanced_features"],
        "expires_at": int(time.time()) + (90 * 24 * 3600),  # 90 days
        "machine_id": None,
        "max_machines": 3
    }
}

sessions_db = {}

@app.route('/api/v1/authenticate', methods=['POST'])
def authenticate():
    """Authenticate user with username/password"""
    try:
        data = request.get_json()
        username = data.get('username')
        password_hash = data.get('password_hash')
        machine_id = data.get('machine_id')
        app_version = data.get('app_version')
        
        if not username or not password_hash:
            return jsonify({
                'authenticated': False,
                'message': 'Username and password required'
            }), 400
        
        # Check if user exists
        if username not in users_db:
            return jsonify({
                'authenticated': False,
                'message': 'Invalid username or password'
            }), 401
        
        user = users_db[username]
        
        # Verify password
        if user['password_hash'] != password_hash:
            return jsonify({
                'authenticated': False,
                'message': 'Invalid username or password'
            }), 401
        
        # Check if account has expired
        if user.get('expires_at') and time.time() > user['expires_at']:
            return jsonify({
                'authenticated': False,
                'message': 'Account has expired'
            }), 401
        
        # Generate session token
        session_token = hashlib.sha256(f"{username}{time.time()}{machine_id}".encode()).hexdigest()
        
        # Store session
        sessions_db[session_token] = {
            'username': username,
            'user_id': user['user_id'],
            'machine_id': machine_id,
            'created_at': time.time(),
            'expires_at': time.time() + (24 * 3600)  # 24 hours
        }
        
        return jsonify({
            'authenticated': True,
            'user_id': user['user_id'],
            'username': username,
            'session_token': session_token,
            'expires_at': time.time() + (24 * 3600),
            'features': user['features'],
            'message': 'Authentication successful'
        })
        
    except Exception as e:
        return jsonify({
            'authenticated': False,
            'message': f'Server error: {str(e)}'
        }), 500

@app.route('/api/v1/validate-license', methods=['POST'])
def validate_license():
    """Validate license key"""
    try:
        data = request.get_json()
        license_key = data.get('license_key')
        machine_id = data.get('machine_id')
        app_version = data.get('app_version')
        
        if not license_key:
            return jsonify({
                'valid': False,
                'message': 'License key required'
            }), 400
        
        # Check if license exists
        if license_key not in licenses_db:
            return jsonify({
                'valid': False,
                'message': 'Invalid license key'
            }), 401
        
        license_data = licenses_db[license_key]
        
        # Check if license has expired
        if license_data.get('expires_at') and time.time() > license_data['expires_at']:
            return jsonify({
                'valid': False,
                'message': 'License has expired'
            }), 401
        
        # Check machine binding (if applicable)
        if license_data.get('machine_id') and license_data['machine_id'] != machine_id:
            return jsonify({
                'valid': False,
                'message': 'License is bound to a different machine'
            }), 401
        
        # Bind license to machine if not already bound
        if not license_data.get('machine_id'):
            license_data['machine_id'] = machine_id
        
        return jsonify({
            'valid': True,
            'user_id': license_data['user_id'],
            'username': license_data['username'],
            'expires_at': license_data['expires_at'],
            'features': license_data['features'],
            'message': 'License validated successfully'
        })
        
    except Exception as e:
        return jsonify({
            'valid': False,
            'message': f'Server error: {str(e)}'
        }), 500

@app.route('/api/v1/heartbeat', methods=['POST'])
def heartbeat():
    """Maintain session with heartbeat"""
    try:
        data = request.get_json()
        session_token = data.get('session_token')
        machine_id = data.get('machine_id')
        
        if not session_token:
            return jsonify({'success': False, 'message': 'Session token required'}), 400
        
        # Check if session exists
        if session_token not in sessions_db:
            return jsonify({'success': False, 'message': 'Invalid session'}), 401
        
        session = sessions_db[session_token]
        
        # Check if session has expired
        if time.time() > session['expires_at']:
            del sessions_db[session_token]
            return jsonify({'success': False, 'message': 'Session expired'}), 401
        
        # Check machine ID
        if session['machine_id'] != machine_id:
            return jsonify({'success': False, 'message': 'Invalid machine'}), 401
        
        # Extend session
        session['expires_at'] = time.time() + (24 * 3600)  # 24 hours
        
        return jsonify({
            'success': True,
            'message': 'Heartbeat successful'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500

@app.route('/api/v1/logout', methods=['POST'])
def logout():
    """Logout and invalidate session"""
    try:
        data = request.get_json()
        session_token = data.get('session_token')
        
        if session_token and session_token in sessions_db:
            del sessions_db[session_token]
        
        return jsonify({'success': True, 'message': 'Logged out successfully'})
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500

@app.route('/api/v1/status', methods=['GET'])
def status():
    """Server status endpoint"""
    return jsonify({
        'status': 'online',
        'timestamp': int(time.time()),
        'active_sessions': len(sessions_db),
        'registered_users': len(users_db),
        'active_licenses': len(licenses_db)
    })

@app.route('/api/v1/admin/users', methods=['GET'])
def list_users():
    """List all users (admin only)"""
    return jsonify({
        'users': [
            {
                'username': username,
                'user_id': user['user_id'],
                'features': user['features'],
                'expires_at': user.get('expires_at')
            }
            for username, user in users_db.items()
        ]
    })

@app.route('/api/v1/admin/licenses', methods=['GET'])
def list_licenses():
    """List all licenses (admin only)"""
    return jsonify({
        'licenses': [
            {
                'license_key': key,
                'username': license['username'],
                'features': license['features'],
                'expires_at': license['expires_at'],
                'machine_id': license.get('machine_id')
            }
            for key, license in licenses_db.items()
        ]
    })

@app.route('/api/v1/admin/create-user', methods=['POST'])
def create_user():
    """Create new user (admin only)"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        features = data.get('features', ['basic_patching'])
        expires_days = data.get('expires_days')
        
        if not username or not password:
            return jsonify({'success': False, 'message': 'Username and password required'}), 400
        
        if username in users_db:
            return jsonify({'success': False, 'message': 'User already exists'}), 409
        
        # Hash password
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        # Calculate expiration
        expires_at = None
        if expires_days:
            expires_at = int(time.time()) + (expires_days * 24 * 3600)
        
        # Create user
        users_db[username] = {
            'password_hash': password_hash,
            'user_id': f"{username}_001",
            'features': features,
            'expires_at': expires_at
        }
        
        return jsonify({
            'success': True,
            'message': f'User {username} created successfully',
            'user_id': users_db[username]['user_id']
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500

@app.route('/api/v1/admin/create-license', methods=['POST'])
def create_license():
    """Create new license (admin only)"""
    try:
        data = request.get_json()
        username = data.get('username')
        features = data.get('features', ['basic_patching'])
        expires_days = data.get('expires_days', 30)
        max_machines = data.get('max_machines', 1)
        
        if not username:
            return jsonify({'success': False, 'message': 'Username required'}), 400
        
        # Generate license key
        import random
        import string
        license_key = f"{username.upper()}-{random.randint(1000, 9999)}-{''.join(random.choices(string.ascii_uppercase + string.digits, k=4))}"
        
        # Calculate expiration
        expires_at = int(time.time()) + (expires_days * 24 * 3600)
        
        # Create license
        licenses_db[license_key] = {
            'user_id': f"{username}_001",
            'username': username,
            'features': features,
            'expires_at': expires_at,
            'machine_id': None,
            'max_machines': max_machines
        }
        
        return jsonify({
            'success': True,
            'message': f'License created successfully',
            'license_key': license_key,
            'expires_at': expires_at
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500

if __name__ == '__main__':
    print("Starting ROTMG Patch Utility Authentication Server...")
    print("Available endpoints:")
    print("  POST /api/v1/authenticate - User authentication")
    print("  POST /api/v1/validate-license - License validation")
    print("  POST /api/v1/heartbeat - Session heartbeat")
    print("  POST /api/v1/logout - Logout")
    print("  GET  /api/v1/status - Server status")
    print("  GET  /api/v1/admin/users - List users")
    print("  GET  /api/v1/admin/licenses - List licenses")
    print("  POST /api/v1/admin/create-user - Create user")
    print("  POST /api/v1/admin/create-license - Create license")
    print("\nDefault users:")
    print("  admin / password")
    print("  demo / demo123")
    print("\nDefault licenses:")
    print("  DEMO-2024-001")
    print("  BETA-2024-002")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
