from datetime import datetime

from .trip_actions import (
    click_search_button,
    crawl_and_parse_each_trip,
    set_search_filters,
    show_more_trips,
)
from src.utils.selenium_utils import create_driver


def crawl_vexere(start_city, dest_city, days=0):
    driver = create_driver(headless=False)
    driver.get("https://vexere.com/")

    set_search_filters(driver, start_city, dest_city, days)
    click_search_button(driver)
    show_more_trips(driver, max_click=1)

    df = crawl_and_parse_each_trip(driver)
    driver.quit()
    return df


if __name__ == "__main__":
    start_time = datetime.now()
    print(f"[{start_time.strftime('%H:%M:%S')}] Bắt đầu crawl...\n")

    start_city = "Sài Gòn"
    dest_city = "Nha Trang"
    days = 2

    df = crawl_vexere(start_city, dest_city, days)
    if not df.empty:
        file_name = f"vexere_{start_city}_{dest_city}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
        df.to_csv(file_name, index=False, encoding="utf-8-sig")
        print(f"\n✅ Đã lưu kết quả: {file_name} ({len(df)} dòng)")
    else:
        print("\n Không thu được dữ liệu nào!")

    end = datetime.now()
    print(
        f"\n[{end.strftime('%H:%M:%S')}] Hoàn tất sau {(end - start_time).total_seconds():.1f}s."
    )
