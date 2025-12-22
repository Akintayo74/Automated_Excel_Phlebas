# Student Portal Automation - Setup Guide

## 📋 Overview
This automation script will:
1. Log into the school portal
2. Search for each student by name
3. Extract their admission number
4. Update your Excel file automatically
5. Highlight updated cells in yellow

## 🔧 Setup Instructions

### Step 1: Install Python
Make sure you have Python 3.7+ installed:
```bash
python --version
```

### Step 2: Install Required Packages
Open terminal/command prompt and run:
```bash
pip install -r requirements.txt
```

### Step 3: Install Chrome Browser
- Download and install Google Chrome if you haven't already
- The script uses Chrome WebDriver (downloads automatically)

### Step 4: Configure Your Credentials

**IMPORTANT:** Open `student_portal_scraper.py` and update these lines (around line 220):

```python
USERNAME = "your_username_here"  # ← Replace with your actual portal username
PASSWORD = "your_password_here"  # ← Replace with your actual portal password
```

### Step 5: Update File Path (if needed)
If your Excel file is in a different location, update line 217:
```python
EXCEL_PATH = "/path/to/your/EXAM_SS3_GOVERNMENT.xlsx"
```

## 🚀 How to Run

### Option 1: Basic Run
```bash
python student_portal_scraper.py
```

### Option 2: Run with Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install packages
pip install -r requirements.txt

# Run the script
python student_portal_scraper.py
```

## 📊 What the Script Does

1. **Opens Chrome browser** - You'll see it open automatically
2. **Logs in** - Uses your credentials to access the portal
3. **Reads Excel** - Loads student names from your file
4. **Searches each student** - One by one, searching by last name
5. **Extracts admission numbers** - Finds the admission number from search results
6. **Updates Excel** - Writes the admission number to Column A
7. **Saves file** - Creates a new file: `EXAM_SS3_GOVERNMENT_updated.xlsx`
8. **Highlights changes** - Updated cells are highlighted in yellow

## ⚙️ Customization Options

### Change Starting Row
If your data starts at a different row, modify line 242:
```python
output_file = scraper.process_students(start_row=3)  # Change 3 to your row number
```

### Skip Already Filled Cells
The script automatically skips rows that already have valid admission numbers (containing "CDSSJOS")

### Adjust Search Delays
If the portal is slow, increase wait times (lines 149, 195):
```python
time.sleep(2)  # Increase to 3 or 4 seconds
```

## 🐛 Troubleshooting

### Issue: "Login failed"
- ✓ Check username and password are correct
- ✓ Try logging in manually first to ensure account works
- ✓ Check if portal requires 2FA (Two-Factor Authentication)

### Issue: "No results found"
- ✓ The script searches by last name (first word in name column)
- ✓ Try searching manually to see if name format matches portal
- ✓ You may need to adjust the `clean_name()` function

### Issue: "Element not found"
- ✓ The portal HTML might have changed
- ✓ You may need to update CSS selectors in the code
- ✓ Run with browser visible (remove headless mode) to debug

### Issue: Script is too fast/slow
Adjust delays:
```python
time.sleep(1)  # At line 204 - delay between each student
time.sleep(2)  # At line 149 - delay after search
```

## 🔒 Security Notes

1. **Never share your script** with credentials in it
2. **Use environment variables** for credentials (advanced):
   ```python
   import os
   USERNAME = os.getenv('PORTAL_USERNAME')
   PASSWORD = os.getenv('PORTAL_PASSWORD')
   ```
3. **Keep your updated Excel file secure** - it contains student data

## 📝 Important Notes

1. **Internet Connection**: Requires stable internet
2. **Portal Availability**: Portal must be accessible
3. **Name Matching**: Script searches by last name (first word)
4. **Rate Limiting**: Has built-in delays to be respectful to server
5. **Backup**: Original Excel file is not modified - creates new file

## 🎯 Expected Output

```
======================================================================
STUDENT PORTAL AUTOMATION SCRIPT
======================================================================

✓ Browser initialized

→ Navigating to https://cdssjos.portal.commandschools.sch.ng/students
→ Waiting for login page...
→ Attempting to log in...
→ Logging in...
✓ Login successful!
✓ Excel file loaded: /path/to/EXAM_SS3_GOVERNMENT.xlsx

======================================================================
Starting to process students...
======================================================================

Row 3: ABANG ANNABEL OUT
  → Searching for: ABANG
  ✓ Found: CDSSJOS/STU/0589
  ✓ Updated in Excel

Row 4: ABANG OSARR BRIGHT
  ⊘ Skipped (already has admission number: CDSSJOS/STU/0577)

... (continues for all students)

======================================================================
✓ Excel file saved: EXAM_SS3_GOVERNMENT_updated.xlsx
======================================================================

Summary:
  • Updated: 15
  • Skipped: 10
  • Errors: 2
  • Total processed: 27

✓ Browser closed
```

## 🆘 Need Help?

If you encounter issues:
1. Run the script with browser visible (comment out headless mode)
2. Take a screenshot of where it fails
3. Check the portal's HTML structure hasn't changed
4. Ensure your credentials are correct

## ⚡ Tips for Best Results

- Run during off-peak hours for faster processing
- Ensure portal is accessible and not under maintenance
- Have a backup of your Excel file
- Test with a small dataset first (copy first 5 rows to test file)
