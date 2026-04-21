import os
import pandas as pd

from data_loader import load_data
from preprocessor import process
from knn_classifier import KNNClassifier

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(BASE_DIR, "..", "data", "orders_result_500.csv")

def main():
    df = load_data(data_path)
    if df is None:
        print("❌ Không đọc được data")
        return

    X, y, processed_df = process(df)

    if y is None:
        print("❌ Dataset không có cột label hoặc vehicle_type để train")
        return

    model = KNNClassifier()
    model.train(X, y)

    print("✅ Train KNN xong, model đã được lưu")
    print("📊 X shape:", X.shape)
    print("🏷️ y sample:")
    print(y.head() if hasattr(y, "head") else y[:5])

if __name__ == "__main__":
    main()
