from src.utils.name_cleaner import get_similarity
import re

class StudentMatcher:
    def __init__(self, logger=None):
        self.logger = logger

    def find_best_match(self, excel_full_name, portal_rows_data):
        """
        Find best match for excel_full_name among portal_rows_data.
        portal_rows_data: list of dicts with {'admission': str, 'name': str}
        """
        full_name_clean = re.sub(r'\s+', ' ', excel_full_name.upper().strip())
        full_name_parts = [p for p in full_name_clean.split() if len(p) >= 3]

        best_match = None
        best_score = 0
        
        # Log matching attempts if needed, or return all scores to controller?
        # Keeping it simple: return the best match tuple (admission, display_name, score)

        for portal_student in portal_rows_data:
            portal_display = portal_student['name']
            admission_number = portal_student['admission']
            
            portal_full_no_space = portal_display.replace(" ", "")
            portal_words = set(portal_display.split())

            # Method 1: Exact word matching
            matching_words = set(full_name_parts).intersection(portal_words)
            exact_score = len(matching_words) / len(full_name_parts) if full_name_parts else 0

            # Method 2: Improved Fuzzy Matching
            fuzzy_points = 0
            for part in full_name_parts:
                if part in portal_full_no_space:
                    fuzzy_points += 1
                else:
                    # Check similarity against each word in the portal name
                    word_sims = [get_similarity(part, w) for w in portal_words]
                    max_sim = max(word_sims) if word_sims else 0
                    if max_sim > 0.8: # Threshold for spelling variants
                        fuzzy_points += max_sim
            
            fuzzy_score = fuzzy_points / len(full_name_parts) if full_name_parts else 0
            normalized_score = max(exact_score, fuzzy_score)

            print(f" • {portal_display}: {admission_number} (Score: {normalized_score:.0%})")

            if normalized_score > best_score:
                best_score = normalized_score
                best_match = (admission_number, portal_display)

        return best_match, best_score
