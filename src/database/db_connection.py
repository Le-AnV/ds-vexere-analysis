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


class DatabaseManager:
    def __init__(
        self,
        database,
        user,
        password,
        host="localhost",
        port=5432,
    ):
        # Connect
        self.conn = psycopg2.connect(
            database=database,
            user=user,
            password=password,
            host=host,
            port=port,
        )

        # Cursor for query
        self.cur = self.conn.cursor()

    def execute(self, query, values=None):
        # Thực thi câu lệnh SQL (INSERT, UPDATE, DELETE)
        try:
            self.cur.execute(query, values or ())
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Database execution error: {e}")
            return False

    def fetch(self, query, values=None):
        # Thực thi câu lệnh SQL (SELECT) và trả về kết quả
        try:
            self.cur.execute(query, values or ())
            return self.cur.fetchall()  # Lấy tất cả dữ liệu từ truy vấn
        except Exception as e:
            print(f"Database fetch error: {e}")
            return []

    def close(self):
        # Đóng kết nối cơ sở dữ liệu
        self.cur.close()
        self.conn.close()
        return "Close done"

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Đóng kết nối khi thoát khỏi khối 'with'."""
        if exc_type:  # Nếu có lỗi xảy ra
            if self.conn:
                self.conn.rollback()  # Hoàn tác các thay đổi chưa được commit
            print(f"⚠️ Lỗi xảy ra trong khối 'with', thực hiện rollback.")
        self.close()
