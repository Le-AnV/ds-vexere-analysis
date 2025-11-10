from .trip_actions import (
    click_search_button,
    crawl_and_parse_each_trip,
    set_search_filters,
    show_more_trips,
)
from src.utils.selenium_utils import create_driver


def crawl_vexere(start_city, dest_city, days=0):
    driver = create_driver(headless=True)
    driver.get("https://vexere.com/")

    set_search_filters(driver, start_city, dest_city, days)
    click_search_button(driver)
    show_more_trips(driver, max_click=2)

    df = crawl_and_parse_each_trip(driver)
    driver.quit()
    return df
