from datetime import datetime, timedelta
import time
import pandas as pd

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, WebDriverException

from .trip_parser import parse_trip_from_container_and_rating_tab
from src.utils.log_utils import log, log_exception
from src.utils.selenium_utils import (
    wait_for_present,
    wait_for_clickable,
    wait_for_invisible,
    click_button,
)


# ========= CORE ACTIONS =========
def show_more_trips(driver, max_click=6):
    click_count = 0
    for i in range(max_click):
        try:
            # tìm nút xem thêm
            btn = wait_for_clickable(driver, ".load-more.ant-btn-primary", timeout=5)
            if not btn:
                log("Không còn nút 'Xem thêm chuyến'")
                break

            click_button(driver, btn, time_range=2.5)
            click_count += 1
            log(f"Click 'Xem thêm chuyến' thành công ({click_count}/{max_click})")

        except Exception as e:
            log(f"Dừng tại click {i+1}: {type(e).__name__}")
            break

    log(f"SHOW MORE TRIP COMPLETE")


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
                    f"SELECTED: {start_city} ⇨ {dest_city}  | {target_day}-{target_month} COMPLETE"
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
            # Re-fetch lại danh sách button mỗi vòng để tránh stale element
            stars = driver.find_elements(By.CSS_SELECTOR, ".ant-btn.bus-rating-button")
            if i >= len(stars):
                break

            star = stars[i]
            click_button(driver, star)
            log(f"Opened rating tab: {i+1}/{total_rating_btns}")

            # Chờ phần đánh giá hiện ra
            try:
                wait_for_present(driver, ".overall-rating")
            except TimeoutException:
                log(f"⚠️ Timeout waiting for .overall-rating (trip {i+1})")
                continue

            # Lấy HTML một cách an toàn (tránh serialize lỗi)
            try:
                container_html = driver.execute_script(
                    """
                    const el = arguments[0].closest('.bus-item, .container');
                    if (!el) return '';
                    const html = el.outerHTML;
                    return html.length > 60000 ? html.substring(0, 60000) : html;
                """,
                    star,
                )
            except WebDriverException as e:
                log(f"[WARN] Serialize DOM lỗi ở chuyến {i+1}: {str(e)[:80]}...")
                container_html = ""

            # Lấy snapshot toàn trang
            page_html = driver.page_source
            df_trip = parse_trip_from_container_and_rating_tab(
                container_html, page_html
            )

            if not df_trip.empty:
                all_dfs.append(df_trip)
                log(f"Parsed trip: {i+1}")
            else:
                log(f"Không tìm thấy dữ liệu cho chuyến {i+1}")

            # Đóng tab rating
            try:
                click_button(driver, star)
                wait_for_invisible(driver, ".overall-rating", timeout=3)
            except Exception:
                log(f"Không đóng được tab rating: {i+1}")

        except TimeoutException:
            log(f"Timeout ở chuyến {i+1}")
            continue
        except WebDriverException as e:
            log(f"[ERROR] WebDriverException ở chuyến {i+1}: {str(e)[:100]}")
            continue
        except Exception as e:
            log_exception("crawl_and_parse_each_trip", e)
            continue

    if not all_dfs:
        log("Không thu được dữ liệu nào.")
        return pd.DataFrame()

    df_final = pd.concat(all_dfs, ignore_index=True)
    log(f"Hoàn tất crawl {len(all_dfs)} chuyến, tổng {len(df_final)} bản ghi.")
    return df_final
