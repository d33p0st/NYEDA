
from nyeda.types.abc import Feature
from pathlib import Path
from typing import TypeVar, Dict, List, Iterable

M = TypeVar('METADATA')

class dirtools(Feature):
    def generate_dirmap(self, metadata: M) -> Dict[str, List[str]]:

        if not isinstance(metadata, Iterable) or not all(isinstance(x, str) for x in metadata):
            return {}
        
        # Initialize the result dictionary
        directory_structure: Dict[str, List[str]] = {"/": []}
        
        # Process each path
        for path_str in metadata:
            # Convert to Path object and normalize
            path = Path(path_str)
            parts = path.parts
            
            # Handle the root directory first
            if len(parts) == 1:
                if not parts[0].startswith('.'):
                    directory_structure["/"].append(parts[0])
                continue
                
            # Process each level of the path
            current_path = "/"
            for i in range(len(parts)):
                # Add the current directory to its parent's content list
                if i == 0:
                    if parts[i] not in directory_structure["/"] and not parts[i].startswith('.'):
                        directory_structure["/"].append(parts[i])
                else:
                    parent_path = "/" + "/".join(parts[:i])
                    if parent_path not in directory_structure:
                        directory_structure[parent_path] = []
                    if parts[i] not in directory_structure[parent_path] and not parts[i].startswith('.'):
                        directory_structure[parent_path].append(parts[i])
                
                # Prepare the next directory path
                if i < len(parts) - 1:
                    current_path = "/" + "/".join(parts[:i+1])
                    if current_path not in directory_structure:
                        directory_structure[current_path] = []
        
        # Sort all lists for consistent output
        for key in directory_structure:
            directory_structure[key].sort()
            
        return directory_structure
