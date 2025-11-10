import psycopg2
from typing import Optional, Dict, Any


class DatabaseManager:
    """Quản lý kết nối và thao tác với PostgreSQL."""

    def __init__(
        self,
        database: str,
        user: str,
        password: str,
        host: str = "localhost",
        port: int = 5432,
    ):
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
        try:
            self.cur.execute(query, params or ())
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"Execution error: {e}")
            return False

    def fetch_one(self, query: str, params: tuple = None) -> Optional[tuple]:
        try:
            self.cur.execute(query, params or ())
            return self.cur.fetchone()
        except Exception as e:
            print(f"Fetch one error: {e}")
            return None

    def execute_returning_id(self, query: str, params: tuple) -> int:
        try:
            with self.conn.cursor() as cur:
                cur.execute(query, params)
                new_id = cur.fetchone()[0]
                self.conn.commit()
                return new_id
        except Exception as e:
            self.conn.rollback()
            print(f"Error executing RETURNING query: {e}")
            raise

    # ==================== CITIES ====================

    def get_or_insert_city(self, city_name: str) -> int:
        query = "SELECT city_id FROM cities WHERE city_name = %s LIMIT 1"
        result = self.fetch_one(query, (city_name,))
        if result:
            return result[0]

        query_insert = """
            INSERT INTO cities (city_name)
            VALUES (%s)
            RETURNING city_id
        """
        return self.execute_returning_id(query_insert, (city_name,))

    # ==================== ROUTES ====================

    def get_or_insert_route(self, start_city_id: int, dest_city_id: int) -> int:
        query = """
            SELECT route_id FROM routes
            WHERE start_city_id = %s AND destination_city_id = %s
            LIMIT 1
        """
        result = self.fetch_one(query, (start_city_id, dest_city_id))
        if result:
            return result[0]

        query_insert = """
            INSERT INTO routes (start_city_id, destination_city_id)
            VALUES (%s, %s)
            RETURNING route_id
        """
        return self.execute_returning_id(query_insert, (start_city_id, dest_city_id))

    # ==================== BUS COMPANY ====================

    def get_or_upsert_company(self, data: Dict[str, Any]) -> int:
        name = data["company_name"]

        query = "SELECT company_id FROM bus_companies WHERE company_name = %s LIMIT 1"
        result = self.fetch_one(query, (name,))

        params = (
            data["reviewer_count"],
            data["rating_overall"],
            data["rating_safety"],
            data["rating_info_accuracy"],
            data["rating_info_completeness"],
            data["rating_staff_attitude"],
            data["rating_comfort"],
            data["rating_service_quality"],
            data["rating_punctuality"],
        )

        if result:
            company_id = result[0]
            update_q = """
                UPDATE bus_companies
                SET reviewer_count = %s, rating_overall = %s, rating_safety = %s,
                    rating_info_accuracy = %s, rating_info_completeness = %s,
                    rating_staff_attitude = %s, rating_comfort = %s,
                    rating_service_quality = %s, rating_punctuality = %s
                WHERE company_id = %s
            """
            self.execute(update_q, params + (company_id,))
            return company_id

        insert_q = """
            INSERT INTO bus_companies (
                company_name, reviewer_count, rating_overall, rating_safety,
                rating_info_accuracy, rating_info_completeness, rating_staff_attitude,
                rating_comfort, rating_service_quality, rating_punctuality
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            RETURNING company_id
        """
        return self.execute_returning_id(insert_q, (name,) + params)

    def insert_company_route_rating(
        self, company_id: int, route_id: int, data: Dict[str, Any], crawl_date: str
    ) -> bool:
        """Lưu lịch sử rating của công ty theo tuyến và theo ngày"""
        query = """
            INSERT INTO company_route_ratings (
                company_id, route_id, crawl_date, reviewer_count,
                rating_overall, rating_safety, rating_info_accuracy,
                rating_info_completeness, rating_staff_attitude,
                rating_comfort, rating_service_quality, rating_punctuality
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT (company_id, route_id, crawl_date) DO NOTHING
        """
        params = (
            company_id,
            route_id,
            crawl_date,
            data["reviewer_count"],
            data["rating_overall"],
            data["rating_safety"],
            data["rating_info_accuracy"],
            data["rating_info_completeness"],
            data["rating_staff_attitude"],
            data["rating_comfort"],
            data["rating_service_quality"],
            data["rating_punctuality"],
        )
        return self.execute(query, params)

    # ==================== TRIPS ====================

    def insert_trip(self, trip: Dict[str, Any]) -> int:
        query = """
            INSERT INTO trips (
                company_id, route_id, number_of_seat,
                departure_date, departure_time, arrival_time,
                duration_minutes, pickup_point, dropoff_point,
                price_original, price_discounted
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            RETURNING trip_id
        """
        params = (
            trip["company_id"],
            trip["route_id"],
            trip.get("number_of_seat"),
            trip["departure_date"],
            trip["departure_time"],
            trip["arrival_time"],
            trip.get("duration_minutes"),
            trip.get("pickup_point"),
            trip.get("dropoff_point"),
            trip["price_original"],
            trip["price_discounted"],
        )
        return self.execute_returning_id(query, params)

    # ==================== CLEANUP ====================

    def close(self):
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.conn.rollback()
        self.close()
