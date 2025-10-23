"""
Server Authentication System for ROTMG Patch Utility Tool
Handles remote authentication, license validation, and access control
"""

import requests
import json
import hashlib
import time
import tkinter as tk
from tkinter import messagebox, ttk
from cryptography.fernet import Fernet
import base64
import os


class ServerAuthManager:
    """Manages server-based authentication and license validation"""
    
    def __init__(self):
        self.config_dir = os.path.join(os.path.expanduser("~"), ".rotmg_patch_utility")
        self.license_file = os.path.join(self.config_dir, "license.json")
        self.server_config_file = os.path.join(self.config_dir, "server_config.json")
        
        # Default server configuration
        self.default_server_config = {
            "auth_server_url": "https://api.rotmg-patch-utility.com",  # Replace with your server
            "license_endpoint": "/api/v1/validate-license",
            "auth_endpoint": "/api/v1/authenticate",
            "heartbeat_endpoint": "/api/v1/heartbeat",
            "timeout": 30,
            "retry_attempts": 3,
            "offline_mode_days": 7,  # Allow offline use for 7 days
            "heartbeat_interval": 3600,  # Check every hour
            "enable_offline_mode": True
        }
        
        # Load server configuration
        self.server_config = self._load_server_config()
        
        # License data
        self.license_data = self._load_license_data()
        
    def _load_server_config(self):
        """Load server configuration"""
        if os.path.exists(self.server_config_file):
            try:
                with open(self.server_config_file, 'r') as f:
                    config = json.load(f)
                    # Merge with defaults
                    for key, value in self.default_server_config.items():
                        if key not in config:
                            config[key] = value
                    return config
            except (json.JSONDecodeError, IOError):
                pass
        
        # Save default config
        self._save_server_config(self.default_server_config)
        return self.default_server_config.copy()
    
    def _save_server_config(self, config):
        """Save server configuration"""
        try:
            with open(self.server_config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except IOError as e:
            print(f"Error saving server config: {e}")
    
    def _load_license_data(self):
        """Load license data"""
        if os.path.exists(self.license_file):
            try:
                with open(self.license_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return None
    
    def _save_license_data(self, data):
        """Save license data"""
        try:
            with open(self.license_file, 'w') as f:
                json.dump(data, f, indent=2)
        except IOError as e:
            print(f"Error saving license data: {e}")
    
    def validate_license(self, license_key: str) -> dict:
        """Validate license key with server"""
        try:
            # Prepare request data
            request_data = {
                "license_key": license_key,
                "machine_id": self._get_machine_id(),
                "app_version": "1.0.0",
                "timestamp": int(time.time())
            }
            
            # Make request to server
            response = requests.post(
                f"{self.server_config['auth_server_url']}{self.server_config['license_endpoint']}",
                json=request_data,
                timeout=self.server_config['timeout']
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('valid'):
                    # Save license data
                    license_data = {
                        "license_key": license_key,
                        "user_id": result.get('user_id'),
                        "username": result.get('username'),
                        "expires_at": result.get('expires_at'),
                        "features": result.get('features', []),
                        "last_validation": int(time.time()),
                        "machine_id": self._get_machine_id()
                    }
                    self._save_license_data(license_data)
                    self.license_data = license_data
                    
                    return {
                        "success": True,
                        "message": "License validated successfully",
                        "user_data": license_data
                    }
                else:
                    return {
                        "success": False,
                        "message": result.get('message', 'Invalid license key')
                    }
            else:
                return {
                    "success": False,
                    "message": f"Server error: {response.status_code}"
                }
                
        except requests.exceptions.RequestException as e:
            # Check if we can use offline mode
            if self._can_use_offline_mode():
                return {
                    "success": True,
                    "message": "Using offline mode (server unavailable)",
                    "offline": True
                }
            else:
                return {
                    "success": False,
                    "message": f"Network error: {str(e)}"
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"Validation error: {str(e)}"
            }
    
    def authenticate_user(self, username: str, password: str) -> dict:
        """Authenticate user with server"""
        try:
            # Hash password for transmission
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            
            request_data = {
                "username": username,
                "password_hash": password_hash,
                "machine_id": self._get_machine_id(),
                "app_version": "1.0.0",
                "timestamp": int(time.time())
            }
            
            response = requests.post(
                f"{self.server_config['auth_server_url']}{self.server_config['auth_endpoint']}",
                json=request_data,
                timeout=self.server_config['timeout']
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('authenticated'):
                    # Save authentication data
                    auth_data = {
                        "username": username,
                        "user_id": result.get('user_id'),
                        "session_token": result.get('session_token'),
                        "expires_at": result.get('expires_at'),
                        "features": result.get('features', []),
                        "last_auth": int(time.time()),
                        "machine_id": self._get_machine_id()
                    }
                    self._save_license_data(auth_data)
                    self.license_data = auth_data
                    
                    return {
                        "success": True,
                        "message": "Authentication successful",
                        "user_data": auth_data
                    }
                else:
                    return {
                        "success": False,
                        "message": result.get('message', 'Invalid credentials')
                    }
            else:
                return {
                    "success": False,
                    "message": f"Server error: {response.status_code}"
                }
                
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "message": f"Network error: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Authentication error: {str(e)}"
            }
    
    def send_heartbeat(self) -> bool:
        """Send heartbeat to server to maintain session"""
        if not self.license_data or not self.license_data.get('session_token'):
            return False
        
        try:
            request_data = {
                "session_token": self.license_data['session_token'],
                "machine_id": self._get_machine_id(),
                "timestamp": int(time.time())
            }
            
            response = requests.post(
                f"{self.server_config['auth_server_url']}{self.server_config['heartbeat_endpoint']}",
                json=request_data,
                timeout=self.server_config['timeout']
            )
            
            return response.status_code == 200
            
        except Exception:
            return False
    
    def is_license_valid(self) -> bool:
        """Check if current license is valid"""
        if not self.license_data:
            return False
        
        # Check if license has expired
        if self.license_data.get('expires_at'):
            if time.time() > self.license_data['expires_at']:
                return False
        
        # Check if offline mode is still valid
        if self._is_offline_mode():
            return self._can_use_offline_mode()
        
        # Check if we need to validate with server
        last_validation = self.license_data.get('last_validation', 0)
        if time.time() - last_validation > self.server_config['heartbeat_interval']:
            # Try to send heartbeat
            if not self.send_heartbeat():
                # If heartbeat fails, check offline mode
                return self._can_use_offline_mode()
        
        return True
    
    def _is_offline_mode(self) -> bool:
        """Check if currently in offline mode"""
        return self.license_data and self.license_data.get('offline', False)
    
    def _can_use_offline_mode(self) -> bool:
        """Check if offline mode is allowed"""
        if not self.server_config.get('enable_offline_mode', True):
            return False
        
        if not self.license_data:
            return False
        
        last_validation = self.license_data.get('last_validation', 0)
        offline_days = self.server_config.get('offline_mode_days', 7)
        
        return time.time() - last_validation < (offline_days * 24 * 3600)
    
    def _get_machine_id(self) -> str:
        """Get unique machine identifier"""
        import platform
        import uuid
        
        # Get system information
        system_info = f"{platform.system()}-{platform.machine()}-{platform.processor()}"
        
        # Generate UUID based on system info
        machine_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, system_info))
        return machine_id
    
    def logout(self):
        """Logout and clear license data"""
        if self.license_data and self.license_data.get('session_token'):
            try:
                # Notify server of logout
                requests.post(
                    f"{self.server_config['auth_server_url']}/api/v1/logout",
                    json={"session_token": self.license_data['session_token']},
                    timeout=self.server_config['timeout']
                )
            except Exception:
                pass  # Ignore logout errors
        
        # Clear local data
        if os.path.exists(self.license_file):
            try:
                os.remove(self.license_file)
            except IOError:
                pass
        
        self.license_data = None
    
    def get_current_user(self) -> str:
        """Get current logged-in username"""
        if self.license_data:
            return self.license_data.get('username')
        return None
    
    def update_server_config(self, **kwargs):
        """Update server configuration"""
        for key, value in kwargs.items():
            if key in self.server_config:
                self.server_config[key] = value
        self._save_server_config(self.server_config)


class AccessCodeManager:
    """Secure access code manager with encrypted storage"""
    
    def __init__(self):
        self.config_dir = os.path.join(os.path.expanduser("~"), ".rotmg_patch_utility")
        self.access_codes_file = os.path.join(self.config_dir, "access_codes.enc")
        self.key_file = os.path.join(self.config_dir, "access_key.enc")
        
        # Generate or load encryption key
        self.encryption_key = self._get_or_create_key()
        
        # Load access codes
        self.access_codes = self._load_access_codes()
        
    def _get_or_create_key(self):
        """Get or create encryption key"""
        if os.path.exists(self.key_file):
            try:
                with open(self.key_file, 'rb') as f:
                    return f.read()
            except IOError:
                pass
        
        # Generate new key
        key = Fernet.generate_key()
        try:
            with open(self.key_file, 'wb') as f:
                f.write(key)
        except IOError:
            pass
        
        return key
    
    def _encrypt_data(self, data):
        """Encrypt data"""
        f = Fernet(self.encryption_key)
        encrypted_data = f.encrypt(json.dumps(data).encode())
        return encrypted_data
    
    def _decrypt_data(self, encrypted_data):
        """Decrypt data"""
        try:
            f = Fernet(self.encryption_key)
            decrypted_data = f.decrypt(encrypted_data)
            return json.loads(decrypted_data.decode())
        except Exception:
            return None
    
    def _load_access_codes(self):
        """Load encrypted access codes"""
        if os.path.exists(self.access_codes_file):
            try:
                with open(self.access_codes_file, 'rb') as f:
                    encrypted_data = f.read()
                return self._decrypt_data(encrypted_data) or self._get_default_codes()
            except IOError:
                pass
        
        # Create default codes
        default_codes = self._get_default_codes()
        self._save_access_codes(default_codes)
        return default_codes
    
    def _get_default_codes(self):
        """Get minimal default access codes (only public demo code)"""
        return {
            "codes": {
                "DEMO-2024-001": {
                    "name": "Demo Access",
                    "expires_at": None,
                    "features": ["basic_patching"],
                    "max_uses": 100,
                    "used_count": 0,
                    "created_at": int(time.time()),
                    "public": True  # Only public demo code
                }
            },
            "settings": {
                "code_length": 12,
                "require_uppercase": True,
                "require_numbers": True,
                "require_dashes": True,
                "max_attempts": 3,
                "lockout_duration": 300
            }
        }
    
    def _save_access_codes(self, data):
        """Save encrypted access codes"""
        try:
            encrypted_data = self._encrypt_data(data)
            with open(self.access_codes_file, 'wb') as f:
                f.write(encrypted_data)
        except IOError as e:
            print(f"Error saving access codes: {e}")
    
    def validate_access_code(self, code: str) -> dict:
        """Validate access code"""
        if not code or code not in self.access_codes["codes"]:
            return {
                "success": False,
                "message": "Invalid access code"
            }
        
        code_data = self.access_codes["codes"][code]
        
        # Check if code has expired
        if code_data.get("expires_at") and time.time() > code_data["expires_at"]:
            return {
                "success": False,
                "message": "Access code has expired"
            }
        
        # Check if code has reached max uses
        if code_data.get("max_uses") and code_data["used_count"] >= code_data["max_uses"]:
            return {
                "success": False,
                "message": "Access code has reached maximum uses"
            }
        
        # Increment usage count
        code_data["used_count"] += 1
        self._save_access_codes(self.access_codes)
        
        return {
            "success": True,
            "message": f"Access granted: {code_data['name']}",
            "code_data": code_data
        }
    
    def add_access_code(self, code: str, name: str, features: list, expires_days: int = None, max_uses: int = None, admin_key: str = None):
        """Add a new access code (requires admin authentication)"""
        # Verify admin key
        if not self._verify_admin_key(admin_key):
            return False
        
        expires_at = None
        if expires_days:
            expires_at = int(time.time()) + (expires_days * 24 * 3600)
        
        self.access_codes["codes"][code] = {
            "name": name,
            "expires_at": expires_at,
            "features": features,
            "max_uses": max_uses,
            "used_count": 0,
            "created_at": int(time.time()),
            "public": False  # Admin-created codes are not public
        }
        
        self._save_access_codes(self.access_codes)
        return True
    
    def _verify_admin_key(self, admin_key: str) -> bool:
        """Verify admin key for code creation"""
        # In production, this should be more secure
        # For now, use a simple key verification
        expected_key = "admin_secret_key_2024"  # Should be configurable
        return admin_key == expected_key
    
    def list_public_codes(self):
        """List only public access codes (what users can see)"""
        public_codes = {}
        for code, data in self.access_codes["codes"].items():
            if data.get("public", False):
                public_codes[code] = data
        return public_codes
    
    def generate_access_code(self, name: str, features: list, expires_days: int = None, max_uses: int = None, admin_key: str = None) -> str:
        """Generate a new access code (requires admin authentication)"""
        # Verify admin key
        if not self._verify_admin_key(admin_key):
            raise PermissionError("Admin authentication required to generate access codes")
        
        import random
        import string
        
        # Generate random code
        code_length = self.access_codes["settings"]["code_length"]
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=code_length-3))
        
        # Add dashes if required
        if self.access_codes["settings"]["require_dashes"]:
            code = f"{code[:4]}-{code[4:8]}-{code[8:]}"
        
        # Calculate expiration
        expires_at = None
        if expires_days:
            expires_at = int(time.time()) + (expires_days * 24 * 3600)
        
        # Add to codes
        self.access_codes["codes"][code] = {
            "name": name,
            "expires_at": expires_at,
            "features": features,
            "max_uses": max_uses,
            "used_count": 0,
            "created_at": int(time.time()),
            "public": False  # Admin-created codes are not public by default
        }
        
        self._save_access_codes(self.access_codes)
        return code
    
    def revoke_access_code(self, code: str) -> bool:
        """Revoke an access code"""
        if code in self.access_codes["codes"]:
            del self.access_codes["codes"][code]
            self._save_access_codes(self.access_codes)
            return True
        return False
    
    def list_access_codes(self, admin_key: str = None) -> dict:
        """List access codes (admin key required to see all codes)"""
        if admin_key and self._verify_admin_key(admin_key):
            # Admin can see all codes
            return self.access_codes["codes"].copy()
        else:
            # Regular users can only see public codes
            return self.list_public_codes()


