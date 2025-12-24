from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class PortalRepository:
    def __init__(self, browser_manager, portal_url):
        self.browser = browser_manager
        self.portal_url = portal_url

    def search_students(self, name):
        """Search for a student and return list of potential matches"""
        driver = self.browser.driver
        results = []
        
        try:
            if "students" not in driver.current_url.lower():
                driver.get(self.portal_url)
                time.sleep(2)

            search_box = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='text']"))
            )
            search_box.clear()
            search_box.send_keys(name)
            time.sleep(2.5) # Increased wait for portal to refresh results

            rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
            
            for row in rows:
                try:
                    # Verify this is a data row
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if len(cells) < 3: 
                        continue

                    admission_number = cells[0].text.strip()
                    first_name_portal = cells[1].text.strip().upper()
                    last_name_portal = cells[2].text.strip().upper()
                    
                    portal_display = f"{first_name_portal} {last_name_portal}"
                    
                    results.append({
                        'admission': admission_number,
                        'name': portal_display
                    })

                except Exception as row_err:
                    continue
            
            return results

        except Exception as e:
            print(f" ✗ Search error: {str(e)}")
            return []
