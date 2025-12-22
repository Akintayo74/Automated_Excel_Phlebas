"""
Student Portal Automation Script
Automatically fetches admission numbers from the school portal and updates Excel file
"""

import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import openpyxl
from openpyxl.styles import PatternFill
from difflib import SequenceMatcher
from dotenv import load_dotenv
import os

load_dotenv()
# Add this helper function at the top of your script
def get_similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

class StudentPortalScraper:
    def __init__(self, excel_path, portal_url):
        self.excel_path = excel_path
        self.portal_url = portal_url
        self.driver = None
        self.wb = None
        self.ws = None
        
    def setup_driver(self):
        """Initialize Chrome WebDriver with appropriate options"""
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        # Remove headless mode so you can see what's happening
        # chrome_options.add_argument('--headless')
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.maximize_window()
        print("✓ Browser initialized")
        
    def login(self, username, password):
        """Login to the portal"""
        try:
            print(f"\n→ Navigating to {self.portal_url}")
            self.driver.get(self.portal_url)
            
            # Wait for login page to load
            print("→ Waiting for login page...")
            time.sleep(3)
            
            # You'll need to inspect the login page to find the correct selectors
            # These are common field names - adjust if needed
            print("→ Attempting to log in...")
            
            # Try to find username/email field
            try:
                username_field = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.NAME, "email"))
                )
            except:
                username_field = self.driver.find_element(By.NAME, "username")
            
            username_field.clear()
            username_field.send_keys(username)
            
            # Find password field
            password_field = self.driver.find_element(By.NAME, "password")
            password_field.clear()
            password_field.send_keys(password)
            
            # Find and click login button
            login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_button.click()
            
            # Wait for navigation after login
            print("→ Logging in...")
            time.sleep(5)
            
            # Check if login was successful by looking for student list page
            if "students" in self.driver.current_url.lower() or "dashboard" in self.driver.current_url.lower():
                print("✓ Login successful!")
                return True
            else:
                print("✗ Login may have failed. Please check credentials.")
                return False
                
        except Exception as e:
            print(f"✗ Login error: {str(e)}")
            return False
    
    def clean_name(self, name):
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
    
    def search_student(self, name, full_name):
        try:
            if "students" not in self.driver.current_url.lower():
                self.driver.get(self.portal_url)
                time.sleep(2)

            # 1. OPTIONAL: Fixed Class Filter (SS3)
            try:
                # This XPath finds the select element appearing after the "CLASS" label
                class_dropdown = self.driver.find_element(By.XPATH, "//label[contains(text(), 'CLASS')]/following::select[1]")
                # ... select logic here ...
            except:
                pass 

            search_box = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='text']"))
            )
            search_box.clear()
            search_box.send_keys(name)
            time.sleep(2.5) # Increased wait for portal to refresh results

            rows = self.driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
            
            full_name_clean = re.sub(r'\s+', ' ', full_name.upper().strip())
            full_name_parts = [p for p in full_name_clean.split() if len(p) >= 3]

            best_match = None
            best_score = 0

            for row in rows:
                try:
                    # FIX 1: Verify this is a data row, not a "No Results" message
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if len(cells) < 3: 
                        continue

                    admission_number = cells[0].text.strip()
                    first_name_portal = cells[1].text.strip().upper()
                    last_name_portal = cells[2].text.strip().upper()
                    
                    portal_display = f"{first_name_portal} {last_name_portal}"
                    portal_full_no_space = portal_display.replace(" ", "")
                    portal_words = set(portal_display.split())

                    # Method 1: Exact word matching
                    matching_words = set(full_name_parts).intersection(portal_words)
                    exact_score = len(matching_words) / len(full_name_parts) if full_name_parts else 0

                    # FIX 2: Improved Fuzzy Matching with SequenceMatcher
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

                except Exception as row_err:
                    # Useful for debugging why a row failed
                    # print(f"  ⚠ Row error: {row_err}")
                    continue

            if best_match and best_score >= 0.45:
                print(f" ✓ Best match: {best_match[1]} → {best_match[0]}")
                return best_match[0]
            
            return None

        except Exception as e:
            print(f" ✗ Search error: {str(e)}")
            return None
    
    def load_excel(self):
        """Load the Excel file"""
        try:
            self.wb = openpyxl.load_workbook(self.excel_path)
            self.ws = self.wb.active
            print(f"✓ Excel file loaded: {self.excel_path}")
            return True
        except Exception as e:
            print(f"✗ Error loading Excel: {str(e)}")
            return False
    
    def process_students(self, start_row=3):
        """Process all students in the Excel file"""
        if not self.ws:
            print("✗ Excel file not loaded")
            return
        
        print(f"\n{'='*70}")
        print("Starting to process students...")
        print(f"{'='*70}\n")
        
        updated_count = 0
        skipped_count = 0
        error_count = 0
        
        # Highlight color for updated cells
        yellow_fill = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")
        
        for row_idx in range(start_row, self.ws.max_row + 1):
            admission_cell = self.ws.cell(row=row_idx, column=1)  # Column A
            name_cell = self.ws.cell(row=row_idx, column=2)        # Column B
            
            current_admission = admission_cell.value
            student_name = name_cell.value
            
            # Skip if no name
            if not student_name or student_name == "NAME":
                continue
            
            print(f"\nRow {row_idx}: {student_name}")
            
            # Skip if admission number already exists and looks valid
            if current_admission and isinstance(current_admission, str) and "CDSSJOS" in current_admission:
                print(f"  ⊘ Skipped (already has admission number: {current_admission})")
                skipped_count += 1
                continue
            
            # Clean and search for the student
            search_name = self.clean_name(student_name)
            if not search_name:
                print(f"  ⊘ Skipped (couldn't parse name)")
                skipped_count += 1
                continue
            
            # Search and get admission number
            admission_number = self.search_student(search_name, student_name)
            
            if admission_number:
                # Update Excel
                admission_cell.value = admission_number
                admission_cell.fill = yellow_fill  # Highlight updated cells
                updated_count += 1
                print(f"  ✓ Updated in Excel")
            else:
                error_count += 1
            
            # Small delay to avoid overwhelming the server
            time.sleep(1)
        
        # Save the Excel file
        try:
            output_path = self.excel_path.replace('.xlsx', '_updated.xlsx')
            self.wb.save(output_path)
            print(f"\n{'='*70}")
            print(f"✓ Excel file saved: {output_path}")
            print(f"{'='*70}")
            print(f"\nSummary:")
            print(f"  • Updated: {updated_count}")
            print(f"  • Skipped: {skipped_count}")
            print(f"  • Errors: {error_count}")
            print(f"  • Total processed: {updated_count + skipped_count + error_count}")
            return output_path
        except Exception as e:
            print(f"\n✗ Error saving Excel: {str(e)}")
            return None
    
    def close(self):
        """Close browser and cleanup"""
        if self.driver:
            self.driver.quit()
            print("\n✓ Browser closed")


