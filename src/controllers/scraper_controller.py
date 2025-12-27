import time
import traceback
import os
from src.models.excel_repository import ExcelRepository
from src.models.student_matcher import StudentMatcher
from src.models.portal_repository import PortalRepository
from src.services.browser_manager import BrowserManager
from src.services.auth_manager import AuthManager
from src.services.class_filter_manager import ClassFilterManager
from src.views.logger_view import LoggerView
from src.utils.name_cleaner import clean_name
from src.utils.log_parser import LogParser
from src.services.smart_matcher import SmartMatcher

class ScraperController:
    def __init__(self, excel_path, portal_url, username, password, target_class=None):
        self.excel_path = excel_path
        self.portal_url = portal_url
        self.username = username
        self.password = password
        self.target_class = target_class
        
        # Initialize components
        self.excel_repo = ExcelRepository(excel_path)
        self.browser_manager = BrowserManager()
        self.auth_manager = AuthManager(self.browser_manager, portal_url)
        self.class_filter_manager = ClassFilterManager(self.browser_manager)
        self.portal_repo = PortalRepository(self.browser_manager, portal_url)
        self.matcher = StudentMatcher()
        self.smart_matcher = SmartMatcher()
        self.logger_view = LoggerView(excel_path)
        self.logger = None

    def run(self):
        # 1. Setup Logging
        log_file, self.logger = self.logger_view.setup_logging()
        self.matcher.logger = self.logger
        
        # 2. Parse Previous Logs (if any)
        latest_log = LogParser.find_latest_log_for_excel(self.excel_path)
        previous_statuses = {}
        if latest_log:
            print(f"ℹ Found previous log: {os.path.basename(latest_log)}")
            previous_statuses = LogParser.parse_log_file(latest_log)
            print(f"ℹ Loaded {len(previous_statuses)} previous statuses.")
        else:
            print("ℹ No previous log found. Starting fresh.")

        try:
            self.browser_manager.setup()
            
            if not self.auth_manager.login(self.username, self.password):
                print(f"\n✗ Failed to login for {self.excel_path}. Skipping...")
                return

            # Set class filter once after login
            self.class_filter_manager.set_class_filter(self.target_class)
            
            if not self.excel_repo.load():
                print(f"\n✗ Failed to load {self.excel_path}. Skipping...")
                return
            
            total_updated = 0
            total_skipped = 0
            total_errors = 0
            
            # Process based on sheets
            sheet_names = self.excel_repo.get_sheet_names()
            
            for sheet_name in sheet_names:
                print(f"\n{'='*70}")
                print(f"  PROCESSING SHEET: {sheet_name}")
                print(f"{'='*70}")
                
                updated, skipped, errors = self.process_sheet(sheet_name, previous_statuses)
                
                total_updated += updated
                total_skipped += skipped
                total_errors += errors
                
            output_path = self.excel_repo.save()
            
            if output_path:
                print(f"\n{'='*70}")
                print(f"✓ ENTIRE WORKBOOK SAVED: {output_path}")
                print(f"{'='*70}")
                print(f"\nFINAL SUMMARY (All Sheets):")
                print(f"  • Total Updated: {total_updated}")
                print(f"  • Total Skipped: {total_skipped}")
                print(f"  • Total Errors: {total_errors}")
                print(f"  • Total Processed: {total_updated + total_skipped + total_errors}")
                
                if self.logger:
                    self.logger.info("="*80)
                    self.logger.info(f"WORKBOOK SAVED: {output_path}")
                    self.logger.info(f"Total Updated: {total_updated} | Skipped: {total_skipped} | Errors: {total_errors}")
                    self.logger.info("="*80)
            
        except KeyboardInterrupt:
            print("\n\n⚠ Process interrupted by user")
        except Exception as e:
            print(f"✗ Fatal error processing {self.excel_path}: {e}")
            traceback.print_exc()
        finally:
            self.browser_manager.close()

    def process_sheet(self, sheet_name, previous_statuses):
        updated_count = 0
        skipped_count = 0
        error_count = 0
        
        # We need a generator or list from the repo
        # The repo method assumes existing logic of iterating rows
        
        for student_data in self.excel_repo.get_students_from_sheet(sheet_name):
            row_idx = student_data['row_idx']
            student_name = student_data['name']
            current_admission = student_data['current_admission']
            
            # Skip if no name
            if not student_name or student_name == "NAME":
                continue
            
            print(f"\nRow {row_idx}: {student_name}")
            
            # Skip if admission number already exists
            if current_admission and isinstance(current_admission, str) and "CDSSJOS" in current_admission:
                print(f"  ⊘ Skipped (already has admission number: {current_admission})")
                skipped_count += 1
                continue
            
            # Check Log Status
            log_status = previous_statuses.get(row_idx)
            
            if log_status == LogParser.STATUS_INFO:
                print(f"  ⏭ Skipped (Previously Matched - INFO)")
                skipped_count += 1
                continue
            
            elif log_status == LogParser.STATUS_WARNING:
                print(f"  ⚠ Re-checking (Previous Low Confidence - WARNING)")
                # Proceed to search code below...
                
            elif log_status == LogParser.STATUS_ERROR:
                print(f"  ↻ Retrying with Smart Matching (Previous Error)")
                # Proceed to search code + enable smart permutation retry
            
            # Clean and search
            search_name = clean_name(student_name)
            
            if not search_name:
                print(f"  ⊘ Skipped (couldn't parse name)")
                skipped_count += 1
                continue
            
            # --- Standard Search ---
            portal_results = self.portal_repo.search_students(search_name)
            best_match, score = self.matcher.find_best_match(student_name, portal_results)
            
            # --- Smart Retry Loop (if no good match) ---
            if (not best_match or score < 0.45):
                print(f"    ... Standard search failed. Trying individual name components...")
                search_terms = self.smart_matcher.generate_search_terms(student_name)
                
                for term in search_terms:
                    if term.lower() == search_name.lower(): continue # Skip what we just did
                    
                    print(f"    ? Trying: {term}")
                    term_results = self.portal_repo.search_students(term)
                    
                    # IMPORTANT: We match against the ORIGINAL FULL NAME logic from Excel,
                    # but using the new results found by the single key term.
                    term_match, term_score = self.matcher.find_best_match(student_name, term_results)
                    
                    if term_match and term_score >= 0.70: # High threshold for safety
                        best_match = term_match
                        score = term_score
                        search_name = term # Update for logging what actually worked
                        print(f"    ✓ Smart Match found via '{term}'!")
                        break
                        
            # Log results (logic was in search_student in original)
            self._log_match_result(student_name, best_match, score, row_idx, search_name)

            if best_match and score >= 0.45:
                admission_number, display_name = best_match
                self.excel_repo.update_student(sheet_name, row_idx, admission_number)
                updated_count += 1
                print(f"  ✓ Updated in Excel")
            else:
                error_count += 1
                
            time.sleep(1) # Delay
            
        print(f"\n{'-'*70}")
        print(f"Sheet Summary ({sheet_name}):")
        print(f"  • Updated: {updated_count}")
        print(f"  • Skipped: {skipped_count}")
        print(f"  • Errors: {error_count}")
        print(f"{'-'*70}")

        return updated_count, skipped_count, error_count

    def _log_match_result(self, full_name, best_match, best_score, row_idx, search_name):
        if not self.logger: return
        
        if best_match and best_score >= 0.45:
            admission, portal_name = best_match
            if best_score < 0.70:
                self.logger.warning(
                    f"LOW CONFIDENCE | Row {row_idx} | "
                    f"Excel: {full_name} | Portal: {portal_name} | "
                    f"Admission: {admission} | Score: {best_score:.2%}"
                )
                print(f" ⚠ LOW CONFIDENCE MATCH ({best_score:.0%}) - Please verify!")
            else:
                self.logger.info(
                    f"MATCHED | Row {row_idx} | "
                    f"Excel: {full_name} | Portal: {portal_name} | "
                    f"Admission: {admission} | Score: {best_score:.2%}"
                )
                print(f" ✓ Best match: {portal_name} → {admission}")
        else:
            self.logger.error(
                f"NO MATCH | Row {row_idx} | "
                f"Excel: {full_name} | Best score: {best_score:.2%} | "
                f"Searched: {search_name}"
            )
