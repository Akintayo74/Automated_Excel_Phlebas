import itertools

class SmartMatcher:
    """
    Provides intelligent name matching capabilities, including generating
    permutations for failed searches.
    """
    
    def __init__(self):
        pass

    def generate_search_terms(self, full_name):
        """
        Generates a list of name variations to try as search terms.
        Includes the full cleaned name and individual valid name parts.
        """
        import re
        if not full_name: return []
        
        # Normalize: Remove extra spaces, uppercase
        full_name = re.sub(r'\s+', ' ', full_name.strip().upper())
        parts = full_name.split()
        
        perms = []
        
        # 1. Original (cleaned)
        perms.append(full_name)
        
        # 2. Individual parts (First, Middle, Last)
        for part in parts:
            if len(part) > 2: # Ignore initials
                perms.append(part)
        
        # Return unique parts, preserving order
        return list(dict.fromkeys(perms))
