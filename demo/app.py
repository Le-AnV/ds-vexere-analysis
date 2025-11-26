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

    # 4. TIME & GIÁ THEO PHÚT
    df["duration_minutes_log"] = np.log1p(df["duration_minutes"])
    df["price_per_minute"] = df["real_price"] / df["duration_minutes"]

    # 5. DISCOUNT RATE
    df["discount_rate"] = 1 - df["price_discounted"] / df["price_original"]

    # 6. SERVICE SCORE
    service_cols = ["rating_staff_attitude", "rating_service_quality", "rating_comfort"]
    df["service_score"] = df[service_cols].mean(axis=1)

    # 7. TRUST SCORE
    trust_cols = ["rating_safety", "rating_punctuality", "rating_info_accuracy"]
    df["trust_score"] = df[trust_cols].mean(axis=1)

    # 8. WILSON SCORE
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

    # 9. PRICE PER SEAT
    df["price_per_seat"] = df["real_price"] / df["number_of_seat"]

    # 10. PRICE–RATING RATIO (ổn định)
    df["price_rating_ratio_stable"] = df["wilson_score"] / df["log_price"]

    # 11. FAIRNESS INDEX
    df["fairness_index"] = df["wilson_score"] / np.sqrt(df["real_price"])

    # 12. LOG thêm
    df["log_price_per_minute"] = np.log1p(df["price_per_minute"])
    df["log_price_per_seat"] = np.log1p(df["price_per_seat"])

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
st.header("1️⃣ Huấn luyện mô hình KMeans từ dữ liệu gốc")

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

st.write(f"✅ Đã load {len(csv_files)} file CSV, tổng số dòng: {df_train_raw.shape[0]}")
st.dataframe(df_train_raw.head())

# Các cột số cần thiết
numeric_cols = [
    "price_original",
    "price_discounted",
    "duration_minutes",
    "rating_overall",
    "rating_safety",
    "rating_info_accuracy",
    "rating_staff_attitude",
    "rating_comfort",
    "rating_service_quality",
    "rating_punctuality",
    "reviewer_count",
    "number_of_seat",
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

# Feature dùng để phân cụm (giống notebook)
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
# 6. NHẬP DỮ LIỆU MỚI TRÊN WEB → DỰ ĐOÁN CỤM
# =========================================================
st.header("2️⃣ Nhập chuyến xe mới để xem thuộc cụm nào")

st.write(
    """
    Nhập các thông tin thô cho chuyến xe mới (giá, rating, thời gian, số ghế, số reviewer).  
    App sẽ dùng **cùng pipeline feature + scaler + model KMeans** đã train để dự đoán cụm
    và giải thích ý nghĩa cụm.
    """
)

# Gợi ý một dòng mẫu để dễ nhập
sample_new = {
    "price_original": [400000],
    "price_discounted": [350000],
    "duration_minutes": [660],
    "rating_overall": [4.6],
    "rating_safety": [4.7],
    "rating_info_accuracy": [4.6],
    "rating_staff_attitude": [4.7],
    "rating_comfort": [4.5],
    "rating_service_quality": [4.5],
    "rating_punctuality": [4.8],
    "reviewer_count": [500],
    "number_of_seat": [34],
}

df_new_input = st.data_editor(
    pd.DataFrame(sample_new),
    num_rows="dynamic",
    key="manual_new_trips",
)

# ====== GIẢI THÍCH Ý NGHĨA CỤM ======
cluster_meanings = {
    0: {
        "name": "Ngon – Bổ – Rẻ",
        "description": """
📌 **Cụm 0 – “Ngon – Bổ – Rẻ”**  
• Giá vé thấp nhất trong 3 nhóm  
• Chất lượng dịch vụ tốt, ổn định  
• Điểm Wilson cao → mức hài lòng bền vững  
• Rất tối ưu về chi phí và giá trị  

👉 Chuyến xe thuộc cụm 0 thường là *dịch vụ chất lượng tốt nhưng giá vẫn mềm, đáng đồng tiền bát gạo*.
""",
    },
    1: {
        "name": "Giá ảo – Chất lượng thấp",
        "description": """
📌 **Cụm 1 – “Giá ảo – Chất lượng thấp”**  
• Giá vé cao nhất thị trường  
• Chất lượng dịch vụ thấp nhất  
• Điểm Wilson thấp → đánh giá kém ổn định  

👉 Chuyến xe thuộc cụm 1 thường là *giá cao nhưng chất lượng không tương xứng* 
(ví dụ: độc quyền tuyến, tăng giá mùa cao điểm nhưng phục vụ kém).
""",
    },
    2: {
        "name": "Cao cấp – Đáng tiền",
        "description": """
📌 **Cụm 2 – “Cao cấp – Đáng tiền”**  
• Giá vé cao  
• Chất lượng dịch vụ tốt nhất  
• Điểm tin cậy (Wilson, Trust Score) cao  

👉 Chuyến xe thuộc cụm 2 là *dịch vụ cao cấp – “tiền nào của nấy”*, 
phù hợp khách hàng ưu tiên trải nghiệm, an toàn và sự chuyên nghiệp.
""",
    },
}

# ====== NÚT DỰ ĐOÁN ======
if st.button("🚀 Dự đoán cụm cho dữ liệu mới"):
    if df_new_input.shape[0] == 0:
        st.warning("Chưa có dòng nào trong bảng dữ liệu mới.")
    else:
        df_new = df_new_input.copy()
        df_new[numeric_cols] = df_new[numeric_cols].apply(
            pd.to_numeric, errors="coerce"
        )
        df_new = df_new.dropna(subset=numeric_cols)

        if df_new.shape[0] == 0:
            st.warning("Tất cả dòng mới đều thiếu dữ liệu ở các cột quan trọng.")
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

                st.subheader("🔮 Kết quả dự đoán cụm cho dữ liệu mới")
                st.dataframe(
                    df_new_fe[
                        [
                            "price_original",
                            "price_discounted",
                            "duration_minutes",
                            "rating_overall",
                            "reviewer_count",
                            "number_of_seat",
                            "real_price",
                            "log_price",
                            "wilson_score",
                            "fairness_index",
                            "trust_score",
                            "service_score",
                            "predicted_cluster",
                        ]
                    ]
                )

                # ======= HIỆN GIẢI THÍCH CỤM CHO TỪNG NHÓM XUẤT HIỆN =======
                st.subheader("📘 Giải thích ý nghĩa các cụm xuất hiện trong dự đoán")

                for c in sorted(df_new_fe["predicted_cluster"].unique()):
                    st.markdown(f"### 🎯 Cluster {c} – {cluster_meanings[c]['name']}")
                    st.markdown(cluster_meanings[c]["description"])
                    idx_list = df_new_fe.index[df_new_fe["predicted_cluster"] == c]
                    st.caption(f"Các dòng thuộc cụm {c}: {list(idx_list)}")
