import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class AuthManager:
    def __init__(self, browser_manager, portal_url):
        self.browser = browser_manager
        self.portal_url = portal_url

    def login(self, username, password):
        """Login to the portal"""
        driver = self.browser.driver
        try:
            print(f"\n→ Navigating to {self.portal_url}")
            driver.get(self.portal_url)
            
            # Wait for login page to load
            print("→ Waiting for login page...")
            time.sleep(3)
            
            print("→ Attempting to log in...")
            
            # Try to find username/email field
            try:
                username_field = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.NAME, "email"))
                )
            except:
                username_field = driver.find_element(By.NAME, "username")
            
            username_field.clear()
            username_field.send_keys(username)
            
            # Find password field
            password_field = driver.find_element(By.NAME, "password")
            password_field.clear()
            password_field.send_keys(password)
            
            # Find and click login button
            login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_button.click()
            
            # Wait for navigation after login
            print("→ Logging in...")
            time.sleep(5)
            
            # Check if login was successful
            if "students" in driver.current_url.lower() or "dashboard" in driver.current_url.lower():
                print("✓ Login successful!")
                return True
            else:
                print("✗ Login may have failed. Please check credentials.")
                return False
                
        except Exception as e:
            print(f"✗ Login error: {str(e)}")
            return False
