import pandas as pd
from sklearn.preprocessing import MinMaxScaler

# tạo bộ scale
scaler = MinMaxScaler()


# 1. làm sạch dữ liệu
def clean_data(df):
    df = df.copy()

    # xử lý số điện thoại
    if "phone" in df.columns:
        df["phone"] = df["phone"].astype(str)
        df["phone"] = df["phone"].str.replace(r"\D", "", regex=True)

    # bỏ dòng bị thiếu
    df = df.dropna()
    return df


# 2. chuyển text -> số
def encode_data(df):
    df = df.copy()

    if "priority" in df.columns:
        df["priority"] = df["priority"].map({
            "normal": 0,
            "fast": 1,
            "express": 2
        })

    if "traffic_level" in df.columns:
        df["traffic_level"] = df["traffic_level"].map({
            "low": 0,
            "medium": 1,
            "high": 2
        })

    return df

# 3. chuẩn hóa (scale)
def scale_data(df):
    df = df.copy()

    cols = ["weight", "volume"]

    # chỉ lấy cột tồn tại
    cols = [c for c in cols if c in df.columns]

    if len(cols) > 0:
        df[cols] = scaler.fit_transform(df[cols])

    return df


# 4. tạo dữ liệu cho KNN
def prepare_data(df):
    X = df[[
        "weight",
        "volume",
        "priority",
        "traffic_level",
        "fragile",
        "cold"
    ]]

    y = None
    if "vehicle_type" in df.columns:
        y = df["vehicle_type"]

    return X, y


# 5. pipeline chính
def process(df):
    df = clean_data(df)
    df = encode_data(df)
    df = scale_data(df)

    X, y = prepare_data(df)

    return X, y


# test thử
if __name__ == "__main__":
    from data_loader import load_data

    df = load_data("data/orders.csv")

    if df is not None:
        X, y = process(df)

        print("X:")
        print(X.head())

        print("y:")
        print(y.head() if y is not None else "không có label")