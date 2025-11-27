import streamlit as st
import pandas as pd
import numpy as np

from sklearn.preprocessing import RobustScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import os, glob


# =========================================================
# 0. HÀM FEATURE ENGINEERING DÙNG CHUNG CHO TRAIN & PREDICT
# =========================================================
def feature_engineering(df_raw: pd.DataFrame) -> pd.DataFrame:
    df = df_raw.copy()

    # 1. Loại các dòng price_original = 0
    df = df[df["price_original"] != 0].copy()

    # 2. REAL PRICE
    df["real_price"] = np.where(
        df["price_discounted"] == 0,
        df["price_original"],
        df["price_discounted"],
    )

    # 3. LOG PRICE
    df["log_price"] = np.log1p(df["real_price"])

    # 4. DISCOUNT RATE
    df["discount_rate"] = 1 - df["price_discounted"] / df["price_original"]

    # 5. SERVICE SCORE
    service_cols = ["rating_staff_attitude", "rating_service_quality", "rating_comfort"]
    df["service_score"] = df[service_cols].mean(axis=1)

    # 6. TRUST SCORE
    trust_cols = ["rating_safety", "rating_punctuality", "rating_info_accuracy"]
    df["trust_score"] = df[trust_cols].mean(axis=1)

    # 7. WILSON SCORE
    def wilson_lower_bound(p, n, z=1.96):
        if n == 0:
            return 0.0
        denom = 1 + z**2 / n
        centre = p + z * z / (2 * n)
        margin = z * np.sqrt((p * (1 - p) + z * z / (4 * n)) / n)
        return (centre - margin) / denom

    df["p"] = df["rating_overall"] / 5.0
    df["wilson_score"] = df.apply(
        lambda r: wilson_lower_bound(r["p"], r["reviewer_count"]), axis=1
    )
    df.drop(columns=["p"], inplace=True)

    # 8. PRICE–RATING RATIO (ổn định)
    df["price_rating_ratio_stable"] = df["wilson_score"] / df["log_price"]

    # 9. FAIRNESS INDEX
    df["fairness_index"] = df["wilson_score"] / np.sqrt(df["real_price"])

    return df


# =========================================================
# 1. TIÊU ĐỀ
# =========================================================
st.title("🚍 Phân cụm chuyến xe khách theo giá & chất lượng dịch vụ")

st.write(
    """
    Flow:
    1) Dùng dữ liệu trong `data/processed` để huấn luyện KMeans (K = 3).  
    2) Sau đó nhập tay chuyến xe mới trên web để xem nó rơi vào cụm nào và ý nghĩa của cụm đó.
    """
)

# =========================================================
# 2. LOAD DỮ LIỆU TRAIN TỪ CSV
# =========================================================
st.header("Huấn luyện mô hình KMeans từ dữ liệu gốc")

folder_path = "data/processed"
csv_files = glob.glob(os.path.join(folder_path, "*.csv"))

if not csv_files:
    st.error(f"Không tìm thấy file CSV nào trong thư mục: {folder_path}")
    st.stop()

dfs = []
for f in csv_files:
    tmp = pd.read_csv(f)
    dfs.append(tmp)

df_train_raw = pd.concat(dfs, ignore_index=True)

st.write(f"Đã load {len(csv_files)} file CSV, tổng số dòng: {df_train_raw.shape[0]}")
st.dataframe(df_train_raw.head())

# Các cột số cần thiết (đÃ BỎ duration_minutes, number_of_seat)
numeric_cols = [
    "price_original",
    "price_discounted",
    "rating_overall",
    "rating_safety",
    "rating_info_accuracy",
    "rating_staff_attitude",
    "rating_comfort",
    "rating_service_quality",
    "rating_punctuality",
    "reviewer_count",
]

df_train_raw[numeric_cols] = df_train_raw[numeric_cols].apply(
    pd.to_numeric, errors="coerce"
)
df_train_raw = df_train_raw.dropna(subset=numeric_cols)

if df_train_raw.shape[0] < 3:
    st.error("Dữ liệu train sau khi làm sạch < 3 dòng, không đủ để phân cụm K=3.")
    st.stop()

# =========================================================
# 3. FEATURE ENGINEERING CHO DỮ LIỆU TRAIN
# =========================================================
df_train_fe = feature_engineering(df_train_raw)

st.subheader("📐 Một số feature đã tạo trên dữ liệu train")
st.dataframe(
    df_train_fe[
        [
            "real_price",
            "log_price",
            "service_score",
            "trust_score",
            "wilson_score",
            "fairness_index",
        ]
    ].head()
)

# Feature dùng để phân cụm
features = [
    "wilson_score",
    "log_price",
    "fairness_index",
    "trust_score",
    "service_score",
]

df_cluster_train = df_train_fe[features].dropna().copy()
df_cluster_train = df_cluster_train.drop_duplicates()

