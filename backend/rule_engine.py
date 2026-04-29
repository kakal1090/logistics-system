from typing import Dict, Any


class RuleEngine:
    """
    Gán phương tiện theo label KNN + thông tin đơn hàng.

    Label dựa trên total_weight = weight × quantity:
        < 200 kg        → Nhẹ
        200 – 1500 kg   → Trung bình
        > 1500 kg       → Nặng

    Rule base phương tiện:
        Xe máy           : tất cả 3 chiều ≤ 80 cm VÀ total_weight < 100 kg
        Xe tải           : Nhẹ / Trung bình không đủ điều kiện xe máy
        Xe dưới 5 tấn   : Nặng, total_weight ≤ 5000 kg
        Xe đầu kéo      : Nặng, total_weight > 5000 kg
    """

    @staticmethod
    def _normalize_text(value: Any) -> str:
        return str(value).strip().lower() if value is not None else ""

    def classify_label(self, order: Dict[str, Any]) -> str:
        """
        Tính nhãn dựa trên total_weight (weight × quantity).
        Fallback khi chưa có KNN.
        """
        weight = float(order.get("weight", 0))
        quantity = int(order.get("quantity", 1))
        total_weight = weight * quantity

        if total_weight < 200:
            return "Nhẹ"
        elif total_weight <= 1500:
            return "Trung bình"
        return "Nặng"

    def _fits_motorbike(self, order: Dict[str, Any]) -> bool:
        """Kiểm tra điều kiện kích thước và khối lượng cho xe máy."""
        length = float(order.get("length", 0))
        width  = float(order.get("width", 0))
        height = float(order.get("height", 0))
        weight   = float(order.get("weight", 0))
        quantity = int(order.get("quantity", 1))
        total_weight = weight * quantity

        return (
            length <= 80
            and width  <= 80
            and height <= 80
            and total_weight < 100
        )

    def assign_vehicle(self, order: Dict[str, Any], label: str | None = None) -> str:
        weight   = float(order.get("weight", 0))
        quantity = int(order.get("quantity", 1))
        total_weight = weight * quantity

        if label is None:
            label = self.classify_label(order)

        label_norm = self._normalize_text(label)

        if label_norm in ("nhẹ", "nhe"):
            if self._fits_motorbike(order):
                return "Xe máy"
            return "Xe tải"

        if label_norm in ("trung bình", "trung_binh", "trung binh"):
            return "Xe tải"

        # Nặng
        if total_weight <= 5000:
            return "Xe dưới 5 tấn"
        return "Xe đầu kéo / Container"

    def process(self, order: Dict[str, Any], label: str | None = None):
        if label is None:
            label = self.classify_label(order)
        vehicle = self.assign_vehicle(order, label)
        return label, vehicle


if __name__ == "__main__":
    engine = RuleEngine()

    test_cases = [
        # Xe máy: nhẹ + kích thước ≤ 80×80×80 + total_weight < 100
        {"order_id": "T01", "weight": 10, "quantity": 2, "length": 50, "width": 40, "height": 30, "distance": 8},
        # Xe tải: nhẹ nhưng kích thước vượt 80cm
        {"order_id": "T02", "weight": 10, "quantity": 2, "length": 100, "width": 40, "height": 30, "distance": 8},
        # Xe tải: Trung bình
        {"order_id": "T03", "weight": 50, "quantity": 5, "length": 60, "width": 60, "height": 60, "distance": 50},
        # Xe dưới 5 tấn: Nặng ≤ 5000
        {"order_id": "T04", "weight": 200, "quantity": 10, "length": 80, "width": 80, "height": 80, "distance": 100},
        # Xe đầu kéo: Nặng > 5000
        {"order_id": "T05", "weight": 500, "quantity": 15, "length": 200, "width": 150, "height": 150, "distance": 500},
    ]

    for o in test_cases:
        label, vehicle = engine.process(o)
        tw = o["weight"] * o["quantity"]
        print(f"{o['order_id']} | total_weight={tw:.0f}kg | label={label} | vehicle={vehicle}")
