import os
import pandas as pd


def to_csv(data: pd.DataFrame, file_path: str):
    """Lưu DataFrame thành file CSV."""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    data.to_csv(file_path, index=False, encoding="utf-8")
    print(f"- Đã lưu dữ liệu vào {file_path}")


def read_csv(file_path: str) -> pd.DataFrame:
    """Đọc file CSV thành DataFrame."""
    if not os.path.exists(file_path):
        print(f"- File {file_path} không tồn tại.")
        return pd.DataFrame()

    data = pd.read_csv(file_path, encoding="utf-8")
    print(f"- Đã đọc dữ liệu từ {file_path}")
    return data
