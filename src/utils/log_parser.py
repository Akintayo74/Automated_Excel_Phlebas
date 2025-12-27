import os
import re
import glob
from pathlib import Path

class LogParser:
    """Parses scraper log files to determine the status of previous runs."""
    
    STATUS_INFO = "INFO"
    STATUS_WARNING = "WARNING"
    STATUS_ERROR = "ERROR"

    @staticmethod
    def find_latest_log_for_excel(excel_path):
        """
        Finds the most recent log file corresponding to the given Excel file.
        Assumes log files are in 'logs/' directory with format '{excel_basename}_{timestamp}.log'.
        """
        excel_name = Path(excel_path).stem
        log_dir = Path("logs")
        
        if not log_dir.exists():
            return None
            
        # Search for logs matching the excel name pattern
        # Pattern: exact name + underscore + timestamp + .log
        pattern = str(log_dir / f"{excel_name}_*.log")
        log_files = glob.glob(pattern)
        
        if not log_files:
            return None
            
        # Sort by modification time (or name which contains timestamp) to get the latest
        # Names have YYYYMMDD_HHMMSS so sorting by name works for finding latest too
        log_files.sort(reverse=True)
        return log_files[0]

    @staticmethod
    def parse_log_file(log_path):
        """
        Parses the log file and returns a dictionary mapping Row Index to its Status.
        Returns: { int(row_index): "INFO" | "WARNING" | "ERROR" }
        """
        row_statuses = {}
        
        if not log_path or not os.path.exists(log_path):
            return row_statuses
            
        try:
            with open(log_path, 'r', encoding='utf-8') as f:
                for line in f:
                    # Extract Status and Row Index
                    # Format: YYYY-MM-DD HH:MM:SS | STATUS | ... | Row X | ...
                    
                    # 1. Check for standard line format
                    parts = line.split('|')
                    if len(parts) < 4:
                        continue
                        
                    status = parts[1].strip()
                    
                    # Find "Row X" segment
                    row_segment = next((p for p in parts if "Row" in p), None)
                    if not row_segment:
                        continue
                        
                    # Extract number from "Row X"
                    match = re.search(r'Row\s+(\d+)', row_segment)
                    if match:
                        row_idx = int(match.group(1))
                        
                        # Store the status. 
                        # Note: Later lines for same row might overwrite earlier ones? 
                        # Typically a row is processed once. But if it appears multiple times, 
                        # the last status is likely the definitive one (or we might want the 'worst' one?).
                        # Assuming linear execution, the last log entry for a row is the final result.
                        if status in [LogParser.STATUS_INFO, LogParser.STATUS_WARNING, LogParser.STATUS_ERROR]:
                            row_statuses[row_idx] = status
                            
        except Exception as e:
            print(f"⚠ Error parsing log file {log_path}: {e}")
            
        return row_statuses
