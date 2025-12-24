import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

class ClassFilterManager:
    def __init__(self, browser_manager):
        self.browser = browser_manager
        self.target_class = None

    def set_class_filter(self, target_class):
        """Set the class filter once after login"""
        self.target_class = target_class
        driver = self.browser.driver
        
        if not self.target_class:
            return False
        
        try:
            print(f"\n→ Setting class filter to: {self.target_class}")
            
            time.sleep(2)
            
            class_dropdown = None
            
            # Strategy 1: By ID
            try:
                class_dropdown = driver.find_element(By.ID, "class")
            except:
                pass
            
            # Strategy 2: By name
            if not class_dropdown:
                try:
                    class_dropdown = driver.find_element(By.NAME, "class")
                except:
                    pass
            
            # Strategy 3: Find select near "CLASS" label
            if not class_dropdown:
                try:
                    selects = driver.find_elements(By.TAG_NAME, "select")
                    for sel in selects:
                        parent_html = sel.find_element(By.XPATH, "./..").get_attribute("innerHTML")
                        if "CLASS" in parent_html.upper():
                            class_dropdown = sel
                            break
                except:
                    pass
            
            # Strategy 4: XPath
            if not class_dropdown:
                try:
                    class_dropdown = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, "//label[contains(text(), 'CLASS')]/following::select[1]"))
                    )
                except:
                    pass
            
            if not class_dropdown:
                print(f"✗ Could not find CLASS dropdown on page\n")
                return False
            
            try:
                select = Select(class_dropdown)
                available_options = [opt.text.strip() for opt in select.options if opt.text.strip()]
                print(f"  Available classes: {available_options}")
                
                # Try exact match
                for option in select.options:
                    if option.text.strip() == self.target_class:
                        select.select_by_visible_text(option.text.strip())
                        print(f"✓ Class filter set to: {option.text.strip()}\n")
                        time.sleep(2)
                        return True
                
                # Try partial match
                for option in select.options:
                    if self.target_class.upper() in option.text.strip().upper():
                        select.select_by_visible_text(option.text.strip())
                        print(f"✓ Class filter set to: {option.text.strip()}\n")
                        time.sleep(2)
                        return True
                
                print(f"✗ Could not find class matching '{self.target_class}' in: {available_options}\n")
                return False
                
            except Exception as e:
                print(f"✗ Error using Select: {e}")
                return False
                
        except Exception as e:
            print(f"⚠ Could not set class filter: {e}\n")
            return False
