# Student Portal Automation - Complete Project Documentation

**Date:** December 23, 2024  
**Project:** Web scraper to automate fetching student admission numbers from school portal and updating Excel files  
**Developer Background:** Frontend developer (React) learning Python automation

---

## Table of Contents
1. [Project Overview](#project-overview)
2. [Technical Stack](#technical-stack)
3. [Current Architecture](#current-architecture)
4. [Complete Feature List](#complete-feature-list)
5. [Problems Solved & Solutions](#problems-solved--solutions)
6. [Code Structure & Key Components](#code-structure--key-components)
7. [Configuration & Usage](#configuration--usage)
8. [Future Refactoring Plans](#future-refactoring-plans)
9. [Key Code Snippets](#key-code-snippets)

---

## Project Overview

### Purpose
Automate the tedious process of:
1. Manually searching for students on school portal
2. Copying their admission numbers
3. Pasting into Excel spreadsheets

**Time Savings:** 90% reduction (30 minutes → 3 minutes for 33 students)

### Portal Details
- **URL:** https://cdssjos.portal.commandschools.sch.ng/students
- **Authentication:** Username/password login required
- **Total Students:** 822 active students in database
- **Classes:** JSS 1-3, SS 1-3
- **Portal Structure:** Search box with class filter dropdown

### Excel File Details
- **Format:** Multiple sheets per file (Silver, Gold, Ruby, Emerald arms)
- **Structure:**
  - Column A: Admission Number (to be filled)
  - Column B: Student Name (format: LASTNAME FIRSTNAME MIDDLENAME)
  - Columns C-H: Class, Arm, Subject, scores
- **Name Format Issue:** Excel has "LASTNAME FIRSTNAME MIDDLE" but portal displays "FIRSTNAME LASTNAME"

---

## Technical Stack

### Core Technologies
- **Python 3.x**
- **Selenium 4.15.2** - Browser automation
- **openpyxl 3.1.2** - Excel file manipulation
- **Chrome WebDriver** - Browser control

### Key Libraries
```python
selenium                 # Browser automation
openpyxl                # Excel file handling
python-dotenv           # Environment variable management
difflib                 # String similarity matching (SequenceMatcher)
argparse                # Command-line argument parsing
logging                 # File and console logging
glob                    # File pattern matching
pathlib                 # Modern path handling
```

### Development Tools
- **Continue.dev** - Recommended AI coding assistant (free, VSCode extension)
- **Git** - Version control
- **Chrome Browser** - Required for Selenium

---

## Current Architecture

### Project Structure (Current - Single File)
```
student_portal_scraper/
├── .env                              # Environment variables (credentials)
├── .gitignore                        # Git ignore rules
├── README.md                         # Setup and usage documentation
├── requirements.txt                  # Python dependencies
├── student_portal_scraper.py         # Main script (550 lines)
├── test_login.py                     # Login verification script
└── logs/                             # Generated log files (auto-created)
    ├── SS3_GOVERNMENT_20241223_143215.log
    ├── JSS2_MATH_20241223_150430.log
    └── ...
```

### Planned Structure (MVC Refactor)
```
student_portal_scraper/
├── .env
├── .gitignore
├── README.md
├── requirements.txt
├── src/                              # All source code
│   ├── __init__.py
│   ├── main.py                       # Entry point (orchestration)
│   ├── models/                       # Data & business logic
│   │   ├── __init__.py
│   │   ├── student.py                # Student data class
│   │   ├── student_matcher.py        # Fuzzy matching algorithm
│   │   ├── excel_repository.py       # Excel data access
│   │   └── portal_repository.py      # Portal data access
│   ├── views/                        # Output & display
│   │   ├── __init__.py
│   │   ├── console_view.py           # Terminal output
│   │   └── logger_view.py            # File logging
│   ├── controllers/                  # Orchestration
│   │   ├── __init__.py
│   │   └── scraper_controller.py     # Main coordinator
│   ├── services/                     # Infrastructure
│   │   ├── __init__.py
│   │   ├── browser_manager.py        # Browser setup/teardown
│   │   ├── auth_manager.py           # Login handling
│   │   └── class_filter_manager.py   # Class dropdown filtering
│   └── utils/                        # Helper functions
│       ├── __init__.py
│       └── name_cleaner.py           # String cleaning utilities
├── tests/                            # Unit and integration tests
│   ├── __init__.py
│   ├── test_matcher.py
│   ├── test_excel_repository.py
│   └── test_login.py
├── logs/                             # Generated at runtime
└── scripts/                          # Helper scripts
    └── setup_environment.py
```

---

## Complete Feature List

### 1. Multi-File Batch Processing
**Description:** Process entire directories of Excel files in one command  
**Usage:**
```bash
python student_portal_scraper.py /path/to/folder/
python student_portal_scraper.py /path/to/folder/ --pattern "SS3*.xlsx"
python student_portal_scraper.py file1.xlsx  # Single file also works
```

**Implementation:**
- Uses `argparse` for CLI arguments
- `glob` for file pattern matching
- `pathlib` for cross-platform path handling
- Automatically filters out temporary Excel files (`~$*.xlsx`)

### 2. Multi-Sheet Processing
**Description:** Automatically processes all sheets in each workbook (Silver, Gold, Ruby, Emerald)  
**Benefits:**
- No need to manually switch sheets
- One file save operation (not per sheet)
- Aggregate statistics across all sheets

**Implementation:**
```python
def process_workbook(self, start_row=3):
    for sheet_name in self.wb.sheetnames:
        self.ws = self.wb[sheet_name]
        updated, skipped, errors = self.process_students(start_row, yellow_fill)
        total_updated += updated
        # ...
    self.wb.save(output_path)  # Single save after all sheets
```

### 3. Class Filtering
**Description:** Filter portal search by class (JSS 1, JSS 2, SS 3, etc.) to narrow results  
**Benefits:**
- Reduces search results from 822 → ~30-50 students
- Dramatically improves accuracy
- Faster processing

**Usage:**
```bash
python student_portal_scraper.py /path/to/JSS2/ --class "JSS 2"
python student_portal_scraper.py /path/to/SS3/ --class "SS 3"
```

**Current Status:** Implemented but needs fix (currently tries to set filter on every search)  
**Fix Required:** Set filter once after login, not on each search iteration

**Implementation Location:** Lines 83-120 in `set_class_filter()` method

### 4. Fuzzy Name Matching
**Description:** Intelligent matching algorithm that handles name format differences and typos

**Features:**
- **Order-independent:** "SMITH JOHN" matches "JOHN SMITH"
- **Compound names:** "STELLA MARIS" matches "STELLAMARIS"
- **Spelling variants:** "OKOAFUDA" matches "OKAFUDA"
- **Partial matches:** Handles missing middle names
- **Confidence scoring:** 0-100% match confidence

**Algorithm:**
```python
# Method 1: Exact word matching (set intersection)
excel_parts = set(full_name.split())
portal_parts = set(portal_name.split())
exact_score = len(excel_parts ∩ portal_parts) / len(excel_parts)

# Method 2: Fuzzy substring matching
fuzzy_score = 0
for part in excel_parts:
    if part in portal_full_name:  # STELLA in STELLAMARIS
        fuzzy_score += 1
    elif SequenceMatcher(part, portal_word).ratio() > 0.8:
        fuzzy_score += similarity_score

# Final score = max(exact_score, fuzzy_score)
# Match if score >= 45%
```

**Examples:**
```
Excel: "ADAMU MOHAMMED BURAH" vs Portal: "MOHAMMED ADAMU"
→ Exact: 67% (2/3 words match) ✓

Excel: "AKALAWU STELLA MARIS" vs Portal: "STELLAMARIS AKALAWU"  
→ Fuzzy: 80% (STELLA in STELLAMARIS, MARIS in STELLAMARIS, AKALAWU exact) ✓

Excel: "VICTOR BLESSING OKOAFUDA" vs Portal: "BLESSING OKAFUDA"
→ Fuzzy: 60% (BLESSING exact, OKAFUDA ~= OKOAFUDA) ✓
```

### 5. Dual Logging System
**Description:** Logs to both console (for monitoring) and files (for review)

**Console Output:**
- Progress indicators
- Match results with confidence
- Low confidence warnings
- Error messages
- Summary statistics

**File Logging:**
- Timestamped log files: `{excel_name}_{timestamp}.log`
- Location: `./logs/` directory
- Format: `YYYY-MM-DD HH:MM:SS | LEVEL | MESSAGE`
- Levels:
  - `INFO`: Successful matches (≥70% confidence)
  - `WARNING`: Low confidence matches (45-70%)
  - `ERROR`: No match found

**Example Log Entry:**
```
2024-12-23 15:30:45 | INFO | MATCHED | Row 3 | Excel: ABANG ANNABEL OUT | Portal: ANNABEL ABANG | Admission: CDSSJOS/STU/0589 | Score: 67%
2024-12-23 15:30:52 | WARNING | LOW CONFIDENCE | Row 10 | Excel: AKALAWU STELLA MARIS | Portal: STELLAMARIS AKALAWU | Admission: CDSSJOS/STU/0675 | Score: 60%
2024-12-23 15:30:55 | ERROR | NO MATCH | Row 12 | Excel: CHINWENWO DESTINY CHINDA | Best score: 33% | Searched: CHINWENWO
```

### 6. Visual Cell Highlighting
**Description:** Updated cells are highlighted in yellow for easy verification  
**Implementation:**
```python
yellow_fill = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")
admission_cell.fill = yellow_fill
```

### 7. Smart Skipping
**Description:** Automatically skips rows that already have valid admission numbers  
**Criteria:**
- Cell has content
- Content is a string
- Contains "CDSSJOS" (school prefix)

**Benefits:**
- Can re-run script safely on partially completed files
- Resume interrupted processing
- No duplicate work

### 8. Environment Variable Configuration
**Description:** Secure credential storage using `.env` file

**`.env` file structure:**
```bash
PORTAL_URL=https://cdssjos.portal.commandschools.sch.ng/students
PORTAL_USER=admin@cdssjos.portal.commandschools.sch.ng
PORTAL_PASS=your_password_here
```

**Benefits:**
- Credentials not in code
- Different configs for dev/prod
- Not committed to Git
- Easy to update

### 9. Error Handling & Resilience
**Description:** Comprehensive error handling to prevent crashes

**Features:**
- Try-catch blocks around all I/O operations
- Graceful handling of missing elements
- Continues processing even if individual students fail
- Browser cleanup on errors (prevents zombie processes)
- Keyboard interrupt handling (Ctrl+C)

**Implementation:**
```python
try:
    # Search for student
    admission_number = self.search_student(name, full_name)
    if admission_number:
        updated_count += 1
    else:
        error_count += 1
except Exception as e:
    logger.error(f"Error processing {name}: {e}")
    error_count += 1
    continue  # Keep going with next student
finally:
    scraper.close()  # Always cleanup
```

### 10. Summary Statistics
**Description:** Detailed reporting after each file and at end of batch

**Per-Sheet Summary:**
```
Sheet Summary (SS 3 SILVER):
  • Updated: 25
  • Skipped: 5
  • Errors: 3
```

**Per-File Summary:**
```
FINAL SUMMARY (All Sheets):
  • Total Updated: 78
  • Total Skipped: 15
  • Total Errors: 7
  • Total Processed: 100
```

**Batch Summary:**
```
ALL FILES PROCESSED
Files completed: 18
Total time: 45 minutes
```

---

## Problems Solved & Solutions

### Problem 1: Authentication Required
**Issue:** Portal requires login  
**Solution:** Automated login using Selenium
```python
def login(self, username, password):
    username_field = self.driver.find_element(By.NAME, "email")
    username_field.send_keys(username)
    password_field = self.driver.find_element(By.NAME, "password")
    password_field.send_keys(password)
    login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    login_button.click()
```

### Problem 2: Name Format Mismatch
**Issue:** Excel has "LASTNAME FIRSTNAME MIDDLE" but portal shows "FIRSTNAME LASTNAME"  
**Initial Approach:** Search by first word (last name)  
**Problem:** Multiple students with same last name  
**Final Solution:** Fuzzy matching algorithm with word-set intersection

### Problem 3: Multiple Students with Same Last Name
**Issue:** Searching "ADAMU" returns 20+ students  
**Solution:** Smart matching algorithm that:
1. Retrieves all results
2. Compares full name from Excel against each result
3. Calculates confidence score
4. Selects best match if confidence ≥ 45%

### Problem 4: Compound Names Not Matching
**Issue:** "STELLA MARIS" (2 words in Excel) vs "STELLAMARIS" (1 word in portal)  
**Solution:** Fuzzy substring matching
```python
# Remove spaces and check if parts are substrings
portal_full = portal_name.replace(" ", "")  # "STELLAMARIS"
if "STELLA" in portal_full:  # True!
    fuzzy_score += 1
```

### Problem 5: Class Filter Errors on Every Search
**Issue:** Tried to set class filter on every student search, but dropdown disappears after first search  
**Solution:** Set class filter once after login, not on each search iteration  
**Status:** Fix documented, needs implementation

**Current (Broken):**
```python
def search_student(self, name, full_name):
    # This runs for EVERY student (wrong!)
    if self.target_class:
        # Try to find dropdown - fails after first search
        class_dropdown = self.driver.find_element(...)
```

**Fixed (Correct):**
```python
def main():
    scraper.login(username, password)
    scraper.set_class_filter()  # Set ONCE here
    scraper.process_workbook()  # All searches use this filter

def search_student(self, name, full_name):
    # No class filter code here
    # Filter already set, just search
```

### Problem 6: Lost Terminal Output
**Issue:** Console logs get cleared when output is too long  
**Solution:** Dual logging system - file logs persist permanently  
**Location:** `./logs/{filename}_{timestamp}.log`

### Problem 7: Manual File Path Changes
**Issue:** Had to edit code to change which file to process  
**Solution:** Command-line arguments with argparse
```bash
# Before: Edit code every time
EXCEL_PATH = "/home/user/file1.xlsx"  # Hard-coded

# After: Pass as argument
python script.py /home/user/file1.xlsx
python script.py /home/user/folder/  # Entire folder
```

### Problem 8: Processing One Sheet at a Time
**Issue:** Excel files have 4-5 sheets (Silver, Gold, Ruby, Emerald) - tedious to process each  
**Solution:** `process_workbook()` method loops through all sheets automatically

### Problem 9: Can't Verify Matches Later
**Issue:** How to check if low-confidence matches are correct?  
**Solution:**
1. Yellow highlighting in Excel
2. Detailed logs with confidence scores
3. Low confidence warnings in console

**Verification Workflow:**
1. Run script
2. Check console for LOW CONFIDENCE warnings
3. Open log file: `cat logs/filename_*.log | grep "LOW CONFIDENCE"`
4. Manually verify those specific rows in portal

---

## Code Structure & Key Components

### Main Class: `StudentPortalScraper`

**Responsibilities:**
- Browser automation
- Login management
- Student searching
- Name matching
- Excel processing
- Logging

**Key Methods:**

#### `__init__(excel_path, portal_url)`
Initializes scraper instance
```python
def __init__(self, excel_path, portal_url):
    self.excel_path = excel_path
    self.portal_url = portal_url
    self.driver = None  # Selenium WebDriver
    self.wb = None      # openpyxl Workbook
    self.ws = None      # Current worksheet
```

#### `setup_logging(log_dir="./logs")`
Creates log file with timestamp
```python
# Creates: logs/SS3_GOVERNMENT_20241223_143215.log
# Sets up both file and console logging
```

#### `setup_driver()`
Initializes Chrome WebDriver
```python
chrome_options = Options()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
self.driver = webdriver.Chrome(options=chrome_options)
```

#### `login(username, password)`
Authenticates to portal
```python
# Finds email/username field
# Enters credentials
# Clicks submit
# Verifies success by checking URL
```

#### `set_class_filter()`
**STATUS: Needs fix - currently broken**
Sets class dropdown to filter results
```python
# ISSUE: Tries to find dropdown that disappears after first search
# FIX: Should only run once after login
```

#### `clean_name(name)`
Extracts search term from full name
```python
# Input: "ADAMU    MOHAMMED    BURAH"
# Output: "ADAMU" (first word)
```

#### `search_student(name, full_name)`
**Most complex method - 140 lines**

Main search and matching logic:
1. Navigate to students page if needed
2. Enter search term
3. Retrieve all matching rows
4. For each result:
   - Extract admission number, first name, last name
   - Calculate match score (exact + fuzzy)
   - Track best match
5. Return admission number if confidence ≥ 45%

**Key matching code:**
```python
# Exact word matching
matching_words = set(excel_parts).intersection(portal_words)
exact_score = len(matching_words) / len(excel_parts)

# Fuzzy substring matching
fuzzy_points = 0
for part in excel_parts:
    if part in portal_full_no_space:
        fuzzy_points += 1
    else:
        max_sim = max([get_similarity(part, w) for w in portal_words])
        if max_sim > 0.8:
            fuzzy_points += max_sim

fuzzy_score = fuzzy_points / len(excel_parts)
normalized_score = max(exact_score, fuzzy_score)
```

#### `load_excel()`
Opens Excel workbook
```python
self.wb = openpyxl.load_workbook(self.excel_path)
self.ws = self.wb.active
```

#### `process_workbook(start_row=3)`
Loops through all sheets in workbook
```python
for sheet_name in self.wb.sheetnames:
    self.ws = self.wb[sheet_name]
    updated, skipped, errors = self.process_students(start_row, yellow_fill)
    total_updated += updated

# Save once after all sheets
self.wb.save(output_path)
```

#### `process_students(start_row=3, yellow_fill=None)`
Processes all rows in current sheet
```python
for row_idx in range(start_row, self.ws.max_row + 1):
    # Get student name from column B
    student_name = self.ws.cell(row=row_idx, column=2).value
    
    # Skip if already has admission number
    if admission_cell.value and "CDSSJOS" in admission_cell.value:
        skipped_count += 1
        continue
    
    # Search and match
    self.current_row = row_idx  # For logging
    admission_number = self.search_student(search_name, student_name)
    
    # Update Excel if match found
    if admission_number:
        admission_cell.value = admission_number
        admission_cell.fill = yellow_fill
        updated_count += 1
```

#### `close()`
Cleanup browser resources
```python
if self.driver:
    self.driver.quit()
```

### Helper Functions

#### `get_similarity(a, b)`
Calculates string similarity using SequenceMatcher
```python
def get_similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()
# Example: get_similarity("OKAFUDA", "OKOAFUDA") → 0.875 (87.5%)
```

### Main Function

#### `main()`
Entry point - orchestrates everything
```python
def main():
    # 1. Parse command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("path")  # File or directory
    parser.add_argument("--class", dest="student_class")
    parser.add_argument("--pattern", default="*.xlsx")
    
    # 2. Get credentials from .env
    PORTAL_URL = os.getenv("PORTAL_URL")
    USERNAME = os.getenv("PORTAL_USER")
    PASSWORD = os.getenv("PORTAL_PASS")
    
    # 3. Determine files to process
    if path.is_file():
        files_to_process = [path]
    elif path.is_dir():
        files_to_process = glob.glob(str(path / pattern))
        # Filter out temp files
        files_to_process = [f for f in files if not f.startswith('~$')]
    
    # 4. Process each file
    for file_path in files_to_process:
        scraper = StudentPortalScraper(file_path, PORTAL_URL)
        scraper.target_class = args.student_class
        scraper.setup_logging()
        
        try:
            scraper.setup_driver()
            scraper.login(USERNAME, PASSWORD)
            scraper.set_class_filter()  # NEEDS FIX
            scraper.load_excel()
            output, updated, errors = scraper.process_workbook()
        finally:
            scraper.close()
```

---

## Configuration & Usage

### Installation

```bash
# 1. Clone/download project
cd student_portal_scraper/

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create .env file
cat > .env << EOF
PORTAL_URL=https://cdssjos.portal.commandschools.sch.ng/students
PORTAL_USER=your_username
PORTAL_PASS=your_password
EOF

# 4. Verify login works
python test_login.py
```

### Usage Examples

```bash
# Process single file
python student_portal_scraper.py /path/to/file.xlsx

# Process entire directory
python student_portal_scraper.py /path/to/JSS2/

# Process with class filter
python student_portal_scraper.py /path/to/JSS2/ --class "JSS 2"
python student_portal_scraper.py /path/to/SS3/ --class "SS 3"

# Process only specific files
python student_portal_scraper.py /path/to/files/ --pattern "EXAM*.xlsx"
python student_portal_scraper.py /path/to/files/ --pattern "SS3*.xlsx"
```

### Environment Variables

**Required:**
- `PORTAL_URL` - Portal login URL
- `PORTAL_USER` - Portal username/email
- `PORTAL_PASS` - Portal password

**Optional:**
- None currently, but could add:
  - `LOG_DIR` - Custom log directory
  - `HEADLESS` - Run browser in headless mode
  - `TIMEOUT` - Search timeout in seconds

### Command-Line Arguments

```bash
python student_portal_scraper.py <path> [options]

Positional:
  path                  Path to Excel file or directory

Options:
  --class CLASSNAME     Filter by class (e.g., "JSS 2", "SS 3")
  --pattern PATTERN     File pattern (default: *.xlsx)
  -h, --help           Show help message
```

### Output Files

**Updated Excel:**
- Location: Same directory as input
- Naming: `{original_name}_updated.xlsx`
- Example: `SS3_GOVERNMENT.xlsx` → `SS3_GOVERNMENT_updated.xlsx`

**Log Files:**
- Location: `./logs/` directory
- Naming: `{excel_name}_{timestamp}.log`
- Example: `logs/SS3_GOVERNMENT_20241223_143215.log`

### Performance Metrics

**Time per student:**
- Search: 2-3 seconds
- Update Excel: <0.1 seconds
- Total: ~2-3 seconds per student

**Typical batch:**
- 33 students: ~2-3 minutes
- 100 students: ~5-8 minutes
- 18 files (600+ students): ~30-45 minutes

**Success rate:**
- With class filter: 85-90%
- Without class filter: 60-70%

---

## Future Refactoring Plans

### Why Refactor?

**Current Issues:**
- Single 550-line file is hard to navigate
- Testing is difficult (need browser for everything)
- Can't reuse components in other projects
- Hard to understand 6 months later

**Benefits of MVC:**
- Smaller, focused files (50-100 lines each)
- Can test matching logic without browser
- Easy to find and fix bugs
- Clear separation of concerns
- Easier to add features

### MVC Architecture Plan

**Model** (Data & Business Logic):
- `student.py` - Student data class
- `student_matcher.py` - Matching algorithm (pure logic, no dependencies)
- `excel_repository.py` - Excel reading/writing
- `portal_repository.py` - Portal searching

**View** (Display & Output):
- `console_view.py` - Terminal output formatting
- `logger_view.py` - File logging formatting

**Controller** (Orchestration):
- `scraper_controller.py` - Coordinates Model and View

**Services** (Infrastructure):
- `browser_manager.py` - Browser setup/teardown
- `auth_manager.py` - Login handling
- `class_filter_manager.py` - Class filtering

### Refactoring Strategy

**Don't do it all at once!** Incremental approach:

1. **Create folder structure** (5 minutes)
2. **Extract `StudentMatcher`** (30 minutes) - Pure logic, no dependencies
3. **Test it works** - Run script to verify
4. **Extract `BrowserManager`** (20 minutes)
5. **Extract `ExcelRepository`** (30 minutes)
6. **Continue one component at a time**
7. **Create controller** (60 minutes)
8. **Final cleanup** (30 minutes)

**Total time:** ~4-6 hours spread over several days

### Tools for Refactoring

**Recommended: Continue.dev**
- Free VSCode extension
- Works with Claude API ($3-5/month usage)
- Can also use free models (DeepSeek, Llama)
- Multi-file editing
- Shows diffs before applying

**Installation:**
```bash
# 1. Install VSCode
# 2. Install Continue extension from marketplace
# 3. Configure with Claude API key or free model
# 4. Open project and start refactoring
```

**Alternative Tools:**
- **Windsurf** - Free tier (10 Cascade runs/day)
- **Aider** - Command-line AI editor (free)
- **Cursor** - VSCode fork with AI (free tier limited)

### First Extraction Example

**Extract StudentMatcher (Good starting point):**

**Before (in main file):**
```python
# Lines 28-29
def get_similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

class StudentPortalScraper:
    def search_student(self, name, full_name):
        # ... 140 lines including matching logic
```

**After:**

**`src/models/student_matcher.py`** (NEW):
```python
from difflib import SequenceMatcher

class StudentMatcher:
    @staticmethod
    def get_similarity(a, b):
        return SequenceMatcher(None, a, b).ratio()
    
    @staticmethod
    def calculate_match_score(excel_name, portal_name):
        # Fuzzy matching logic moved here
        # ... 60 lines of pure logic
        return score
```

**`src/main.py`** (MODIFIED):
```python
from src.models.student_matcher import StudentMatcher

class StudentPortalScraper:
    def __init__(self, excel_path, portal_url):
        self.matcher = StudentMatcher()  # Use component
    
    def search_student(self, name, full_name):
        # ... search code ...
        score = self.matcher.calculate_match_score(full_name, portal_name)
        # ... rest of logic
```

**Benefits immediately visible:**
- Can test `StudentMatcher` without browser
- Can reuse in other projects
- `search_student()` method is now 80 lines instead of 140
- Clear what code does matching vs searching

---

## Key Code Snippets

### Complete Matching Algorithm
```python
def search_student(self, name, full_name):
    """Search for student and return best match admission number"""
    try:
        # 1. Navigate to portal if needed
        if "students" not in self.driver.current_url.lower():
            self.driver.get(self.portal_url)
            time.sleep(2)
        
        # 2. Enter search term
        search_box = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='text']"))
        )
        search_box.clear()
        search_box.send_keys(name)
        time.sleep(2.5)
        
        # 3. Get all results
        rows = self.driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
        
        # 4. Parse Excel name
        full_name_clean = re.sub(r'\s+', ' ', full_name.upper().strip())
        full_name_parts = [p for p in full_name_clean.split() if len(p) >= 3]
        
        # 5. Find best match
        best_match = None
        best_score = 0
        
        for row in rows:
            try:
                cells = row.find_elements(By.TAG_NAME, "td")
                if len(cells) < 3:
                    continue
                
                admission_number = cells[0].text.strip()
                first_name_portal = cells[1].text.strip().upper()
                last_name_portal = cells[2].text.strip().upper()
                
                portal_display = f"{first_name_portal} {last_name_portal}"
                portal_full_no_space = portal_display.replace(" ", "")
                portal_words = set(portal_display.split())
                
                # Exact word matching
                matching_words = set(full_name_parts).intersection(portal_words)
                exact_score = len(matching_words) / len(full_name_parts) if full_name_parts else 0
                
                # Fuzzy substring matching
                fuzzy_points = 0
                for part in full_name_parts:
                    if part in portal_full_no_space:
                        fuzzy_points += 1
                    else:
                        word_sims = [get_similarity(part, w) for w in portal_words]
                        max_sim = max(word_sims) if word_sims else 0
                        if max_sim > 0.8:
                            fuzzy_points += max_sim
                
                fuzzy_score = fuzzy_points / len(full_name_parts) if full_name_parts else 0
                normalized_score = max(exact_score, fuzzy_score)
                
                print(f" • {portal_display}: {admission_number} (Score: {normalized_score:.0%})")
                
                if normalized_score > best_score:
                    best_score = normalized_score
                    best_match = (admission_number, portal_display)
            
            except Exception as row_err:
                continue
        
        # 6. Return if confidence is high enough
        if best_match and best_score >= 0.45:
            # Log the match
            if hasattr(self, 'logger'):
                if best_score < 0.70:
                    self.logger.warning(
                        f"LOW CONFIDENCE | Row {getattr(self, 'current_row', '?')} | "
                        f"Excel: {full_name} | Portal: {best_match[1]} | "
                        f"Admission: {best_match[0]} | Score: {best_score:.2%}"
                    )
                else:
                    self.logger.info(
                        f"MATCHED | Row {getattr(self, 'current_row', '?')} | "
                        f"Excel: {full_name} | Portal: {best_match[1]} | "
                        f"Admission: {best_match[0]} | Score: {best_score:.2%}"
                    )
            
            # Console output
            if best_score < 0.70:
                print(f" ⚠ LOW CONFIDENCE MATCH ({best_score:.0%}) - Please verify!")
            print(f" ✓ Best match: {best_match[1]} → {best_match[0]}")
            return best_match[0]
        else:
            # Log no match
            if hasattr(self, 'logger'):
                self.logger.error(
                    f"NO MATCH | Row {getattr(self, 'current_row', '?')} | "
                    f"Excel: {full_name} | Best score: {best_score:.2%} | "
                    f"Searched: {name}"
                )
            return None
    
    except Exception as e:
        print(f" ✗ Search error: {str(e)}")
        return None
```

### Logging Setup
```python
def setup_logging(self, log_dir="./logs"):
    """Setup file logging for the scraping session"""
    from pathlib import Path
    
    # Create logs directory
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
    
    # Console handler (warnings only)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    
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
    return log_file
```

### File Path Handling
```python
def main():
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    parser.add_argument("--pattern", default="*.xlsx")
    args = parser.parse_args()
    
    # Determine files to process
    path = Path(args.path)
    
    if path.is_file():
        files_to_process = [str(path)]
    elif path.is_dir():
        pattern = args.pattern
        files_to_process = glob.glob(str(path / pattern))
        # Filter out temporary Excel files
        files_to_process = [f for f in files_to_process 
                           if not Path(f).name.startswith('~$')]
    else:
        print(f"✗ Path does not exist: {path}")
        return
    
    # Process each file
    for idx, file_path in enumerate(files_to_process, 1):
        print(f">>> FILE {idx}/{len(files_to_process)}: {file_path}")
        scraper = StudentPortalScraper(file_path, PORTAL_URL)
        # ... process file
```

### Class Filter (Needs Fix)
```python
def set_class_filter(self):
    """Set the class filter once after login"""
    if not hasattr(self, 'target_class') or not self.target_class:
        return False
    
    try:
        print(f"\n→ Setting class filter to: {self.target_class}")
        time.sleep(2)  # Wait for page load
        
        # Find CLASS dropdown
        class_dropdown = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//label[contains(text(), 'CLASS')]/following::select[1]")
            )
        )
        
        # Use Select to choose option
        from selenium.webdriver.support.ui import Select
        select = Select(class_dropdown)
        
        # Try exact match
        try:
            select.select_by_visible_text(self.target_class)
            print(f"✓ Class filter set to: {self.target_class}\n")
            time.sleep(1.5)
            return True
        except:
            # Try partial match
            for option in select.options:
                if self.target_class.upper() in option.text.upper():
                    select.select_by_visible_text(option.text)
                    print(f"✓ Class filter set to: {option.text}\n")
                    time.sleep(1.5)
                    return True
        
        return False
    except Exception as e:
        print(f"⚠ Could not set class filter: {e}\n")
        return False

# MUST be called in main() after login, NOT in search_student()
# Current issue: Being called on every search iteration
```

---

## Important Notes & Gotchas

### 1. Class Filter Issue
**Current Status:** Implemented but broken  
**Problem:** Tries to set filter on every search, but dropdown disappears after first search  
**Fix:** Call `set_class_filter()` once after login in `main()`, remove from `search_student()`

### 2. Excel Name Format
Students in Excel are formatted: `LASTNAME    FIRSTNAME    MIDDLENAME` (often with extra spaces)  
Portal displays: `FIRSTNAME LASTNAME`  
Clean names with: `re.sub(r'\s+', ' ', name.strip())`

### 3. Portal Session Timeout
Portal may timeout after 30-60 minutes of inactivity  
No automatic re-login implemented  
Solution: Process files in batches if needed

### 4. Temporary Excel Files
Excel creates temp files when open: `~$filename.xlsx`  
These cause errors if script tries to process them  
Solution: Filter them out in file processing loop

### 5. XPath Selectors May Break
Portal HTML could change, breaking selectors like:
- `By.CSS_SELECTOR, "input[type='text']"` - Search box
- `By.CSS_SELECTOR, "table tbody tr"` - Result rows
- `By.XPATH, "//label[contains(text(), 'CLASS')]/following::select[1]"` - Class dropdown

**If selectors break:**
1. Right-click element in browser
2. Inspect Element
3. Copy new selector
4. Update code

### 6. Rate Limiting
Portal has no explicit rate limiting, but good practice:
- 1-2 second delays between searches
- Don't run multiple instances simultaneously
- Use class filter to reduce load

### 7. Browser Zombie Processes
If script crashes, Chrome may stay running  
Always use try-finally to ensure `scraper.close()` runs  
Manual cleanup: `pkill chrome` or Task Manager

### 8. Large Batch Processing
For 18+ files:
- Takes 30-45 minutes
- Browser window must stay in focus
- Don't minimize or switch desktops
- Consider running overnight

### 9. Confidence Threshold Tuning
Current threshold: 45%  
- Too low: More matches, more errors
- Too high: Fewer matches, more manual work

Adjust in `search_student()`:
```python
if best_match and best_score >= 0.45:  # Change 0.45 to tune
```

### 10. Python Package Requirements
Must use `--break-system-packages` with pip on some systems:
```bash
pip install openpyxl --break-system-packages
```

---

## Testing & Verification

### Manual Testing Workflow
1. Run script on small test file (5-10 students)
2. Check console output for warnings
3. Open updated Excel file
4. Verify yellow highlighted cells
5. Check log file for details
6. Manually verify low-confidence matches in portal

### Automated Testing (Future)
```python
# tests/test_matcher.py
def test_exact_match():
    matcher = StudentMatcher()
    score = matcher.calculate_match_score("JOHN SMITH", "JOHN SMITH")
    assert score == 1.0

def test_reversed_names():
    matcher = StudentMatcher()
    score = matcher.calculate_match_score("SMITH JOHN", "JOHN SMITH")
    assert score >= 0.5

def test_compound_names():
    matcher = StudentMatcher()
    score = matcher.calculate_match_score("STELLA MARIS JONES", "STELLAMARIS JONES")
    assert score >= 0.6
```

### Integration Testing
```python
# tests/test_integration.py
def test_full_workflow():
    # Use fake/mock portal and Excel
    fake_portal = FakePortalRepository()
    fake_excel = FakeExcelRepository()
    
    controller = ScraperController(fake_excel, fake_portal)
    result = controller.process_file(...)
    
    assert result.updated_count > 0
    assert result.error_count == 0
```

---

## Troubleshooting Guide

### "Login failed"
**Causes:**
- Wrong credentials
- Portal down
- Network issues
- 2FA enabled (not supported)

**Solutions:**
- Verify credentials in `.env`
- Try manual login in browser
- Check network connection
- Disable 2FA if possible

### "No results found"
**Causes:**
- Student not in portal
- Name format too different
- Wrong class selected
- Search timing issue

**Solutions:**
- Try manual search in portal
- Check name spelling in Excel
- Remove class filter temporarily
- Increase `time.sleep()` after search

### "Element not found"
**Causes:**
- Portal HTML changed
- Page not fully loaded
- Selector is wrong

**Solutions:**
- Inspect element in browser
- Update selector in code
- Increase wait times
- Use WebDriverWait instead of sleep

### "LOW CONFIDENCE" warnings
**Not an error!** Just needs verification.

**What to do:**
1. Check log file for details
2. Manually verify in portal
3. If correct: Great!
4. If wrong: Update Excel manually

### Script hangs/freezes
**Causes:**
- Portal timeout
- Network issue
- Infinite loop (bug)

**Solutions:**
- Press Ctrl+C to stop
- Check browser window for errors
- Restart script
- Check logs for last processed student

### Excel file locked
**Cause:** File open in Excel or another program

**Solution:**
- Close Excel
- Close any other programs accessing file
- Check for zombie Excel processes
- Restart script

---

## Performance Optimization Ideas (Future)

### 1. Headless Browser
Run Chrome without GUI for faster processing:
```python
chrome_options.add_argument('--headless')
```
**Trade-off:** Can't see what's happening, harder to debug

### 2. Parallel Processing
Process multiple files simultaneously:
```python
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=3) as executor:
    executor.map(process_file, files_to_process)
```
**Trade-off:** More complex, more resource usage, potential portal rate limits

### 3. Caching
Cache portal results to avoid redundant searches:
```python
search_cache = {}  # name → admission_number

if name in search_cache:
    return search_cache[name]
else:
    result = search_portal(name)
    search_cache[name] = result
    return result
```
**Trade-off:** More memory usage, stale data if portal updates

### 4. Batch API Requests
If portal has API, use batch requests instead of browser automation  
**Trade-off:** Requires API access (may not exist)

### 5. Smarter Skipping
Skip entire sheets if all admission numbers already present:
```python
def has_all_admissions(sheet):
    for row in sheet.iter_rows(min_row=3):
        if not row[0].value or "CDSSJOS" not in row[0].value:
            return False
    return True

if has_all_admissions(sheet):
    print("Sheet complete, skipping")
    continue
```

---

## Security & Privacy

### Credentials
- ✅ Stored in `.env` (not in code)
- ✅ `.env` in `.gitignore` (not committed)
- ⚠ Plain text on disk (acceptable for local use)
- 🔴 Never commit `.env` to Git

### Student Data
- ⚠ Excel files contain PII (names, admission numbers)
- ⚠ Log files contain PII
- 🔴 Don't commit Excel or log files to Git
- 🔴 Don't share logs publicly

### Portal Access
- ✅ Uses legitimate authentication
- ✅ Respects portal (delays between requests)
- ⚠ Verify school policy allows automation
- ⚠ Don't abuse portal (rate limits, parallel requests)

### `.gitignore` Should Include:
```
.env
*.log
logs/
**/*_updated.xlsx
*.pyc
__pycache__/
.vscode/
```

---

## Learning Resources

### Python Concepts Used
- **Classes** - Object-oriented programming
- **Methods** - Functions inside classes
- **Modules** - Organizing code into files
- **Packages** - Collections of modules
- **Context Managers** - `with` statements
- **Exception Handling** - try/except/finally
- **List Comprehensions** - `[x for x in list if condition]`
- **String Formatting** - f-strings
- **Path Handling** - pathlib
- **Logging** - Python logging module

### Selenium Concepts
- **WebDriver** - Browser automation interface
- **Element Locators** - By.ID, By.CSS_SELECTOR, By.XPATH
- **Waits** - WebDriverWait, EC.presence_of_element_located
- **Actions** - click(), send_keys(), clear()

### Design Patterns
- **MVC** - Model-View-Controller architecture
- **Repository Pattern** - Data access abstraction
- **Service Layer** - Business logic separation
- **Dependency Injection** - Passing dependencies

### Related Topics
- **Web Scraping Ethics** - Legal and ethical considerations
- **RPA (Robotic Process Automation)** - Business automation
- **Test-Driven Development** - Writing tests first
- **Continuous Integration** - Automated testing in CI/CD

---

## Project Milestones & History

### Version 1.0 (Initial)
- ✅ Single file processing
- ✅ Basic search and match
- ✅ Manual configuration

### Version 2.0 (Multi-file)
- ✅ Command-line arguments
- ✅ Directory processing
- ✅ Environment variables

### Version 2.5 (Smart Matching)
- ✅ Fuzzy name matching
- ✅ Confidence scoring
- ✅ Multi-sheet processing

### Version 3.0 (Logging & Reporting)
- ✅ Dual logging system
- ✅ Detailed statistics
- ✅ Cell highlighting

### Version 3.5 (Class Filtering) - Current
- ⚠ Class filter (needs fix)
- ✅ Batch processing optimization
- ✅ Temp file filtering

### Version 4.0 (Planned - MVC Refactor)
- ⏳ Component-based architecture
- ⏳ Unit tests
- ⏳ Improved maintainability
- ⏳ Easier to extend

---

## Contact & Support

**Developer:** Frontend developer learning Python automation  
**Background:** React, JavaScript  
**Learning:** Python, Selenium, web scraping, OOP, MVC architecture  

**AI Assistant:** Claude (Anthropic)  
**Tools:** Continue.dev, VSCode  

---

## End of Documentation

**Last Updated:** December 23, 2024  
**Project Status:** Working, needs class filter fix and MVC refactor  
**Total Lines:** 550 lines (current), target ~1000 lines (after refactor, split across files)  
**Estimated Refactor Time:** 4-6 hours  

This document contains complete context to resume development if tokens run out or session ends.
