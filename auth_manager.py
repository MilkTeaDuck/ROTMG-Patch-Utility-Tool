"""
Authentication Manager for ROTMG Patch Utility Tool
Handles user login, credential storage, and session management
"""

import os
import json
import hashlib
import base64
import tkinter as tk
from tkinter import messagebox
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class AuthManager:
    """Manages user authentication and secure credential storage"""
    
    def __init__(self):
        self.config_dir = os.path.join(os.path.expanduser("~"), ".rotmg_patch_utility")
        self.config_file = os.path.join(self.config_dir, "config.json")
        self.credentials_file = os.path.join(self.config_dir, "credentials.enc")
        self.session_file = os.path.join(self.config_dir, "session.json")
        
        # Ensure config directory exists
        os.makedirs(self.config_dir, exist_ok=True)
        
        # Load configuration
        self.config = self._load_config()
        
    def _load_config(self):
        """Load application configuration"""
        default_config = {
            "remember_me": False,
            "auto_login": False,
            "session_timeout": 3600,  # 1 hour in seconds
            "max_login_attempts": 3,
            "lockout_duration": 300,  # 5 minutes
            "password_min_length": 8,
            "require_uppercase": True,
            "require_lowercase": True,
            "require_numbers": True,
            "require_special_chars": False
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    # Merge with defaults for any missing keys
                    for key, value in default_config.items():
                        if key not in config:
                            config[key] = value
                    return config
            except (json.JSONDecodeError, IOError):
                pass
        
        # Save default config
        self._save_config(default_config)
        return default_config
    
    def _save_config(self, config):
        """Save application configuration"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except IOError as e:
            print(f"Error saving config: {e}")
    
    def _generate_key(self, password: str, salt: bytes) -> bytes:
        """Generate encryption key from password and salt"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))
    
    def _encrypt_data(self, data: str, password: str) -> tuple:
        """Encrypt data with password"""
        salt = os.urandom(16)
        key = self._generate_key(password, salt)
        f = Fernet(key)
        encrypted_data = f.encrypt(data.encode())
        return encrypted_data, salt
    
    def _decrypt_data(self, encrypted_data: bytes, password: str, salt: bytes) -> str:
        """Decrypt data with password"""
        key = self._generate_key(password, salt)
        f = Fernet(key)
        decrypted_data = f.decrypt(encrypted_data)
        return decrypted_data.decode()
    
    def register_user(self, username: str, password: str, email: str = "") -> bool:
        """Register a new user"""
        if not self._validate_password(password):
            return False
        
        if os.path.exists(self.credentials_file):
            return False  # User already exists
        
        # Hash password for storage
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        user_data = {
            "username": username,
            "password_hash": password_hash,
            "email": email,
            "created_at": str(os.path.getctime(self.config_file)),
            "last_login": None,
            "login_attempts": 0,
            "locked_until": None
        }
        
        try:
            encrypted_data, salt = self._encrypt_data(json.dumps(user_data), password)
            
            with open(self.credentials_file, 'wb') as f:
                f.write(salt + encrypted_data)
            
            return True
        except Exception as e:
            print(f"Error registering user: {e}")
            return False
    
    def authenticate_user(self, username: str, password: str) -> bool:
        """Authenticate user credentials"""
        if not os.path.exists(self.credentials_file):
            return False
        
        try:
            with open(self.credentials_file, 'rb') as f:
                data = f.read()
            
            salt = data[:16]
            encrypted_data = data[16:]
            
            decrypted_data = self._decrypt_data(encrypted_data, password, salt)
            user_data = json.loads(decrypted_data)
            
            # Verify username and password
            if user_data["username"] != username:
                return False
            
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            if user_data["password_hash"] != password_hash:
                return False
            
            # Check if account is locked
            if user_data.get("locked_until"):
                import time
                if time.time() < user_data["locked_until"]:
                    return False
            
            # Update last login
            user_data["last_login"] = str(time.time())
            user_data["login_attempts"] = 0
            user_data["locked_until"] = None
            
            # Save updated data
            encrypted_data, salt = self._encrypt_data(json.dumps(user_data), password)
            with open(self.credentials_file, 'wb') as f:
                f.write(salt + encrypted_data)
            
            # Create session
            self._create_session(username)
            return True
            
        except Exception as e:
            print(f"Error authenticating user: {e}")
            return False
    
    def _create_session(self, username: str):
        """Create user session"""
        import time
        session_data = {
            "username": username,
            "created_at": time.time(),
            "expires_at": time.time() + self.config["session_timeout"]
        }
        
        try:
            with open(self.session_file, 'w') as f:
                json.dump(session_data, f)
        except IOError as e:
            print(f"Error creating session: {e}")
    
    def is_session_valid(self) -> bool:
        """Check if current session is valid"""
        if not os.path.exists(self.session_file):
            return False
        
        try:
            import time
            with open(self.session_file, 'r') as f:
                session_data = json.load(f)
            
            return time.time() < session_data["expires_at"]
        except (json.JSONDecodeError, IOError):
            return False
    
    def logout(self):
        """Logout user and clear session"""
        if os.path.exists(self.session_file):
            try:
                os.remove(self.session_file)
            except IOError:
                pass
    
    def _validate_password(self, password: str) -> bool:
        """Validate password strength"""
        if len(password) < self.config["password_min_length"]:
            return False
        
        if self.config["require_uppercase"] and not any(c.isupper() for c in password):
            return False
        
        if self.config["require_lowercase"] and not any(c.islower() for c in password):
            return False
        
        if self.config["require_numbers"] and not any(c.isdigit() for c in password):
            return False
        
        if self.config["require_special_chars"] and not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            return False
        
        return True
    
    def get_current_user(self) -> str:
        """Get current logged-in username"""
        if not self.is_session_valid():
            return None
        
        try:
            with open(self.session_file, 'r') as f:
                session_data = json.load(f)
            return session_data["username"]
        except (json.JSONDecodeError, IOError):
            return None
    
    def update_config(self, **kwargs):
        """Update configuration settings"""
        for key, value in kwargs.items():
            if key in self.config:
                self.config[key] = value
        self._save_config(self.config)


class LoginDialog:
    """Login dialog window"""
    
    def __init__(self, parent, auth_manager: AuthManager):
        self.parent = parent
        self.auth_manager = auth_manager
        self.result = None
        self.dialog = None
        
    def show(self):
        """Show login dialog"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("ROTMG Patch Utility - Login")
        self.dialog.geometry("400x300")
        self.dialog.resizable(False, False)
        
        # Center the dialog
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Make dialog modal
        self.parent.wait_window(self.dialog)
        
        return self.result
    
    def create_widgets(self):
        """Create login dialog widgets"""
        # Main frame
        main_frame = tk.Frame(self.dialog, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(main_frame, text="ROTMG Patch Utility", 
                              font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Login frame
        login_frame = tk.Frame(main_frame)
        login_frame.pack(fill=tk.X, pady=10)
        
        # Username
        tk.Label(login_frame, text="Username:").pack(anchor=tk.W)
        self.username_var = tk.StringVar()
        username_entry = tk.Entry(login_frame, textvariable=self.username_var, width=30)
        username_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Password
        tk.Label(login_frame, text="Password:").pack(anchor=tk.W)
        self.password_var = tk.StringVar()
        password_entry = tk.Entry(login_frame, textvariable=self.password_var, 
                                 show="*", width=30)
        password_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Remember me checkbox
        self.remember_var = tk.BooleanVar()
        remember_check = tk.Checkbutton(login_frame, text="Remember me", 
                                       variable=self.remember_var)
        remember_check.pack(anchor=tk.W, pady=(0, 10))
        
        # Buttons frame
        buttons_frame = tk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=10)
        
        # Login button
        login_btn = tk.Button(buttons_frame, text="Login", 
                             command=self.login, bg="#4CAF50", fg="white",
                             font=("Arial", 10, "bold"))
        login_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Register button
        register_btn = tk.Button(buttons_frame, text="Register", 
                                command=self.show_register, bg="#2196F3", fg="white")
        register_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Cancel button
        cancel_btn = tk.Button(buttons_frame, text="Cancel", 
                              command=self.cancel, bg="#f44336", fg="white")
        cancel_btn.pack(side=tk.RIGHT)
        
        # Status label
        self.status_label = tk.Label(main_frame, text="", fg="red")
        self.status_label.pack(pady=(10, 0))
        
        # Focus on username entry
        username_entry.focus()
        
        # Bind Enter key to login
        self.dialog.bind('<Return>', lambda e: self.login())
    
    def login(self):
        """Handle login attempt"""
        username = self.username_var.get().strip()
        password = self.password_var.get()
        
        if not username or not password:
            self.status_label.config(text="Please enter both username and password")
            return
        
        if self.auth_manager.authenticate_user(username, password):
            self.result = {"action": "login", "username": username, 
                          "remember": self.remember_var.get()}
            self.dialog.destroy()
        else:
            self.status_label.config(text="Invalid username or password")
    
    def show_register(self):
        """Show registration dialog"""
        register_dialog = RegisterDialog(self.dialog, self.auth_manager)
        result = register_dialog.show()
        
        if result and result.get("action") == "register":
            self.status_label.config(text="Registration successful! Please login.")
    
    def cancel(self):
        """Cancel login"""
        self.result = {"action": "cancel"}
        self.dialog.destroy()


class RegisterDialog:
    """Registration dialog window"""
    
    def __init__(self, parent, auth_manager: AuthManager):
        self.parent = parent
        self.auth_manager = auth_manager
        self.result = None
        self.dialog = None
        
    def show(self):
        """Show registration dialog"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Register New User")
        self.dialog.geometry("400x400")
        self.dialog.resizable(False, False)
        
        # Center the dialog
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        self.create_widgets()
        
        # Make dialog modal
        self.parent.wait_window(self.dialog)
        
        return self.result
    
    def create_widgets(self):
        """Create registration dialog widgets"""
        # Main frame
        main_frame = tk.Frame(self.dialog, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(main_frame, text="Register New User", 
                              font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Form frame
        form_frame = tk.Frame(main_frame)
        form_frame.pack(fill=tk.X, pady=10)
        
        # Username
        tk.Label(form_frame, text="Username:").pack(anchor=tk.W)
        self.username_var = tk.StringVar()
        username_entry = tk.Entry(form_frame, textvariable=self.username_var, width=30)
        username_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Email
        tk.Label(form_frame, text="Email (optional):").pack(anchor=tk.W)
        self.email_var = tk.StringVar()
        email_entry = tk.Entry(form_frame, textvariable=self.email_var, width=30)
        email_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Password
        tk.Label(form_frame, text="Password:").pack(anchor=tk.W)
        self.password_var = tk.StringVar()
        password_entry = tk.Entry(form_frame, textvariable=self.password_var, 
                                 show="*", width=30)
        password_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Confirm Password
        tk.Label(form_frame, text="Confirm Password:").pack(anchor=tk.W)
        self.confirm_password_var = tk.StringVar()
        confirm_password_entry = tk.Entry(form_frame, textvariable=self.confirm_password_var, 
                                        show="*", width=30)
        confirm_password_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Password requirements
        requirements_text = (
            f"Password must be at least {self.auth_manager.config['password_min_length']} characters long"
        )
        if self.auth_manager.config['require_uppercase']:
            requirements_text += ", contain uppercase letters"
        if self.auth_manager.config['require_lowercase']:
            requirements_text += ", contain lowercase letters"
        if self.auth_manager.config['require_numbers']:
            requirements_text += ", contain numbers"
        if self.auth_manager.config['require_special_chars']:
            requirements_text += ", contain special characters"
        
        requirements_label = tk.Label(form_frame, text=requirements_text, 
                                   font=("Arial", 8), fg="gray", wraplength=350)
        requirements_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Buttons frame
        buttons_frame = tk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=10)
        
        # Register button
        register_btn = tk.Button(buttons_frame, text="Register", 
                                command=self.register, bg="#4CAF50", fg="white",
                                font=("Arial", 10, "bold"))
        register_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Cancel button
        cancel_btn = tk.Button(buttons_frame, text="Cancel", 
                              command=self.cancel, bg="#f44336", fg="white")
        cancel_btn.pack(side=tk.RIGHT)
        
        # Status label
        self.status_label = tk.Label(main_frame, text="", fg="red")
        self.status_label.pack(pady=(10, 0))
        
        # Focus on username entry
        username_entry.focus()
        
        # Bind Enter key to register
        self.dialog.bind('<Return>', lambda e: self.register())
    
    def register(self):
        """Handle registration attempt"""
        username = self.username_var.get().strip()
        email = self.email_var.get().strip()
        password = self.password_var.get()
        confirm_password = self.confirm_password_var.get()
        
        if not username or not password:
            self.status_label.config(text="Please enter username and password")
            return
        
        if password != confirm_password:
            self.status_label.config(text="Passwords do not match")
            return
        
        if not self.auth_manager._validate_password(password):
            self.status_label.config(text="Password does not meet requirements")
            return
        
        if self.auth_manager.register_user(username, password, email):
            self.result = {"action": "register", "username": username}
            self.dialog.destroy()
        else:
            self.status_label.config(text="Registration failed. User may already exist.")
    
    def cancel(self):
        """Cancel registration"""
        self.result = {"action": "cancel"}
        self.dialog.destroy()
