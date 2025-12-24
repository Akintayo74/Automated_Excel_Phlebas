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
Make sure you have **Python 3.7+** installed:
```bash
python3 --version
```

### Step 2: Install Required Packages
Open terminal and run:
```bash
pip install -r requirements.txt
```

### Step 3: Install Chrome Browser
- Download and install Google Chrome if you haven't already
- The script uses Chrome WebDriver (downloads automatically)

### Step 4: Configure Your Credentials
1. Create a `.env` file in the project root:
   ```bash
   touch .env
   ```
2. Add your credentials to the `.env` file:
   ```bash
   PORTAL_URL=https://cdssjos.portal.commandschools.sch.ng/students
   PORTAL_USER=your_username_here
   PORTAL_PASS=your_password_here
   ```

## 🚀 How to Run

### Basic Usage
```bash
python3 student_portal_scraper.py [path_to_excel_or_folder] [options]
```

### Example Commands
**Process a Specific Folder with Class Filter (Recommended):**
```bash
python3 student_portal_scraper.py /home/akintayo74/Downloads/JSS1/ --class "JSS 1"
```

**Process a Single File:**
```bash
python3 student_portal_scraper.py /path/to/EXAM_SS3_GOVERNMENT.xlsx
```

**Process All Files in a Folder:**
```bash
python3 student_portal_scraper.py /path/to/folder/
```

## ⚙️ Customization options

### Command Line Arguments
- `path`: The file or directory to process (Required)
- `--class`: Filter search results by class name (e.g., "JSS 1", "SS 3"). Highly recommended for accuracy.
- `--pattern`: File pattern to match when scanning directories (default: `*.xlsx`)

## 📊 What the Script Does

1. **Opens Chrome browser** - Managed by `src/services/browser_manager.py`
2. **Logs in** - Uses credentials from `.env`
3. **Reads Excel** - Loads student names
4. **Searches & Matches** - Uses fuzzy logic to find the best match for each student
5. **Updates Excel** - Writes the admission number and highlights in yellow
6. **Saves Result** - Creates `filename_updated.xlsx`

## 🐛 Troubleshooting

### Issue: "Missing environment variables"
- Ensure you have created the `.env` file with `PORTAL_USER` and `PORTAL_PASS`.

### Issue: "Login failed"
- Check username and password in `.env`.
- Try logging in manually to ensuring the account is active.

### Issue: "ModuleNotFoundError"
- Ensure you activated your virtual environment and ran `pip install -r requirements.txt`.

## 🔒 Security Notes
- **Never commit your `.env` file** to version control.
- Keep your updated Excel files secure as they contain student data.
