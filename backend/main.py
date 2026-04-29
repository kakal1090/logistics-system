import os
import time
import logging
from typing import Dict, Any, List

import numpy as np
import pandas as pd

from knn_classifier import KNNClassifier
from rule_engine import RuleEngine

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class OrderProcessingPipeline:
    """
    Flow chính:
    Input -> preprocess -> KNN label -> Rule engine assign vehicle -> output
    """

    def __init__(self):
        self.knn_classifier = KNNClassifier()
        self.rule_engine = RuleEngine()

    @staticmethod
    def normalize_text(value: Any) -> str:
        if value is None:
            return ""
        return str(value).strip().lower()

    def preprocess_order(self, raw_order: Dict[str, Any]) -> Dict[str, Any]:
        """
        Chuẩn hóa input từ frontend/socket về format nội bộ thống nhất.
        """
        order = raw_order.copy()

        # chuẩn hóa text
        order["order_id"] = str(order.get("order_id", "")).strip()
        order["customer_name"] = str(order.get("customer_name", "")).strip()
        order["phone"] = str(order.get("phone", "")).strip()
        order["email"] = str(order.get("email", "")).strip()
        order["address"] = str(order.get("address", "")).strip()
        order["product_type"] = self.normalize_text(order.get("product_type"))
        order["priority"] = self.normalize_text(order.get("priority"))
        order["note"] = str(order.get("note", "")).strip()

        # ép kiểu số
        order["weight"] = float(order.get("weight", 0))
        order["length"] = float(order.get("length", 0))
        order["width"] = float(order.get("width", 0))
        order["height"] = float(order.get("height", 0))
        order["distance"] = float(order.get("distance", 0))

        # feature phụ
        order["volume"] = order["length"] * order["width"] * order["height"]

        # encode priority
        priority_map = {
            "thuong": 0,
            "nhanh": 1,
            "hoa_toc": 2
        }
        order["priority_encoded"] = priority_map.get(order["priority"], 0)

        # encode product_type
        product_type_map = {
            "tieu_chuan": 0,
            "nong_san": 1,
            "linh_kien_dien_tu": 2,
            "my_pham": 3,
            "dong_lanh": 4,
            "de_vo": 5,
            "cong_kenh": 6,
            "nguy_hiem": 7,
            "hang_tieu_dung": 8
        }
        order["product_type_encoded"] = product_type_map.get(order["product_type"], 0)

        return order

    def build_knn_features(self, order: Dict[str, Any]) -> np.ndarray:
        """
        Tạo vector đặc trưng cho KNN.
        Feature phải khớp với hướng preprocess của nhóm.
        """
        features = np.array([[
            order["weight"],
            order["length"],
            order["width"],
            order["height"],
            order["distance"],
            order["volume"],
            order["priority_encoded"],
            order["product_type_encoded"]
        ]])
        return features

    def fallback_label(self, order: Dict[str, Any]) -> str:
        """
        Nếu chưa có model train sẵn thì fallback đơn giản theo weight.
        """
        return "Nhẹ" if order["weight"] < 200 else "Nặng"

    def predict_label(self, order: Dict[str, Any]) -> str:
        """
        Gọi KNN nếu model đã sẵn sàng, ngược lại fallback.
        """
        try:
            features = self.build_knn_features(order)
           def predict_label(self, order: Dict[str, Any]) -> str:
    """
    Gọi KNN nếu model đã sẵn sàng, ngược lại fallback.
    """
    try:
        features = self.build_knn_features(order)
        predictions, _ = self.knn_classifier.predict(features)
        label = str(predictions[0]).strip().lower()

        label_map = {
            "0": "Nhẹ",
            "1": "Trung bình",
            "2": "Nặng",
            "nhe": "Nhẹ",
            "nhẹ": "Nhẹ",
            "trung_binh": "Trung bình",
            "trung bình": "Trung bình",
            "trung binh": "Trung bình",
            "nang": "Nặng",
            "nặng": "Nặng"
        }

        return label_map.get(label, label)

    except Exception as e:
        logger.warning(f"KNN chưa sẵn sàng hoặc predict lỗi, dùng fallback. Chi tiết: {e}")
        return self.fallback_label(order)

    def process_single_order(self, raw_order: Dict[str, Any]) -> Dict[str, Any]:
        start_time = time.perf_counter()

        order = self.preprocess_order(raw_order)
        order_id = order["order_id"]

        logger.info(f"Xử lý đơn: {order_id}")

        # 1. KNN -> label
        label = self.predict_label(order)

        # 2. Rule engine -> vehicle
        vehicle = self.rule_engine.assign_vehicle(order, label)

        elapsed = time.perf_counter() - start_time

        result = {
            "order_id": order["order_id"],
            "customer_name": order["customer_name"],
            "product_type": order["product_type"],
            "weight": order["weight"],
            "distance": order["distance"],
            "priority": order["priority"],
            "label": label,
            "assigned_vehicle": vehicle,
            "process_status": "done",
            "processed_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "processing_time": f"{elapsed:.3f}s"
        }

        logger.info(f"Kết quả: {result}")
        return result

    def batch_process(self, orders: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [self.process_single_order(order) for order in orders]


# HÀM ĐỂ NGƯỜI 3 IMPORT ĐÚNG
def process_order(raw_order: Dict[str, Any]):
    """
    Người 3 đang import hàm này từ socket_server.py
    Chỉ trả ra (label, vehicle) để giữ tương thích với socket_server hiện tại.
    """
    pipeline = OrderProcessingPipeline()
    result = pipeline.process_single_order(raw_order)
    return result["label"], result["assigned_vehicle"]


if __name__ == "__main__":
    pipeline = OrderProcessingPipeline()

    demo_orders = [
        {
            "order_id": "ORD001",
            "customer_name": "Nguyen Van A",
            "phone": "0909123456",
            "email": "a@gmail.com",
            "address": "Quan 1 TP.HCM",
            "product_type": "de_vo",
            "weight": 12.5,
            "length": 50,
            "width": 40,
            "height": 30,
            "distance": 8,
            "priority": "nhanh",
            "note": "Hang de vo"
        },
        {
            "order_id": "ORD002",
            "customer_name": "Tran Thi B",
            "phone": "0987654321",
            "email": "b@gmail.com",
            "address": "Quan 7 TP.HCM",
            "product_type": "tieu_chuan",
            "weight": 320,
            "length": 30,
            "width": 20,
            "height": 25,
            "distance": 150,
            "priority": "thuong",
            "note": ""
        }
    ]

    results = pipeline.batch_process(demo_orders)

    print("\nOUTPUT:")
    for result in results:
        print(result)

    os.makedirs("output", exist_ok=True)
    pd.DataFrame(results).to_csv("output/processed_orders.csv", index=False)
