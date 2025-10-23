"""
Configuration Management for ROTMG Patch Utility Tool
Handles user preferences, application settings, and secure storage
"""

import os
import json
import tkinter as tk
from tkinter import ttk, messagebox
from auth_manager import AuthManager


class ConfigManager:
    """Manages application configuration and user preferences"""
    
    def __init__(self, auth_manager: AuthManager):
        self.auth_manager = auth_manager
        self.config_dir = auth_manager.config_dir
        self.user_config_file = os.path.join(self.config_dir, "user_config.json")
        self.app_config_file = os.path.join(self.config_dir, "app_config.json")
        
        # Default configurations
        self.default_user_config = {
            "theme": "default",
            "window_geometry": "1000x700",
            "last_resources_path": "",
            "last_patches_path": "",
            "auto_backup": True,
            "backup_location": "",
            "log_level": "INFO",
            "max_log_lines": 1000,
            "auto_save_patches": True,
            "patch_auto_load": True,
            "character_count_preservation": True,
            "show_preview": True,
            "confirm_patch_application": True,
            "confirm_backup_restore": True,
            "remember_window_state": True,
            "recent_files": [],
            "max_recent_files": 10
        }
        
        self.default_app_config = {
            "version": "1.0.0",
            "first_run": True,
            "update_check": True,
            "update_frequency": "weekly",
            "telemetry": False,
            "crash_reporting": True,
            "performance_monitoring": False,
            "debug_mode": False,
            "experimental_features": False,
            "patch_validation": True,
            "backup_retention_days": 30,
            "max_backup_files": 10
        }
        
        # Load configurations
        self.user_config = self._load_config(self.user_config_file, self.default_user_config)
        self.app_config = self._load_config(self.app_config_file, self.default_app_config)
    
    def _load_config(self, config_file: str, default_config: dict) -> dict:
        """Load configuration from file"""
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    # Merge with defaults for any missing keys
                    for key, value in default_config.items():
                        if key not in config:
                            config[key] = value
                    return config
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading config {config_file}: {e}")
        
        # Save default config
        self._save_config(config_file, default_config)
        return default_config.copy()
    
    def _save_config(self, config_file: str, config: dict):
        """Save configuration to file"""
        try:
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except IOError as e:
            print(f"Error saving config {config_file}: {e}")
    
    def get_user_config(self, key: str, default=None):
        """Get user configuration value"""
        return self.user_config.get(key, default)
    
    def set_user_config(self, key: str, value):
        """Set user configuration value"""
        self.user_config[key] = value
        self._save_config(self.user_config_file, self.user_config)
    
    def get_app_config(self, key: str, default=None):
        """Get application configuration value"""
        return self.app_config.get(key, default)
    
    def set_app_config(self, key: str, value):
        """Set application configuration value"""
        self.app_config[key] = value
        self._save_config(self.app_config_file, self.app_config)
    
    def add_recent_file(self, file_path: str):
        """Add file to recent files list"""
        recent_files = self.user_config.get("recent_files", [])
        
        # Remove if already exists
        if file_path in recent_files:
            recent_files.remove(file_path)
        
        # Add to beginning
        recent_files.insert(0, file_path)
        
        # Limit to max recent files
        max_files = self.user_config.get("max_recent_files", 10)
        recent_files = recent_files[:max_files]
        
        self.set_user_config("recent_files", recent_files)
    
    def get_recent_files(self) -> list:
        """Get list of recent files"""
        return self.user_config.get("recent_files", [])
    
    def clear_recent_files(self):
        """Clear recent files list"""
        self.set_user_config("recent_files", [])
    
    def reset_to_defaults(self):
        """Reset all configurations to defaults"""
        self.user_config = self.default_user_config.copy()
        self.app_config = self.default_app_config.copy()
        
        self._save_config(self.user_config_file, self.user_config)
        self._save_config(self.app_config_file, self.app_config)
    
    def export_config(self, file_path: str):
        """Export configuration to file"""
        export_data = {
            "user_config": self.user_config,
            "app_config": self.app_config,
            "exported_at": str(os.path.getctime(self.user_config_file))
        }
        
        try:
            with open(file_path, 'w') as f:
                json.dump(export_data, f, indent=2)
            return True
        except IOError as e:
            print(f"Error exporting config: {e}")
            return False
    
    def import_config(self, file_path: str):
        """Import configuration from file"""
        try:
            with open(file_path, 'r') as f:
                import_data = json.load(f)
            
            if "user_config" in import_data:
                self.user_config.update(import_data["user_config"])
                self._save_config(self.user_config_file, self.user_config)
            
            if "app_config" in import_data:
                self.app_config.update(import_data["app_config"])
                self._save_config(self.app_config_file, self.app_config)
            
            return True
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error importing config: {e}")
            return False


