import itertools

class SmartMatcher:
    """
    Provides intelligent name matching capabilities, including generating
    permutations for failed searches.
    """
    
    def __init__(self):
        pass

    def generate_permutations(self, full_name):
        """
        Generates a list of likely name variations to try when exact match fails.
        """
        if not full_name:
            return []
            
        parts = [p for p in full_name.strip().split() if len(p) > 1]
        if not parts:
            return []
            
        permutations = []
        
        # 1. Original
        permutations.append(" ".join(parts))
        
        # 2. Reverse order (Last First Middle)
        if len(parts) > 1:
            permutations.append(" ".join(reversed(parts)))
            
        # 3. Last Name Only (often unique enough combined with school filter if applicable, but risky)
        # We'll skip single names for safety unless requested, or maybe just try the first part (Surname usually)
        if len(parts) >= 2:
            permutations.append(parts[0]) # Assuming Surname is first
        
        # 4. First + Last (skip middle)
        if len(parts) > 2:
             permutations.append(f"{parts[0]} {parts[-1]}")
             permutations.append(f"{parts[-1]} {parts[0]}")

        # Remove duplicates while preserving order
        unique_permutations = list(dict.fromkeys(permutations))
        
        return unique_permutations
