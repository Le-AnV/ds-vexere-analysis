from db_connection import DatabaseManager
import pandas as pd
import json, os

# ===== 1️⃣ Load cấu hình kết nối DB =====
with open(
    os.path.join(os.path.dirname(__file__), "config.json"), encoding="utf-8"
) as f:
    db_conf = json.load(f)["DB_CONNECTION"]

db_manager = DatabaseManager(
    **{
        "host": db_conf["HOST"],
        "port": db_conf["PORT"],
        "database": db_conf["DATABASE"],
        "user": db_conf["USER"],
        "password": db_conf["PASSWORD"],
    }
)

# ===== 2️⃣ Đọc toàn bộ dữ liệu =====
df = pd.read_csv("data/clean/vexere_db.csv", keep_default_na=False, na_values=[])


# ===== 3️⃣ Hàm xử lý từng dòng dữ liệu =====
def process_row(row):
    company_data = {
        k.replace("company_", "bus_"): getattr(row, k)
        for k in df.columns
        if k.startswith("company_") or k.startswith("rating_")
    }
    trip_data = {
        k: getattr(row, k)
        for k in [
            "number_of_seat" "departure_date",
            "departure_time",
            "duration_minutes",
            "pickup_point",
            "dropoff_point",
            "price_original",
            "price_discounted",
        ]
    }
    return company_data, trip_data


# ===== 4️⃣ Ingest dữ liệu =====
for i, row in enumerate(df.itertuples(index=False), start=1):
    try:
        company_data, trip_data = process_row(row)
        trip_id = db_manager.insert_complete_trip(
            start_city=row.start_point,
            destination_city=row.destination,
            company_data=company_data,
            trip_data=trip_data,
        )
        print(
            f"✅ ({i}) Đã insert trip ID {trip_id}: {row.start_point} → {row.destination}"
        )
        if i % 50 == 0:
            print(f"--- Đã xử lý {i} chuyến xe ---")
    except Exception as e:
        print(f"❌ Lỗi ở dòng {i}: {e}")
