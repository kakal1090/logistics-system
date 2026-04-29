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
    Input -> preprocess -> KNN tham khảo -> Rule chuẩn chốt label -> RuleEngine gán xe.

    Lưu ý:
    - Label cuối cùng được chốt theo total_weight để đảm bảo:
        < 200       -> Nhẹ
        200 - 1500  -> Trung bình
        > 1500      -> Nặng
    - KNN không được phép làm sai rule chuẩn này.
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
        Feature dùng cho KNN tham khảo.
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
        Chốt label cuối cùng theo rule chuẩn.

        Case bạn đang lỗi:
            weight = 2
            quantity = 231
            total_weight = 462
            -> bắt buộc là Trung bình
        """

        total_weight = float(order.get("total_weight", 0))

        # Label chuẩn, không cho KNN làm sai nhóm Trung bình
        if total_weight < 200:
            final_label = "Nhẹ"
        elif total_weight <= 1500:
            final_label = "Trung bình"
        else:
            final_label = "Nặng"

        # KNN chỉ log tham khảo
        try:
            features = self.build_knn_features(order)
            predictions, probabilities = self.knn_classifier.predict(features)

            knn_label = str(predictions[0]).strip()
            confidence = float(probabilities[0])

            logger.info(
                f"KNN dự đoán={knn_label}, confidence={confidence:.2f} | "
                f"Rule chốt={final_label}, total_weight={total_weight:.2f}"
            )

        except Exception as e:
            logger.warning(f"KNN lỗi hoặc chưa có model, dùng rule chuẩn: {e}")

        return final_label

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


def process_order(raw_order: Dict[str, Any]):
    """
    Hàm cho socket_server.py import.
    Trả về tuple: (label, vehicle)
    """

    pipeline = OrderProcessingPipeline()
    result = pipeline.process_single_order(raw_order)

    return result["label"], result["assigned_vehicle"]


if __name__ == "__main__":
    pipeline = OrderProcessingPipeline()

    demo_orders = [
        {
            "order_id": "TEST_LIGHT",
            "customer_name": "Nguyen Van A",
            "phone": "0909123456",
            "email": "a@gmail.com",
            "address": "TP.HCM",
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
            "order_id": "TEST_MEDIUM",
            "customer_name": "Nguyen Van B",
            "phone": "0966112419",
            "email": "b@gmail.com",
            "address": "TP.HCM",
            "product_type": "linh_kien_dien_tu",
            "weight": 2,
            "quantity": 231,
            "length": 22,
            "width": 44,
            "height": 33,
            "distance": 33,
            "priority": "thuong",
            "note": "Test trung bình",
        },
        {
            "order_id": "TEST_HEAVY",
            "customer_name": "Tran Thi C",
            "phone": "0987654321",
            "email": "c@gmail.com",
            "address": "TP.HCM",
            "product_type": "tieu_chuan",
            "weight": 200,
            "quantity": 10,
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
    pd.DataFrame(results).to_csv(
        "output/processed_orders.csv",
        index=False,
        encoding="utf-8-sig",
    )
