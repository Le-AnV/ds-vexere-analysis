import psycopg2
import pandas as pd

from typing import Optional, Dict, Tuple, Any


class DatabaseManager:
    """Quản lý kết nối và thao tác với PostgreSQL database."""

    def __init__(
        self,
        database: str,
        user: str,
        password: str,
        host: str = "localhost",
        port: int = 5432,
    ):
        """Khởi tạo kết nối database."""
        self.conn = psycopg2.connect(
            database=database,
            user=user,
            password=password,
            host=host,
            port=port,
        )
        self.cur = self.conn.cursor()

    # ==================== CÁC HÀM CƠ BẢN ====================

    def execute(self, query: str, params: tuple = None) -> bool:
        """Thực thi câu lệnh SQL (INSERT, UPDATE, DELETE)."""
        try:
            self.cur.execute(query, params or ())
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"❌ Lỗi thực thi: {e}")
            return False

    def fetch_all(self, query: str, params: tuple = None) -> list:
        """Lấy tất cả kết quả từ câu truy vấn SELECT."""
        try:
            self.cur.execute(query, params or ())
            return self.cur.fetchall()
        except Exception as e:
            print(f"❌ Lỗi fetch: {e}")
            return []

    def fetch_one(self, query: str, params: tuple = None) -> Optional[tuple]:
        """Lấy 1 kết quả từ câu truy vấn SELECT."""
        try:
            self.cur.execute(query, params or ())
            return self.cur.fetchone()
        except Exception as e:
            print(f"❌ Lỗi fetch_one: {e}")
            return None

    def execute_returning_id(self, query, params):
        try:
            with self.conn.cursor() as cur:
                cur.execute(query, params)
                new_id = cur.fetchone()[0]
                self.conn.commit()
                return new_id
        except Exception as e:
            print(f"❌ Lỗi execute_returning_id: {e}")
            self.conn.rollback()
            raise

    # ==================== BƯỚC 1: QUẢN LÝ CITIES ====================

    def get_or_insert_city(self, city_name: str, city_abbr: str = None) -> int:
        """
        Tìm city_id theo tên. Nếu chưa có thì insert mới.

        Returns:
            city_id (int)
        """
        # Tìm kiếm
        query_select = "SELECT city_id FROM cities WHERE city_name = %s LIMIT 1"
        result = self.fetch_one(query_select, (city_name,))

        if result:
            return result[0]

        # Insert mới
        query_insert = """
            INSERT INTO cities (city_name, city_abbr)
            VALUES (%s, %s)
            RETURNING city_id
        """
        city_id = self.execute_returning_id(query_insert, (city_name, city_abbr))
        print(f"✅ Thêm mới city: {city_name} (ID: {city_id})")
        return city_id

    # ==================== BƯỚC 2: QUẢN LÝ ROUTES ====================

    def get_or_insert_route(self, start_city_id: int, destination_city_id: int) -> int:
        """
        Tìm route_id theo start và destination city. Nếu chưa có thì insert mới.

        Returns:
            route_id (int)
        """
        # Tìm kiếm
        query_select = """
            SELECT route_id FROM routes
            WHERE start_city_id = %s AND destination_city_id = %s
            LIMIT 1
        """
        result = self.fetch_one(query_select, (start_city_id, destination_city_id))

        if result:
            return result[0]

        # Insert mới
        query_insert = """
            INSERT INTO routes (start_city_id, destination_city_id)
            VALUES (%s, %s)
            RETURNING route_id
        """
        route_id = self.execute_returning_id(
            query_insert, (start_city_id, destination_city_id)
        )
        print(
            f"✅ Thêm mới route: {start_city_id} → {destination_city_id} (ID: {route_id})"
        )
        return route_id

    # ==================== BƯỚC 3: QUẢN LÝ BUS COMPANIES ====================

    def get_or_upsert_company(self, company_data: Dict[str, Any]) -> int:
        """
        Tìm bus_company theo tên:
        - Nếu tồn tại: UPDATE rating
        - Nếu chưa có: INSERT mới

        Args:
            company_data: Dict chứa các key:
                - bus_name (str)
                - reviewer_count (int)
                - overall_rating (float)
                - rating_safety (float)
                - rating_info_accuracy (float)
                - rating_info_completeness (float)
                - rating_staff_attitude (float)
                - rating_comfort (float)
                - rating_service_quality (float)
                - rating_punctuality (float)

        Returns:
            bus_company_id (int)
        """
        bus_name = company_data["bus_name"]

        # Tìm kiếm
        query_select = """
            SELECT company_id FROM bus_companies
            WHERE company_name = %s
            LIMIT 1
        """
        result = self.fetch_one(query_select, (bus_name,))

        rating_params = (
            company_data["reviewer_count"],
            company_data["rating_overall"],
            company_data["rating_safety"],
            company_data["rating_info_accuracy"],
            company_data["rating_info_completeness"],
            company_data["rating_staff_attitude"],
            company_data["rating_comfort"],
            company_data["rating_service_quality"],
            company_data["rating_punctuality"],
        )

        if result:
            # UPDATE rating
            company_id = result[0]
            query_update = """
                UPDATE bus_companies SET
                    reviewer_count = %s,
                    rating_overall = %s,
                    rating_safety = %s,
                    rating_info_accuracy = %s,
                    rating_info_completeness = %s,
                    rating_staff_attitude = %s,
                    rating_comfort = %s,
                    rating_service_quality = %s,
                    rating_punctuality = %s
                WHERE company_id = %s
            """
            self.execute(query_update, rating_params + (company_id,))
            print(f"🔄 Cập nhật rating cho: {bus_name} (ID: {company_id})")
            return company_id

        else:
            # INSERT mới
            query_insert = """
                INSERT INTO bus_companies (
                    company_name,
                    reviewer_count,
                    rating_overall,
                    rating_safety,
                    rating_info_accuracy,
                    rating_info_completeness,
                    rating_staff_attitude,
                    rating_comfort,
                    rating_service_quality,
                    rating_punctuality
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING company_id
            """
            company_id = self.execute_returning_id(
                query_insert, (bus_name,) + rating_params
            )
            print(f"✅ Thêm mới company: {bus_name} (ID: {company_id})")
            return company_id

    # ==================== BƯỚC 4: INSERT TRIP ====================

    def insert_trip(self, trip_data: Dict[str, Any]) -> int:
        """
        Insert một chuyến xe mới vào bảng trips.

        Args:
            trip_data: Dict chứa thông tin chuyến xe:
                - bus_company_id (int)
                - route_id (int)
                - departure_time (str hoặc datetime)
                - arrival_time (str hoặc datetime)
                - price (float)
                - seat_type (str, optional)
                - available_seats (int, optional)
                ... (các trường khác tùy schema)

        Returns:
            trip_id (int)
        """
        query = """
        INSERT INTO trips (
            company_id,
            route_id,
            departure_date,
            departure_time,
            duration_minutes,
            pickup_point,
            dropoff_point,
            price_original,
            price_discounted
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING trip_id
    """
        params = (
            trip_data["company_id"],
            trip_data["route_id"],
            trip_data["departure_date"],
            trip_data["departure_time"],
            trip_data["duration_minutes"],
            trip_data.get("pickup_point"),
            trip_data.get("dropoff_point"),
            trip_data["price_original"],
            trip_data["price_discounted"],
        )

        trip_id = self.execute_returning_id(query, params)
        print(f"✅ Thêm mới trip (ID: {trip_id})")
        return trip_id

    # ==================== WORKFLOW HOÀN CHỈNH ====================

    def insert_complete_trip(
        self,
        start_city: str,
        destination_city: str,
        company_data: Dict[str, Any],
        trip_data: Dict[str, Any],
        start_city_abbr: str = None,
        dest_city_abbr: str = None,
    ) -> int:
        """
        Workflow hoàn chỉnh để insert 1 chuyến xe:

        1. Get/Insert start_city → start_city_id
        2. Get/Insert destination_city → destination_city_id
        3. Get/Insert route → route_id
        4. Get/Upsert bus_company → bus_company_id
        5. Insert trip

        Returns:
            trip_id (int)
        """
        print(f"\n{'='*60}")
        print(f"🚌 Bắt đầu insert chuyến: {start_city} → {destination_city}")
        print(f"{'='*60}")

        # Bước 1 & 2: Cities
        start_city_id = self.get_or_insert_city(start_city, start_city_abbr)
        dest_city_id = self.get_or_insert_city(destination_city, dest_city_abbr)

        # Bước 3: Route
        route_id = self.get_or_insert_route(start_city_id, dest_city_id)

        # Bước 4: Bus Company
        company_id = self.get_or_upsert_company(company_data)

        # Bước 5: Trip
        trip_data["company_id"] = company_id
        trip_data["route_id"] = route_id
        trip_id = self.insert_trip(trip_data)

        print(f"{'='*60}")
        print(f"✅ HOÀN THÀNH! Trip ID: {trip_id}")
        print(f"{'='*60}\n")

        return trip_id

    # ==================== ĐÓNG KẾT NỐI ====================

    def close(self):
        """Đóng cursor và connection."""
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()
        print("🔒 Đã đóng kết nối database")

    def __enter__(self):
        """Hỗ trợ context manager (with statement)."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Tự động đóng kết nối khi thoát khỏi with block."""
        if exc_type:
            self.conn.rollback()
            print(f"⚠️ Có lỗi xảy ra, đã rollback")
        self.close()

    import pandas as pd


