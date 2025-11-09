import pandas as pd


def normalize_location_type(df: pd.DataFrame, col: str) -> pd.DataFrame:
    """
    Chuẩn hóa loại địa điểm (ví dụ: 'Bến xe', 'Văn phòng', 'Other')
    trong cột chỉ định của DataFrame bằng cách mở rộng các từ viết tắt thông dụng.

    Parameters:
        df (pd.DataFrame): DataFrame chứa dữ liệu cần xử lý.
        col_name (str): Tên cột chứa dữ liệu văn bản cần chuẩn hóa
                        (ví dụ: 'pick_up_point' hoặc 'drop_off_point').

    Returns:
        pd.DataFrame: DataFrame với cột đã được chuẩn hóa loại địa điểm.
    """
    df[col] = (
        df[col]
        .str.lower()
        .apply(
            lambda x: (
                "Bến xe"
                if "bx" in x or "bến xe" in x
                else "Văn phòng" if "vp" in x or "văn phòng" in x else "Other"
            )
        )
    )

    return df
