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
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def create_driver(headless: bool = True) -> webdriver.Chrome:
    """Tạo Chrome driver tối ưu cho crawl dữ liệu."""
    options = webdriver.ChromeOptions()

    if headless:
        options.add_argument("--headless=new")

    # Tắt tối đa các thành phần không cần thiết
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-background-networking")
    options.add_argument("--disable-default-apps")
    options.add_argument("--blink-settings=imagesEnabled=false")
    options.add_argument("--mute-audio")
    options.add_argument("--js-flags=--max-old-space-size=4096")
    options.add_argument("--disable-blink-features=AutomationControlled")

    # Giảm tải thêm qua preferences
    options.add_experimental_option(
        "prefs",
        {
            "profile.default_content_setting_values": {
                "images": 2,
                "plugins": 2,
                "popups": 2,
                "geolocation": 2,
                "notifications": 2,
                "automatic_downloads": 2,
                "media_stream": 2,
            },
            "profile.managed_default_content_settings.stylesheets": 2,
            "profile.managed_default_content_settings.fonts": 2,
            "profile.managed_default_content_settings.cookies": 1,
        },
    )

    # Khởi tạo driver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_page_load_timeout(30)
    driver.implicitly_wait(5)
    return driver


# ====================================
#           WAIT HELPERS
# ====================================
def wait_for_clickable(driver, selector: str, timeout: int = 15):
    """Chờ phần tử có thể click."""
    wait = WebDriverWait(driver, timeout)
    return wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))


def wait_for_invisible(driver, selector: str, timeout: int = 10):
    """Chờ phần tử biến mất hoặc ẩn đi."""
    wait = WebDriverWait(driver, timeout, poll_frequency=0.3)
    return wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, selector)))


def wait_for_present(driver, selector: str, timeout: int = 10):
    """Chờ phần tử có mặt trong DOM (chưa cần visible)."""
    wait = WebDriverWait(driver, timeout, poll_frequency=0.2)
    return wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))


# ====================================
#           CLICK HELPERS
# ====================================
def click_button(driver, element: WebElement, time_range=0.2):
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)
    time.sleep(time_range)
    driver.execute_script("arguments[0].click();", element)
