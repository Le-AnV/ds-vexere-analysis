import psycopg2

# import json
# import os

# current_dir = os.path.dirname(os.path.abspath(__file__))
# json_path = os.path.join(current_dir, "config.json")

# with open(json_path, "r", encoding="utf-8") as f:
#     config = json.load(f)

# DATABASE = config["DB_CONNECTION"]
# host = DATABASE["HOST"]
# port = DATABASE["PORT"]
# database = DATABASE["DATABASE"]
# user = DATABASE["USER"]
# password = DATABASE["PASSWORD"]


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

    def fetch_one(self, query, values=None):
        # Thực thi câu lệnh SQL (SELECT) và trả về kết quả
        try:
            self.cur.execute(query, values or ())
            return self.cur.fetchone()  # Lấy tất cả dữ liệu từ truy vấn
        except Exception as e:
            print(f"Database fetch error: {e}")
            return []

    def get_or_insert_city(self, city_name, city_abbr=None):
        """
        Tìm city_id dựa trên city_name. Nếu không tồn tại, chèn mới và trả về ID.

        city_name (str): Tên thành phố (ví dụ: 'Sài Gòn').
        city_abbr (str | None): Tên viết tắt (ví dụ: 'SG').

        Trả về: city_id (INTEGER).
        """

        # 1. TÌM KIẾM
        select_query = """
            SELECT city_id FROM cities
            WHERE city_name = %s
            LIMIT 1;
        """
        existing = self.fetch_one(select_query, (city_name,))

        if existing:
            # Nếu đã tồn tại, trả về ID
            return existing[0]

        # 2. CHÈN MỚI
        insert_query = """
            INSERT INTO cities (city_name, city_abbr)
            VALUES (%s, %s)
            RETURNING city_id;
        """
        # Giả định self.execute_and_get_id chạy lệnh INSERT và dùng RETURNING để lấy ID
        new_city_id = self.execute_and_get_id(insert_query, (city_name, city_abbr))

        print(f"Đã chèn thành phố mới: {city_name} (ID: {new_city_id})")
        return new_city_id

    def execute_and_get_id(self, query: str, params: tuple = None) -> int:
        """
        Thực thi lệnh INSERT có chứa mệnh đề RETURNING [id_column_name].
        Trả về ID (INTEGER) của bản ghi vừa được chèn.
        """
        if self.conn is None:
            raise Exception("Chưa có kết nối Database.")

        new_id = None

        try:
            with self.conn.cursor() as cursor:
                # 1. Thực thi truy vấn
                cursor.execute(query, params)

                # 2. Lấy ID từ mệnh đề RETURNING
                # fetchone() sẽ trả về hàng đầu tiên của kết quả (ví dụ: (101,))
                result = cursor.fetchone()

                if result:
                    new_id = result[0]

                # 3. Commit thay đổi vào database
                self.conn.commit()

        except psycopg2.Error as e:
            # Rollback nếu có lỗi
            self.conn.rollback()
            print(f"Lỗi SQL khi thực thi và lấy ID: {e}")
            raise

        if new_id is None:
            raise Exception(f"Không lấy được ID sau khi thực thi truy vấn: {query}")

        return new_id

    def get_or_insert_route(self, start_city_id, destination_city_id):
        """
        Tìm route_id dựa trên cặp start_city_id và destination_city_id.
        Nếu không tồn tại, chèn mới và trả về ID.
        """

        # 1. TÌM KIẾM
        select_query = """
            SELECT route_id FROM routes
            WHERE start_city_id = %s AND destination_city_id = %s
            LIMIT 1;
        """
        existing = self.fetch_one(select_query, (start_city_id, destination_city_id))

        if existing:
            # Nếu đã tồn tại, trả về ID
            return existing[0]

        # 2. CHÈN MỚI
        insert_query = """
            INSERT INTO routes (start_city_id, destination_city_id)
            VALUES (%s, %s)
            RETURNING route_id;
        """
        new_route_id = self.execute_and_get_id(
            insert_query, (start_city_id, destination_city_id)
        )

        print(
            f"Đã chèn tuyến đường mới: {start_city_id} -> {destination_city_id} (ID: {new_route_id})"
        )
        return new_route_id

    def get_or_update_company(self, company_data: dict):
        """
        Tìm công ty xe buýt theo tên. Nếu tồn tại, cập nhật rating. Nếu không, chèn mới.
        Luôn trả về bus_company_id.

        company_data (dict): Dictionary chứa dữ liệu công ty, bao gồm:
            'bus_name', 'overall_rating', 'reviewer_count',
            'rating_service', 'rating_comfort', 'rating_punctuality',
            'rating_staff_attitude', 'rating_safety', 'rating_info_accuracy'
        """

        bus_name = company_data["bus_name"]

        # 1. TÌM KIẾM CÔNG TY BẰNG TÊN
        select_query = """
            SELECT bus_company_id FROM bus_companies
            WHERE bus_company_name = %s
            LIMIT 1;
        """
        existing_company = self.fetch_one(select_query, (bus_name,))

        params_rating = (
            company_data["overall_rating"],
            company_data["reviewer_count"],
            company_data["rating_service"],
            company_data["rating_comfort"],
            company_data["rating_punctuality"],
            company_data["rating_staff_attitude"],
            company_data["rating_safety"],
            company_data["rating_info_accuracy"],
        )

        if existing_company:
            # --- CẬP NHẬT (Update) ---
            company_id = existing_company[0]

            update_query = """
                UPDATE bus_companies SET
                    rating_overall = %s,
                    reviewer_count = %s,
                    rating_service_quantity = %s,
                    rating_comfort = %s,
                    rating_punctuality = %s,
                    rating_staff_attitude = %s,
                    rating_safety = %s,
                    rating_info_accuracy = %s
                WHERE bus_company_id = %s;
            """
            params_update = params_rating + (company_id,)
            self.execute(update_query, params_update)

            print(f"🔄 Cập nhật Rating mới cho {bus_name} (ID: {company_id})")
            return company_id

        else:
            # --- CHÈN MỚI (Insert) ---
            insert_query = """
                INSERT INTO bus_companies (
                    bus_company_name, rating_overall, reviewer_count,
                    rating_service_quantity, rating_comfort, rating_punctuality, 
                    rating_staff_attitude, rating_safety, rating_info_accuracy
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING bus_company_id;
            """
            params_insert = (bus_name,) + params_rating

            # Giả định self.execute_and_get_id trả về ID từ mệnh đề RETURNING
            new_company_id = self.execute_and_get_id(insert_query, params_insert)

            print(f"Chèn mới công ty {bus_name} (ID: {new_company_id})")
            return new_company_id

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Đóng kết nối khi thoát khỏi khối 'with'."""
        if exc_type:  # Nếu có lỗi xảy ra
            if self.conn:
                self.conn.rollback()  # Hoàn tác các thay đổi chưa được commit
            print(f"⚠️ Lỗi xảy ra trong khối 'with', thực hiện rollback.")
        self.close()

    def close(self):
        self.conn.close()

    query = """SELECT reviewer_count, rating_overall FROM bus_companies WHERE bus_company_name=%s"""

    def update_rating_for_bus(self):
        pass

    def insert_new_bus(self):
        """Đây là hàm con của `check_rating` dùng để insert dữ liệu nhà xe chưa có"""
        pass

    def check_rating(self, query, site_review_count, site_rating_overall, values=None):
        """
        Kiểm tra dữ liệu phần đánh giá từ nhà xe từ container.

        Parameters:
        ----------
        query : str
            Câu truy vấn SQL để lấy dữ liệu đánh giá từ database.
        site_review_count : int
        site_rating_overall : float
        values : tuple | None

        Returns :
        -------

        """
        data = self.fetch_one(query=query, values=values)

        reviewer_count, rating_overall = data[0]
        if not data:
            return "new"  # call insert func

        elif (reviewer_count != site_review_count) & (
            rating_overall != site_rating_overall
        ):
            return "update"  # call update func

        return "pass"  # dữ liệu trùng (mới) không cần làm gì, pass qua container mới

    # Cần thêm diver để click -> lấy data -> insert/update
