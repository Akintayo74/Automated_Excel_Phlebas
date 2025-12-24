import re
from difflib import SequenceMatcher

def clean_name(name):
    """Clean student name for searching"""
    if not name or name == "NAME":
        return None
    # Remove extra spaces and convert to title case
    name = re.sub(r'\s+', ' ', str(name).strip())
    # Extract last name (usually the first word in your format)
    parts = name.split()
    if len(parts) > 0:
        return parts[0]  # Return first word (last name)
    return name

def get_similarity(a, b):
    """Calculate similarity ratio between two strings"""
    return SequenceMatcher(None, a, b).ratio()
