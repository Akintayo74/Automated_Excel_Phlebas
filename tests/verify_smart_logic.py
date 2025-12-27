import unittest
import os
from src.services.smart_matcher import SmartMatcher
from src.utils.log_parser import LogParser
from src.utils.name_cleaner import clean_name

class TestSmartLogic(unittest.TestCase):
    def setUp(self):
        self.matcher = SmartMatcher()

    def test_search_terms_basic(self):
        name = "JOHN DOE"
        terms = self.matcher.generate_search_terms(name)
        # Expected: ["JOHN", "DOE"]
        self.assertEqual(terms, ["JOHN", "DOE"])

    def test_search_terms_three_names(self):
        name = "JOHN MIDDLE DOE"
        terms = self.matcher.generate_search_terms(name)
        # Expected: ["JOHN", "MIDDLE", "DOE"]
        self.assertEqual(terms, ["JOHN", "MIDDLE", "DOE"])
        
    def test_search_terms_duplicates(self):
        name = "JOHN JOHN DOE"
        terms = self.matcher.generate_search_terms(name)
        # Expected: ["JOHN", "DOE"] (unique only)
        self.assertEqual(terms, ["JOHN", "DOE"])

    def test_log_parser(self):
        # Create dummy log
        log_content = """
2025-12-23 15:46:41 | INFO | Row 1 | Some info
2025-12-23 15:47:10 | STATUS_UNKNOWN | Row 2 | ...
2025-12-23 15:47:29 | WARNING | Row 3 | Low confidence
2025-12-23 15:47:37 | ERROR | Row 4 | No match
        """
        filename = "test_log_123.log"
        with open(filename, "w") as f:
            f.write(log_content)
            
        try:
            statuses = LogParser.parse_log_file(filename)
            self.assertEqual(statuses.get(1), "INFO")
            self.assertIsNone(statuses.get(2)) # Unknown status not parsed
            self.assertEqual(statuses.get(3), "WARNING")
            self.assertEqual(statuses.get(4), "ERROR")
        finally:
            if os.path.exists(filename):
                os.remove(filename)

if __name__ == '__main__':
    unittest.main()