if df_cluster_train.shape[0] <= 3:
    st.error("Sau khi drop NaN/duplicates, dữ liệu train còn quá ít để phân cụm K=3.")
    st.stop()

# =========================================================
# 4. SCALE + TRAIN KMEANS VỚI K = 3
# =========================================================
scaler = RobustScaler()
X_train_scaled = scaler.fit_transform(df_cluster_train[features])

K = 3
model = KMeans(n_clusters=K, random_state=40, n_init=10)
train_labels = model.fit_predict(X_train_scaled)

df_cluster_train = df_cluster_train.copy()
df_cluster_train["cluster"] = train_labels

# Join cluster về lại df_train_fe (theo index)
df_train_result = df_train_fe.join(df_cluster_train["cluster"], how="left")

st.success("✅ Đã huấn luyện KMeans với K = 3 trên dữ liệu CSV.")
st.subheader("📄 Một phần dữ liệu train sau phân cụm")
st.dataframe(df_train_result.head())

# =========================================================
# 5. PCA TRÊN DỮ LIỆU TRAIN (OPTIONAL)
# =========================================================
if df_cluster_train.shape[0] >= 2:
    st.subheader("📊 PCA 2D trên dữ liệu train")

    pca = PCA(n_components=2)
    X_train_pca = pca.fit_transform(X_train_scaled)

    fig, ax = plt.subplots()
    ax.scatter(X_train_pca[:, 0], X_train_pca[:, 1], c=train_labels, cmap="viridis")
    ax.set_xlabel("PCA 1")
    ax.set_ylabel("PCA 2")
    ax.set_title("PCA Visualization (Train Data, K = 3)")

    st.pyplot(fig)


# =========================================================
# 6. HÀM HỖ TRỢ FORMAT & PARSE GIÁ TIỀN
# =========================================================
def parse_price(text: str) -> int:
    """
    Nhận chuỗi giá tiền có thể có dấu . ngăn cách hàng nghìn,
    trả về số nguyên (VND). Rỗng -> 0.
    """
    text = str(text).strip()
    if text == "":
        return 0
    text = text.replace(".", "")
    return int(text)


def format_price(v: float | int) -> str:
    """
    Format số thành chuỗi có dấu . ngăn cách hàng nghìn.
    """
    return f"{int(v):,}".replace(",", ".")


# =========================================================
# 7. NHẬP DỮ LIỆU MỚI TRÊN WEB → DỰ ĐOÁN CỤM
# =========================================================
st.header("2️⃣ Nhập chuyến xe mới để xem thuộc cụm nào")

st.write(
    """
    Nhập các thông tin thô cho chuyến xe mới (giá, rating, số lượng người đánh giá).  
    App sẽ dùng **cùng pipeline feature + scaler + model KMeans** đã train để dự đoán cụm
    và giải thích ý nghĩa cụm.
    """
)

st.subheader("🔧 Thông tin chuyến xe mới")

col_price1, col_price2 = st.columns(2)
with col_price1:
    price_original_str = st.text_input("Giá gốc (VND)", "400.000")
with col_price2:
    price_discounted_str = st.text_input("Giá khuyến mãi (VND)", "350.000")

col_rating1, col_rating2, col_rating3 = st.columns(3)
with col_rating1:
    rating_overall = st.slider("Điểm tổng thể", 0.0, 5.0, 4.6, 0.1)
    rating_safety = st.slider("An toàn", 0.0, 5.0, 4.7, 0.1)
with col_rating2:
    rating_info_accuracy = st.slider("Độ chính xác thông tin", 0.0, 5.0, 4.6, 0.1)
    rating_staff_attitude = st.slider("Thái độ nhân viên", 0.0, 5.0, 4.7, 0.1)
with col_rating3:
    rating_comfort = st.slider("Tiện nghi", 0.0, 5.0, 4.5, 0.1)
    rating_service_quality = st.slider("Chất lượng dịch vụ", 0.0, 5.0, 4.5, 0.1)

rating_punctuality = st.slider("Đúng giờ", 0.0, 5.0, 4.8, 0.1)

reviewer_count = st.number_input(
    "Số lượng người đánh giá", min_value=1, max_value=100000, value=500, step=10
)

