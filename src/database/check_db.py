from db_connection import DatabaseManager

import json
import os

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

db_manager = DatabaseManager(
    host=host, port=port, user=user, database=database, password=password
)

query = """INSERT INTO cities(city_name, city_abbr) VALUES(%s, %s)"""
query_1 = """SELECT * FROM cities"""
data = db_manager.fetch(query_1)
db_manager.close()
print(data)
