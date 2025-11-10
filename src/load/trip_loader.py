import pandas as pd
from typing import Any, Dict
from datetime import date
from src.database.db_manager import DatabaseManager


def insert_trips_from_dataframe(db: DatabaseManager, df: pd.DataFrame):
    """Duyệt DataFrame và insert toàn bộ dữ liệu chuyến xe + lưu lịch sử rating."""
    crawl_date = str(date.today())

    for idx, row in df.iterrows():
        try:
            # Company info
            company_data: Dict[str, Any] = {
                "company_name": row["company_name"],
                "reviewer_count": row["reviewer_count"],
                "rating_overall": row["rating_overall"],
                "rating_safety": row["rating_safety"],
                "rating_info_accuracy": row["rating_info_accuracy"],
                "rating_info_completeness": row["rating_info_completeness"],
                "rating_staff_attitude": row["rating_staff_attitude"],
                "rating_comfort": row["rating_comfort"],
                "rating_service_quality": row["rating_service_quality"],
                "rating_punctuality": row["rating_punctuality"],
            }

            # Trip info
            trip_data: Dict[str, Any] = {
                "departure_date": row["departure_date"],
                "departure_time": row["departure_time"],
                "arrival_time": row["arrival_time"],
                "price_original": row["price_original"],
                "price_discounted": row["price_discounted"],
                "pickup_point": row.get("pickup_point"),
                "dropoff_point": row.get("dropoff_point"),
                "number_of_seat": row.get("number_of_seat"),
                "duration_minutes": row.get("duration_minutes"),
            }

            # Cities and routes
            start_city = row["start_point"]
            dest_city = row["destination"]
            start_city_id = db.get_or_insert_city(start_city)
            dest_city_id = db.get_or_insert_city(dest_city)
            route_id = db.get_or_insert_route(start_city_id, dest_city_id)
            company_id = db.get_or_upsert_company(company_data)

            # Save rating history (theo tuyến)
            db.insert_company_route_rating(
                company_id, route_id, company_data, crawl_date
            )

            # Insert trip
            trip_data["company_id"] = company_id
            trip_data["route_id"] = route_id
            db.insert_trip(trip_data)

        except Exception as e:
            db.conn.rollback()
            print(f"Error inserting row {idx}: {e}")
