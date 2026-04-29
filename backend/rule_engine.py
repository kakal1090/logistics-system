from typing import Dict, Any


class RuleEngine:
    """
    Rule chuẩn của hệ thống:

    Label dựa trên total_weight = weight × quantity:
        < 200 kg        -> Nhẹ
        200 – 1500 kg   -> Trung bình
        > 1500 kg       -> Nặng

    Gán phương tiện:
        Nhẹ + kích thước <= 80x80x80 + total_weight < 100 -> Xe máy
        Nhẹ còn lại -> Xe tải
        Trung bình -> Xe tải
        Nặng <= 5000kg -> Xe dưới 5 tấn
        Nặng > 5000kg -> Xe đầu kéo / Container
    """

    @staticmethod
    def _normalize_text(value: Any) -> str:
        return str(value).strip().lower() if value is not None else ""

    @staticmethod
    def _safe_float(value: Any, default: float = 0.0) -> float:
        try:
            if value in (None, ""):
                return default
            return float(value)
        except (ValueError, TypeError):
            return default

    @staticmethod
    def _safe_int(value: Any, default: int = 1) -> int:
        try:
            if value in (None, ""):
                return default
            return int(float(value))
        except (ValueError, TypeError):
            return default

    def get_total_weight(self, order: Dict[str, Any]) -> float:
        weight = self._safe_float(order.get("weight"), 0.0)
        quantity = self._safe_int(order.get("quantity"), 1)

        if quantity <= 0:
            quantity = 1

        return weight * quantity

    def classify_label(self, order: Dict[str, Any]) -> str:
        total_weight = self.get_total_weight(order)

        if total_weight < 200:
            return "Nhẹ"

        if total_weight <= 1500:
            return "Trung bình"

        return "Nặng"

    def _fits_motorbike(self, order: Dict[str, Any]) -> bool:
        length = self._safe_float(order.get("length"), 0.0)
        width = self._safe_float(order.get("width"), 0.0)
        height = self._safe_float(order.get("height"), 0.0)
        total_weight = self.get_total_weight(order)

        return (
            length <= 80
            and width <= 80
            and height <= 80
            and total_weight < 100
        )

    def assign_vehicle(self, order: Dict[str, Any], label: str | None = None) -> str:
        total_weight = self.get_total_weight(order)

        if label is None:
            label = self.classify_label(order)

        label_norm = self._normalize_text(label)

        if label_norm in ("nhẹ", "nhe", "light"):
            if self._fits_motorbike(order):
                return "Xe máy"
            return "Xe tải"

        if label_norm in ("trung bình", "trung_binh", "trung binh", "medium"):
            return "Xe tải"

        if label_norm in ("nặng", "nang", "heavy"):
            if total_weight <= 5000:
                return "Xe dưới 5 tấn"
            return "Xe đầu kéo / Container"

        # Nếu label lạ thì tự phân loại lại theo total_weight
        fixed_label = self.classify_label(order)
        return self.assign_vehicle(order, fixed_label)

    def process(self, order: Dict[str, Any], label: str | None = None):
        if label is None:
            label = self.classify_label(order)

        vehicle = self.assign_vehicle(order, label)
        return label, vehicle


if __name__ == "__main__":
    engine = RuleEngine()

    test_cases = [
        {"order_id": "TEST_LIGHT", "weight": 1, "quantity": 123, "length": 50, "width": 40, "height": 30, "distance": 8},
        {"order_id": "TEST_MEDIUM", "weight": 2, "quantity": 231, "length": 22, "width": 44, "height": 33, "distance": 33},
        {"order_id": "TEST_HEAVY", "weight": 200, "quantity": 10, "length": 120, "width": 100, "height": 90, "distance": 300},
    ]

    for order in test_cases:
        label, vehicle = engine.process(order)
        total_weight = engine.get_total_weight(order)
        print(
            f"{order['order_id']} | total_weight={total_weight:.2f}kg "
            f"| label={label} | vehicle={vehicle}"
        )
