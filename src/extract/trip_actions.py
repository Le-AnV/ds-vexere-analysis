from datetime import datetime, timedelta
import time
import pandas as pd

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

from .trip_parser import parse_trip_from_container_and_rating_tab
from src.utils.log_utils import log, log_exception
from src.utils.selenium_utils import (
    wait_for_present,
    wait_for_clickable,
    click_button,
)


# ========= CORE ACTIONS =========
def show_more_trips(driver, max_click=5):

    for i in range(max_click):
        try:
            elem = driver.find_element(By.CSS_SELECTOR, ".load-more.ant-btn-primary")
            if not elem:
                log("Không tìm thấy button `Xem thêm chuyến`")
                break

            # Sử dụng wait để đợi btn hiển thị (có thể để click)
            btn = wait_for_clickable(driver, ".load-more.ant-btn-primary")
            click_button(driver, btn)
            log(f"Đã click button 'Xem thêm chuyến': ({i+1}/{max_click})")
            time.sleep(0.8)
        except Exception as e:
            log_exception("show_more_trips", e)
            break
    log("SHOW MORE TRIP COMPLETE")


def click_search_button(driver):
    """Click vào button tìm kiếm sau quá trình fill start_point, destination, departure_date"""
    try:
        btn = driver.find_element(By.CSS_SELECTOR, ".button-search")
        click_button(driver, btn)
        log("Click `search` DONE")
        return True

    except Exception as e:
        log_exception("click_search_button", e)
    return False


def get_target_date_components(days_offset=0):
    target_date = datetime.today() + timedelta(days=days_offset)

    return {
        "day": str(target_date.day),
        "month_year": f"{target_date.month:02d}-{target_date.year}",
    }


def set_search_filters(driver, start_city, dest_city, days_offset=0):

    try:
        departure_input = wait_for_present(
            driver, "#from_input"
        )  # Đợi ô nhập dữ liệu xuất hiện
        destination_input = driver.find_element(By.CSS_SELECTOR, "#to_input")

        # Làm sạch phần text box
        departure_input.clear()
        destination_input.clear()

        # Truyền dữ liệu vào
        departure_input.send_keys(start_city)
        destination_input.send_keys(dest_city)

        date_btn = driver.find_element(By.CLASS_NAME, "departure-date-select")
        date_btn.click()

        target = get_target_date_components(days_offset)
        target_day, target_month = target["day"], target["month_year"]

        month_section = driver.find_element(By.ID, target_month)

        for day in month_section.find_elements(By.CSS_SELECTOR, "p.day"):
            if day.text.strip() == target_day:
                click_button(driver, day)
                log(
                    f"SELECTED: {start_city} ⇾ {dest_city}  | {target_day}-{target_month} COMPLETE"
                )
                return True

        log("NOT FOUND SELECTED DAY")
        return False

    except Exception as e:
        log_exception("set_search_filters", e)
        return False


# ========= MAIN PARSE FLOW =========
def crawl_and_parse_each_trip(driver):

    stars = driver.find_elements(By.CSS_SELECTOR, ".ant-btn.bus-rating-button")
    total_rating_btns = len(stars)
    log(f"Total ratings button: {total_rating_btns}")

    all_dfs = []

    for i in range(total_rating_btns):
        try:
            stars = driver.find_elements(By.CSS_SELECTOR, ".ant-btn.bus-rating-button")

            if i >= len(stars):
                break

            star = stars[i]
            click_button(driver, star)
            log(f"Opened rating tab: {i+1}/{total_rating_btns}")

            # Khi mở tab rating ra sẽ xuất hiện class `overall-rating` => Đợi trang load
            wait_for_present(driver, ".overall-rating")

            container_html = driver.execute_script(
                "return arguments[0].closest('.bus-item, .container')?.outerHTML;", star
            )
            page_html = driver.page_source  # Lấy html về để parse dữ liệu
            df_trip = parse_trip_from_container_and_rating_tab(
                container_html, page_html
            )

            if not df_trip.empty:
                all_dfs.append(df_trip)
                log(f"Parsed trip: {i+1}")
            else:
                log(f"Không tìm thấy dữ liệu cho chuyến {i+1}")

            # Đóng tab rating sau khi đã parse
            try:
                click_button(driver, star)
                WebDriverWait(driver, 15).until_not(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".overall-rating"))
                )
            except Exception:
                log(f"Không đóng được tab rating: {i+1}")

        except TimeoutException:
            log("TimeoutException")
        except Exception as e:
            log_exception("crawl_and_parse_each_trip", e)
            continue

    if not all_dfs:
        log("❌ Không thu được dữ liệu nào.")
        return pd.DataFrame()

    df_final = pd.concat(all_dfs, ignore_index=True)
    log(f"Hoàn tất crawl {len(all_dfs)} chuyến, tổng {len(df_final)} bản ghi.")
    return df_final
