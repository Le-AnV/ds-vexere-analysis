from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.remote.webelement import WebElement
import time


# ====================================
#           DRIVER SETUP
# ====================================
def create_driver(headless: bool = True) -> webdriver.Chrome:
    """Tạo Chrome driver với cấu hình tối ưu."""
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_experimental_option(
        "prefs", {"profile.default_content_setting_values.images": 2}
    )
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver


# ====================================
#           WAIT HELPERS
# ====================================
def wait_for_clickable(driver, selector: str, timeout: int = 10):
    """Chờ phần tử có thể click."""
    wait = WebDriverWait(driver, timeout)
    return wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))


def wait_for_visible(driver, selector: str, timeout: int = 10):
    """Chờ phần tử hiển thị (visible)."""
    wait = WebDriverWait(driver, timeout)
    return wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, selector)))


def wait_for_present(driver, selector: str, timeout: int = 10):
    """Chờ phần tử có mặt trong DOM (chưa cần visible)."""
    wait = WebDriverWait(driver, timeout)
    return wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))


# ====================================
#           CLICK HELPERS
# ====================================
def click_button(driver, element: WebElement):
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)
    driver.execute_script("arguments[0].click();", element)
