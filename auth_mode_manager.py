"""
Authentication Mode Manager for ROTMG Patch Utility Tool
Handles switching between different authentication methods
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from auth_manager import AuthManager, LoginDialog
from server_auth import ServerAuthManager, ServerAuthDialog, AccessCodeManager, AccessCodeDialog


class AuthModeManager:
    """Manages different authentication modes"""
    
    def __init__(self):
        self.config_dir = os.path.join(os.path.expanduser("~"), ".rotmg_patch_utility")
        self.auth_config_file = os.path.join(self.config_dir, "auth_config.json")
        
        # Available authentication modes
        self.modes = {
            "local": {
                "name": "Local Authentication",
                "description": "Store credentials locally with encryption",
                "manager_class": AuthManager,
                "dialog_class": LoginDialog
            },
            "server": {
                "name": "Server Authentication", 
                "description": "Authenticate with remote server",
                "manager_class": ServerAuthManager,
                "dialog_class": ServerAuthDialog
            },
            "access_code": {
                "name": "Access Code",
                "description": "Use access codes for authentication",
                "manager_class": AccessCodeManager,
                "dialog_class": AccessCodeDialog
            }
        }
        
        # Load authentication configuration
        self.auth_config = self._load_auth_config()
        
        # Initialize current auth manager
        self.current_mode = self.auth_config.get("current_mode", "local")
        self.auth_manager = self._get_auth_manager()
        
    def _load_auth_config(self):
        """Load authentication configuration"""
        default_config = {
            "current_mode": "local",
            "available_modes": ["local", "server", "access_code"],
            "mode_settings": {
                "local": {
                    "enabled": True,
                    "auto_login": False
                },
                "server": {
                    "enabled": True,
                    "server_url": "https://api.rotmg-patch-utility.com",
                    "offline_mode": True
                },
                "access_code": {
                    "enabled": True,
                    "require_code_on_startup": True
                }
            }
        }
        
        if os.path.exists(self.auth_config_file):
            try:
                with open(self.auth_config_file, 'r') as f:
                    config = json.load(f)
                    # Merge with defaults
                    for key, value in default_config.items():
                        if key not in config:
                            config[key] = value
                    return config
            except (json.JSONDecodeError, IOError):
                pass
        
        # Save default config
        self._save_auth_config(default_config)
        return default_config
    
    def _save_auth_config(self, config):
        """Save authentication configuration"""
        try:
            with open(self.auth_config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except IOError as e:
            print(f"Error saving auth config: {e}")
    
    def _get_auth_manager(self):
        """Get current authentication manager"""
        mode_info = self.modes.get(self.current_mode)
        if not mode_info:
            return None
        
        manager_class = mode_info["manager_class"]
        return manager_class()
    
    def set_auth_mode(self, mode: str):
        """Set authentication mode"""
        if mode not in self.modes:
            raise ValueError(f"Invalid authentication mode: {mode}")
        
        if not self.auth_config["mode_settings"][mode]["enabled"]:
            raise ValueError(f"Authentication mode {mode} is disabled")
        
        self.current_mode = mode
        self.auth_config["current_mode"] = mode
        self._save_auth_config(self.auth_config)
        
        # Initialize new auth manager
        self.auth_manager = self._get_auth_manager()
    
    def get_available_modes(self):
        """Get list of available authentication modes"""
        available = []
        for mode, info in self.modes.items():
            if self.auth_config["mode_settings"][mode]["enabled"]:
                available.append({
                    "id": mode,
                    "name": info["name"],
                    "description": info["description"]
                })
        return available
    
    def authenticate(self, parent):
        """Authenticate using current mode"""
        if not self.auth_manager:
            return None
        
        mode_info = self.modes[self.current_mode]
        dialog_class = mode_info["dialog_class"]
        
        dialog = dialog_class(parent, self.auth_manager)
        return dialog.show()
    
    def is_authenticated(self):
        """Check if user is authenticated"""
        if not self.auth_manager:
            return False
        
        if self.current_mode == "local":
            return self.auth_manager.is_session_valid()
        elif self.current_mode == "server":
            return self.auth_manager.is_license_valid()
        elif self.current_mode == "access_code":
            # Access codes are validated per session
            return True
        
        return False
    
    def get_current_user(self):
        """Get current user information"""
        if not self.auth_manager:
            return None
        
        if self.current_mode == "local":
            return self.auth_manager.get_current_user()
        elif self.current_mode == "server":
            return self.auth_manager.get_current_user()
        elif self.current_mode == "access_code":
            return "Access Code User"
        
        return None
    
    def logout(self):
        """Logout from current authentication"""
        if self.auth_manager:
            self.auth_manager.logout()
    
    def update_mode_settings(self, mode: str, settings: dict):
        """Update settings for a specific mode"""
        if mode in self.auth_config["mode_settings"]:
            self.auth_config["mode_settings"][mode].update(settings)
            self._save_auth_config(self.auth_config)


class AuthModeSelectorDialog:
    """Dialog for selecting authentication mode"""
    
    def __init__(self, parent, auth_mode_manager: AuthModeManager):
        self.parent = parent
        self.auth_mode_manager = auth_mode_manager
        self.result = None
        self.dialog = None
        
    def show(self):
        """Show authentication mode selector"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Select Authentication Method")
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
        """Create authentication mode selector widgets"""
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(main_frame, text="Select Authentication Method", 
                              font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Instructions
        instructions = tk.Label(main_frame, 
                               text="Choose how you want to authenticate with the application:",
                               justify=tk.CENTER)
        instructions.pack(pady=(0, 20))
        
        # Mode selection frame
        mode_frame = ttk.LabelFrame(main_frame, text="Available Methods", padding="15")
        mode_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        self.selected_mode = tk.StringVar(value=self.auth_mode_manager.current_mode)
        
        # Create radio buttons for each mode
        available_modes = self.auth_mode_manager.get_available_modes()
        for i, mode in enumerate(available_modes):
            mode_info = self.auth_mode_manager.modes[mode["id"]]
            
            # Radio button
            radio = ttk.Radiobutton(
                mode_frame, 
                text=mode["name"], 
                variable=self.selected_mode, 
                value=mode["id"]
            )
            radio.grid(row=i*2, column=0, sticky=tk.W, pady=(5, 0))
            
            # Description
            desc_label = tk.Label(
                mode_frame, 
                text=mode["description"], 
                font=("Arial", 9), 
                foreground="gray"
            )
            desc_label.grid(row=i*2+1, column=0, sticky=tk.W, padx=(20, 0), pady=(0, 10))
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Settings button
        settings_btn = ttk.Button(buttons_frame, text="Settings", 
                                command=self.show_settings)
        settings_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Continue button
        continue_btn = ttk.Button(buttons_frame, text="Continue", 
                                 command=self.continue_auth, style="Accent.TButton")
        continue_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Cancel button
        cancel_btn = ttk.Button(buttons_frame, text="Cancel", command=self.cancel)
        cancel_btn.pack(side=tk.RIGHT)
    
    def continue_auth(self):
        """Continue with selected authentication method"""
        selected_mode = self.selected_mode.get()
        
        try:
            self.auth_mode_manager.set_auth_mode(selected_mode)
            self.result = {
                "action": "continue",
                "mode": selected_mode
            }
            self.dialog.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to set authentication mode: {str(e)}")
    
    def show_settings(self):
        """Show authentication settings"""
        settings_dialog = AuthSettingsDialog(self.dialog, self.auth_mode_manager)
        settings_dialog.show()
    
    def cancel(self):
        """Cancel authentication"""
        self.result = {"action": "cancel"}
        self.dialog.destroy()


class AuthSettingsDialog:
    """Dialog for authentication settings"""
    
    def __init__(self, parent, auth_mode_manager: AuthModeManager):
        self.parent = parent
        self.auth_mode_manager = auth_mode_manager
        self.dialog = None
        
    def show(self):
        """Show authentication settings"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Authentication Settings")
        self.dialog.geometry("600x500")
        self.dialog.resizable(True, True)
        
        # Center the dialog
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        self.create_widgets()
        
        # Make dialog modal
        self.parent.wait_window(self.dialog)
    
    def create_widgets(self):
        """Create authentication settings widgets"""
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # General settings tab
        self.create_general_tab(notebook)
        
        # Local auth tab
        self.create_local_auth_tab(notebook)
        
        # Server auth tab
        self.create_server_auth_tab(notebook)
        
        # Access code tab
        self.create_access_code_tab(notebook)
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Buttons
        ttk.Button(buttons_frame, text="Reset to Defaults", 
                  command=self.reset_defaults).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(buttons_frame, text="OK", 
                  command=self.save_and_close).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(buttons_frame, text="Cancel", 
                  command=self.cancel).pack(side=tk.RIGHT)
    
    def create_general_tab(self, notebook):
        """Create general settings tab"""
        frame = ttk.Frame(notebook, padding="10")
        notebook.add(frame, text="General")
        
        # Current mode
        ttk.Label(frame, text="Current Authentication Mode:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        current_mode_label = ttk.Label(frame, text=self.auth_mode_manager.modes[self.auth_mode_manager.current_mode]["name"], 
                                      font=("Arial", 10, "bold"))
        current_mode_label.grid(row=0, column=1, sticky=tk.W, pady=(0, 5))
        
        # Available modes
        ttk.Label(frame, text="Available Authentication Methods:", font=("Arial", 10, "bold")).grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(20, 10))
        
        available_modes = self.auth_mode_manager.get_available_modes()
        for i, mode in enumerate(available_modes):
            enabled_var = tk.BooleanVar(value=self.auth_mode_manager.auth_config["mode_settings"][mode["id"]]["enabled"])
            ttk.Checkbutton(frame, text=f"Enable {mode['name']}", 
                          variable=enabled_var).grid(row=i+2, column=0, columnspan=2, sticky=tk.W, pady=2)
    
    def create_local_auth_tab(self, notebook):
        """Create local authentication settings tab"""
        frame = ttk.Frame(notebook, padding="10")
        notebook.add(frame, text="Local Auth")
        
        # Auto login
        auto_login_var = tk.BooleanVar(value=self.auth_mode_manager.auth_config["mode_settings"]["local"]["auto_login"])
        ttk.Checkbutton(frame, text="Enable auto-login", 
                       variable=auto_login_var).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        # Session timeout
        ttk.Label(frame, text="Session Timeout (minutes):").grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        session_timeout_var = tk.IntVar(value=60)  # Default 1 hour
        ttk.Spinbox(frame, textvariable=session_timeout_var, from_=5, to=480, 
                   increment=15).grid(row=1, column=1, sticky=tk.W, pady=(0, 5))
    
    def create_server_auth_tab(self, notebook):
        """Create server authentication settings tab"""
        frame = ttk.Frame(notebook, padding="10")
        notebook.add(frame, text="Server Auth")
        
        # Server URL
        ttk.Label(frame, text="Server URL:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        server_url_var = tk.StringVar(value=self.auth_mode_manager.auth_config["mode_settings"]["server"]["server_url"])
        ttk.Entry(frame, textvariable=server_url_var, width=50).grid(row=0, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # Offline mode
        offline_mode_var = tk.BooleanVar(value=self.auth_mode_manager.auth_config["mode_settings"]["server"]["offline_mode"])
        ttk.Checkbutton(frame, text="Enable offline mode", 
                       variable=offline_mode_var).grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(10, 5))
        
        # Offline mode days
        ttk.Label(frame, text="Offline Mode Duration (days):").grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        offline_days_var = tk.IntVar(value=7)
        ttk.Spinbox(frame, textvariable=offline_days_var, from_=1, to=30, 
                   increment=1).grid(row=2, column=1, sticky=tk.W, pady=(0, 5))
    
    def create_access_code_tab(self, notebook):
        """Create access code settings tab"""
        frame = ttk.Frame(notebook, padding="10")
        notebook.add(frame, text="Access Codes")
        
        # Require code on startup
        require_code_var = tk.BooleanVar(value=self.auth_mode_manager.auth_config["mode_settings"]["access_code"]["require_code_on_startup"])
        ttk.Checkbutton(frame, text="Require access code on startup", 
                       variable=require_code_var).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        # Code management
        ttk.Label(frame, text="Access Code Management:", font=("Arial", 10, "bold")).grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(20, 10))
        
        # Generate code button
        ttk.Button(frame, text="Generate New Access Code", 
                  command=self.generate_access_code).grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        # List codes button
        ttk.Button(frame, text="List Access Codes", 
                  command=self.list_access_codes).grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
    
    def generate_access_code(self):
        """Generate new access code"""
        # Simple dialog for code generation
        dialog = tk.Toplevel(self.dialog)
        dialog.title("Generate Access Code")
        dialog.geometry("400x300")
        dialog.transient(self.dialog)
        dialog.grab_set()
        
        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Code Name:").pack(anchor=tk.W)
        name_var = tk.StringVar()
        ttk.Entry(frame, textvariable=name_var, width=30).pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(frame, text="Expires in (days, 0 = never):").pack(anchor=tk.W)
        expires_var = tk.IntVar(value=30)
        ttk.Spinbox(frame, textvariable=expires_var, from_=0, to=365, 
                   increment=1).pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(frame, text="Max Uses (0 = unlimited):").pack(anchor=tk.W)
        max_uses_var = tk.IntVar(value=10)
        ttk.Spinbox(frame, textvariable=max_uses_var, from_=0, to=1000, 
                   increment=1).pack(fill=tk.X, pady=(0, 20))
        
        def generate():
            if not name_var.get().strip():
                messagebox.showerror("Error", "Please enter a code name")
                return
            
            # Generate code
            code_manager = AccessCodeManager()
            # Get admin key
            admin_key = "admin_secret_key_2024"  # In production, this should be configurable
            
            code = code_manager.generate_access_code(
                name_var.get().strip(),
                ["basic_patching"],
                expires_var.get() if expires_var.get() > 0 else None,
                max_uses_var.get() if max_uses_var.get() > 0 else None,
                admin_key=admin_key
            )
            
            messagebox.showinfo("Access Code Generated", f"Code: {code}")
            dialog.destroy()
        
        ttk.Button(frame, text="Generate", command=generate).pack(pady=(0, 10))
        ttk.Button(frame, text="Cancel", command=dialog.destroy).pack()
    
    def list_access_codes(self):
        """List access codes"""
        code_manager = AccessCodeManager()
        # Use admin key to see all codes
        admin_key = "admin_secret_key_2024"  # In production, this should be configurable
        codes = code_manager.list_access_codes(admin_key)
        
        if not codes:
            messagebox.showinfo("Access Codes", "No access codes found")
            return
        
        # Create list dialog
        dialog = tk.Toplevel(self.dialog)
        dialog.title("Access Codes")
        dialog.geometry("600x400")
        dialog.transient(self.dialog)
        dialog.grab_set()
        
        frame = ttk.Frame(dialog, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview for codes
        columns = ("Code", "Name", "Uses", "Expires", "Visibility")
        tree = ttk.Treeview(frame, columns=columns, show="headings")
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)
        
        # Add codes to tree
        for code, data in codes.items():
            expires = "Never" if not data.get("expires_at") else "Expired" if data["expires_at"] < time.time() else "Valid"
            visibility = "Public" if data.get("public", False) else "Private"
            tree.insert("", "end", values=(
                code,
                data["name"],
                f"{data['used_count']}/{data.get('max_uses', '∞')}",
                expires,
                visibility
            ))
        
        tree.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        ttk.Button(frame, text="Close", command=dialog.destroy).pack()
    
    def reset_defaults(self):
        """Reset settings to defaults"""
        if messagebox.askyesno("Reset Settings", "Are you sure you want to reset all authentication settings to defaults?"):
            # Reset to default config
            default_config = {
                "current_mode": "local",
                "available_modes": ["local", "server", "access_code"],
                "mode_settings": {
                    "local": {"enabled": True, "auto_login": False},
                    "server": {"enabled": True, "server_url": "https://api.rotmg-patch-utility.com", "offline_mode": True},
                    "access_code": {"enabled": True, "require_code_on_startup": True}
                }
            }
            self.auth_mode_manager.auth_config = default_config
            self.auth_mode_manager._save_auth_config(default_config)
            messagebox.showinfo("Settings Reset", "All settings have been reset to defaults.")
            self.dialog.destroy()
    
    def save_and_close(self):
        """Save settings and close"""
        # Save settings (implementation would depend on the specific settings)
        self.dialog.destroy()
    
    def cancel(self):
        """Cancel without saving"""
        self.dialog.destroy()
