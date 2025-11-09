import pandas as pd


def extract_overall_and_num_reviews(df: pd.DataFrame, col: str) -> pd.DataFrame:
    """
    Tách điểm trung bình và số lượt đánh giá từ cột 'bus_rating'.

    Ví dụ:
        "4.7 (123)" -> rating_overall=4.7, reviewer_count=123

    Parameters:
        df (pd.DataFrame): DataFrame chứa dữ liệu cần xử lý.
        col_name (str): Tên cột chứa dữ liệu đánh giá, ví dụ 'bus_rating'.

    Returns:
        pd.DataFrame: Thêm 2 cột 'rating_overall' và 'reviewer_count'.
    """
    split_cols = df[col].str.split(" ", expand=True)
    df["rating_overall"] = pd.to_numeric(split_cols[0], errors="coerce")

    df["reviewer_count"] = split_cols[1].replace(r"[()]", "", regex=True).astype(int)
    return df


def rename_rating_title(df: pd.DataFrame) -> pd.DataFrame:
    RENAME_RATING_COLS = {
        # ratings
        "An toàn": "rating_safety",
        "Thông tin chính xác": "rating_info_accuracy",
        "Thông tin đầy đủ": "rating_info_completeness",
        "Thái độ nhân viên": "rating_staff_attitude",
        "Tiện nghi & thoải mái": "rating_comfort",
        "Chất lượng dịch vụ": "rating_service_quanlity",
        "Đúng giờ": "rating_punctuality",
    }

    return df.rename(columns=RENAME_RATING_COLS)
