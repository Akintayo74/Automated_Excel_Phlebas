import argparse
import glob
import os
from pathlib import Path
from dotenv import load_dotenv
from src.controllers.scraper_controller import ScraperController

def main():
    """Main execution function with command-line argument support"""
    parser = argparse.ArgumentParser(
        description="Automated Student Portal Scraper",
        epilog="Example: python script.py /path/to/folder/ --class 'JSS 3'"
    )
    parser.add_argument(
        "path", 
        help="Path to Excel file(s) or directory containing Excel files"
    )
    parser.add_argument(
        "--pattern",
        default="*.xlsx",
        help="File pattern to match (default: *.xlsx)"
    )
    parser.add_argument(
        "--class",
        dest="student_class",
        default=None,
        help="Filter by class (e.g., 'JSS 3', 'SS 3') - speeds up search"
    )
    args = parser.parse_args()

    load_dotenv()

    # 2. Get Credentials from .env
    PORTAL_URL = os.getenv("PORTAL_URL")
    USERNAME = os.getenv("PORTAL_USER")
    PASSWORD = os.getenv("PORTAL_PASS")
    
    # Validate environment variables
    if not all([PORTAL_URL, USERNAME, PASSWORD]):
        print("✗ Error: Missing environment variables!")
        print("  Please ensure your .env file contains:")
        print("    PORTAL_URL=https://...")
        print("    PORTAL_USER=your_username")
        print("    PORTAL_PASS=your_password")
        return

    # 3. Determine which files to process
    path = Path(args.path)
    
    if path.is_file():
        # Single file provided
        files_to_process = [str(path)]
    elif path.is_dir():
        # Directory provided - find all Excel files
        pattern = args.pattern
        files_to_process = glob.glob(str(path / pattern))
        if not files_to_process:
            print(f"✗ No files matching '{pattern}' found in {path}")
            return
    else:
        print(f"✗ Path does not exist: {path}")
        return
    
    # 4. Display files to process
    print("\n" + "="*70)
    print("STUDENT PORTAL AUTOMATION SCRIPT")
    print("="*70)
    print(f"Files to process: {len(files_to_process)}")
    for f in files_to_process:
        print(f"  • {Path(f).name}")
    print("="*70 + "\n")
    
    # 5. Process each file
    for idx, file_path in enumerate(files_to_process, 1):
        print(f"\n{'#'*70}")
        print(f">>> FILE {idx}/{len(files_to_process)}: {file_path}")
        print(f"{'#'*70}")
        
        # Instantiate and run controller
        controller = ScraperController(
            file_path, 
            PORTAL_URL, 
            USERNAME, 
            PASSWORD, 
            target_class=args.student_class
        )
        controller.run()
    
    print(f"\n{'='*70}")
    print("ALL FILES PROCESSED")
    print(f"{'='*70}\n")

if __name__ == "__main__":
    main()
