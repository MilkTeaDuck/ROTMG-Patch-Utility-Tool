import json
import os
import sys
from typing import List, Dict, Any, Optional

class PatchManager:
    """Manages patch data loading, saving, and validation"""
    
    def __init__(self):
        self.patches = []
        
    def load_patches(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Load patches from a JSON file
        
        Args:
            file_path: Path to the JSON file containing patches
            
        Returns:
            List of patch dictionaries
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            json.JSONDecodeError: If the file contains invalid JSON
            ValueError: If the patch data is invalid
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Patch file does not exist: {file_path}")
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                patches = json.load(f)
                
            # Handle both single patch and array of patches
            if isinstance(patches, dict):
                patches = [patches]
            elif not isinstance(patches, list):
                raise ValueError("Patch file must contain a single patch object or an array of patches")
                
            # Validate the loaded patches
            self.validate_patches(patches)
            
            self.patches = patches
            return patches
            
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"Failed to decode patches file: {e}")
        except Exception as e:
            raise ValueError(f"Error loading patches: {e}")
            
    def load_patches_from_directory(self, directory_path: str) -> List[Dict[str, Any]]:
        """
        Load all patch files from a directory
        
        Args:
            directory_path: Path to the directory containing patch files
            
        Returns:
            List of patch dictionaries
            
        Raises:
            FileNotFoundError: If the directory doesn't exist
            ValueError: If any patch file is invalid
        """
        if not os.path.exists(directory_path):
            raise FileNotFoundError(f"Patches directory does not exist: {directory_path}")
            
        if not os.path.isdir(directory_path):
            raise ValueError(f"Path is not a directory: {directory_path}")
            
        patches = []
        json_files = [f for f in os.listdir(directory_path) if f.endswith('.json')]
        json_files.sort()  # Sort to maintain consistent order
        
        for filename in json_files:
            file_path = os.path.join(directory_path, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    patch_data = json.load(f)
                    
                # Handle both single patch and array of patches
                if isinstance(patch_data, dict):
                    patch_data = [patch_data]
                elif not isinstance(patch_data, list):
                    raise ValueError(f"File {filename} must contain a single patch object or an array of patches")
                    
                patches.extend(patch_data)
                
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON in file {filename}: {e}")
            except Exception as e:
                raise ValueError(f"Error loading patch file {filename}: {e}")
                
        # Validate all loaded patches
        self.validate_patches(patches)
        
        self.patches = patches
        return patches
            
    def save_patches(self, file_path: str, patches: List[Dict[str, Any]]) -> None:
        """
        Save patches to a JSON file
        
        Args:
            file_path: Path where to save the JSON file
            patches: List of patch dictionaries to save
            
        Raises:
            ValueError: If the patch data is invalid
            IOError: If the file cannot be written
        """
        # Validate patches before saving
        self.validate_patches(patches)
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(patches, f, indent=2, ensure_ascii=False)
                
            self.patches = patches
            
        except Exception as e:
            raise IOError(f"Error saving patches: {e}")
            
    def validate_patches(self, patches: List[Dict[str, Any]]) -> bool:
        """
        Validate patch data structure
        
        Args:
            patches: List of patch dictionaries to validate
            
        Returns:
            True if valid
            
        Raises:
            ValueError: If validation fails
        """
        if not isinstance(patches, list):
            raise ValueError("Patches must be a list")
            
        for i, patch in enumerate(patches):
            if not isinstance(patch, dict):
                raise ValueError(f"Patch {i} must be a dictionary")
                
            # Check required fields
            required_fields = ['name', 'locator', 'patches']
            for field in required_fields:
                if field not in patch:
                    raise ValueError(f"Patch {i} missing required field: {field}")
                    
            # Check field types
            if not isinstance(patch['name'], str):
                raise ValueError(f"Patch {i} 'name' must be a string")
                
            if not isinstance(patch['locator'], str):
                raise ValueError(f"Patch {i} 'locator' must be a string")
                
            if not isinstance(patch['patches'], list):
                raise ValueError(f"Patch {i} 'patches' must be a list")
                
            # Validate individual patch rules
            for j, patch_rule in enumerate(patch['patches']):
                if not isinstance(patch_rule, dict):
                    raise ValueError(f"Patch {i}, rule {j} must be a dictionary")
                    
                if 'target' not in patch_rule or 'replacement' not in patch_rule:
                    raise ValueError(f"Patch {i}, rule {j} missing 'target' or 'replacement'")
                    
                if not isinstance(patch_rule['target'], str):
                    raise ValueError(f"Patch {i}, rule {j} 'target' must be a string")
                    
                if not isinstance(patch_rule['replacement'], str):
                    raise ValueError(f"Patch {i}, rule {j} 'replacement' must be a string")
                    
        return True
        
    def add_patch(self, patch: Dict[str, Any]) -> None:
        """
        Add a new patch to the current patches list
        
        Args:
            patch: Patch dictionary to add
            
        Raises:
            ValueError: If the patch is invalid
        """
        self.validate_patches([patch])
        self.patches.append(patch)
        
    def remove_patch(self, index: int) -> None:
        """
        Remove a patch by index
        
        Args:
            index: Index of the patch to remove
            
        Raises:
            IndexError: If index is out of range
        """
        if index < 0 or index >= len(self.patches):
            raise IndexError("Patch index out of range")
            
        del self.patches[index]
        
    def get_patch(self, index: int) -> Dict[str, Any]:
        """
        Get a patch by index
        
        Args:
            index: Index of the patch to get
            
        Returns:
            Patch dictionary
            
        Raises:
            IndexError: If index is out of range
        """
        if index < 0 or index >= len(self.patches):
            raise IndexError("Patch index out of range")
            
        return self.patches[index]
        
    def update_patch(self, index: int, patch: Dict[str, Any]) -> None:
        """
        Update a patch by index
        
        Args:
            index: Index of the patch to update
            patch: New patch data
            
        Raises:
            IndexError: If index is out of range
            ValueError: If the patch is invalid
        """
        if index < 0 or index >= len(self.patches):
            raise IndexError("Patch index out of range")
            
        self.validate_patches([patch])
        self.patches[index] = patch
        
    def get_patches_count(self) -> int:
        """
        Get the number of loaded patches
        
        Returns:
            Number of patches
        """
        return len(self.patches)
        
    def clear_patches(self) -> None:
        """Clear all patches"""
        self.patches = []
        
    def search_patches(self, query: str) -> List[Dict[str, Any]]:
        """
        Search patches by name
        
        Args:
            query: Search query
            
        Returns:
            List of matching patches
        """
        query_lower = query.lower()
        return [patch for patch in self.patches if query_lower in patch['name'].lower()]
        
    def export_patches(self, file_path: str, patch_indices: Optional[List[int]] = None) -> None:
        """
        Export selected patches to a file
        
        Args:
            file_path: Path where to save the exported patches
            patch_indices: List of patch indices to export (None for all)
            
        Raises:
            ValueError: If patch indices are invalid
            IOError: If the file cannot be written
        """
        if patch_indices is None:
            patches_to_export = self.patches
        else:
            patches_to_export = []
            for index in patch_indices:
                if index < 0 or index >= len(self.patches):
                    raise ValueError(f"Invalid patch index: {index}")
                patches_to_export.append(self.patches[index])
                
        self.save_patches(file_path, patches_to_export)
        
    def import_patches(self, file_path: str, merge: bool = False) -> None:
        """
        Import patches from a file
        
        Args:
            file_path: Path to the file to import
            merge: If True, merge with existing patches; if False, replace
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the patch data is invalid
        """
        imported_patches = self.load_patches(file_path)
        
        if merge:
            self.patches.extend(imported_patches)
        else:
            self.patches = imported_patches
            
    def get_patch_summary(self) -> Dict[str, Any]:
        """
        Get a summary of all patches
        
        Returns:
            Dictionary containing patch statistics
        """
        total_patches = len(self.patches)
        total_rules = sum(len(patch['patches']) for patch in self.patches)
        
        return {
            'total_patches': total_patches,
            'total_rules': total_rules,
            'patch_names': [patch['name'] for patch in self.patches]
        }
