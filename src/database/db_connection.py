import psycopg2
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


def connect_db():
    conn = None
    try:
        conn = psycopg2.connect(
            host=host,
            database=database,
            port=port,
            user=user,
            password=password,
        )
        print("Database connection successful.")
    except psycopg2.Error as e:
        print(f"Error connecting to the database: {e}")
    return conn


def close_db(conn):
    if conn:
        conn.close()
        print("Database connection closed.")


def execute(conn, query, values=None):
    try:
        with conn.cursor() as cur:
            cur.execute(query, values or ())
            conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"Database execution error: {e}")
        return False


def fetch(conn, query, values=None):
    try:
        with conn.cursor() as cur:
            cur.execute(query, values or ())
            return cur.fetchall()
    except Exception as e:
        print(f"Database fetch error: {e}")
        return []
