from src.extract.crawling import (
    crawl_vexere,
)
from src.transform.cleaning.cleaner_main import clean_vexere
from src.load.trip_loader import insert_trips_from_dataframe

from src.database.db_manager import DatabaseManager
from src.utils.file_utils import read_csv, to_csv, load_routes
import pandas as pd
import time
from datetime import datetime, timedelta
import json

# ==============================================
#                 PARAMETERS
# ===============================================
DAYSOFF = 2
target_date = datetime.today() + timedelta(days=DAYSOFF)
file_name = str(target_date.date()).replace("-", "_")

# database config
with open("src/database/config.json", "r", encoding="utf-8") as f:
    db_config = json.load(f)["DB_CONNECTION"]

# load routes
routes = load_routes("routes.json")

# ===============================================
# STEP 1: CRAWLING
# ===============================================
all_trips_raw = []
for from_city, to_city in routes:
    df = crawl_vexere(start_city=from_city, dest_city=to_city, days=DAYSOFF)
    time.sleep(8)
    all_trips_raw.append(df)

if all_trips_raw:
    df = pd.concat(all_trips_raw, axis=0)
    df.to_csv(f"./data/raw/{file_name}_raw.csv", index=False)
else:
    print("Không có dữ liệu nào được crawl.")
    exit()

# ===============================================
# STEP 2: CLEANING
# ===============================================
df = pd.read_csv(f"./data/raw/{file_name}_raw.csv")
if not df.empty:
    df = clean_vexere(df)
df.to_csv(f"./data/processed/{file_name}_cleaned.csv", index=False)

# ===============================================
# STEP 3: LOADING
# ===============================================
df = pd.read_csv(f"./data/processed/{file_name}_cleaned.csv")

with DatabaseManager(
    database=db_config["DATABASE"],
    user=db_config["USER"],
    password=db_config["PASSWORD"],
) as db:
    insert_trips_from_dataframe(db, df)

print("DONE ✅")
