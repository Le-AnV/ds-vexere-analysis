import pandas as pd
from bs4 import BeautifulSoup


def safe_text(elem, default=""):
    return elem.get_text(strip=True) if elem else default


# ============= FARE PARSING LOGIC =============
def is_regular_fare(block) -> bool:
    fare = block.find("div", class_="fare")
    return bool(fare)


def parse_regular_fare(block):
    fare = block.find("div", class_="fare")
    price_original = safe_text(fare)
    return {
        "price_original": price_original,
        "price_discounted": None,
        "percent_discount": None,
    }


def parse_discount_metadata(block):
    fare_small = block.find("div", class_="fareSmall")
    price_original = (
        safe_text(fare_small.find("div", class_="small")) if fare_small else None
    )
    percent_discount = (
        safe_text(fare_small.find("div", class_="percent")) if fare_small else None
    )
    return price_original, percent_discount


def parse_discounted_fare(block):
    price_original, percent_discount = parse_discount_metadata(block)
    fare_sale = block.find("div", class_="fare-sale")
    price_discounted = safe_text(fare_sale)
    return {
        "price_original": price_original,
        "price_discounted": price_discounted,
        "percent_discount": percent_discount,
    }


def parse_fare_element(block):
    return (
        parse_regular_fare(block)
        if is_regular_fare(block)
        else parse_discounted_fare(block)
    )


# ============= TRIP INFO PARSING LOGIC =============
def parse_trip_info(container):
    company_name = safe_text(container.find("div", class_="bus-name"))
    bus_rating = safe_text(container.find("div", class_="bus-rating").find("span"))
    seat_type = safe_text(container.find("div", class_="seat-type"))
    return {
        "company_name": company_name,
        "bus_rating": bus_rating,
        "seat_type": seat_type,
    }


# ============= FILTER INFO (ROUTE) =============
def parse_filter_info(soup):
    try:
        departure_date = safe_text(soup.find("p", class_="date-input-value"))
        start_point = soup.find(id="from_input").get("value", None)
        destination = soup.find(id="to_input").get("value", None)
        return {
            "departure_date": departure_date,
            "start_point": start_point,
            "destination": destination,
        }
    except Exception:
        return {"departure_date": None, "start_point": None, "destination": None}


# ============= DEPARTURE / ARRIVAL =============
def parse_departure_info(from_content):
    if not from_content:
        return {"departure_time": None, "pickup_point": None}
    return {
        "departure_time": safe_text(from_content.find("div", class_="hour")),
        "pickup_point": safe_text(from_content.find("div", class_="place")),
    }


def parse_arrival_info(to_content):
    if not to_content:
        return {"arrival_date": None, "arrival_time": None, "dropoff_point": None}
    content_to_info = to_content.find("div", class_="content-to-info")
    return {
        "arrival_date": safe_text(
            to_content.find("span", class_="text-date-arrival-time")
        ),
        "arrival_time": (
            safe_text(content_to_info.find("div", class_="hour"))
            if content_to_info
            else None
        ),
        "dropoff_point": (
            safe_text(content_to_info.find("div", class_="place"))
            if content_to_info
            else None
        ),
    }


def parse_trip_timing(container):
    from_to_content = container.find("div", class_="from-to-content")
    if not from_to_content:
        return {
            "duration": None,
            "departure_time": None,
            "pickup_point": None,
            "departure_date": None,
            "arrival_date": None,
            "arrival_time": None,
            "dropoff_point": None,
        }
    from_content = from_to_content.find("div", class_="content from")
    to_content = from_to_content.find("div", class_="content to")
    dict_departure = parse_departure_info(from_content)
    dict_arrival = parse_arrival_info(to_content)
    duration = safe_text(from_to_content.find("div", class_="duration"))
    return dict_departure | dict_arrival | {"duration": duration}


# ============= COMPILE TRIP MAIN =============
def compile_trip_info(block):
    return parse_trip_info(block) | parse_trip_timing(block) | parse_fare_element(block)


# ============= RATING PARSING (FROM MODAL) =============
def parse_trip_rating_from_rating_tab(page_soup: BeautifulSoup) -> dict:
    """Parse rating hiển thị trong modal/drawer (sau khi click)."""
    rating_dict = {}

    rate_tab = page_soup.find(class_="detail-rating")
    if not rate_tab:
        # Không có modal rating
        return rating_dict

    for rate in rate_tab.find_all(class_="rate-title"):
        ps = rate.find_all("p")
        if len(ps) < 2:
            continue  # bỏ qua hàng không đủ 2 <p>
        title = ps[0].get_text(strip=True)
        point = ps[1].get_text(strip=True)
        if title and point:
            rating_dict[title] = point

    return rating_dict


def parse_trip_from_container_and_rating_tab(
    container_html: str, page_html: str
) -> pd.DataFrame:
    """Parse 1 chuyến duy nhất (container + modal)."""
    if not container_html or not page_html:
        return pd.DataFrame()

    container_soup = BeautifulSoup(container_html, "html.parser")
    page_soup = BeautifulSoup(page_html, "html.parser")

    dict_route = parse_filter_info(page_soup)
    dict_trip = compile_trip_info(container_soup)
    dict_rating = parse_trip_rating_from_rating_tab(page_soup)

    return pd.DataFrame([dict_trip | dict_route | dict_rating])
