import pandas as pd
import json
import os


def load_data(path: str):
    """
    Đọc dữ liệu từ CSV hoặc JSON.
    Trả về DataFrame nếu thành công, ngược lại trả None.
    """
    if not os.path.exists(path):
        print(f"Lỗi: Không tìm thấy file -> {path}")
        return None

    ext = os.path.splitext(path)[1].lower()

    try:
        if ext == ".csv":
            df = pd.read_csv(path)
        elif ext == ".json":
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if isinstance(data, list):
                df = pd.DataFrame(data)
            else:
                df = pd.DataFrame([data])
        else:
            print(f"Lỗi: Chưa hỗ trợ định dạng file {ext}")
            return None

        print(f"Đã đọc dữ liệu thành công: {path}")
        print(f"Số dòng: {len(df)} | Số cột: {len(df.columns)}")
        return df

    except Exception as e:
        print(f"Lỗi khi đọc file: {e}")
        return None


if __name__ == "__main__":
    # đổi path test tùy theo file đang có thật trong repo
    df = load_data("../data/orders_result_500.csv")
    if df is not None:
        print(df.head())
