```markdown
# Vexere ETL Pipeline (Crawl → Clean → Load)

Dự án tự động crawl dữ liệu chuyến xe khách từ **Vexere**, làm sạch dữ liệu và lưu vào cơ sở dữ liệu PostgreSQL.  
Pipeline gồm 3 bước chính: **CRAWLING → CLEANING → LOADING**, tất cả được chạy trong file `main.py`.

---

## 📌 Chức năng chính

- **Crawl dữ liệu Vexere**

  - Tự động mở trình duyệt, nhập điểm đi – điểm đến – ngày.
  - Bấm “Xem thêm chuyến” nhiều lần.
  - Parse từng chuyến + rating chi tiết.
  - Mã crawl nằm trong:
    - `src/extract/crawling.py`
    - `src/extract/trip_actions.py`
    - `src/extract/trip_parser.py`

- **Làm sạch dữ liệu**

  - Chuẩn hóa giá vé, thời gian, ngày tháng.
  - Chuẩn hóa rating, loại ghế, tên nhà xe, thời lượng.
  - Lọc dữ liệu lỗi, trùng, thiếu.
  - Logic làm sạch nằm trong:
    - `src/transform/cleaning/cleaning.py`

- **Load dữ liệu vào PostgreSQL**
  - Tự động tạo city, route, company nếu chưa tồn tại.
  - Lưu lịch sử rating theo tuyến.
  - Insert từng chuyến xe.
  - Mã load nằm trong:
    - `src/load/loading.py`
    - `src/database/db_manager.py`

---

## 📂 Cấu trúc thư mục (ngắn gọn)

project/
│── main.py
│── routes.json
│── requirements.txt
│
├── data/
│ ├── raw/
│ └── processed/
│
└── src/
├── extract/
├── transform/cleaning/
├── load/
├── database/
└── utils/
```

## ![Flow project](assets/readme_img/pipeline_project.jpg)

## 🚀 Cách chạy dự án

### 1. Cài thư viện

```bash
pip install -r requirements.txt
```

### 2. Cấu hình database

Chỉnh file:

```
src/database/config.json
```

### 3. Chạy pipeline

```bash
python main.py
```

Pipeline sẽ tự động:

1. Đọc các tuyến trong `routes.json`
2. Crawl dữ liệu → lưu vào `data/raw/xxxx_raw.csv`
3. Làm sạch → lưu `data/processed/xxxx_cleaned.csv`
4. Load vào PostgreSQL

---

## ⚙️ Giải thích file `main.py`

`main.py` thực hiện 3 bước:

### **1) Crawl**

```python
df = crawl_vexere(start_city, dest_city, days=DAYSOFF)
```

### **2) Clean**

```python
df = clean_vexere(df)
```

### **3) Load DB**

## ![Database schema](assets/readme_img/image.png)

```python
insert_trips_from_dataframe(db, df)
```
