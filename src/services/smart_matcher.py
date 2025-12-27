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
        Generates a list of individual name components to try as search terms.
        Splits by space and returns unique, valid words (>= 2 chars).
        """
        if not full_name:
            return []
            
        # Split by whitespace to get full words (e.g. "Adamu", "Lee")
        parts = [p for p in full_name.strip().split() if len(p) >= 2]
        
        if not parts:
            return []
            
        # Return unique parts, preserving order (left-to-right is usually most significant)
        unique_terms = list(dict.fromkeys(parts))
        
        return unique_terms
