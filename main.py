import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import json
import os
import threading
import re
from patcher_core import ROTMGPatcher
from patch_manager import PatchManager

class ROTMGPatchUtilityGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("ROTMG Assets Patch Utility Tool")
        self.root.geometry("1000x700")
        self.root.resizable(True, True)
        
        # Initialize components
        self.patcher = ROTMGPatcher()
        self.patch_manager = PatchManager()
        
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
        dialog = PatchEditDialog(self.root, "Add New Patch")
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
        dialog = PatchEditDialog(self.root, "Edit Patch", patch)
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
                self.patcher.apply_patches(self.resources_path.get(), patches, self.log_message, self.progress_var)
                
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

class PatchEditDialog:
    def __init__(self, parent, title, patch_data=None):
        self.result = None
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("600x500")
        self.dialog.resizable(True, True)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        # Create widgets
        self.create_widgets(patch_data)
        
        # Wait for dialog to close
        self.dialog.wait_window()
        
    def create_widgets(self, patch_data):
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Patch name
        ttk.Label(main_frame, text="Patch Name:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.name_var = tk.StringVar(value=patch_data['name'] if patch_data else "")
        ttk.Entry(main_frame, textvariable=self.name_var, width=50).grid(row=0, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # Locator pattern
        ttk.Label(main_frame, text="Locator Pattern:").grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        self.locator_var = tk.StringVar(value=patch_data['locator'] if patch_data else "")
        locator_entry = ttk.Entry(main_frame, textvariable=self.locator_var, width=50)
        locator_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # Patches list
        ttk.Label(main_frame, text="Patches:").grid(row=2, column=0, sticky=(tk.W, tk.N), pady=(10, 0))
        
        patches_frame = ttk.Frame(main_frame)
        patches_frame.grid(row=2, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        patches_frame.columnconfigure(0, weight=1)
        
        self.patches_listbox = tk.Listbox(patches_frame, height=8)
        self.patches_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        patches_scrollbar = ttk.Scrollbar(patches_frame, orient=tk.VERTICAL, command=self.patches_listbox.yview)
        patches_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.patches_listbox.configure(yscrollcommand=patches_scrollbar.set)
        
        # Patch buttons
        patch_buttons = ttk.Frame(patches_frame)
        patch_buttons.grid(row=0, column=2, sticky=(tk.N, tk.S), padx=(5, 0))
        
        ttk.Button(patch_buttons, text="Add", command=self.add_patch).pack(fill=tk.X, pady=(0, 5))
        ttk.Button(patch_buttons, text="Edit", command=self.edit_patch).pack(fill=tk.X, pady=(0, 5))
        ttk.Button(patch_buttons, text="Remove", command=self.remove_patch).pack(fill=tk.X, pady=(0, 5))
        
        # Load patches if provided
        self.patches = patch_data['patches'].copy() if patch_data else []
        self.update_patches_list()
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=(20, 0))
        
        ttk.Button(button_frame, text="OK", command=self.ok_clicked).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Cancel", command=self.cancel_clicked).pack(side=tk.LEFT)
        
        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
    def update_patches_list(self):
        """Update the patches listbox"""
        self.patches_listbox.delete(0, tk.END)
        for i, patch in enumerate(self.patches):
            self.patches_listbox.insert(tk.END, f"{i+1}. {patch['target'][:50]}...")
            
    def add_patch(self):
        """Add a new patch"""
        dialog = PatchRuleDialog(self.dialog, "Add Patch Rule")
        if dialog.result:
            self.patches.append(dialog.result)
            self.update_patches_list()
            
    def edit_patch(self):
        """Edit selected patch"""
        selection = self.patches_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a patch to edit")
            return
            
        index = selection[0]
        patch = self.patches[index]
        dialog = PatchRuleDialog(self.dialog, "Edit Patch Rule", patch)
        if dialog.result:
            self.patches[index] = dialog.result
            self.update_patches_list()
            
    def remove_patch(self):
        """Remove selected patch"""
        selection = self.patches_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a patch to remove")
            return
            
        index = selection[0]
        del self.patches[index]
        self.update_patches_list()
        
    def ok_clicked(self):
        """OK button clicked"""
        if not self.name_var.get().strip():
            messagebox.showerror("Error", "Patch name is required")
            return
            
        if not self.locator_var.get().strip():
            messagebox.showerror("Error", "Locator pattern is required")
            return
            
        if not self.patches:
            messagebox.showerror("Error", "At least one patch rule is required")
            return
            
        self.result = {
            'name': self.name_var.get().strip(),
            'locator': self.locator_var.get().strip(),
            'patches': self.patches
        }
        self.dialog.destroy()
        
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
