import pandas as pd

from src.utils.log_utils import log
from src.transform.cleaning.bus_info_cleaner import (
    clean_bus_company_name,
    extract_number_of_seats,
)
from src.transform.cleaning.location_cleaner import normalize_location_type
from src.transform.cleaning.rating_cleaner import (
    extract_overall_and_num_reviews,
    rename_rating_title,
    fill_na_rating_cols,
)
from src.transform.cleaning.schedule_price_cleaner import (
    normalize_date_format,
    normalize_fare_values,
    normalize_time_format,
    convert_duration_to_minutes,
)

rating_cols = [
    "rating_safety",
    "rating_info_accuracy",
    "rating_info_completeness",
    "rating_staff_attitude",
    "rating_comfort",
    "rating_service_quality",
    "rating_punctuality",
]


def filter_logic(df: pd.DataFrame) -> pd.DataFrame:
    """Lọc dữ liệu theo quy tắc hợp lý."""
    before = len(df)

    df = df[(df["reviewer_count"] > 0) | (df["price_original"] > 0)]
    df = df[df["price_original"] >= df["price_discounted"]]
    df = df[df["duration_minutes"] > 0]
    df = df[df["number_of_seat"] >= 1]

    log(f"Filtered {before - len(df)} rows based on logic rules")
    return df


def remove_useless_cols(df: pd.DataFrame) -> pd.DataFrame:
    drop_cols = [
        "bus_rating",
        "seat_type",
        "arrival_date",
        "duration",
        "percent_discount",
    ]
    return df.drop(columns=drop_cols, errors="ignore")


def clean_vexere(df: pd.DataFrame, rating_cols=rating_cols) -> pd.DataFrame:
    """Làm sạch dữ liệu Vexere."""

    print("Start cleaning data...")

    # 1. Tách và chuẩn hóa dữ liệu
    df = extract_overall_and_num_reviews(df, "bus_rating")
    df = extract_number_of_seats(df, "seat_type")

    # 2. Chuẩn hóa giá và thời gian
    df = normalize_fare_values(df, ["price_original", "price_discounted"])
    df = normalize_time_format(df, "departure_time")
    df = normalize_date_format(df, "departure_date")
    df = convert_duration_to_minutes(df, "duration")

    # 3. Làm sạch văn bản
    df = clean_bus_company_name(df, "company_name")
    df = normalize_location_type(df, "pickup_point")
    df = normalize_location_type(df, "dropoff_point")
    df = rename_rating_title(df)

    # 4. Lọc và xử lý logic
    df = filter_logic(df)
    df = fill_na_rating_cols(df, rating_cols)

    # 6. Loại bỏ cột thừa
    df = remove_useless_cols(df)

    # 5. Loại bỏ thiếu và trùng
    df.dropna(axis=0, how="any", inplace=True)
    df.drop_duplicates(keep="first", inplace=True)

    log("Clean data set complete")
    return df