def main():
    """Main execution function"""
    # Configuration
    EXCEL_PATH = "/home/akintayo74/Downloads/SS3/EXAM SS3 GOVERNMENT.xlsx"
    PORTAL_URL = "https://cdssjos.portal.commandschools.sch.ng/students"
    
    # Login credentials - REPLACE THESE WITH YOUR ACTUAL CREDENTIALS
    USERNAME = os.getenv("PORTAL_USER")  # ← CHANGE THIS
    PASSWORD = os.getenv("PORTAL_PASS")  # ← CHANGE THIS
    
    print("\n" + "="*70)
    print("STUDENT PORTAL AUTOMATION SCRIPT")
    print("="*70 + "\n")
    
    # Initialize scraper
    scraper = StudentPortalScraper(EXCEL_PATH, PORTAL_URL)
    
    try:
        # Step 1: Setup browser
        scraper.setup_driver()
        
        # Step 2: Login
        if not scraper.login(USERNAME, PASSWORD):
            print("\n✗ Failed to login. Please check your credentials and try again.")
            scraper.close()
            return
        
        # Step 3: Load Excel
        if not scraper.load_excel():
            scraper.close()
            return
        
        # Step 4: Process students
        output_file = scraper.process_students(start_row=3)
        
        if output_file:
            print(f"\n✓ Success! Check your updated file: {output_file}")
        
    except KeyboardInterrupt:
        print("\n\n⚠ Process interrupted by user")
    except Exception as e:
        print(f"\n✗ Unexpected error: {str(e)}")
    finally:
        scraper.close()


if __name__ == "__main__":
    main()