class ServerAuthDialog:
    """Server authentication dialog"""
    
    def __init__(self, parent, auth_manager: ServerAuthManager):
        self.parent = parent
        self.auth_manager = auth_manager
        self.result = None
        self.dialog = None
        
    def show(self):
        """Show server auth dialog"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Server Authentication")
        self.dialog.geometry("450x350")
        self.dialog.resizable(False, False)
        
        # Center the dialog
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        self.create_widgets()
        
        # Make dialog modal
        self.parent.wait_window(self.dialog)
        
        return self.result
    
    def create_widgets(self):
        """Create server auth dialog widgets"""
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(main_frame, text="Server Authentication", 
                              font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Auth type selection
        auth_frame = ttk.LabelFrame(main_frame, text="Authentication Method", padding="10")
        auth_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.auth_type = tk.StringVar(value="license")
        
        ttk.Radiobutton(auth_frame, text="License Key", variable=self.auth_type, 
                       value="license", command=self.toggle_auth_type).pack(anchor=tk.W)
        ttk.Radiobutton(auth_frame, text="Username/Password", variable=self.auth_type, 
                       value="credentials", command=self.toggle_auth_type).pack(anchor=tk.W)
        
        # Input frame
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill=tk.X, pady=(0, 15))
        
        # License key input
        self.license_frame = ttk.Frame(input_frame)
        self.license_frame.pack(fill=tk.X)
        
        ttk.Label(self.license_frame, text="License Key:").pack(anchor=tk.W)
        self.license_var = tk.StringVar()
        license_entry = ttk.Entry(self.license_frame, textvariable=self.license_var, width=40)
        license_entry.pack(fill=tk.X, pady=(5, 0))
        
        # Username/Password input
        self.credentials_frame = ttk.Frame(input_frame)
        
        ttk.Label(self.credentials_frame, text="Username:").pack(anchor=tk.W)
        self.username_var = tk.StringVar()
        username_entry = ttk.Entry(self.credentials_frame, textvariable=self.username_var, width=40)
        username_entry.pack(fill=tk.X, pady=(5, 10))
        
        ttk.Label(self.credentials_frame, text="Password:").pack(anchor=tk.W)
        self.password_var = tk.StringVar()
        password_entry = ttk.Entry(self.credentials_frame, textvariable=self.password_var, 
                                  show="*", width=40)
        password_entry.pack(fill=tk.X, pady=(5, 0))
        
        # Server settings
        settings_frame = ttk.LabelFrame(main_frame, text="Server Settings", padding="10")
        settings_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(settings_frame, text="Server URL:").pack(anchor=tk.W)
        self.server_url_var = tk.StringVar(value=self.auth_manager.server_config['auth_server_url'])
        server_entry = ttk.Entry(settings_frame, textvariable=self.server_url_var, width=40)
        server_entry.pack(fill=tk.X, pady=(5, 0))
        
        # Buttons
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=(10, 0))
        
        authenticate_btn = ttk.Button(buttons_frame, text="Authenticate", 
                                     command=self.authenticate, style="Accent.TButton")
        authenticate_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        cancel_btn = ttk.Button(buttons_frame, text="Cancel", command=self.cancel)
        cancel_btn.pack(side=tk.RIGHT)
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="", foreground="red")
        self.status_label.pack(pady=(10, 0))
        
        # Initialize
        self.toggle_auth_type()
        license_entry.focus()
    
    def toggle_auth_type(self):
        """Toggle between license and credentials input"""
        if self.auth_type.get() == "license":
            self.license_frame.pack(fill=tk.X)
            self.credentials_frame.pack_forget()
        else:
            self.license_frame.pack_forget()
            self.credentials_frame.pack(fill=tk.X)
    
    def authenticate(self):
        """Handle authentication"""
        # Update server URL
        self.auth_manager.update_server_config(
            auth_server_url=self.server_url_var.get()
        )
        
        if self.auth_type.get() == "license":
            license_key = self.license_var.get().strip()
            if not license_key:
                self.status_label.config(text="Please enter a license key")
                return
            
            result = self.auth_manager.validate_license(license_key)
        else:
            username = self.username_var.get().strip()
            password = self.password_var.get()
            if not username or not password:
                self.status_label.config(text="Please enter username and password")
                return
            
            result = self.auth_manager.authenticate_user(username, password)
        
        if result["success"]:
            self.result = {
                "action": "authenticate",
                "user_data": result["user_data"],
                "offline": result.get("offline", False)
            }
            self.dialog.destroy()
        else:
            self.status_label.config(text=result["message"])
    
    def cancel(self):
        """Cancel authentication"""
        self.result = {"action": "cancel"}
        self.dialog.destroy()


class AccessCodeDialog:
    """Access code dialog"""
    
    def __init__(self, parent, code_manager: AccessCodeManager):
        self.parent = parent
        self.code_manager = code_manager
        self.result = None
        self.dialog = None
        
    def show(self):
        """Show access code dialog"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Access Code")
        self.dialog.geometry("400x250")
        self.dialog.resizable(False, False)
        
        # Center the dialog
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        self.create_widgets()
        
        # Make dialog modal
        self.parent.wait_window(self.dialog)
        
        return self.result
    
    def create_widgets(self):
        """Create access code dialog widgets"""
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(main_frame, text="Enter Access Code", 
                              font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Instructions
        instructions = tk.Label(main_frame, 
                               text="Enter your access code to use the application.\nContact the administrator if you don't have one.",
                               justify=tk.CENTER, wraplength=350)
        instructions.pack(pady=(0, 20))
        
        # Input frame
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(input_frame, text="Access Code:").pack(anchor=tk.W)
        self.code_var = tk.StringVar()
        code_entry = ttk.Entry(input_frame, textvariable=self.code_var, width=30, 
                              font=("Arial", 12))
        code_entry.pack(fill=tk.X, pady=(5, 0))
        
        # Buttons
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=(10, 0))
        
        validate_btn = ttk.Button(buttons_frame, text="Validate Code", 
                                 command=self.validate_code, style="Accent.TButton")
        validate_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        cancel_btn = ttk.Button(buttons_frame, text="Cancel", command=self.cancel)
        cancel_btn.pack(side=tk.RIGHT)
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="", foreground="red")
        self.status_label.pack(pady=(10, 0))
        
        # Focus on code entry
        code_entry.focus()
        
        # Bind Enter key
        self.dialog.bind('<Return>', lambda e: self.validate_code())
    
    def validate_code(self):
        """Validate access code"""
        code = self.code_var.get().strip()
        if not code:
            self.status_label.config(text="Please enter an access code")
            return
        
        result = self.code_manager.validate_access_code(code)
        
        if result["success"]:
            self.result = {
                "action": "validate",
                "code_data": result["code_data"]
            }
            self.dialog.destroy()
        else:
            self.status_label.config(text=result["message"])
    
    def cancel(self):
        """Cancel validation"""
        self.result = {"action": "cancel"}
        self.dialog.destroy()
