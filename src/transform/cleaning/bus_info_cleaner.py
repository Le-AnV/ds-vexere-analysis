import pandas as pd


def extract_number_of_seats(df: pd.DataFrame, col: str) -> pd.DataFrame:
    """
    Trích xuất số lượng ghế từ cột 'seat_type' và tạo cột mới 'number_of_seat'.

    Ví dụ:
        "Xe giường nằm 40 chỗ"  ->  40
        "Ghế ngồi 29 chỗ"       ->  29

    Parameters:
        df (pd.DataFrame): DataFrame chứa dữ liệu cần xử lý.

    Returns:
        pd.DataFrame: DataFrame đã được thêm cột 'number_of_seat'.
    """

    df["number_of_seat"] = df[col].replace(
        r"[^0-9]", "", regex=True
    )  # Chỉ giữ lại các chữ số
    df["number_of_seat"] = pd.to_numeric(df["number_of_seat"], errors="coerce").astype(
        "Int64"
    )

    return df


def clean_bus_company_name(df: pd.DataFrame, col: str) -> pd.DataFrame:
    """
    Chuẩn hóa tên nhà xe bằng cách loại bỏ phần trong ngoặc.

    Ví dụ:
        "Hoàng Long (Ghế ngồi)" -> "Hoàng Long"

    Parameters:
        df (pd.DataFrame): DataFrame chứa dữ liệu cần xử lý.

    Returns:
        pd.DataFrame: DataFrame với cột 'bus_name' đã được làm sạch.
    """

    df[col].replace(r"\s*\([^)]+\)", "", regex=True, inplace=True)
    return df
