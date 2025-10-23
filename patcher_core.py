import UnityPy
import os
import re
import shutil
import traceback
from typing import List, Dict, Any, Callable, Optional

class ROTMGPatcher:
    """Core patching functionality for ROTMG resources.assets files"""
    
    def __init__(self):
        self.verbose = False
        
    def set_verbose(self, verbose: bool):
        """Set verbose logging mode"""
        self.verbose = verbose
        
    def log_verbose(self, message: str, log_callback: Optional[Callable] = None):
        """Log verbose message"""
        if self.verbose:
            if log_callback:
                log_callback(f"[VERBOSE] {message}")
            else:
                print(f"[VERBOSE] {message}")
                
    def create_backup(self, resources_path: str) -> str:
        """
        Create a backup of the resources.assets file
        
        Args:
            resources_path: Path to the resources.assets file
            
        Returns:
            Path to the backup file
            
        Raises:
            FileNotFoundError: If resources.assets doesn't exist
            IOError: If backup creation fails
        """
        if not os.path.exists(resources_path):
            raise FileNotFoundError(f"Resources file does not exist: {resources_path}")
            
        backup_path = f"{resources_path}.backup"
        
        try:
            shutil.copy2(resources_path, backup_path)
            self.log_verbose(f"Created backup: {backup_path}")
            return backup_path
        except Exception as e:
            raise IOError(f"Failed to create backup: {e}")
            
    def restore_backup(self, resources_path: str) -> None:
        """
        Restore from backup file
        
        Args:
            resources_path: Path to the resources.assets file
            
        Raises:
            FileNotFoundError: If backup doesn't exist
            IOError: If restore fails
        """
        backup_path = f"{resources_path}.backup"
        
        if not os.path.exists(backup_path):
            raise FileNotFoundError(f"Backup file does not exist: {backup_path}")
            
        try:
            shutil.copy2(backup_path, resources_path)
            self.log_verbose(f"Restored from backup: {backup_path}")
        except Exception as e:
            raise IOError(f"Failed to restore backup: {e}")
            
    def load_text_asset_string(self, data) -> str:
        """Load text asset string from UnityPy data"""
        try:
            return str(data.m_Script.encode("unicode_escape").decode("utf-8"))
        except Exception as e:
            raise ValueError(f"Failed to load text asset: {e}")
            
    def encode_text_to_asset_string(self, data: str) -> bytes:
        """Encode text string to UnityPy asset format"""
        try:
            return data.encode("utf-8").decode("unicode_escape")
        except Exception as e:
            raise ValueError(f"Failed to encode text asset: {e}")
            
    def matching_asset(self, string_data: str, pattern: str) -> bool:
        """Check if asset content matches the locator pattern"""
        try:
            match = re.search(pattern, string_data)
            return match is not None
        except re.error as e:
            raise ValueError(f"Invalid regex pattern: {e}")
            
    def patch_asset_content(self, string_data: str, patch_rule: Dict[str, str]) -> str:
        """Apply a single patch rule to asset content"""
        try:
            target_pattern = patch_rule['target']
            replacement_pattern = patch_rule['replacement']
            return re.sub(target_pattern, replacement_pattern, string_data)
        except re.error as e:
            raise ValueError(f"Invalid regex in patch rule: {e}")
            
    def apply_patches(self, resources_path: str, patches: List[Dict[str, Any]], 
                     log_callback: Optional[Callable] = None, 
                     progress_callback: Optional[Callable] = None) -> None:
        """
        Apply patches to the resources.assets file
        
        Args:
            resources_path: Path to the resources.assets file
            patches: List of patch dictionaries to apply
            log_callback: Optional callback function for logging
            progress_callback: Optional callback function for progress updates
            
        Raises:
            FileNotFoundError: If resources.assets doesn't exist
            ValueError: If patch data is invalid
            IOError: If patching fails
        """
        if not os.path.exists(resources_path):
            raise FileNotFoundError(f"Resources file does not exist: {resources_path}")
            
        temp_path = resources_path + '.temp'
        applied_patches = 0
        total_patches = len(patches)
        
        def log(message: str):
            if log_callback:
                log_callback(message)
            else:
                print(message)
                
        def update_progress(value: float):
            if progress_callback:
                progress_callback(value)
                
        try:
            log("Loading assets file...")
            env = UnityPy.load(resources_path)
            log("Assets file loaded successfully")
            
            log(f"Searching for objects to patch...")
            total_objects = len(list(env.objects))
            processed_objects = 0
            
            for obj in env.objects:
                processed_objects += 1
                progress = (processed_objects / total_objects) * 50  # First half for processing
                update_progress(progress)
                
                if obj.type.name == "TextAsset":
                    data = obj.read()
                    script_content = self.load_text_asset_string(data)
                    
                    for patch_def in patches:
                        if self.matching_asset(script_content, patch_def['locator']):
                            log(f"Found asset file for patch: {patch_def['name']}")
                            self.log_verbose(f"Object to patch: {data.m_Name}", log)
                            
                            original_length = len(script_content)
                            
                            # Apply all patch rules for this patch definition
                            for patch_rule in patch_def['patches']:
                                script_content = self.patch_asset_content(script_content, patch_rule)
                                
                            new_length = len(script_content)
                            self.log_verbose(f"Content length changed from {original_length} to {new_length}", log)
                            
                            # Save the modified content
                            data.m_Script = self.encode_text_to_asset_string(script_content)
                            data.save()
                            
                            applied_patches += 1
                            log(f"Applied patch: {patch_def['name']}")
                            
            log("Saving patched data...")
            update_progress(75)
            
            # Save the modified assets file
            with open(temp_path, "wb") as f:
                f.write(env.file.save())
                
            # Replace original file with patched version
            shutil.move(temp_path, resources_path)
            
            update_progress(100)
            log(f"Patching complete! Applied {applied_patches} patches.")
            
        except Exception as e:
            # Clean up temp file if it exists
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
            error_msg = f"Error during patching: {e}"
            log(error_msg)
            self.log_verbose(traceback.format_exc(), log)
            raise IOError(error_msg)
            
    def validate_patches(self, patches: List[Dict[str, Any]]) -> bool:
        """
        Validate patch data before applying
        
        Args:
            patches: List of patch dictionaries to validate
            
        Returns:
            True if all patches are valid
            
        Raises:
            ValueError: If any patch is invalid
        """
        for i, patch in enumerate(patches):
            if not isinstance(patch, dict):
                raise ValueError(f"Patch {i} must be a dictionary")
                
            required_fields = ['name', 'locator', 'patches']
            for field in required_fields:
                if field not in patch:
                    raise ValueError(f"Patch {i} missing required field: {field}")
                    
            if not isinstance(patch['patches'], list):
                raise ValueError(f"Patch {i} 'patches' must be a list")
                
            # Validate locator pattern
            try:
                re.compile(patch['locator'])
            except re.error as e:
                raise ValueError(f"Patch {i} has invalid locator pattern: {e}")
                
            # Validate patch rules
            for j, patch_rule in enumerate(patch['patches']):
                if not isinstance(patch_rule, dict):
                    raise ValueError(f"Patch {i}, rule {j} must be a dictionary")
                    
                if 'target' not in patch_rule or 'replacement' not in patch_rule:
                    raise ValueError(f"Patch {i}, rule {j} missing 'target' or 'replacement'")
                    
                # Validate regex patterns
                try:
                    re.compile(patch_rule['target'])
                except re.error as e:
                    raise ValueError(f"Patch {i}, rule {j} has invalid target pattern: {e}")
                    
        return True
        
    def get_file_info(self, resources_path: str) -> Dict[str, Any]:
        """
        Get information about the resources.assets file
        
        Args:
            resources_path: Path to the resources.assets file
            
        Returns:
            Dictionary containing file information
            
        Raises:
            FileNotFoundError: If file doesn't exist
            IOError: If file cannot be read
        """
        if not os.path.exists(resources_path):
            raise FileNotFoundError(f"Resources file does not exist: {resources_path}")
            
        try:
            file_size = os.path.getsize(resources_path)
            
            # Try to load and get basic info
            env = UnityPy.load(resources_path)
            object_count = len(list(env.objects))
            text_asset_count = len([obj for obj in env.objects if obj.type.name == "TextAsset"])
            
            return {
                'file_path': resources_path,
                'file_size': file_size,
                'file_size_mb': round(file_size / (1024 * 1024), 2),
                'total_objects': object_count,
                'text_assets': text_asset_count,
                'backup_exists': os.path.exists(f"{resources_path}.backup")
            }
            
        except Exception as e:
            raise IOError(f"Failed to read file info: {e}")
            
    def test_patch_patterns(self, resources_path: str, patches: List[Dict[str, Any]], 
                           log_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """
        Test patch patterns without applying them
        
        Args:
            resources_path: Path to the resources.assets file
            patches: List of patch dictionaries to test
            log_callback: Optional callback function for logging
            
        Returns:
            Dictionary containing test results
        """
        if not os.path.exists(resources_path):
            raise FileNotFoundError(f"Resources file does not exist: {resources_path}")
            
        def log(message: str):
            if log_callback:
                log_callback(message)
            else:
                print(message)
                
        results = {
            'total_patches': len(patches),
            'matched_patches': 0,
            'patch_results': []
        }
        
        try:
            log("Loading assets file for testing...")
            env = UnityPy.load(resources_path)
            
            for patch_def in patches:
                patch_result = {
                    'name': patch_def['name'],
                    'matched': False,
                    'matched_objects': []
                }
                
                for obj in env.objects:
                    if obj.type.name == "TextAsset":
                        data = obj.read()
                        script_content = self.load_text_asset_string(data)
                        
                        if self.matching_asset(script_content, patch_def['locator']):
                            patch_result['matched'] = True
                            patch_result['matched_objects'].append(data.m_Name)
                            
                if patch_result['matched']:
                    results['matched_patches'] += 1
                    
                results['patch_results'].append(patch_result)
                
            log(f"Test complete. {results['matched_patches']}/{results['total_patches']} patches would match.")
            return results
            
        except Exception as e:
            raise IOError(f"Failed to test patches: {e}")
