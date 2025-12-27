import sys
import os

print("Testing imports...")
try:
    from src.controllers.scraper_controller import ScraperController
    print("✓ src.controllers.scraper_controller imported")
    
    from src.utils.log_parser import LogParser
    print("✓ src.utils.log_parser imported")
    
    from src.services.smart_matcher import SmartMatcher
    print("✓ src.services.smart_matcher imported")
    
    print("\nAll imports successful!")
except ImportError as e:
    print(f"\n✗ Import Error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"\n✗ Error: {e}")
    sys.exit(1)
