import os
import random
import pandas as pd

from sklearn.model_selection import train_test_split

from knn_classifier import KNNClassifier


DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "orders_result_500.csv")
MODEL_PATH = "models/knn_model.pkl"


def build_label(total_weight: float) -> str:
    """
    Nhãn chuẩn của hệ thống:
        < 200 kg      -> Nhẹ
        200 - 1500 kg -> Trung bình
        > 1500 kg     -> Nặng
    """
    if total_weight < 200:
        return "Nhẹ"
    elif total_weight <= 1500:
        return "Trung bình"
    return "Nặng"


def assign_vehicle(label: str, total_weight: float, length: float, width: float, height: float) -> str:
    """
    Gán xe chuẩn:
        Nhẹ + kích thước <= 80x80x80 + total < 100 -> Xe máy
        Nhẹ còn lại -> Xe tải
        Trung bình -> Xe tải
        Nặng <= 5000 -> Xe dưới 5 tấn
        Nặng > 5000 -> Xe đầu kéo / Container
    """

    fits_motorbike = (
        length <= 80
        and width <= 80
        and height <= 80
        and total_weight < 100
    )

    if label == "Nhẹ":
        if fits_motorbike:
            return "Xe máy"
        return "Xe tải"

    if label == "Trung bình":
        return "Xe tải"

    if label == "Nặng":
        if total_weight <= 5000:
            return "Xe dưới 5 tấn"
        return "Xe đầu kéo / Container"

    return "Chưa xác định"


def encode_priority(value) -> int:
    value = str(value or "").strip().lower()

    mapping = {
        "thuong": 0,
        "thường": 0,
        "normal": 0,
        "nhanh": 1,
        "fast": 1,
        "hoa_toc": 2,
        "hỏa tốc": 2,
        "hoa toc": 2,
        "express": 2,
    }

    return mapping.get(value, 0)


def encode_product_type(value) -> int:
    value = str(value or "").strip().lower()

    mapping = {
        "tieu_chuan": 0,
        "nong_san": 1,
        "linh_kien_dien_tu": 2,
        "my_pham": 3,
        "dong_lanh": 4,
        "de_vo": 5,
        "cong_kenh": 6,
        "nguy_hiem": 7,
        "hang_tieu_dung": 8,
        "do_gia_dung": 8,
    }

    return mapping.get(value, 0)


def generate_standard_logistics_data(n_rows: int = 500) -> pd.DataFrame:
    os.makedirs(DATA_DIR, exist_ok=True)

    priorities = ["thuong", "nhanh", "hoa_toc"]

    product_types = [
        "tieu_chuan",
        "nong_san",
        "linh_kien_dien_tu",
        "my_pham",
        "dong_lanh",
        "de_vo",
        "cong_kenh",
        "nguy_hiem",
        "hang_tieu_dung",
    ]

    data = []

    for i in range(1, n_rows + 1):
        weight = round(random.uniform(1, 500), 2)
        quantity = random.randint(1, 20)
        total_weight = round(weight * quantity, 2)

        length = round(random.uniform(10, 200), 2)
        width = round(random.uniform(10, 150), 2)
        height = round(random.uniform(10, 150), 2)
        volume = round(length * width * height, 2)

        distance = random.randint(1, 1500)
        priority = random.choice(priorities)
        product_type = random.choice(product_types)

        label = build_label(total_weight)
        vehicle_type = assign_vehicle(label, total_weight, length, width, height)

        data.append({
            "order_id": f"ORD{i:03d}",
            "customer_name": f"Khach hang {i}",
            "phone": f"090{i:07d}"[-10:],
            "email": f"khach{i}@test.vn",
            "address": "TP.HCM",

            "product_type": product_type,
            "weight": weight,
            "quantity": quantity,
            "total_weight": total_weight,

            "length": length,
            "width": width,
            "height": height,
            "volume": volume,

            "distance": distance,
            "priority": priority,

            "priority_encoded": encode_priority(priority),
            "product_type_encoded": encode_product_type(product_type),

            "label": label,
            "vehicle_type": vehicle_type,
            "note": "Giao hàng hệ thống",
        })

    df = pd.DataFrame(data)

    df.to_csv(DATA_PATH, index=False, encoding="utf-8-sig")

    print("✅ Đã tạo mới 500 dòng data chuẩn")
    print(df["label"].value_counts())
    print(df["vehicle_type"].value_counts())

    return df


