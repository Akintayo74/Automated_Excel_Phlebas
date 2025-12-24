from selenium import webdriver
from selenium.webdriver.chrome.options import Options

class BrowserManager:
    def __init__(self):
        self.driver = None

    def setup(self):
        """Initialize Chrome WebDriver with appropriate options"""
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        # Remove headless mode so you can see what's happening
        # chrome_options.add_argument('--headless')
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.maximize_window()
        print("✓ Browser initialized")
        return self.driver

    def close(self):
        """Close browser and cleanup"""
        if self.driver:
            self.driver.quit()
            print("\n✓ Browser closed")
