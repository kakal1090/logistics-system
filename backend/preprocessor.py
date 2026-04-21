import pandas as pd
from sklearn.preprocessing import StandardScaler


scaler = StandardScaler()


def normalize_text(value):
    """
    Chuẩn hóa text về lowercase, bỏ khoảng trắng thừa.
    """
    if pd.isna(value):
        return value
    return str(value).strip().lower()


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Làm sạch dữ liệu đầu vào.
    """
    df = df.copy()

    # chuẩn hóa tên cột
    df.columns = [str(col).strip().lower() for col in df.columns]

    # chuẩn hóa text cho các cột thường gặp
    text_cols = [
        "customer_name", "phone", "email", "address",
        "product_type", "priority", "note", "vehicle_type", "label"
    ]
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].apply(normalize_text)

    # xử lý số điện thoại
    if "phone" in df.columns:
        df["phone"] = df["phone"].astype(str).str.replace(r"\D", "", regex=True)

    # ép kiểu số
    numeric_cols = ["weight", "length", "width", "height", "distance"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # bỏ giá trị âm không hợp lệ
    for col in ["weight", "length", "width", "height", "distance"]:
        if col in df.columns:
            df.loc[df[col] < 0, col] = pd.NA

    # bỏ dòng thiếu các cột bắt buộc cho KNN
    required_cols = ["weight", "distance", "priority", "product_type"]
    existing_required = [c for c in required_cols if c in df.columns]
    if existing_required:
        df = df.dropna(subset=existing_required)

    return df


def encode_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Mã hóa dữ liệu text -> số để đưa vào KNN.
    """
    df = df.copy()

    # chuẩn hóa priority theo dữ liệu nhóm đang dùng
    priority_map = {
        "thuong": 0,
        "thường": 0,
        "normal": 0,

        "nhanh": 1,
        "fast": 1,

        "hoa_toc": 2,
        "hỏa tốc": 2,
        "hoa toc": 2,
        "express": 2
    }

    if "priority" in df.columns:
        df["priority_encoded"] = df["priority"].map(priority_map)

    # chuẩn hóa product_type
    product_type_map = {
        "tieu_chuan": 0,
        "tiêu chuẩn": 0,
        "nong_san": 1,
        "nông sản": 1,
        "linh_kien_dien_tu": 2,
        "linh kiện điện tử": 2,
        "my_pham": 3,
        "mỹ phẩm": 3,
        "dong_lanh": 4,
        "đông lạnh": 4,
        "hang dong lanh": 4,
        "de_vo": 5,
        "dễ vỡ": 5,
        "hang de vo": 5,
        "cong_kenh": 6,
        "cồng kềnh": 6
    }

    if "product_type" in df.columns:
        df["product_type_encoded"] = df["product_type"].map(product_type_map)

    return df


def add_volume_feature(df: pd.DataFrame) -> pd.DataFrame:
    """
    Tạo thêm thể tích nếu có đủ length/width/height.
    """
    df = df.copy()

    if all(col in df.columns for col in ["length", "width", "height"]):
        df["volume"] = df["length"] * df["width"] * df["height"]

    return df


def scale_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Chuẩn hóa các cột số cho KNN.
    """
    df = df.copy()

    cols = [
        "weight",
        "length",
        "width",
        "height",
        "distance",
        "volume",
        "priority_encoded",
        "product_type_encoded"
    ]
    cols = [c for c in cols if c in df.columns]

    if cols:
        df[cols] = scaler.fit_transform(df[cols])

    return df


def prepare_data(df: pd.DataFrame):
    """
    Tạo X, y cho KNN.
    Ưu tiên label nếu có; nếu không thì fallback vehicle_type.
    """
    df = df.copy()

    feature_cols = [
        "weight",
        "length",
        "width",
        "height",
        "distance",
        "volume",
        "priority_encoded",
        "product_type_encoded"
    ]
    feature_cols = [c for c in feature_cols if c in df.columns]

    X = df[feature_cols]

    y = None
    if "label" in df.columns:
        y = df["label"]
    elif "vehicle_type" in df.columns:
        y = df["vehicle_type"]

    return X, y


def process(df: pd.DataFrame):
    """
    Pipeline tiền xử lý chính.
    """
    df = clean_data(df)
    df = encode_data(df)
    df = add_volume_feature(df)
    df = scale_data(df)
    X, y = prepare_data(df)
    return X, y, df


if __name__ == "__main__":
    from data_loader import load_data

    df = load_data("../data/orders_result_500.csv")

    if df is not None:
        X, y, processed_df = process(df)

        print("Features X:")
        print(X.head())

        print("\nLabel y:")
        print(y.head() if y is not None else "không có label")

        print("\nProcessed Data:")
        print(processed_df.head())
