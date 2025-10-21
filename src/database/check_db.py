from db_connection import DatabaseManager
import json
import os


# ===== Lấy dữ liệu connect DB từ json ======
current_dir = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(current_dir, "config.json")

with open(json_path, "r", encoding="utf-8") as f:
    config = json.load(f)

DATABASE = config["DB_CONNECTION"]
host = DATABASE["HOST"]
port = DATABASE["PORT"]
database = DATABASE["DATABASE"]
user = DATABASE["USER"]
password = DATABASE["PASSWORD"]

# ====== Khỏi tạo Database ======
db_manager = DatabaseManager(
    host=host, port=port, user=user, database=database, password=password
)

query = """SELECT city_id FROM cities WHERE city_name = %s OR city_abbr = %s"""


id_departure = db_manager.get_or_insert_route(
    db_manager.execute_and_get_id(query, ("Sài Gòn", None)),
    db_manager.execute_and_get_id(query, ("Phú Yên", None)),
)
print(id_departure)