# ====== GIẢI THÍCH Ý NGHĨA CỤM ======
cluster_meanings = {
    0: {
        "name": "Giá hợp lý – Dịch vụ ổn định",
        "description": """
📌 **Cụm 0 – Giá hợp lý – Dịch vụ ổn định**  
• Mức giá dễ tiếp cận, phù hợp đa số hành khách  
• Chất lượng dịch vụ đồng đều, ít biến động  
• Wilson Score khá tốt → phản ánh sự hài lòng ổn định theo thời gian  

👉 Các chuyến xe ở cụm này thường mang lại **trải nghiệm tốt với chi phí vừa phải**, phù hợp hành khách ưu tiên tính kinh tế nhưng vẫn muốn dịch vụ đáng tin cậy.
""",
    },
    1: {
        "name": "Giá cao – Trải nghiệm chưa tương xứng",
        "description": """
📌 **Cụm 1 – Giá cao – Trải nghiệm chưa tương xứng**  
• Giá vé nằm ở nhóm trên trung bình  
• Mức độ hài lòng và điểm đánh giá thấp, thiếu sự ổn định  
• Wilson Score thấp → chất lượng thực tế không đồng đều  

👉 Những chuyến xe rơi vào cụm này thường **có mức giá không phản ánh đúng giá trị dịch vụ**, có thể chịu ảnh hưởng bởi thời điểm cao nhu cầu, thương hiệu hoặc độc quyền tuyến.
""",
    },
    2: {
        "name": "Dịch vụ chất lượng cao – Trải nghiệm trọn vẹn",
        "description": """
📌 **Cụm 2 – Dịch vụ chất lượng cao – Trải nghiệm trọn vẹn**  
• Giá vé thuộc nhóm cao, đi kèm chất lượng phục vụ tốt  
• Điểm hài lòng ổn định và mức độ tin cậy vượt trội  
• Wilson Score cao → phản ánh sự đồng thuận lớn từ người dùng  

👉 Cụm này đại diện cho **dịch vụ cao cấp**, phù hợp hành khách chú trọng trải nghiệm, sự an toàn và tính chuyên nghiệp trong suốt hành trình.
""",
    },
}


# ====== NÚT DỰ ĐOÁN ======
if st.button("🚀 Dự đoán cụm cho dữ liệu mới"):
    try:
        price_original = parse_price(price_original_str)
        price_discounted = parse_price(price_discounted_str)
    except ValueError:
        st.error(
            "Giá tiền không hợp lệ. Vui lòng chỉ nhập số và dấu chấm '.' ngăn cách hàng nghìn."
        )
        st.stop()

    data_new = {
        "price_original": [price_original],
        "price_discounted": [price_discounted],
        "rating_overall": [rating_overall],
        "rating_safety": [rating_safety],
        "rating_info_accuracy": [rating_info_accuracy],
        "rating_staff_attitude": [rating_staff_attitude],
        "rating_comfort": [rating_comfort],
        "rating_service_quality": [rating_service_quality],
        "rating_punctuality": [rating_punctuality],
        "reviewer_count": [reviewer_count],
    }

    df_new = pd.DataFrame(data_new)
    df_new[numeric_cols] = df_new[numeric_cols].apply(pd.to_numeric, errors="coerce")
    df_new = df_new.dropna(subset=numeric_cols)

    if df_new.shape[0] == 0:
        st.warning("Dữ liệu mới đang thiếu giá trị ở các cột quan trọng.")
    else:
        # Feature engineering cho dữ liệu mới
        df_new_fe = feature_engineering(df_new)

        # Lấy đúng các feature đã dùng khi train
        df_new_cluster = df_new_fe[features].dropna().copy()

        if df_new_cluster.shape[0] == 0:
            st.warning("Không tạo được đủ feature cho dữ liệu mới (NaN hết).")
        else:
            # Scale bằng scaler đã FIT trên train
            X_new_scaled = scaler.transform(df_new_cluster[features])

            # Dự đoán cụm bằng model đã FIT
            new_labels = model.predict(X_new_scaled)

            df_new_fe = df_new_fe.loc[df_new_cluster.index].copy()
            df_new_fe["predicted_cluster"] = new_labels

            # Tạo bản hiển thị với giá đã format
            df_display = df_new_fe[
                [
                    "price_original",
                    "price_discounted",
                    "rating_overall",
                    "reviewer_count",
                    "real_price",
                    "log_price",
                    "wilson_score",
                    "fairness_index",
                    "trust_score",
                    "service_score",
                    "predicted_cluster",
                ]
            ].copy()

            df_display["price_original"] = df_display["price_original"].apply(
                format_price
            )
            df_display["price_discounted"] = df_display["price_discounted"].apply(
                format_price
            )
            df_display["real_price"] = df_display["real_price"].apply(format_price)

            st.subheader("🔮 Kết quả dự đoán cụm cho dữ liệu mới")
            st.dataframe(df_display)

            # ======= HIỆN GIẢI THÍCH CỤM CHO TỪNG NHÓM XUẤT HIỆN =======
            st.subheader("📘 Giải thích ý nghĩa các cụm xuất hiện trong dự đoán")

            for c in sorted(df_new_fe["predicted_cluster"].unique()):
                st.markdown(f"### 🎯 Cluster {c} – {cluster_meanings[c]['name']}")
                st.markdown(cluster_meanings[c]["description"])
                idx_list = df_new_fe.index[df_new_fe["predicted_cluster"] == c]
                st.caption(f"Các dòng thuộc cụm {c}: {list(idx_list)}")
