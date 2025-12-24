import logging
import os
from pathlib import Path
from datetime import datetime

class LoggerView:
    def __init__(self, excel_path):
        self.excel_path = excel_path
        self.logger = None

    def setup_logging(self, log_dir="./logs"):
        """Setup file logging for the scraping session"""
        
        # Create logs directory if it doesn't exist
        Path(log_dir).mkdir(exist_ok=True)
        
        # Create log filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        excel_name = Path(self.excel_path).stem
        log_file = f"{log_dir}/{excel_name}_{timestamp}.log"
        
        # Setup logger
        self.logger = logging.getLogger(f"Scraper_{excel_name}")
        self.logger.setLevel(logging.INFO)
        
        # File handler
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        # Console handler (still print important stuff)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)  # Only warnings/errors to console
        
        # Format
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        self.logger.info("="*80)
        self.logger.info(f"SCRAPING SESSION STARTED: {excel_name}")
        self.logger.info(f"Log file: {log_file}")
        self.logger.info("="*80)
        
        print(f"📝 Logging to: {log_file}")
        return log_file, self.logger
