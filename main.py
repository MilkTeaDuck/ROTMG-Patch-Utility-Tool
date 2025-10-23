import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import json
import os
import threading
import re
from patcher_core import ROTMGPatcher
from patch_manager import PatchManager
from object_parser import ObjectBlockParser

class ROTMGPatchUtilityGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("ROTMG Assets Patch Utility Tool")
        self.root.geometry("1000x700")
        self.root.resizable(True, True)
        
        # Initialize components
        self.patcher = ROTMGPatcher()
        self.patch_manager = PatchManager()
        self.object_parser = ObjectBlockParser()
        
        # Variables
        self.resources_path = tk.StringVar()
        self.patches_file = tk.StringVar()
        self.selected_patches = []
        self.patch_data = []
        
        # Create GUI
        self.create_widgets()
        self.load_default_patches()
        
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # File selection frame
        file_frame = ttk.LabelFrame(main_frame, text="File Selection", padding="5")
        file_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        file_frame.columnconfigure(1, weight=1)
        
        # Resources.assets path
        ttk.Label(file_frame, text="Resources.assets:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        ttk.Entry(file_frame, textvariable=self.resources_path, width=50).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(file_frame, text="Browse", command=self.browse_resources).grid(row=0, column=2)
        
        # Patches file path
        ttk.Label(file_frame, text="Patches JSON:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        ttk.Entry(file_frame, textvariable=self.patches_file, width=50).grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 5), pady=(5, 0))
        ttk.Button(file_frame, text="Browse", command=self.browse_patches).grid(row=1, column=2, pady=(5, 0))
        
        # Patch management frame
        patch_frame = ttk.LabelFrame(main_frame, text="Patch Management", padding="5")
        patch_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        patch_frame.columnconfigure(0, weight=1)
        
        # Patch list with checkboxes
        self.patch_listbox = tk.Listbox(patch_frame, height=8, selectmode=tk.MULTIPLE)
        self.patch_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        # Scrollbar for patch list
        patch_scrollbar = ttk.Scrollbar(patch_frame, orient=tk.VERTICAL, command=self.patch_listbox.yview)
        patch_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.patch_listbox.configure(yscrollcommand=patch_scrollbar.set)
        
        # Patch management buttons
        button_frame = ttk.Frame(patch_frame)
        button_frame.grid(row=0, column=2, sticky=(tk.N, tk.S), padx=(5, 0))
        
        ttk.Button(button_frame, text="Add Patch", command=self.add_patch).pack(fill=tk.X, pady=(0, 5))
        ttk.Button(button_frame, text="Edit Patch", command=self.edit_patch).pack(fill=tk.X, pady=(0, 5))
        ttk.Button(button_frame, text="Remove Patch", command=self.remove_patch).pack(fill=tk.X, pady=(0, 5))
        ttk.Button(button_frame, text="Save Patches", command=self.save_patches).pack(fill=tk.X, pady=(0, 5))
        ttk.Button(button_frame, text="Save to Directory", command=self.save_patches_to_directory).pack(fill=tk.X, pady=(0, 5))
        ttk.Button(button_frame, text="Load Patches", command=self.load_patches).pack(fill=tk.X, pady=(0, 5))
        
        # Control buttons frame
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(control_frame, text="Create Backup", command=self.create_backup).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(control_frame, text="Restore Backup", command=self.restore_backup).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(control_frame, text="Apply Selected Patches", command=self.apply_patches).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(control_frame, text="Apply All Patches", command=self.apply_all_patches).pack(side=tk.LEFT, padx=(0, 5))
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Log output
        log_frame = ttk.LabelFrame(main_frame, text="Log Output", padding="5")
        log_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, state=tk.DISABLED)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
    def log_message(self, message):
        """Add message to log output"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.root.update_idletasks()
        
    def browse_resources(self):
        """Browse for resources.assets file"""
        filename = filedialog.askopenfilename(
            title="Select resources.assets file",
            filetypes=[("Assets files", "*.assets"), ("All files", "*.*")]
        )
        if filename:
            self.resources_path.set(filename)
            self.log_message(f"Selected resources file: {filename}")
            
    def browse_patches(self):
        """Browse for patches JSON file"""
        filename = filedialog.askopenfilename(
            title="Select patches JSON file",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            self.patches_file.set(filename)
            self.load_patches()
            
    def load_default_patches(self):
        """Load default patches from the patches directory"""
        patches_dir = "patches"
        if os.path.exists(patches_dir) and os.path.isdir(patches_dir):
            try:
                self.patch_data = self.patch_manager.load_patches_from_directory(patches_dir)
                self.update_patch_list()
                self.log_message(f"Auto-loaded {len(self.patch_data)} patches from patches directory")
            except Exception as e:
                self.log_message(f"Error auto-loading patches: {str(e)}")
                # Fallback to old method if patches directory fails
                default_path = r"d:\Games\Other Games\ROTMG Exalt\Patching Resources\patches.json"
                if os.path.exists(default_path):
                    self.patches_file.set(default_path)
                    self.load_patches()
            
    def load_patches(self):
        """Load patches from JSON file"""
        if not self.patches_file.get():
            messagebox.showerror("Error", "Please select a patches JSON file")
            return
            
        try:
            self.patch_data = self.patch_manager.load_patches(self.patches_file.get())
            self.update_patch_list()
            self.log_message(f"Loaded {len(self.patch_data)} patches from {self.patches_file.get()}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load patches: {str(e)}")
            self.log_message(f"Error loading patches: {str(e)}")
            
    def update_patch_list(self):
        """Update the patch listbox with current patches"""
        self.patch_listbox.delete(0, tk.END)
        for i, patch in enumerate(self.patch_data):
            self.patch_listbox.insert(tk.END, f"{i+1}. {patch['name']}")
            
    def add_patch(self):
        """Add a new patch"""
        dialog = EnhancedPatchDialog(self.root, "Add New Patch", self.object_parser)
        if dialog.result:
            self.patch_data.append(dialog.result)
            self.update_patch_list()
            self.log_message(f"Added patch: {dialog.result['name']}")
            
    def edit_patch(self):
        """Edit selected patch"""
        selection = self.patch_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a patch to edit")
            return
            
        index = selection[0]
        patch = self.patch_data[index]
        
        # Use the enhanced patch dialog for editing
        dialog = EnhancedPatchEditDialog(self.root, "Edit Patch", patch, self.object_parser)
        if dialog.result:
            self.patch_data[index] = dialog.result
            self.update_patch_list()
            self.log_message(f"Updated patch: {dialog.result['name']}")
            
    def remove_patch(self):
        """Remove selected patch"""
        selection = self.patch_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a patch to remove")
            return
            
        index = selection[0]
        patch_name = self.patch_data[index]['name']
        if messagebox.askyesno("Confirm", f"Remove patch '{patch_name}'?"):
            del self.patch_data[index]
            self.update_patch_list()
            self.log_message(f"Removed patch: {patch_name}")
            
    def save_patches(self):
        """Save patches to JSON file"""
        if not self.patches_file.get():
            filename = filedialog.asksaveasfilename(
                title="Save patches JSON file",
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            if filename:
                self.patches_file.set(filename)
            else:
                return
                
        try:
            self.patch_manager.save_patches(self.patches_file.get(), self.patch_data)
            self.log_message(f"Saved {len(self.patch_data)} patches to {self.patches_file.get()}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save patches: {str(e)}")
            self.log_message(f"Error saving patches: {str(e)}")
            
    def save_patches_to_directory(self):
        """Save all patches as individual files to the patches directory"""
        patches_dir = "patches"
        if not os.path.exists(patches_dir):
            os.makedirs(patches_dir)
            
        try:
            saved_count = 0
            for i, patch in enumerate(self.patch_data):
                filename = f"{i+1:02d}_{self.sanitize_filename(patch['name'])}.json"
                filepath = os.path.join(patches_dir, filename)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(patch, f, indent=2, ensure_ascii=False)
                    
                saved_count += 1
                
            self.log_message(f"Saved {saved_count} patches to patches directory")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save patches to directory: {str(e)}")
            self.log_message(f"Error saving patches to directory: {str(e)}")
            
    def sanitize_filename(self, name):
        """Convert patch name to a valid filename"""
        import re
        # Remove or replace invalid characters
        filename = re.sub(r'[<>:"/\\|?*]', '_', name)
        filename = re.sub(r'\s+', '_', filename)
        filename = filename.strip('_')
        return filename
            
    def create_backup(self):
        """Create backup of resources.assets"""
        if not self.resources_path.get():
            messagebox.showerror("Error", "Please select a resources.assets file")
            return
            
        try:
            self.patcher.create_backup(self.resources_path.get())
            self.log_message("Backup created successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create backup: {str(e)}")
            self.log_message(f"Error creating backup: {str(e)}")
            
    def restore_backup(self):
        """Restore backup of resources.assets"""
        if not self.resources_path.get():
            messagebox.showerror("Error", "Please select a resources.assets file")
            return
            
        try:
            self.patcher.restore_backup(self.resources_path.get())
            self.log_message("Backup restored successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to restore backup: {str(e)}")
            self.log_message(f"Error restoring backup: {str(e)}")
            
    def apply_patches(self):
        """Apply selected patches"""
        selection = self.patch_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select patches to apply")
            return
            
        selected_patches = [self.patch_data[i] for i in selection]
        self._apply_patches_thread(selected_patches)
        
    def apply_all_patches(self):
        """Apply all patches"""
        if not self.patch_data:
            messagebox.showwarning("Warning", "No patches loaded")
            return
            
        self._apply_patches_thread(self.patch_data)
        
    def _apply_patches_thread(self, patches):
        """Apply patches in a separate thread"""
        if not self.resources_path.get():
            messagebox.showerror("Error", "Please select a resources.assets file")
            return
            
        def apply_thread():
            try:
                self.status_var.set("Applying patches...")
                self.progress_var.set(0)
                
                # Create backup first
                self.patcher.create_backup(self.resources_path.get())
                self.log_message("Backup created before applying patches")
                
                # Apply patches
                def update_progress(value):
                    self.progress_var.set(value)
                self.patcher.apply_patches(self.resources_path.get(), patches, self.log_message, update_progress)
                
                self.status_var.set("Patches applied successfully")
                self.progress_var.set(100)
                self.log_message("All patches applied successfully!")
                
            except Exception as e:
                self.status_var.set("Error applying patches")
                self.log_message(f"Error applying patches: {str(e)}")
                messagebox.showerror("Error", f"Failed to apply patches: {str(e)}")
                
        thread = threading.Thread(target=apply_thread)
        thread.daemon = True
        thread.start()


class EnhancedPatchDialog:
    def __init__(self, parent, title, object_parser):
        self.result = None
        self.object_parser = object_parser
        self.parsed_object = None
        self.changes = {}
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("800x600")
        self.dialog.resizable(True, True)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        # Create widgets
        self.create_widgets()
        
        # Wait for dialog to close
        self.dialog.wait_window()

class EnhancedPatchEditDialog:
    def __init__(self, parent, title, existing_patch, object_parser):
        self.result = None
        self.object_parser = object_parser
        self.existing_patch = existing_patch
        self.parsed_object = None
        self.changes = {}
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("800x600")
        self.dialog.resizable(True, True)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        # Create widgets
        self.create_widgets()
        
        # Wait for dialog to close
        self.dialog.wait_window()
        
    def create_widgets(self):
        # Main notebook for tabs
        notebook = ttk.Notebook(self.dialog)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Patch Information Tab
        self.create_patch_info_tab(notebook)
        
        # Patch Rules Tab
        self.create_patch_rules_tab(notebook)
        
        # Preview Tab
        self.create_preview_tab(notebook)
        
        # Buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        ttk.Button(button_frame, text="OK", command=self.ok_clicked).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Cancel", command=self.cancel_clicked).pack(side=tk.RIGHT)
        
    def create_patch_info_tab(self, notebook):
        """Create the patch information tab"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Patch Info")
        
        # Patch name
        ttk.Label(frame, text="Patch Name:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 5))
        self.name_var = tk.StringVar(value=self.existing_patch['name'])
        ttk.Entry(frame, textvariable=self.name_var, width=60).grid(row=0, column=1, sticky=(tk.W, tk.E), pady=(10, 5))
        
        # Locator pattern
        ttk.Label(frame, text="Locator Pattern:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(0, 5))
        self.locator_var = tk.StringVar(value=self.existing_patch['locator'])
        locator_entry = ttk.Entry(frame, textvariable=self.locator_var, width=60)
        locator_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # Character count preservation toggle
        toggle_frame = ttk.Frame(frame)
        toggle_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.preserve_count_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(toggle_frame, text="Preserve character count for spoofing", 
                       variable=self.preserve_count_var,
                       command=self.toggle_character_preservation).pack(side=tk.LEFT)
        
        # Configure grid weights
        frame.columnconfigure(1, weight=1)
        
    def create_patch_rules_tab(self, notebook):
        """Create the patch rules tab"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Patch Rules")
        
        # Instructions
        ttk.Label(frame, text="Edit patch rules:").pack(anchor=tk.W, pady=(0, 10))
        
        # Create scrollable frame for patch rules
        canvas = tk.Canvas(frame)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        self.rules_frame = scrollable_frame
        self.rule_vars = {}
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Populate with existing patch rules
        self.populate_patch_rules()
        
    def create_preview_tab(self, notebook):
        """Create the preview tab"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Preview")
        
        # Current patch info
        ttk.Label(frame, text="Current Patch Definition:").pack(anchor=tk.W, pady=(0, 5))
        self.current_preview = scrolledtext.ScrolledText(frame, height=15, wrap=tk.WORD, state=tk.DISABLED)
        self.current_preview.pack(fill=tk.BOTH, expand=True)
        
        # Update preview button
        ttk.Button(frame, text="Update Preview", 
                  command=self.update_preview).pack(pady=(10, 0))
        
        # Show current patch definition
        self.update_current_preview()
        
    def populate_patch_rules(self):
        """Populate the patch rules tab with existing rules"""
        # Clear existing widgets
        for widget in self.rules_frame.winfo_children():
            widget.destroy()
            
        self.rule_vars = {}
        
        for i, patch_rule in enumerate(self.existing_patch['patches']):
            # Rule number
            ttk.Label(self.rules_frame, text=f"Rule {i+1}:").grid(row=i*2, column=0, sticky=tk.W, padx=(0, 10), pady=(5, 2))
            
            # Target pattern
            ttk.Label(self.rules_frame, text="Target:").grid(row=i*2+1, column=0, sticky=tk.W, padx=(0, 10), pady=(0, 5))
            target_var = tk.StringVar(value=patch_rule['target'])
            self.rule_vars[f'target_{i}'] = target_var
            ttk.Entry(self.rules_frame, textvariable=target_var, width=50).grid(row=i*2+1, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
            
            # Replacement pattern
            ttk.Label(self.rules_frame, text="Replacement:").grid(row=i*2+1, column=2, sticky=tk.W, padx=(10, 10), pady=(0, 5))
            replacement_var = tk.StringVar(value=patch_rule['replacement'])
            self.rule_vars[f'replacement_{i}'] = replacement_var
            ttk.Entry(self.rules_frame, textvariable=replacement_var, width=50).grid(row=i*2+1, column=3, sticky=(tk.W, tk.E), pady=(0, 5))
            
        # Configure grid weights
        self.rules_frame.columnconfigure(1, weight=1)
        self.rules_frame.columnconfigure(3, weight=1)
        
    def update_current_preview(self):
        """Update the current patch preview"""
        import json
        preview_text = json.dumps(self.existing_patch, indent=2)
        
        self.current_preview.config(state=tk.NORMAL)
        self.current_preview.delete("1.0", tk.END)
        self.current_preview.insert("1.0", preview_text)
        self.current_preview.config(state=tk.DISABLED)
        
    def update_preview(self):
        """Update the preview with current changes"""
        try:
            # Collect current values
            updated_patch = {
                'name': self.name_var.get().strip(),
                'locator': self.locator_var.get().strip(),
                'patches': []
            }
            
            # Collect patch rules
            for i in range(len(self.existing_patch['patches'])):
                target = self.rule_vars[f'target_{i}'].get().strip()
                replacement = self.rule_vars[f'replacement_{i}'].get().strip()
                
                if target and replacement:
                    updated_patch['patches'].append({
                        'target': target,
                        'replacement': replacement
                    })
            
            # Update preview
            import json
            preview_text = json.dumps(updated_patch, indent=2)
            
            self.current_preview.config(state=tk.NORMAL)
            self.current_preview.delete("1.0", tk.END)
            self.current_preview.insert("1.0", preview_text)
            self.current_preview.config(state=tk.DISABLED)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update preview: {str(e)}")
            
    def toggle_character_preservation(self):
        """Toggle character count preservation"""
        self.object_parser.set_character_count_preservation(self.preserve_count_var.get())
        
    def ok_clicked(self):
        """OK button clicked"""
        if not self.name_var.get().strip():
            messagebox.showerror("Error", "Patch name is required")
            return
            
        if not self.locator_var.get().strip():
            messagebox.showerror("Error", "Locator pattern is required")
            return
            
        try:
            # Collect current values
            updated_patch = {
                'name': self.name_var.get().strip(),
                'locator': self.locator_var.get().strip(),
                'patches': []
            }
            
            # Collect patch rules
            for i in range(len(self.existing_patch['patches'])):
                target = self.rule_vars[f'target_{i}'].get().strip()
                replacement = self.rule_vars[f'replacement_{i}'].get().strip()
                
                if target and replacement:
                    updated_patch['patches'].append({
                        'target': target,
                        'replacement': replacement
                    })
            
            if not updated_patch['patches']:
                messagebox.showerror("Error", "At least one patch rule is required")
                return
                
            self.result = updated_patch
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update patch: {str(e)}")
            
    def cancel_clicked(self):
        """Cancel button clicked"""
        self.dialog.destroy()

class EnhancedPatchDialog:
    def __init__(self, parent, title, object_parser):
        self.result = None
        self.object_parser = object_parser
        self.parsed_object = None
        self.changes = {}
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("800x600")
        self.dialog.resizable(True, True)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        # Create widgets
        self.create_widgets()
        
        # Wait for dialog to close
        self.dialog.wait_window()
        
    def create_widgets(self):
        # Main notebook for tabs
        notebook = ttk.Notebook(self.dialog)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Object Block Input Tab
        self.create_object_input_tab(notebook)
        
        # Field Changes Tab
        self.create_field_changes_tab(notebook)
        
        # Preview Tab
        self.create_preview_tab(notebook)
        
        # Buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        ttk.Button(button_frame, text="OK", command=self.ok_clicked).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Cancel", command=self.cancel_clicked).pack(side=tk.RIGHT)
        
    def create_object_input_tab(self, notebook):
        """Create the object block input tab"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Object Block")
        
        # Character count preservation toggle
        toggle_frame = ttk.Frame(frame)
        toggle_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.preserve_count_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(toggle_frame, text="Preserve character count for spoofing", 
                       variable=self.preserve_count_var,
                       command=self.toggle_character_preservation).pack(side=tk.LEFT)
        
        # Object block input
        ttk.Label(frame, text="Paste the original object block:").pack(anchor=tk.W, pady=(0, 5))
        
        self.object_text = scrolledtext.ScrolledText(frame, height=15, wrap=tk.WORD)
        self.object_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Parse button
        parse_frame = ttk.Frame(frame)
        parse_frame.pack(fill=tk.X)
        
        ttk.Button(parse_frame, text="Parse Object Block", 
                  command=self.parse_object_block).pack(side=tk.LEFT)
        
        self.parse_status = ttk.Label(parse_frame, text="")
        self.parse_status.pack(side=tk.LEFT, padx=(10, 0))
        
    def create_field_changes_tab(self, notebook):
        """Create the field changes tab"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Field Changes")
        
        # Instructions
        ttk.Label(frame, text="Select fields to modify and enter new values:").pack(anchor=tk.W, pady=(0, 10))
        
        # Create scrollable frame for field entries
        canvas = tk.Canvas(frame)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        self.field_frame = scrollable_frame
        self.field_vars = {}
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
    def create_preview_tab(self, notebook):
        """Create the preview tab"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Preview")
        
        # Original block
        ttk.Label(frame, text="Original Object Block:").pack(anchor=tk.W, pady=(0, 5))
        self.original_preview = scrolledtext.ScrolledText(frame, height=8, wrap=tk.WORD, state=tk.DISABLED)
        self.original_preview.pack(fill=tk.X, pady=(0, 10))
        
        # Modified block
        ttk.Label(frame, text="Modified Object Block:").pack(anchor=tk.W, pady=(0, 5))
        self.modified_preview = scrolledtext.ScrolledText(frame, height=8, wrap=tk.WORD, state=tk.DISABLED)
        self.modified_preview.pack(fill=tk.BOTH, expand=True)
        
        # Update preview button
        ttk.Button(frame, text="Update Preview", 
                  command=self.update_preview).pack(pady=(10, 0))
        
    def toggle_character_preservation(self):
        """Toggle character count preservation"""
        self.object_parser.set_character_count_preservation(self.preserve_count_var.get())
        
    def parse_object_block(self):
        """Parse the object block and populate field changes"""
        object_text = self.object_text.get("1.0", tk.END).strip()
        
        if not object_text:
            self.parse_status.config(text="Please enter an object block", foreground="red")
            return
            
        # Validate and parse
        is_valid, error_msg = self.object_parser.validate_object_block(object_text)
        if not is_valid:
            self.parse_status.config(text=f"Error: {error_msg}", foreground="red")
            return
            
        try:
            self.parsed_object = self.object_parser.parse_object_block(object_text)
            self.populate_field_changes()
            self.update_original_preview()
            self.parse_status.config(text="Object block parsed successfully", foreground="green")
            
        except Exception as e:
            self.parse_status.config(text=f"Parse error: {str(e)}", foreground="red")
            
    def populate_field_changes(self):
        """Populate the field changes tab with editable fields"""
        # Clear existing widgets
        for widget in self.field_frame.winfo_children():
            widget.destroy()
            
        self.field_vars = {}
        
        if not self.parsed_object:
            return
            
        # Get editable fields
        fields = self.object_parser.get_editable_fields(self.parsed_object)
        
        row = 0
        for field in fields:
            # Field label
            ttk.Label(self.field_frame, text=f"{field}:").grid(row=row, column=0, sticky=tk.W, padx=(0, 10), pady=2)
            
            # Current value
            if field in self.parsed_object['object_attributes']:
                current_value = self.parsed_object['object_attributes'][field]
            elif field in self.parsed_object['elements']:
                current_value = self.parsed_object['elements'][field]
            else:
                current_value = ""
                
            # Entry widget
            var = tk.StringVar(value=current_value)
            self.field_vars[field] = var
            
            entry = ttk.Entry(self.field_frame, textvariable=var, width=50)
            entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=2)
            
            # Change indicator
            change_label = ttk.Label(self.field_frame, text="", foreground="blue")
            change_label.grid(row=row, column=2, padx=(10, 0), pady=2)
            
            # Bind change detection
            var.trace('w', lambda *args, f=field, l=change_label: self.detect_field_change(f, l))
            
            row += 1
            
        # Configure grid weights
        self.field_frame.columnconfigure(1, weight=1)
        
    def detect_field_change(self, field_name, change_label):
        """Detect when a field value changes"""
        current_value = self.field_vars[field_name].get()
        
        # Get original value
        if field_name in self.parsed_object['object_attributes']:
            original_value = self.parsed_object['object_attributes'][field_name]
        elif field_name in self.parsed_object['elements']:
            original_value = self.parsed_object['elements'][field_name]
        else:
            original_value = ""
            
        if current_value != original_value:
            change_label.config(text="*", foreground="red")
            self.changes[field_name] = current_value
        else:
            change_label.config(text="")
            if field_name in self.changes:
                del self.changes[field_name]
                
    def update_original_preview(self):
        """Update the original preview"""
        if self.parsed_object:
            self.original_preview.config(state=tk.NORMAL)
            self.original_preview.delete("1.0", tk.END)
            self.original_preview.insert("1.0", self.parsed_object['original_block'])
            self.original_preview.config(state=tk.DISABLED)
            
    def update_preview(self):
        """Update the modified preview"""
        if not self.parsed_object:
            messagebox.showwarning("Warning", "Please parse an object block first")
            return
            
        if not self.changes:
            messagebox.showwarning("Warning", "Please make some changes to preview")
            return
            
        try:
            preview_text = self.object_parser.preview_changes(self.parsed_object, self.changes)
            
            self.modified_preview.config(state=tk.NORMAL)
            self.modified_preview.delete("1.0", tk.END)
            self.modified_preview.insert("1.0", preview_text)
            self.modified_preview.config(state=tk.DISABLED)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate preview: {str(e)}")
            
    def ok_clicked(self):
        """OK button clicked"""
        if not self.parsed_object:
            messagebox.showerror("Error", "Please parse an object block first")
            return
            
        if not self.changes:
            messagebox.showerror("Error", "Please make at least one change")
            return
            
        try:
            # Create patch definition
            patch_def = self.object_parser.create_patch_from_changes(self.parsed_object, self.changes)
            self.result = patch_def
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create patch: {str(e)}")
            
    def cancel_clicked(self):
        """Cancel button clicked"""
        self.dialog.destroy()

class PatchRuleDialog:
    def __init__(self, parent, title, patch_rule=None):
        self.result = None
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("500x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 100, parent.winfo_rooty() + 100))
        
        # Create widgets
        self.create_widgets(patch_rule)
        
        # Wait for dialog to close
        self.dialog.wait_window()
        
    def create_widgets(self, patch_rule):
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Target pattern
        ttk.Label(main_frame, text="Target Pattern:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.target_var = tk.StringVar(value=patch_rule['target'] if patch_rule else "")
        target_entry = ttk.Entry(main_frame, textvariable=self.target_var, width=60)
        target_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # Replacement pattern
        ttk.Label(main_frame, text="Replacement Pattern:").grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        self.replacement_var = tk.StringVar(value=patch_rule['replacement'] if patch_rule else "")
        replacement_entry = ttk.Entry(main_frame, textvariable=self.replacement_var, width=60)
        replacement_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=(20, 0))
        
        ttk.Button(button_frame, text="OK", command=self.ok_clicked).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Cancel", command=self.cancel_clicked).pack(side=tk.LEFT)
        
        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        
    def ok_clicked(self):
        """OK button clicked"""
        if not self.target_var.get().strip():
            messagebox.showerror("Error", "Target pattern is required")
            return
            
        if not self.replacement_var.get().strip():
            messagebox.showerror("Error", "Replacement pattern is required")
            return
            
        self.result = {
            'target': self.target_var.get().strip(),
            'replacement': self.replacement_var.get().strip()
        }
        self.dialog.destroy()
        
    def cancel_clicked(self):
        """Cancel button clicked"""
        self.dialog.destroy()

def main():
    root = tk.Tk()
    app = ROTMGPatchUtilityGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
