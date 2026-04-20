import pandas as pd
def load_data(path):
    # đọc dữ liệu từ file csv
    try:
        df = pd.read_csv(path)
        print("Đã đọc dữ liệu")
        return df
    except:
        print("Lỗi khi đọc file")
        return None
# test nhanh
if __name__ == "__main__":
    df = load_data("data/orders.csv")
    if df is not None:
        print(df.head())