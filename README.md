        vexere_project/
        │
        ├── src/
        │   ├── crawl/                # Code crawl data
        │   │   └── vexere_crawler.py
        │   ├── processing/           # Tiền xử lý dữ liệu
        │   │   └── clean_data.ipynb
        │   ├── database/             # Kết nối và thao tác DB
        │   │   ├── db_connection.py
        │   │   ├── db_insert.py
        │   │   └── db_utils.py
        │   ├── sql/                  # Chứa file .sql riêng
        │   │   ├── create_tables.sql
        │   │   └── insert_bus_data.sql
        │   ├── ml/                   # Học máy (phân cụm, phân tích)
        │   │   └── clustering.ipynb
        │   ├── utils.py              # Hàm tiện ích dùng chung
        │   └── prefect_flow.py       # Flow orchestration bằng Prefect
        │
        ├── data/
        │   ├── raw/                  # Dữ liệu gốc crawl về
        │   └── processed/            # Dữ liệu sau khi clean
        │
        ├── .gitignore
        ├── .gitattributes
        ├── requirements.txt
        ├── README.md
        └── config.json               # Config kết nối DB, v.v.

![Database schema](assets/readme_img/image.png)
