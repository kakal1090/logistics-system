import pandas as pd
from sklearn.preprocessing import StandardScaler

scaler = StandardScaler()


def normalize_text(value):
    if pd.isna(value):
        return value
    return str(value).strip().lower()


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(col).strip().lower() for col in df.columns]

    text_cols = [
        "customer_name", "phone", "email", "address",
        "product_type", "priority", "note", "vehicle_type", "label"
    ]
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].apply(normalize_text)

    if "phone" in df.columns:
        df["phone"] = df["phone"].astype(str).str.replace(r"\D", "", regex=True)

    numeric_cols = ["weight", "quantity", "length", "width", "height", "distance"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    for col in ["weight", "length", "width", "height", "distance"]:
        if col in df.columns:
            df.loc[df[col] < 0, col] = pd.NA

    if "quantity" in df.columns:
        df["quantity"] = df["quantity"].fillna(1).clip(lower=1)

    required_cols = ["weight", "distance", "priority"]
    existing_required = [c for c in required_cols if c in df.columns]
    if existing_required:
        df = df.dropna(subset=existing_required)

    return df


def encode_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    priority_map = {
        "thuong": 0, "thường": 0, "normal": 0, "thap": 0,
        "nhanh": 1, "fast": 1,
        "hoa_toc": 2, "hỏa tốc": 2, "hoa toc": 2, "express": 2,
    }
    if "priority" in df.columns:
        df["priority_encoded"] = df["priority"].map(priority_map)

    return df


def add_derived_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    if "quantity" not in df.columns:
        df["quantity"] = 1

    if "weight" in df.columns:
        df["total_weight"] = df["weight"] * df["quantity"]

    if all(col in df.columns for col in ["length", "width", "height"]):
        df["volume"] = df["length"] * df["width"] * df["height"]

    return df


def scale_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    cols = [
        "total_weight", "quantity", "length", "width", "height",
        "distance", "volume", "priority_encoded",
    ]
    cols = [c for c in cols if c in df.columns]

    if cols:
        df[cols] = scaler.fit_transform(df[cols])

    return df


def prepare_data(df: pd.DataFrame):
    df = df.copy()

    feature_cols = [
        "total_weight", "quantity", "length", "width", "height",
        "distance", "volume", "priority_encoded",
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
    df = clean_data(df)
    df = encode_data(df)
    df = add_derived_features(df)

    required_after_encode = [
        "total_weight", "quantity", "length", "width", "height",
        "distance", "volume", "priority_encoded",
    ]
    existing_required = [c for c in required_after_encode if c in df.columns]
    if existing_required:
        df = df.dropna(subset=existing_required)

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
        print(y.head() if y is not None else "Không có label")

        print("\nProcessed Data:")
        print(processed_df.head())
