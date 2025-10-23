import re
import xml.etree.ElementTree as ET
from typing import Dict, List, Tuple, Optional, Any

class ObjectBlockParser:
    """Parser for ROTMG object blocks with character count preservation"""
    
    def __init__(self):
        self.preserve_character_count = True
        
    def set_character_count_preservation(self, enabled: bool):
        """Enable or disable character count preservation"""
        self.preserve_character_count = enabled
        
    def parse_object_block(self, object_block: str) -> Dict[str, Any]:
        """
        Parse an object block and extract its components
        
        Args:
            object_block: The XML-like object block string
            
        Returns:
            Dictionary containing parsed components
        """
        try:
            # Clean up the object block
            cleaned_block = object_block.strip()
            
            # Extract object tag attributes
            object_match = re.match(r'<Object\s+([^>]+)>', cleaned_block)
            if not object_match:
                raise ValueError("Invalid object block format")
                
            attributes_str = object_match.group(1)
            attributes = self._parse_attributes(attributes_str)
            
            # Extract inner content
            inner_content = cleaned_block[object_match.end():-8]  # Remove </Object>
            
            # Parse inner elements
            elements = self._parse_inner_elements(inner_content)
            
            return {
                'object_attributes': attributes,
                'elements': elements,
                'original_block': cleaned_block,
                'original_length': len(cleaned_block)
            }
            
        except Exception as e:
            raise ValueError(f"Failed to parse object block: {e}")
            
    def _parse_attributes(self, attributes_str: str) -> Dict[str, str]:
        """Parse object tag attributes"""
        attributes = {}
        # Simple attribute parsing - handles quoted values
        attr_pattern = r'(\w+)="([^"]*)"'
        matches = re.findall(attr_pattern, attributes_str)
        
        for name, value in matches:
            attributes[name] = value
            
        return attributes
        
    def _parse_inner_elements(self, inner_content: str) -> Dict[str, str]:
        """Parse inner elements of the object block"""
        elements = {}
        
        # Find all XML-like elements
        element_pattern = r'<(\w+)>([^<]*)</\1>'
        matches = re.findall(element_pattern, inner_content)
        
        for tag_name, content in matches:
            elements[tag_name] = content
            
        return elements
        
    def create_patch_from_changes(self, parsed_object: Dict[str, Any], 
                                 changes: Dict[str, str]) -> Dict[str, Any]:
        """
        Create a patch definition from parsed object and user changes
        
        Args:
            parsed_object: Parsed object block data
            changes: Dictionary of field changes (field_name: new_value)
            
        Returns:
            Patch definition dictionary
        """
        # Store the parsed object for name generation
        self._current_parsed_object = parsed_object
        
        original_block = parsed_object['original_block']
        original_length = parsed_object['original_length']
        
        # Create the modified block
        modified_block = original_block
        
        # Apply changes to object attributes
        if 'id' in changes:
            modified_block = re.sub(
                r'(<Object[^>]*id=")[^"]*(")',
                f'\\1{changes["id"]}\\2',
                modified_block
            )
            
        if 'type' in changes:
            modified_block = re.sub(
                r'(<Object[^>]*type=")[^"]*(")',
                f'\\1{changes["type"]}\\2',
                modified_block
            )
            
        # Apply changes to inner elements
        for field_name, new_value in changes.items():
            if field_name not in ['id', 'type']:  # Skip attributes already handled
                if field_name in parsed_object['elements']:
                    old_value = parsed_object['elements'][field_name]
                    
                    # Handle character count preservation for Description field
                    if field_name == 'Description' and self.preserve_character_count:
                        # Calculate length difference and adjust the new value
                        length_diff = len(old_value) - len(new_value)
                        if length_diff > 0:
                            # Need to add characters (spaces)
                            adjusted_value = new_value + ' ' * length_diff
                        elif length_diff < 0:
                            # Need to remove characters
                            adjusted_value = new_value[:len(old_value)]
                        else:
                            # Lengths are the same
                            adjusted_value = new_value
                        
                        # Replace the element content with adjusted value
                        element_pattern = f'<{field_name}>{re.escape(old_value)}</{field_name}>'
                        replacement = f'<{field_name}>{adjusted_value}</{field_name}>'
                        modified_block = re.sub(element_pattern, replacement, modified_block)
                    else:
                        # Regular replacement without character count preservation
                        element_pattern = f'<{field_name}>{re.escape(old_value)}</{field_name}>'
                        replacement = f'<{field_name}>{new_value}</{field_name}>'
                        modified_block = re.sub(element_pattern, replacement, modified_block)
        
        # Create locator pattern
        locator = self._create_locator_pattern(parsed_object)
        
        # Create patch rules
        patches = []
        
        # Add object ID change if needed
        if 'id' in changes:
            patches.append({
                'target': r'(<Object[^>]*id=")[^"]*(")',
                'replacement': f'\\1{changes["id"]}\\2'
            })
            
        # Add object type change if needed
        if 'type' in changes:
            patches.append({
                'target': r'(<Object[^>]*type=")[^"]*(")',
                'replacement': f'\\1{changes["type"]}\\2'
            })
            
        # Add element changes
        for field_name, new_value in changes.items():
            if field_name not in ['id', 'type']:
                if field_name in parsed_object['elements']:
                    old_value = parsed_object['elements'][field_name]
                    
                    # Handle character count preservation for Description field
                    if field_name == 'Description' and self.preserve_character_count:
                        # Calculate length difference and adjust the new value
                        length_diff = len(old_value) - len(new_value)
                        if length_diff > 0:
                            # Need to add characters (spaces)
                            adjusted_value = new_value + ' ' * length_diff
                        elif length_diff < 0:
                            # Need to remove characters
                            adjusted_value = new_value[:len(old_value)]
                        else:
                            # Lengths are the same
                            adjusted_value = new_value
                        
                        # Create target pattern for this specific element
                        target_pattern = f'<{field_name}>{re.escape(old_value)}</{field_name}>'
                        replacement_pattern = f'<{field_name}>{adjusted_value}</{field_name}>'
                        
                        patches.append({
                            'target': target_pattern,
                            'replacement': replacement_pattern
                        })
                    else:
                        # Regular patch without character count preservation
                        target_pattern = f'<{field_name}>{re.escape(old_value)}</{field_name}>'
                        replacement_pattern = f'<{field_name}>{new_value}</{field_name}>'
                        
                        patches.append({
                            'target': target_pattern,
                            'replacement': replacement_pattern
                        })
        
        # If ID was changed and character count preservation is enabled, 
        # automatically adjust Description to maintain character count
        if 'id' in changes and self.preserve_character_count and 'Description' in parsed_object['elements']:
            # Only add Description patch if it wasn't already added above
            if 'Description' not in changes:
                old_desc = parsed_object['elements']['Description']
                # Create a generic description for the new item
                new_desc = f"A potion that boosts speed. Lasts 30 minutes."
                
                # Calculate length difference and adjust
                length_diff = len(old_desc) - len(new_desc)
                if length_diff > 0:
                    # Need to add characters (spaces)
                    adjusted_desc = new_desc + ' ' * length_diff
                elif length_diff < 0:
                    # Need to remove characters
                    adjusted_desc = new_desc[:len(old_desc)]
                else:
                    # Lengths are the same
                    adjusted_desc = new_desc
                
                # Create target pattern for Description
                target_pattern = f'<Description>{re.escape(old_desc)}</Description>'
                replacement_pattern = f'<Description>{adjusted_desc}</Description>'
                
                patches.append({
                    'target': target_pattern,
                    'replacement': replacement_pattern
                })
        
        # Generate patch name
        patch_name = self._generate_patch_name(changes)
        
        return {
            'name': patch_name,
            'locator': locator,
            'patches': patches
        }
        
    def _preserve_description_length(self, modified_block: str, old_desc: str, 
                                   new_desc: str, original_length: int) -> str:
        """Preserve the total character count by adjusting description length"""
        current_length = len(modified_block)
        length_diff = original_length - current_length
        
        if length_diff != 0:
            # Adjust the description length
            if length_diff > 0:
                # Need to add characters (spaces)
                adjusted_desc = new_desc + ' ' * length_diff
            else:
                # Need to remove characters
                adjusted_desc = new_desc[:length_diff]
                
            # Replace the description in the modified block
            desc_pattern = f'<Description>{re.escape(new_desc)}</Description>'
            replacement = f'<Description>{adjusted_desc}</Description>'
            modified_block = re.sub(desc_pattern, replacement, modified_block)
            
        return modified_block
        
    def _create_length_preservation_patch(self, old_value: str, new_value: str, 
                                        field_name: str) -> Dict[str, str]:
        """Create a patch rule for length preservation"""
        length_diff = len(old_value) - len(new_value)
        
        if length_diff > 0:
            # Need to add characters to match original length
            adjusted_value = new_value + ' ' * length_diff
        elif length_diff < 0:
            # Need to remove characters to match original length
            adjusted_value = new_value[:len(old_value)]
        else:
            # Lengths are the same, no adjustment needed
            adjusted_value = new_value
            
        return {
            'target': f'<{field_name}>{re.escape(new_value)}</{field_name}>',
            'replacement': f'<{field_name}>{adjusted_value}</{field_name}>'
        }
        
    def _create_locator_pattern(self, parsed_object: Dict[str, Any]) -> str:
        """Create a locator pattern for the object"""
        attributes = parsed_object['object_attributes']
        
        # Use ID if available, otherwise use type
        if 'id' in attributes:
            return f'<Object[^>]*id="{re.escape(attributes["id"])}"[^>]*>.*?</Object>'
        elif 'type' in attributes:
            return f'<Object[^>]*type="{re.escape(attributes["type"])}"[^>]*>.*?</Object>'
        else:
            # Fallback to generic pattern
            return r'<Object[^>]*>.*?</Object>'
            
    def _generate_patch_name(self, changes: Dict[str, str]) -> str:
        """Generate a descriptive name for the patch"""
        if 'id' in changes:
            # Try to get the original ID from the parsed object
            if hasattr(self, '_current_parsed_object') and self._current_parsed_object:
                original_id = self._current_parsed_object['object_attributes'].get('id', 'Unknown')
            else:
                original_id = 'Unknown'
            new_id = changes['id']
            return f"Spoof {original_id} as {new_id}"
        else:
            return "Custom Object Patch"
            
    def validate_object_block(self, object_block: str) -> Tuple[bool, str]:
        """
        Validate if the input is a valid object block
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Basic validation
            if not object_block.strip().startswith('<Object'):
                return False, "Object block must start with '<Object'"
                
            if not object_block.strip().endswith('</Object>'):
                return False, "Object block must end with '</Object>'"
                
            # Try to parse it
            self.parse_object_block(object_block)
            return True, ""
            
        except Exception as e:
            return False, str(e)
            
    def get_editable_fields(self, parsed_object: Dict[str, Any]) -> List[str]:
        """Get list of fields that can be edited"""
        fields = []
        
        # Add object attributes
        fields.extend(parsed_object['object_attributes'].keys())
        
        # Add inner elements
        fields.extend(parsed_object['elements'].keys())
        
        return sorted(list(set(fields)))
        
    def preview_changes(self, parsed_object: Dict[str, Any], 
                       changes: Dict[str, str]) -> str:
        """Preview what the modified object block would look like"""
        try:
            patch_def = self.create_patch_from_changes(parsed_object, changes)
            
            # Apply patches to original block
            modified_block = parsed_object['original_block']
            
            for patch in patch_def['patches']:
                modified_block = re.sub(
                    patch['target'], 
                    patch['replacement'], 
                    modified_block
                )
                
            return modified_block
            
        except Exception as e:
            return f"Error generating preview: {e}"
