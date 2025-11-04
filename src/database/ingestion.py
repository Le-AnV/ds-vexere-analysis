import pandas as pd
from typing import Optional
from database.db_manager import DatabaseManager


class DataIngestor:
    """
    Lớp hỗ trợ nạp dữ liệu (ETL Ingestion) từ file hoặc DataFrame
    vào PostgreSQL thông qua DatabaseManager.
    """

    def __init__(self, db_params: Optional[dict] = None):
        """
        Khởi tạo DataIngestor với tham số kết nối database.
        Args:
            db_params (dict): Từ điển chứa thông tin kết nối database.
                Ví dụ:
                {
                    "database": "vexere_db",
                    "user": "postgres",
                    "password": "1234",
                    "host": "localhost",
                    "port": 5432
                }
        """
        self.db_params = db_params or {
            "database": "vexere_db",
            "user": "postgres",
            "password": "1234",
            "host": "localhost",
            "port": 5432,
        }
        self.db = DatabaseManager(**self.db_params)

    # =========================================================
    # 1️⃣ ĐỌC DỮ LIỆU
    # =========================================================
    def load_data(self, file_path: str) -> pd.DataFrame:
        """
        Tự động đọc file CSV hoặc Parquet.
        Returns:
            DataFrame
        """
        print(f"📂 Đang đọc dữ liệu từ: {file_path}")
        if file_path.endswith(".csv"):
            df = pd.read_csv(file_path)
        elif file_path.endswith(".parquet"):
            df = pd.read_parquet(file_path)
        else:
            raise ValueError("❌ Chỉ hỗ trợ .csv hoặc .parquet")
        print(f"✅ Đọc thành công {len(df)} dòng dữ liệu")
        return df

    # =========================================================
    # 2️⃣ INSERT DỮ LIỆU TỪ DATAFRAME
    # =========================================================
    def insert_from_dataframe(self, df: pd.DataFrame):
        """
        Duyệt qua DataFrame và insert từng chuyến xe vào database.
        Tự động gọi các hàm trong DatabaseManager.
        """
        total = len(df)
        success, fail = 0, 0

        print(f"\n🚀 Bắt đầu nạp {total} chuyến xe vào database...\n")

        for idx, row in df.iterrows():
            try:
                company_data = {
                    "company_name": row["company_name"],
                    "rating_overall": row.get("rating_overall"),
                    "reviewer_count": row.get("reviewer_count"),
                    "rating_safety": row.get("rating_safety"),
                    "rating_info_accuracy": row.get("rating_info_accuracy"),
                    "rating_info_completeness": row.get("rating_info_completeness"),
                    "rating_staff_attitude": row.get("rating_staff_attitude"),
                    "rating_comfort": row.get("rating_comfort"),
                    "rating_service_quality": row.get("rating_service_quality"),
                    "rating_punctuality": row.get("rating_punctuality"),
                }

                trip_data = {
                    "departure_date": row["departure_date"],
                    "departure_time": row["departure_time"],
                    "duration_minutes": row.get("duration_minutes", None),
                    "pickup_point": row.get("pickup_point", None),
                    "dropoff_point": row.get("dropoff_point", None),
                    "price_original": row.get("price_original", row.get("price")),
                    "price_discounted": row.get("price_discounted", row.get("price")),
                }

                self.db.insert_complete_trip(
                    start_city=row["start_city"],
                    destination_city=row["destination_city"],
                    company_data=company_data,
                    trip_data=trip_data,
                )
                success += 1

            except Exception as e:
                print(f"⚠️ Lỗi ở dòng {idx}: {e}")
                self.db.conn.rollback()
                fail += 1

        print(f"\n📊 Kết quả nạp dữ liệu:")
        print(f"   ✅ Thành công: {success}")
        print(f"   ❌ Thất bại: {fail}")

    # =========================================================
    # 3️⃣ INSERT TỪ FILE CSV HOẶC PARQUET
    # =========================================================
    def insert_from_file(self, file_path: str):
        """
        Đọc dữ liệu từ file và insert vào database.
        """
        df = self.load_data(file_path)
        self.insert_from_dataframe(df)

    # =========================================================
    # 4️⃣ ĐÓNG KẾT NỐI
    # =========================================================
    def close(self):
        """Đóng kết nối database."""
        self.db.close()


if __name__ == "__main__":
    # Ví dụ chạy độc lập
    ingestor = DataIngestor()
    ingestor.insert_from_file("data/processed/trips_clean.csv")
    ingestor.close()
