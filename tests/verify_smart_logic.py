import unittest
import os
from src.services.smart_matcher import SmartMatcher
from src.utils.log_parser import LogParser
from src.utils.name_cleaner import clean_name

class TestSmartLogic(unittest.TestCase):
    def setUp(self):
        self.matcher = SmartMatcher()

    def test_permutations_basic(self):
        name = "JOHN DOE"
        perms = self.matcher.generate_permutations(name)
        # Expected: "JOHN DOE", "DOE JOHN", "JOHN"
        self.assertIn("JOHN DOE", perms)
        self.assertIn("DOE JOHN", perms)
        self.assertIn("JOHN", perms)

    def test_permutations_three_names(self):
        name = "JOHN MIDDLE DOE"
        perms = self.matcher.generate_permutations(name)
        # Expected: "JOHN MIDDLE DOE", "DOE MIDDLE JOHN", "JOHN", "JOHN DOE", "DOE JOHN"
        # The logic implementation:
        # 1. Original: JOHN MIDDLE DOE
        # 2. Reversed: DOE MIDDLE JOHN
        # 3. First Part: JOHN (if >=2 parts)
        # 4. First+Last: JOHN DOE, DOE JOHN (if >2 parts)
        
        self.assertIn("JOHN MIDDLE DOE", perms)
        self.assertIn("DOE MIDDLE JOHN", perms)
        self.assertIn("JOHN DOE", perms)
        self.assertIn("DOE JOHN", perms)

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
