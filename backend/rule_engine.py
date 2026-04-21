from typing import Dict, Any


class RuleEngine:
    """Gán phương tiện theo label KNN + thông tin đơn hàng"""

    @staticmethod
    def _normalize_text(value: Any) -> str:
        return str(value).strip().lower() if value is not None else ""

    def classify_label(self, order: Dict[str, Any]) -> str:
        """
        Fallback khi chưa có KNN:
        < 200kg -> Nhẹ
        >= 200kg -> Nặng
        """
        weight = float(order.get("weight", 0))
        return "Nhe" if weight < 200 else "Nang"

    def assign_vehicle(self, order: Dict[str, Any], label: str | None = None) -> str:
        product_type = self._normalize_text(order.get("product_type"))
        weight = float(order.get("weight", 0))
        distance = float(order.get("distance", 0))

        if label is None:
            label = self.classify_label(order)

        # Rule đặc biệt theo loại hàng
        if product_type == "dong_lanh":
            return "Xe lạnh"

        if product_type == "de_vo":
            if weight < 200:
                return "Xe Tải Van"
            return "Xe tải 1.5 tấn"

        # Rule chính theo label + weight + distance
        if label.lower() in ["nhe", "nhẹ"]:
            if weight < 15 and distance < 10:
                return "Xe máy"
            return "Xe Tải Van"

        if weight <= 1500:
            return "Xe tải 1.5 tấn"
        elif weight <= 5000:
            return "Xe tải 5 tấn"
        else:
            return "Xe Đầu kéo / Container"

    def process(self, order: Dict[str, Any], label: str | None = None):
        if label is None:
            label = self.classify_label(order)
        vehicle = self.assign_vehicle(order, label)
        return label, vehicle


if __name__ == "__main__":
    engine = RuleEngine()
    test_order = {
        "order_id": "ORD001",
        "product_type": "de_vo",
        "weight": 12.5,
        "length": 50,
        "width": 40,
        "height": 30,
        "distance": 8,
        "priority": "nhanh"
    }

    label, vehicle = engine.process(test_order)
    print(f"Label: {label}, Vehicle: {vehicle}")
