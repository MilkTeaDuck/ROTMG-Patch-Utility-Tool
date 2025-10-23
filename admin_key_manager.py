"""
Secure Admin Key Management for ROTMG Patch Utility Tool
Handles secure storage and verification of admin keys
"""

import os
import json
import hashlib
import secrets
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64


class AdminKeyManager:
    """Manages secure admin key storage and verification"""
    
    def __init__(self):
        self.config_dir = os.path.join(os.path.expanduser("~"), ".rotmg_patch_utility")
        self.admin_key_file = os.path.join(self.config_dir, "admin_key.enc")
        self.admin_config_file = os.path.join(self.config_dir, "admin_config.json")
        
        # Load or create admin configuration
        self.admin_config = self._load_admin_config()
        
    def _load_admin_config(self):
        """Load admin configuration"""
        default_config = {
            "admin_key_hash": None,
            "key_salt": None,
            "created_at": None,
            "last_used": None,
            "key_version": "1.0",
            "max_attempts": 3,
            "lockout_duration": 300,  # 5 minutes
            "failed_attempts": 0,
            "locked_until": None
        }
        
        if os.path.exists(self.admin_config_file):
            try:
                with open(self.admin_config_file, 'r') as f:
                    config = json.load(f)
                    # Merge with defaults
                    for key, value in default_config.items():
                        if key not in config:
                            config[key] = value
                    return config
            except (json.JSONDecodeError, IOError):
                pass
        
        # Save default config
        self._save_admin_config(default_config)
        return default_config
    
    def _save_admin_config(self, config):
        """Save admin configuration"""
        try:
            with open(self.admin_config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except IOError as e:
            print(f"Error saving admin config: {e}")
    
    def _hash_key(self, key: str, salt: bytes) -> str:
        """Hash admin key with salt"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key_hash = base64.urlsafe_b64encode(kdf.derive(key.encode()))
        return key_hash.decode()
    
    def set_admin_key(self, key: str) -> bool:
        """Set new admin key"""
        import time
        
        # Generate salt
        salt = secrets.token_bytes(16)
        
        # Hash the key
        key_hash = self._hash_key(key, salt)
        
        # Update config
        self.admin_config.update({
            "admin_key_hash": key_hash,
            "key_salt": base64.b64encode(salt).decode(),
            "created_at": int(time.time()),
            "last_used": None,
            "failed_attempts": 0,
            "locked_until": None
        })
        
        self._save_admin_config(self.admin_config)
        return True
    
    def verify_admin_key(self, key: str) -> bool:
        """Verify admin key"""
        import time
        
        # Check if account is locked
        if self.admin_config.get("locked_until"):
            if time.time() < self.admin_config["locked_until"]:
                return False
        
        # Check if key is set
        if not self.admin_config.get("admin_key_hash"):
            return False
        
        # Get salt and hash
        salt = base64.b64decode(self.admin_config["key_salt"])
        stored_hash = self.admin_config["admin_key_hash"]
        
        # Hash provided key
        provided_hash = self._hash_key(key, salt)
        
        # Verify
        if provided_hash == stored_hash:
            # Success - update last used and reset failed attempts
            self.admin_config.update({
                "last_used": int(time.time()),
                "failed_attempts": 0,
                "locked_until": None
            })
            self._save_admin_config(self.admin_config)
            return True
        else:
            # Failed attempt
            self._handle_failed_attempt()
            return False
    
    def _handle_failed_attempt(self):
        """Handle failed admin key attempt"""
        import time
        
        failed_attempts = self.admin_config.get("failed_attempts", 0) + 1
        max_attempts = self.admin_config.get("max_attempts", 3)
        lockout_duration = self.admin_config.get("lockout_duration", 300)
        
        self.admin_config["failed_attempts"] = failed_attempts
        
        if failed_attempts >= max_attempts:
            # Lock account
            self.admin_config["locked_until"] = int(time.time()) + lockout_duration
        
        self._save_admin_config(self.admin_config)
    
    def is_admin_key_set(self) -> bool:
        """Check if admin key is set"""
        return bool(self.admin_config.get("admin_key_hash"))
    
    def is_account_locked(self) -> bool:
        """Check if admin account is locked"""
        import time
        locked_until = self.admin_config.get("locked_until")
        return locked_until and time.time() < locked_until
    
    def get_lockout_time_remaining(self) -> int:
        """Get remaining lockout time in seconds"""
        import time
        locked_until = self.admin_config.get("locked_until")
        if locked_until:
            remaining = int(locked_until - time.time())
            return max(0, remaining)
        return 0
    
    def reset_admin_key(self, current_key: str) -> bool:
        """Reset admin key (requires current key)"""
        if not self.verify_admin_key(current_key):
            return False
        
        # Clear the key
        self.admin_config.update({
            "admin_key_hash": None,
            "key_salt": None,
            "created_at": None,
            "last_used": None,
            "failed_attempts": 0,
            "locked_until": None
        })
        
        self._save_admin_config(self.admin_config)
        return True
    
    def get_admin_info(self) -> dict:
        """Get admin account information"""
        return {
            "key_set": self.is_admin_key_set(),
            "locked": self.is_account_locked(),
            "lockout_remaining": self.get_lockout_time_remaining(),
            "failed_attempts": self.admin_config.get("failed_attempts", 0),
            "last_used": self.admin_config.get("last_used"),
            "created_at": self.admin_config.get("created_at")
        }


class AdminKeySetupDialog:
    """Dialog for setting up admin key"""
    
    def __init__(self, parent):
        self.parent = parent
        self.result = None
        self.dialog = None
        
    def show(self):
        """Show admin key setup dialog"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Admin Key Setup")
        self.dialog.geometry("500x400")
        self.dialog.resizable(False, False)
        
        # Center the dialog
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        self.create_widgets()
        
        # Make dialog modal
        self.parent.wait_window(self.dialog)
        
        return self.result
    
    def create_widgets(self):
        """Create admin key setup widgets"""
        import tkinter as tk
        from tkinter import ttk, messagebox
        
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(main_frame, text="Admin Key Setup", 
                              font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Instructions
        instructions = tk.Label(main_frame, 
                               text="Set up an admin key to create and manage access codes.\nThis key will be required for all admin operations.",
                               justify=tk.CENTER, wraplength=400)
        instructions.pack(pady=(0, 20))
        
        # Key input frame
        key_frame = ttk.LabelFrame(main_frame, text="Admin Key", padding="15")
        key_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(key_frame, text="Enter Admin Key:").pack(anchor=tk.W)
        self.key_var = tk.StringVar()
        key_entry = ttk.Entry(key_frame, textvariable=self.key_var, show="*", width=40)
        key_entry.pack(fill=tk.X, pady=(5, 10))
        
        ttk.Label(key_frame, text="Confirm Admin Key:").pack(anchor=tk.W)
        self.confirm_key_var = tk.StringVar()
        confirm_key_entry = ttk.Entry(key_frame, textvariable=self.confirm_key_var, show="*", width=40)
        confirm_key_entry.pack(fill=tk.X, pady=(5, 0))
        
        # Security notice
        security_frame = ttk.LabelFrame(main_frame, text="Security Notice", padding="10")
        security_frame.pack(fill=tk.X, pady=(0, 20))
        
        security_text = tk.Label(security_frame, 
                                text="• Keep your admin key secure and private\n• This key cannot be recovered if lost\n• Use a strong, unique password\n• Store it safely offline",
                                justify=tk.LEFT, font=("Arial", 9))
        security_text.pack(anchor=tk.W)
        
        # Buttons
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=(10, 0))
        
        setup_btn = ttk.Button(buttons_frame, text="Setup Admin Key", 
                              command=self.setup_key, style="Accent.TButton")
        setup_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        cancel_btn = ttk.Button(buttons_frame, text="Cancel", command=self.cancel)
        cancel_btn.pack(side=tk.RIGHT)
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="", foreground="red")
        self.status_label.pack(pady=(10, 0))
        
        # Focus on key entry
        key_entry.focus()
        
        # Bind Enter key
        self.dialog.bind('<Return>', lambda e: self.setup_key())
    
    def setup_key(self):
        """Setup admin key"""
        key = self.key_var.get()
        confirm_key = self.confirm_key_var.get()
        
        if not key or not confirm_key:
            self.status_label.config(text="Please enter and confirm the admin key")
            return
        
        if key != confirm_key:
            self.status_label.config(text="Admin keys do not match")
            return
        
        if len(key) < 8:
            self.status_label.config(text="Admin key must be at least 8 characters")
            return
        
        # Setup the key
        admin_manager = AdminKeyManager()
        if admin_manager.set_admin_key(key):
            self.result = {"action": "setup", "success": True}
            self.dialog.destroy()
        else:
            self.status_label.config(text="Failed to setup admin key")


# Example usage
if __name__ == "__main__":
    print("Admin Key Management System")
    print("=" * 50)
    
    # Test admin key manager
    admin_manager = AdminKeyManager()
    
    print(f"Admin key set: {admin_manager.is_admin_key_set()}")
    print(f"Account locked: {admin_manager.is_account_locked()}")
    
    if not admin_manager.is_admin_key_set():
        print("\nSetting up admin key...")
        admin_manager.set_admin_key("my_secure_admin_key_2024")
        print("Admin key set successfully!")
    
    print(f"\nVerifying admin key...")
    result = admin_manager.verify_admin_key("my_secure_admin_key_2024")
    print(f"Verification result: {result}")
    
    print(f"\nAdmin info: {admin_manager.get_admin_info()}")
    
    print("\nFiles created:")
    print(f"  Admin config: {admin_manager.admin_config_file}")
    print(f"  Admin key hash: {admin_manager.admin_config.get('admin_key_hash', 'Not set')[:20]}...")
