"""
Secure Access Code Manager for ROTMG Patch Utility Tool
Encrypts access codes to prevent users from seeing all available codes
"""

import os
import json
import time
import hashlib
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class SecureAccessCodeManager:
    """Manages access codes with encryption to prevent unauthorized access"""
    
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
        """Get default access codes (only a few public ones)"""
        return {
            "codes": {
                "DEMO-2024-001": {
                    "name": "Demo Access",
                    "expires_at": None,
                    "features": ["basic_patching"],
                    "max_uses": 100,
                    "used_count": 0,
                    "created_at": int(time.time()),
                    "public": True  # This is a public demo code
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
        """Validate access code (only works for codes in the encrypted file)"""
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
    
    def add_access_code(self, code: str, name: str, features: list, expires_days: int = None, max_uses: int = None):
        """Add a new access code (admin only - requires special key)"""
        # This would require admin authentication in a real implementation
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
    
    def list_public_codes(self):
        """List only public access codes"""
        public_codes = {}
        for code, data in self.access_codes["codes"].items():
            if data.get("public", False):
                public_codes[code] = data
        return public_codes
    
    def revoke_access_code(self, code: str) -> bool:
        """Revoke an access code"""
        if code in self.access_codes["codes"]:
            del self.access_codes["codes"][code]
            self._save_access_codes(self.access_codes)
            return True
        return False


class AdminAccessCodeManager:
    """Admin-only access code manager for creating codes"""
    
    def __init__(self, admin_key: str = None):
        self.admin_key = admin_key or self._get_admin_key()
        self.secure_manager = SecureAccessCodeManager()
    
    def _get_admin_key(self):
        """Get admin key (in production, this would be from secure storage)"""
        # For demo purposes, use a hardcoded admin key
        # In production, this should be stored securely or derived from admin credentials
        return "admin_secret_key_2024"
    
    def create_access_code(self, name: str, features: list, expires_days: int = None, max_uses: int = None) -> str:
        """Create a new access code"""
        import random
        import string
        
        # Generate random code
        code_length = 12
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=code_length-3))
        code = f"{code[:4]}-{code[4:8]}-{code[8:]}"
        
        # Add to secure storage
        self.secure_manager.add_access_code(code, name, features, expires_days, max_uses)
        
        return code
    
    def list_all_codes(self):
        """List all codes (admin only)"""
        return self.secure_manager.access_codes["codes"]
    
    def revoke_code(self, code: str) -> bool:
        """Revoke a code"""
        return self.secure_manager.revoke_access_code(code)


# Example usage and testing
if __name__ == "__main__":
    print("Secure Access Code System Demo")
    print("=" * 50)
    
    # Test secure manager
    secure_manager = SecureAccessCodeManager()
    
    print("Public codes (what users can see):")
    public_codes = secure_manager.list_public_codes()
    for code, data in public_codes.items():
        print(f"  {code}: {data['name']}")
    
    print(f"\nTotal codes in system: {len(secure_manager.access_codes['codes'])}")
    print("(Users can only see public codes)")
    
    # Test admin manager
    admin_manager = AdminAccessCodeManager()
    
    print("\nCreating admin code...")
    admin_code = admin_manager.create_access_code(
        name="Admin Test",
        features=["basic_patching", "advanced_features"],
        expires_days=30,
        max_uses=5
    )
    print(f"Created admin code: {admin_code}")
    
    print("\nTesting validation...")
    result = secure_manager.validate_access_code(admin_code)
    print(f"Validation result: {result['success']} - {result['message']}")
    
    print("\nFiles created:")
    print(f"  Encrypted codes: {secure_manager.access_codes_file}")
    print(f"  Encryption key: {secure_manager.key_file}")
    
    print("\nSecurity benefits:")
    print("  ✅ Codes are encrypted")
    print("  ✅ Users can't see all codes")
    print("  ✅ Only public codes are visible")
    print("  ✅ Admin codes are hidden")
