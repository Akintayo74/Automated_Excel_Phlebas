"""
Test Login Script - Use this to verify your credentials work
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def test_login():
    """Test login to the portal"""
    
    # ENTER YOUR CREDENTIALS HERE
    USERNAME = "your_username_here"  # ← CHANGE THIS
    PASSWORD = "your_password_here"  # ← CHANGE THIS
    PORTAL_URL = "https://cdssjos.portal.commandschools.sch.ng/students"
    
    print("\n" + "="*70)
    print("TESTING LOGIN TO SCHOOL PORTAL")
    print("="*70 + "\n")
    
    # Setup Chrome
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    # Browser will be visible so you can see what's happening
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window()
    
    try:
        print(f"→ Opening portal: {PORTAL_URL}")
        driver.get(PORTAL_URL)
        
        print("→ Waiting for login page to load...")
        time.sleep(3)
        
        print(f"→ Current URL: {driver.current_url}")
        
        # Try to find and fill login form
        print("→ Looking for login form...")
        
        try:
            # Try common field names
            try:
                username_field = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.NAME, "email"))
                )
                print("  ✓ Found email field")
            except:
                username_field = driver.find_element(By.NAME, "username")
                print("  ✓ Found username field")
            
            password_field = driver.find_element(By.NAME, "password")
            print("  ✓ Found password field")
            
            # Fill in credentials
            print("→ Entering credentials...")
            username_field.clear()
            username_field.send_keys(USERNAME)
            password_field.clear()
            password_field.send_keys(PASSWORD)
            
            # Find login button
            login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            print("  ✓ Found login button")
            
            # Click login
            print("→ Clicking login button...")
            login_button.click()
            
            # Wait for page to load
            print("→ Waiting for login to complete...")
            time.sleep(5)
            
            # Check result
            current_url = driver.current_url
            print(f"→ Current URL after login: {current_url}")
            
            if "students" in current_url.lower() or "dashboard" in current_url.lower():
                print("\n" + "="*70)
                print("✅ LOGIN SUCCESSFUL!")
                print("="*70)
                print("\nYou can now use the main script: student_portal_scraper.py")
                print("The browser will stay open for 10 seconds so you can verify...")
                time.sleep(10)
            else:
                print("\n" + "="*70)
                print("⚠️  LOGIN MAY HAVE FAILED")
                print("="*70)
                print("\nPossible issues:")
                print("  1. Incorrect username or password")
                print("  2. Portal requires 2FA (Two-Factor Authentication)")
                print("  3. Portal HTML structure is different")
                print("\nThe browser will stay open for 30 seconds.")
                print("Please check if you see any error messages on screen...")
                time.sleep(30)
                
        except Exception as e:
            print(f"\n✗ Error during login: {str(e)}")
            print("\nTroubleshooting steps:")
            print("  1. Check if the portal login page looks correct")
            print("  2. Try logging in manually in this browser window")
            print("  3. The browser will stay open for 30 seconds...")
            time.sleep(30)
            
    except Exception as e:
        print(f"\n✗ Unexpected error: {str(e)}")
        time.sleep(10)
        
    finally:
        print("\n→ Closing browser...")
        driver.quit()
        print("✓ Done!\n")


if __name__ == "__main__":
    print("\n⚠️  IMPORTANT: Make sure you've updated USERNAME and PASSWORD in this file!\n")
    response = input("Have you updated your credentials? (yes/no): ").strip().lower()
    
    if response == "yes" or response == "y":
        test_login()
    else:
        print("\nPlease update the USERNAME and PASSWORD variables in this file first.")
        print("Look for these lines near the top:")
        print('  USERNAME = "your_username_here"')
        print('  PASSWORD = "your_password_here"')