class SettingsDialog:
    """Settings dialog window"""
    
    def __init__(self, parent, config_manager: ConfigManager):
        self.parent = parent
        self.config_manager = config_manager
        self.dialog = None
        
    def show(self):
        """Show settings dialog"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Settings")
        self.dialog.geometry("600x500")
        self.dialog.resizable(True, True)
        
        # Center the dialog
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        self.create_widgets()
        
        # Make dialog modal
        self.parent.wait_window(self.dialog)
    
    def create_widgets(self):
        """Create settings dialog widgets"""
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # General settings tab
        self.create_general_tab(notebook)
        
        # Patch settings tab
        self.create_patch_tab(notebook)
        
        # Security settings tab
        self.create_security_tab(notebook)
        
        # Advanced settings tab
        self.create_advanced_tab(notebook)
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Buttons
        ttk.Button(buttons_frame, text="Reset to Defaults", 
                  command=self.reset_defaults).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(buttons_frame, text="Export Settings", 
                  command=self.export_settings).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(buttons_frame, text="Import Settings", 
                  command=self.import_settings).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(buttons_frame, text="OK", 
                  command=self.save_and_close).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(buttons_frame, text="Cancel", 
                  command=self.cancel).pack(side=tk.RIGHT)
    
    def create_general_tab(self, notebook):
        """Create general settings tab"""
        frame = ttk.Frame(notebook, padding="10")
        notebook.add(frame, text="General")
        
        # Theme
        ttk.Label(frame, text="Theme:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.theme_var = tk.StringVar(value=self.config_manager.get_user_config("theme"))
        theme_combo = ttk.Combobox(frame, textvariable=self.theme_var, 
                                  values=["default", "dark", "light"], state="readonly")
        theme_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # Auto backup
        self.auto_backup_var = tk.BooleanVar(value=self.config_manager.get_user_config("auto_backup"))
        ttk.Checkbutton(frame, text="Create automatic backup before patching", 
                        variable=self.auto_backup_var).grid(row=1, column=0, columnspan=2, 
                                                           sticky=tk.W, pady=(0, 5))
        
        # Confirmations
        self.confirm_patch_var = tk.BooleanVar(value=self.config_manager.get_user_config("confirm_patch_application"))
        ttk.Checkbutton(frame, text="Confirm before applying patches", 
                        variable=self.confirm_patch_var).grid(row=2, column=0, columnspan=2, 
                                                           sticky=tk.W, pady=(0, 5))
        
        self.confirm_backup_var = tk.BooleanVar(value=self.config_manager.get_user_config("confirm_backup_restore"))
        ttk.Checkbutton(frame, text="Confirm before restoring backup", 
                        variable=self.confirm_backup_var).grid(row=3, column=0, columnspan=2, 
                                                             sticky=tk.W, pady=(0, 5))
        
        # Log level
        ttk.Label(frame, text="Log Level:").grid(row=4, column=0, sticky=tk.W, pady=(10, 5))
        self.log_level_var = tk.StringVar(value=self.config_manager.get_user_config("log_level"))
        log_level_combo = ttk.Combobox(frame, textvariable=self.log_level_var, 
                                      values=["DEBUG", "INFO", "WARNING", "ERROR"], state="readonly")
        log_level_combo.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=(10, 5))
        
        # Max log lines
        ttk.Label(frame, text="Max Log Lines:").grid(row=5, column=0, sticky=tk.W, pady=(0, 5))
        self.max_log_lines_var = tk.IntVar(value=self.config_manager.get_user_config("max_log_lines"))
        ttk.Spinbox(frame, textvariable=self.max_log_lines_var, from_=100, to=10000, 
                   increment=100).grid(row=5, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
    
    def create_patch_tab(self, notebook):
        """Create patch settings tab"""
        frame = ttk.Frame(notebook, padding="10")
        notebook.add(frame, text="Patches")
        
        # Auto save patches
        self.auto_save_patches_var = tk.BooleanVar(value=self.config_manager.get_user_config("auto_save_patches"))
        ttk.Checkbutton(frame, text="Auto-save patches after creation", 
                        variable=self.auto_save_patches_var).grid(row=0, column=0, columnspan=2, 
                                                               sticky=tk.W, pady=(0, 5))
        
        # Auto load patches
        self.patch_auto_load_var = tk.BooleanVar(value=self.config_manager.get_user_config("patch_auto_load"))
        ttk.Checkbutton(frame, text="Auto-load patches on startup", 
                        variable=self.patch_auto_load_var).grid(row=1, column=0, columnspan=2, 
                                                              sticky=tk.W, pady=(0, 5))
        
        # Character count preservation
        self.char_count_preservation_var = tk.BooleanVar(value=self.config_manager.get_user_config("character_count_preservation"))
        ttk.Checkbutton(frame, text="Preserve character count when spoofing items", 
                        variable=self.char_count_preservation_var).grid(row=2, column=0, columnspan=2, 
                                                                       sticky=tk.W, pady=(0, 5))
        
        # Show preview
        self.show_preview_var = tk.BooleanVar(value=self.config_manager.get_user_config("show_preview"))
        ttk.Checkbutton(frame, text="Show preview in patch dialogs", 
                        variable=self.show_preview_var).grid(row=3, column=0, columnspan=2, 
                                                           sticky=tk.W, pady=(0, 5))
        
        # Patch validation
        self.patch_validation_var = tk.BooleanVar(value=self.config_manager.get_app_config("patch_validation"))
        ttk.Checkbutton(frame, text="Validate patches before applying", 
                        variable=self.patch_validation_var).grid(row=4, column=0, columnspan=2, 
                                                               sticky=tk.W, pady=(10, 5))
    
    def create_security_tab(self, notebook):
        """Create security settings tab"""
        frame = ttk.Frame(notebook, padding="10")
        notebook.add(frame, text="Security")
        
        # Session timeout
        ttk.Label(frame, text="Session Timeout (minutes):").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        session_timeout = self.config_manager.auth_manager.config.get("session_timeout", 3600) // 60
        self.session_timeout_var = tk.IntVar(value=session_timeout)
        ttk.Spinbox(frame, textvariable=self.session_timeout_var, from_=5, to=480, 
                   increment=15).grid(row=0, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # Max login attempts
        ttk.Label(frame, text="Max Login Attempts:").grid(row=1, column=0, sticky=tk.W, pady=(10, 5))
        max_attempts = self.config_manager.auth_manager.config.get("max_login_attempts", 3)
        self.max_attempts_var = tk.IntVar(value=max_attempts)
        ttk.Spinbox(frame, textvariable=self.max_attempts_var, from_=1, to=10, 
                   increment=1).grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(10, 5))
        
        # Lockout duration
        ttk.Label(frame, text="Lockout Duration (minutes):").grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        lockout_duration = self.config_manager.auth_manager.config.get("lockout_duration", 300) // 60
        self.lockout_duration_var = tk.IntVar(value=lockout_duration)
        ttk.Spinbox(frame, textvariable=self.lockout_duration_var, from_=1, to=60, 
                   increment=1).grid(row=2, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # Password requirements
        ttk.Label(frame, text="Password Requirements:", font=("Arial", 10, "bold")).grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=(20, 5))
        
        min_length = self.config_manager.auth_manager.config.get("password_min_length", 8)
        self.password_min_length_var = tk.IntVar(value=min_length)
        ttk.Label(frame, text="Minimum Length:").grid(row=4, column=0, sticky=tk.W, pady=(0, 5))
        ttk.Spinbox(frame, textvariable=self.password_min_length_var, from_=4, to=32, 
                   increment=1).grid(row=4, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        
        self.require_uppercase_var = tk.BooleanVar(value=self.config_manager.auth_manager.config.get("require_uppercase", True))
        ttk.Checkbutton(frame, text="Require uppercase letters", 
                        variable=self.require_uppercase_var).grid(row=5, column=0, columnspan=2, 
                                                               sticky=tk.W, pady=(0, 5))
        
        self.require_lowercase_var = tk.BooleanVar(value=self.config_manager.auth_manager.config.get("require_lowercase", True))
        ttk.Checkbutton(frame, text="Require lowercase letters", 
                        variable=self.require_lowercase_var).grid(row=6, column=0, columnspan=2, 
                                                               sticky=tk.W, pady=(0, 5))
        
        self.require_numbers_var = tk.BooleanVar(value=self.config_manager.auth_manager.config.get("require_numbers", True))
        ttk.Checkbutton(frame, text="Require numbers", 
                        variable=self.require_numbers_var).grid(row=7, column=0, columnspan=2, 
                                                              sticky=tk.W, pady=(0, 5))
        
        self.require_special_var = tk.BooleanVar(value=self.config_manager.auth_manager.config.get("require_special_chars", False))
        ttk.Checkbutton(frame, text="Require special characters", 
                        variable=self.require_special_var).grid(row=8, column=0, columnspan=2, 
                                                              sticky=tk.W, pady=(0, 5))
    
    def create_advanced_tab(self, notebook):
        """Create advanced settings tab"""
        frame = ttk.Frame(notebook, padding="10")
        notebook.add(frame, text="Advanced")
        
        # Debug mode
        self.debug_mode_var = tk.BooleanVar(value=self.config_manager.get_app_config("debug_mode"))
        ttk.Checkbutton(frame, text="Enable debug mode", 
                        variable=self.debug_mode_var).grid(row=0, column=0, columnspan=2, 
                                                         sticky=tk.W, pady=(0, 5))
        
        # Experimental features
        self.experimental_var = tk.BooleanVar(value=self.config_manager.get_app_config("experimental_features"))
        ttk.Checkbutton(frame, text="Enable experimental features", 
                        variable=self.experimental_var).grid(row=1, column=0, columnspan=2, 
                                                           sticky=tk.W, pady=(0, 5))
        
        # Telemetry
        self.telemetry_var = tk.BooleanVar(value=self.config_manager.get_app_config("telemetry"))
        ttk.Checkbutton(frame, text="Send anonymous usage data", 
                        variable=self.telemetry_var).grid(row=2, column=0, columnspan=2, 
                                                        sticky=tk.W, pady=(0, 5))
        
        # Crash reporting
        self.crash_reporting_var = tk.BooleanVar(value=self.config_manager.get_app_config("crash_reporting"))
        ttk.Checkbutton(frame, text="Send crash reports", 
                        variable=self.crash_reporting_var).grid(row=3, column=0, columnspan=2, 
                                                              sticky=tk.W, pady=(0, 5))
        
        # Performance monitoring
        self.performance_var = tk.BooleanVar(value=self.config_manager.get_app_config("performance_monitoring"))
        ttk.Checkbutton(frame, text="Monitor performance", 
                        variable=self.performance_var).grid(row=4, column=0, columnspan=2, 
                                                           sticky=tk.W, pady=(10, 5))
        
        # Backup settings
        ttk.Label(frame, text="Backup Settings:", font=("Arial", 10, "bold")).grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=(20, 5))
        
        retention_days = self.config_manager.get_app_config("backup_retention_days", 30)
        self.backup_retention_var = tk.IntVar(value=retention_days)
        ttk.Label(frame, text="Backup Retention (days):").grid(row=6, column=0, sticky=tk.W, pady=(0, 5))
        ttk.Spinbox(frame, textvariable=self.backup_retention_var, from_=1, to=365, 
                   increment=1).grid(row=6, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        
        max_backups = self.config_manager.get_app_config("max_backup_files", 10)
        self.max_backups_var = tk.IntVar(value=max_backups)
        ttk.Label(frame, text="Max Backup Files:").grid(row=7, column=0, sticky=tk.W, pady=(0, 5))
        ttk.Spinbox(frame, textvariable=self.max_backups_var, from_=1, to=100, 
                   increment=1).grid(row=7, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
    
    def save_and_close(self):
        """Save settings and close dialog"""
        # Save user config
        self.config_manager.set_user_config("theme", self.theme_var.get())
        self.config_manager.set_user_config("auto_backup", self.auto_backup_var.get())
        self.config_manager.set_user_config("confirm_patch_application", self.confirm_patch_var.get())
        self.config_manager.set_user_config("confirm_backup_restore", self.confirm_backup_var.get())
        self.config_manager.set_user_config("log_level", self.log_level_var.get())
        self.config_manager.set_user_config("max_log_lines", self.max_log_lines_var.get())
        self.config_manager.set_user_config("auto_save_patches", self.auto_save_patches_var.get())
        self.config_manager.set_user_config("patch_auto_load", self.patch_auto_load_var.get())
        self.config_manager.set_user_config("character_count_preservation", self.char_count_preservation_var.get())
        self.config_manager.set_user_config("show_preview", self.show_preview_var.get())
        
        # Save app config
        self.config_manager.set_app_config("patch_validation", self.patch_validation_var.get())
        self.config_manager.set_app_config("debug_mode", self.debug_mode_var.get())
        self.config_manager.set_app_config("experimental_features", self.experimental_var.get())
        self.config_manager.set_app_config("telemetry", self.telemetry_var.get())
        self.config_manager.set_app_config("crash_reporting", self.crash_reporting_var.get())
        self.config_manager.set_app_config("performance_monitoring", self.performance_var.get())
        self.config_manager.set_app_config("backup_retention_days", self.backup_retention_var.get())
        self.config_manager.set_app_config("max_backup_files", self.max_backups_var.get())
        
        # Save auth config
        self.config_manager.auth_manager.update_config(
            session_timeout=self.session_timeout_var.get() * 60,
            max_login_attempts=self.max_attempts_var.get(),
            lockout_duration=self.lockout_duration_var.get() * 60,
            password_min_length=self.password_min_length_var.get(),
            require_uppercase=self.require_uppercase_var.get(),
            require_lowercase=self.require_lowercase_var.get(),
            require_numbers=self.require_numbers_var.get(),
            require_special_chars=self.require_special_var.get()
        )
        
        self.dialog.destroy()
    
    def cancel(self):
        """Cancel without saving"""
        self.dialog.destroy()
    
    def reset_defaults(self):
        """Reset all settings to defaults"""
        if messagebox.askyesno("Reset Settings", "Are you sure you want to reset all settings to defaults?"):
            self.config_manager.reset_to_defaults()
            messagebox.showinfo("Settings Reset", "All settings have been reset to defaults.")
            self.dialog.destroy()
    
    def export_settings(self):
        """Export settings to file"""
        from tkinter import filedialog
        file_path = filedialog.asksaveasfilename(
            title="Export Settings",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            if self.config_manager.export_config(file_path):
                messagebox.showinfo("Export Successful", f"Settings exported to {file_path}")
            else:
                messagebox.showerror("Export Failed", "Failed to export settings.")
    
    def import_settings(self):
        """Import settings from file"""
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(
            title="Import Settings",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            if self.config_manager.import_config(file_path):
                messagebox.showinfo("Import Successful", "Settings imported successfully.")
                self.dialog.destroy()
            else:
                messagebox.showerror("Import Failed", "Failed to import settings.")
