import pandas as pd


def normalize_fare_values(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    """
    Chuẩn hoá giá vé về dạng số nguyên (VND).

    Ví dụ:
        "Từ 350.000đ" -> 350000
        "200.000đ"    -> 200000

    Parameters:
        df (pd.DataFrame):DataFrame chứa dữ liệu cần xử lý.
        cols (list[str]): Danh sách 2 cột ['price_original', 'price_discounted'].

    Returns:
        pd.DataFrame: Đã được chuẩn hoá về giá.
    """

    price = df[cols].replace(r"[^0-9]", "", regex=True)
    # fillna = 0 và ép kiểu sang int
    price = price.apply(pd.to_numeric, errors="coerce").fillna(0).astype("Int64")

    df["price_original"] = price.iloc[:, 0]
    df["price_discounted"] = price.iloc[:, 1]

    # Nếu discounted = 0 thì lấy giá original
    df.loc[df["price_discounted"] == 0, "price_discounted"] = df["price_original"]

    return df


def normalize_time_format(df: pd.DataFrame, col: str) -> pd.DataFrame:
    """
    Chuyển đổi cột thời gian từ chuỗi (string) sang kiểu datetime.time.

    Ví dụ:
        "07:30"  ->  "7:30:00"
        "21:05"  ->  "21:05:00"

    Parameters:
        df (pd.DataFrame): DataFrame chứa dữ liệu cần xử lý.
        col_name (str): Tên cột chứa dữ liệu thời gian (ví dụ 'departure_time').

    Returns:
        pd.DataFrame: DataFrame với cột đã được chuyển sang kiểu datetime.time.
    """

    df[col] = pd.to_datetime(df[col], format="%H:%M", errors="coerce").dt.time
    return df


def normalize_date_format(df: pd.DataFrame, col: str) -> pd.DataFrame:
    """
    Chuẩn hóa cột ngày tháng từ chuỗi sang định dạng 'YYYY-MM-DD'.

    Ví dụ:
        "T4, 17/10/2025"  ->  "2025-10-17"

    Parameters:
        df (pd.DataFrame): DataFrame chứa dữ liệu cần xử lý.
        col_name (str): Tên cột chứa dữ liệu ngày tháng (ví dụ 'departure_date').

    Returns:
        pd.DataFrame: DataFrame với cột 'departure_time' đã được chuẩn hóa.
    """

    date = df[col].str.split(", ", expand=True)[1]
    df[col] = pd.to_datetime(date, format="%d/%m/%Y", errors="coerce").dt.strftime(
        "%Y-%m-%d"
    )
    return df


def convert_duration_to_minutes(df: pd.DataFrame, col: str) -> pd.DataFrame:
    """
    Chuẩn hóa cột thời lượng di chuyển sang tổng số phút (int).

    Ví dụ:
        "2h30m" -> 150
        "1h"    -> 60
        "45m"   -> 45

    Parameters:
        df (pd.DataFrame): DataFrame chứa dữ liệu cần xử lý.
        col_name (str): Tên cột chứa thời lượng di chuyển (ví dụ 'duration').

    Returns:
        pd.DataFrame: DataFrame với cột mới 'duration_m' biểu thị tổng số phút di chuyển.
    """

    # Trích xuất phần giờ và phút
    hours = df[col].str.extract(r"(\d+)h")[0].astype("Int64").fillna(0)
    mins = df[col].str.extract(r"(\d+)m")[0].astype("Int64").fillna(0)

    # Tính tổng số phút
    df["duration_minutes"] = hours * 60 + mins
    return df
