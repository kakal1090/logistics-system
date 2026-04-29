import os
import time
import logging
from typing import Dict, Any, List

import numpy as np
import pandas as pd

from knn_classifier import KNNClassifier
from rule_engine import RuleEngine


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


class OrderProcessingPipeline:
    """
    Flow chính:
    raw input -> chuẩn hóa -> tạo feature -> KNN dự đoán label -> RuleEngine gán xe.
    """

    def __init__(self):
        self.knn_classifier = KNNClassifier(model_path="models/knn_model.pkl")
        self.rule_engine = RuleEngine()

    @staticmethod
    def normalize_text(value: Any) -> str:
        if value is None:
            return ""
        return str(value).strip().lower()

    @staticmethod
    def safe_float(value: Any, default: float = 0.0) -> float:
        try:
            if value in (None, ""):
                return default
            return float(value)
        except (ValueError, TypeError):
            return default

    @staticmethod
    def safe_int(value: Any, default: int = 1) -> int:
        try:
            if value in (None, ""):
                return default
            return int(float(value))
        except (ValueError, TypeError):
            return default

    def preprocess_order(self, raw_order: Dict[str, Any]) -> Dict[str, Any]:
        order = raw_order.copy()

        order["order_id"] = str(order.get("order_id", "")).strip()
        order["customer_name"] = str(order.get("customer_name", "")).strip()
        order["phone"] = str(order.get("phone", "")).strip()
        order["email"] = str(order.get("email", "")).strip()
        order["address"] = str(order.get("address", "")).strip()
        order["product_type"] = self.normalize_text(order.get("product_type"))
        order["priority"] = self.normalize_text(order.get("priority"))
        order["note"] = str(order.get("note", "")).strip()

        order["weight"] = self.safe_float(order.get("weight"), 0.0)
        order["quantity"] = self.safe_int(order.get("quantity"), 1)
        order["length"] = self.safe_float(order.get("length"), 0.0)
        order["width"] = self.safe_float(order.get("width"), 0.0)
        order["height"] = self.safe_float(order.get("height"), 0.0)
        order["distance"] = self.safe_float(order.get("distance"), 0.0)

        if order["quantity"] <= 0:
            order["quantity"] = 1

        order["total_weight"] = order["weight"] * order["quantity"]
        order["volume"] = order["length"] * order["width"] * order["height"]

        priority_map = {
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

        product_type_map = {
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

        order["priority_encoded"] = priority_map.get(order["priority"], 0)
        order["product_type_encoded"] = product_type_map.get(order["product_type"], 0)

        return order

    def build_knn_features(self, order: Dict[str, Any]) -> np.ndarray:
        """
        Feature phải khớp 100% với train_model.py.

        Thứ tự feature:
        1. total_weight
        2. quantity
        3. length
        4. width
        5. height
        6. distance
        7. volume
        8. priority_encoded
        9. product_type_encoded
        """

        features = np.array([[
            order["total_weight"],
            order["quantity"],
            order["length"],
            order["width"],
            order["height"],
            order["distance"],
            order["volume"],
            order["priority_encoded"],
            order["product_type_encoded"],
        ]])

        return features

    def predict_label(self, order: Dict[str, Any]) -> str:
        """
        Ưu tiên dùng KNN.
        Nếu model chưa train hoặc lỗi thì fallback sang rule_engine.
        """

        try:
            features = self.build_knn_features(order)
            predictions, probabilities = self.knn_classifier.predict(features)

            label = str(predictions[0]).strip()
            confidence = float(probabilities[0])

            logger.info(f"KNN label={label}, confidence={confidence:.2f}")

            return label

        except Exception as e:
            logger.warning(f"KNN lỗi hoặc chưa có model, fallback RuleEngine: {e}")
            return self.rule_engine.classify_label(order)

    def process_single_order(self, raw_order: Dict[str, Any]) -> Dict[str, Any]:
        start_time = time.perf_counter()

        order = self.preprocess_order(raw_order)

        logger.info(
            f"Xử lý đơn {order['order_id']} | "
            f"weight={order['weight']} | quantity={order['quantity']} | "
            f"total_weight={order['total_weight']}"
        )

        label = self.predict_label(order)
        vehicle = self.rule_engine.assign_vehicle(order, label)

        elapsed = time.perf_counter() - start_time

        result = {
            "order_id": order["order_id"],
            "customer_name": order["customer_name"],
            "product_type": order["product_type"],

            "weight": order["weight"],
            "quantity": order["quantity"],
            "total_weight": order["total_weight"],

            "distance": order["distance"],
            "priority": order["priority"],

            "label": label,
            "assigned_vehicle": vehicle,

            "process_status": "done",
            "processed_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "processing_time": f"{elapsed:.3f}s",
        }

        logger.info(f"Kết quả: {result}")

        return result

    def batch_process(self, orders: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [self.process_single_order(order) for order in orders]


# Hàm cho socket_server.py import
def process_order(raw_order: Dict[str, Any]):
    pipeline = OrderProcessingPipeline()
    result = pipeline.process_single_order(raw_order)

    return result["label"], result["assigned_vehicle"]


if __name__ == "__main__":
    pipeline = OrderProcessingPipeline()

    demo_orders = [
        {
            "order_id": "TEST001",
            "customer_name": "Nguyen Van A",
            "phone": "0909123456",
            "email": "a@gmail.com",
            "address": "Quan 1 TP.HCM",
            "product_type": "tieu_chuan",
            "weight": 1,
            "quantity": 123,
            "length": 50,
            "width": 40,
            "height": 30,
            "distance": 8,
            "priority": "nhanh",
            "note": "Test nhẹ",
        },
        {
            "order_id": "TEST002",
            "customer_name": "Tran Thi B",
            "phone": "0987654321",
            "email": "b@gmail.com",
            "address": "Quan 7 TP.HCM",
            "product_type": "tieu_chuan",
            "weight": 300,
            "quantity": 8,
            "length": 120,
            "width": 100,
            "height": 90,
            "distance": 150,
            "priority": "thuong",
            "note": "Test nặng",
        },
    ]

    results = pipeline.batch_process(demo_orders)

    print("\nOUTPUT:")
    for result in results:
        print(result)

    os.makedirs("output", exist_ok=True)
    pd.DataFrame(results).to_csv("output/processed_orders.csv", index=False, encoding="utf-8-sig")
