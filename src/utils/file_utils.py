import os
import pandas as pd
import json
from typing import List, Tuple


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


import pandas as pd
from pathlib import Path
from datetime import date

# ====== CONFIG ======
BASE_PATH = Path("data")


def get_today_str() -> str:
    return date.today().strftime("%Y-%m-%d")


def save_df(df: pd.DataFrame, stage: str, name: str = "trips") -> Path:
    """
    Lưu DataFrame theo stage: raw / interim / processed
    """
    folder = BASE_PATH / stage
    folder.mkdir(parents=True, exist_ok=True)
    filename = f"{get_today_str()}_{stage}.csv"
    filepath = folder / filename
    df.to_csv(filepath, index=False, encoding="utf-8-sig")
    print(f"Saved to {filepath}")
    return filepath


def read_df(stage: str, name: str = "trips", day: str = None) -> pd.DataFrame:
    """
    Đọc DataFrame theo stage và ngày (mặc định là hôm nay)
    """
    folder = BASE_PATH / stage
    day = day or get_today_str()
    filepath = folder / f"{day}_{stage}.csv"
    df = pd.read_csv(filepath)
    print(f"Loaded {filepath} ({len(df)} rows)")
    return df


def list_files(stage: str) -> list[Path]:
    """
    Liệt kê tất cả file trong một stage (raw/interim/processed)
    """
    folder = BASE_PATH / stage
    return sorted(folder.glob("*.csv"))


def load_routes(file_path: str = "data/routes.json") -> List[Tuple[str, str]]:
    """
    Đọc file routes.json và trả về danh sách cặp (departure, arrival)
    để crawler sử dụng.

    Returns:
        List[Tuple[str, str]]: Danh sách các tuyến (from_city, to_city)
    """
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    routes = data.get("routes", [])
    route_pairs = []

    for route in routes:
        from_city = route.get("from_city")
        to_cities = route.get("to_cities", [])
        for to_city in to_cities:
            route_pairs.append((from_city, to_city))

    print(f"Loaded {len(route_pairs)} routes from {len(routes)} departure cities.")
    return route_pairs