def insert_trips_from_dataframe(self, df: pd.DataFrame):
    """
    Insert toàn bộ chuyến xe từ DataFrame vào database.

    Yêu cầu: DataFrame phải có các cột:
        start_city, destination_city, bus_name,
        overall_rating, reviewer_count, rating_service,
        rating_comfort, rating_punctuality, rating_staff_attitude,
        rating_safety, rating_info_accuracy,
        departure_time, arrival_time, price
    """

    for idx, row in df.iterrows():
        try:
            company_data = {
                "bus_name": row["bus_name"],
                "overall_rating": row["overall_rating"],
                "reviewer_count": row["reviewer_count"],
                "rating_service": row["rating_service"],
                "rating_comfort": row["rating_comfort"],
                "rating_punctuality": row["rating_punctuality"],
                "rating_staff_attitude": row["rating_staff_attitude"],
                "rating_safety": row["rating_safety"],
                "rating_info_accuracy": row["rating_info_accuracy"],
            }

            trip_data = {
                "departure_time": row["departure_time"],
                "arrival_time": row["arrival_time"],
                "price": row["price"],
            }

            # Gọi workflow hoàn chỉnh
            self.insert_complete_trip(
                start_city=row["start_city"],
                destination_city=row["destination_city"],
                company_data=company_data,
                trip_data=trip_data,
            )

        except Exception as e:
            print(f"⚠️ Lỗi ở dòng {idx}: {e}")
            self.conn.rollback()
