# pipeline_prefect.py
from prefect import flow, task
import pandas as pd
from datetime import datetime
import os


# ====== TASK 1: CRAWL DATA ======
@task
def crawl_data_task():
    # --- Gọi code crawl của bạn ở đây ---
    # Ví dụ nếu bạn có hàm crawl_data() trong file crawler.py
    from src import crawl_data

    df = crawl_data()  # trả về DataFrame
    os.makedirs("data/raw", exist_ok=True)
    raw_path = f"data/raw/bus_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    df.to_csv(raw_path, index=False)
    print(f"✅ Đã crawl dữ liệu xong: {raw_path}")
    return raw_path


# ====== TASK 2: CLEAN DATA ======
@task
def clean_data_task(raw_path: str):
    from src.data_processing import clean_data

    df = pd.read_csv(raw_path)
    df_clean = clean_data(df)

    os.makedirs("data/processed", exist_ok=True)
    clean_path = (
        f"data/processed/bus_data_clean_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    )
    df_clean.to_csv(clean_path, index=False)
    print(f"✅ Dữ liệu sau khi clean: {clean_path}")
    return clean_path


# ====== FLOW: GỘP TOÀN BỘ ======
@flow(name="Bus Data Pipeline")
def bus_data_pipeline():
    raw_file = crawl_data_task()
    clean_file = clean_data_task(raw_file)
    print("🚀 Pipeline hoàn tất!")
    return clean_file


if __name__ == "__main__":
    bus_data_pipeline()