def load_or_build_training_data() -> pd.DataFrame:
    os.makedirs(DATA_DIR, exist_ok=True)

    if os.path.exists(DATA_PATH):
        print(f"✅ Đọc file train hiện có: {DATA_PATH}")
        df = pd.read_csv(DATA_PATH)
    else:
        print("⚠️ Chưa có file train, tạo mới data chuẩn.")
        df = generate_standard_logistics_data(500)

    # Chuẩn hóa tên cột
    df.columns = [str(c).strip().lower() for c in df.columns]

    # Bổ sung cột thiếu
    if "quantity" not in df.columns:
        df["quantity"] = 1

    if "product_type" not in df.columns:
        df["product_type"] = "tieu_chuan"

    if "priority" not in df.columns:
        df["priority"] = "thuong"

    # Ép kiểu số
    numeric_cols = ["weight", "quantity", "length", "width", "height", "distance"]
    for col in numeric_cols:
        if col not in df.columns:
            df[col] = 0
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["quantity"] = df["quantity"].fillna(1).clip(lower=1)
    df["weight"] = df["weight"].fillna(0).clip(lower=0)
    df["length"] = df["length"].fillna(0).clip(lower=0)
    df["width"] = df["width"].fillna(0).clip(lower=0)
    df["height"] = df["height"].fillna(0).clip(lower=0)
    df["distance"] = df["distance"].fillna(0).clip(lower=0)

    # QUAN TRỌNG:
    # Luôn tính lại total_weight và label theo rule chuẩn.
    # Không tin label cũ trong file, để tránh lỗi "Xe lạnh", "Xe tải 1.5 tấn" từ data cũ.
    df["total_weight"] = df["weight"] * df["quantity"]
    df["volume"] = df["length"] * df["width"] * df["height"]

    df["priority"] = df["priority"].astype(str).str.strip().str.lower()
    df["product_type"] = df["product_type"].astype(str).str.strip().str.lower()

    df["priority_encoded"] = df["priority"].apply(encode_priority)
    df["product_type_encoded"] = df["product_type"].apply(encode_product_type)

    df["label"] = df["total_weight"].apply(build_label)

    df["vehicle_type"] = df.apply(
        lambda r: assign_vehicle(
            r["label"],
            r["total_weight"],
            r["length"],
            r["width"],
            r["height"],
        ),
        axis=1,
    )

    # Lưu lại file đã làm sạch
    df.to_csv(DATA_PATH, index=False, encoding="utf-8-sig")

    print("✅ Đã chuẩn hóa lại file train")
    print(df["label"].value_counts())
    print(df["vehicle_type"].value_counts())

    return df


def train_knn_model():
    df = load_or_build_training_data()

    feature_cols = [
        "total_weight",
        "quantity",
        "length",
        "width",
        "height",
        "distance",
        "volume",
        "priority_encoded",
        "product_type_encoded",
    ]

    required_cols = feature_cols + ["label"]

    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        raise ValueError(f"File train thiếu cột: {missing}")

    df = df.dropna(subset=required_cols)

    X = df[feature_cols]
    y = df["label"]

    if y.nunique() < 2:
        raise ValueError("Data train phải có ít nhất 2 loại label khác nhau.")

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    clf = KNNClassifier(model_path=MODEL_PATH)
    clf.train(X_train, y_train, X_test, y_test)

    print("✅ Đã train và lưu KNN model thành công")
    print(f"📁 Model : {MODEL_PATH}")
    print(f"📁 Scaler: {MODEL_PATH.replace('.pkl', '_scaler.pkl')}")


if __name__ == "__main__":
    train_knn_model()
