"""
Test 20 cases cho hệ thống phân loại đơn hàng vận tải.

Tiêu chí phân loại:
    Label dựa trên total_weight = weight × quantity:
        < 200 kg       → Nhẹ
        200 – 1500 kg  → Trung bình
        > 1500 kg      → Nặng

    Rule gán phương tiện:
        Xe máy          : tất cả 3 chiều ≤ 80 cm VÀ total_weight < 100 kg
        Xe tải          : Nhẹ / Trung bình không đủ điều kiện xe máy
        Xe dưới 5 tấn   : Nặng, total_weight ≤ 5000 kg
        Xe đầu kéo      : Nặng, total_weight > 5000 kg
"""


class RuleEngine:
    # ---------- helpers ----------
    @staticmethod
    def _build_label(total_weight: float) -> str:
        if total_weight < 200:
            return "Nhẹ"
        elif total_weight <= 1500:
            return "Trung bình"
        return "Nặng"

    @staticmethod
    def _fits_motorbike(length, width, height, total_weight) -> bool:
        return length <= 80 and width <= 80 and height <= 80 and total_weight < 100

    # ---------- classify ----------
    def classify(self, order: dict):
        # --- validate ---
        if order["weight"] < 0:
            return "LỖI: Trọng tải âm (-)"
        if order["weight"] == 0:
            return "LỖI: Trọng tải bằng 0"
        if order["distance"] < 0:
            return "LỖI: Khoảng cách âm (-)"
        if order.get("quantity", 1) <= 0:
            return "LỖI: Số lượng không hợp lệ"

        quantity     = order.get("quantity", 1)
        total_weight = order["weight"] * quantity
        label        = self._build_label(total_weight)

        length = order.get("length", 0)
        width  = order.get("width",  0)
        height = order.get("height", 0)

        if label == "Nhẹ":
            if self._fits_motorbike(length, width, height, total_weight):
                vehicle = "Xe máy"
            else:
                vehicle = "Xe tải"

        elif label == "Trung bình":
            vehicle = "Xe tải"

        else:  # Nặng
            if total_weight <= 5000:
                vehicle = "Xe dưới 5 tấn"
            else:
                vehicle = "Xe đầu kéo / Container"

        return f"{label} → {vehicle}"


# ──────────────────────────────────────────────
# 20 TEST CASES
# ──────────────────────────────────────────────
def run_test():
    engine = RuleEngine()

    # Mỗi case: order_id, weight, quantity, length, width, height, distance, priority, note, expected
    test_data = [
        # ── Nhóm 1: Xe máy (kích thước ≤ 80×80×80, total_weight < 100 kg) ──
        {
            "order_id": "ORD001", "weight": 10, "quantity": 2,
            "length": 50, "width": 40, "height": 30, "distance": 8,
            "priority": "nhanh", "note": "Đơn nhỏ đủ điều kiện xe máy",
            "expected": "Nhẹ → Xe máy",
        },
        {
            "order_id": "ORD002", "weight": 5, "quantity": 5,
            "length": 80, "width": 80, "height": 80, "distance": 15,
            "priority": "thuong", "note": "Đúng biên 80cm, total=25kg",
            "expected": "Nhẹ → Xe máy",
        },
        {
            "order_id": "ORD003", "weight": 30, "quantity": 3,
            "length": 70, "width": 60, "height": 50, "distance": 5,
            "priority": "nhanh", "note": "total=90kg < 100, kích thước OK",
            "expected": "Nhẹ → Xe máy",
        },

        # ── Nhóm 2: Nhẹ nhưng KHÔNG đủ điều kiện xe máy → Xe tải ──
        {
            "order_id": "ORD004", "weight": 20, "quantity": 3,
            "length": 100, "width": 40, "height": 30, "distance": 20,
            "priority": "nhanh", "note": "length > 80 → xe tải",
            "expected": "Nhẹ → Xe tải",
        },
        {
            "order_id": "ORD005", "weight": 50, "quantity": 3,
            "length": 70, "width": 60, "height": 50, "distance": 30,
            "priority": "thuong", "note": "total=150kg >= 100 → xe tải",
            "expected": "Nhẹ → Xe tải",
        },
        {
            "order_id": "ORD006", "weight": 15, "quantity": 8,
            "length": 60, "width": 50, "height": 90, "distance": 25,
            "priority": "hoa_toc", "note": "height > 80 → xe tải dù nhẹ",
            "expected": "Nhẹ → Xe tải",
        },
        {
            "order_id": "ORD007", "weight": 10, "quantity": 10,
            "length": 50, "width": 50, "height": 50, "distance": 50,
            "priority": "nhanh", "note": "total=100kg, không < 100 → xe tải",
            "expected": "Nhẹ → Xe tải",
        },

        # ── Nhóm 3: Trung bình → Xe tải ──
        {
            "order_id": "ORD008", "weight": 50, "quantity": 5,
            "length": 60, "width": 60, "height": 60, "distance": 100,
            "priority": "thuong", "note": "total=250kg → Trung bình",
            "expected": "Trung bình → Xe tải",
        },
        {
            "order_id": "ORD009", "weight": 100, "quantity": 8,
            "length": 80, "width": 80, "height": 70, "distance": 200,
            "priority": "nhanh", "note": "total=800kg → Trung bình",
            "expected": "Trung bình → Xe tải",
        },
        {
            "order_id": "ORD010", "weight": 200, "quantity": 7,
            "length": 100, "width": 90, "height": 80, "distance": 350,
            "priority": "thuong", "note": "total=1400kg ≤ 1500 → Trung bình",
            "expected": "Trung bình → Xe tải",
        },

        # ── Nhóm 4: Nặng, total ≤ 5000 → Xe dưới 5 tấn ──
        {
            "order_id": "ORD011", "weight": 200, "quantity": 10,
            "length": 120, "width": 100, "height": 90, "distance": 300,
            "priority": "thuong", "note": "total=2000kg → Nặng",
            "expected": "Nặng → Xe dưới 5 tấn",
        },
        {
            "order_id": "ORD012", "weight": 300, "quantity": 8,
            "length": 150, "width": 120, "height": 100, "distance": 400,
            "priority": "nhanh", "note": "total=2400kg → Nặng",
            "expected": "Nặng → Xe dưới 5 tấn",
        },
        {
            "order_id": "ORD013", "weight": 500, "quantity": 9,
            "length": 180, "width": 150, "height": 120, "distance": 500,
            "priority": "thuong", "note": "total=4500kg ≤ 5000 → Nặng",
            "expected": "Nặng → Xe dưới 5 tấn",
        },

        # ── Nhóm 5: Nặng, total > 5000 → Xe đầu kéo ──
        {
            "order_id": "ORD014", "weight": 400, "quantity": 15,
            "length": 200, "width": 150, "height": 150, "distance": 700,
            "priority": "thuong", "note": "total=6000kg → Xe đầu kéo",
            "expected": "Nặng → Xe đầu kéo / Container",
        },
        {
            "order_id": "ORD015", "weight": 600, "quantity": 12,
            "length": 200, "width": 180, "height": 160, "distance": 1000,
            "priority": "thuong", "note": "total=7200kg → Xe đầu kéo",
            "expected": "Nặng → Xe đầu kéo / Container",
        },
        {
            "order_id": "ORD016", "weight": 1000, "quantity": 20,
            "length": 200, "width": 200, "height": 200, "distance": 1500,
            "priority": "thuong", "note": "total=20000kg → Xe đầu kéo",
            "expected": "Nặng → Xe đầu kéo / Container",
        },

        # ── Nhóm 6: Biên giới giữa các nhãn ──
        {
            "order_id": "ORD017", "weight": 199, "quantity": 1,
            "length": 50, "width": 50, "height": 50, "distance": 10,
            "priority": "nhanh", "note": "total=199kg nhưng ≥ 100 → xe tải dù kích thước OK",
            "expected": "Nhẹ → Xe tải",
        },
        {
            "order_id": "ORD018", "weight": 200, "quantity": 1,
            "length": 50, "width": 50, "height": 50, "distance": 10,
            "priority": "nhanh", "note": "total=200kg biên Trung bình",
            "expected": "Trung bình → Xe tải",
        },
        # ── Nhóm 7: Lỗi dữ liệu ──
        {
            "order_id": "ORD019", "weight": -5, "quantity": 1,
            "length": 50, "width": 40, "height": 30, "distance": 100,
            "priority": "invalid", "note": "Trọng tải âm",
            "expected": "LỖI: Trọng tải âm (-)",
        },
        {
            "order_id": "ORD020", "weight": 0, "quantity": 1,
            "length": 50, "width": 40, "height": 30, "distance": 50,
            "priority": "invalid", "note": "Trọng tải bằng 0",
            "expected": "LỖI: Trọng tải bằng 0",
        },
    ]

    # ── Header ──
    w = [8, 8, 4, 6, 6, 6, 6, 8, 8, 35, 30]
    header = (
        f"{'Order ID':<{w[0]}} | {'Total KL':>{w[1]}} | {'SL':>{w[2]}} | "
        f"{'L':>{w[3]}} | {'W':>{w[4]}} | {'H':>{w[5]}} | {'Dist':>{w[6]}} | "
        f"{'Ưu tiên':<{w[7]}} | {'Kết quả':<{w[8]}} | {'Expected':<{w[9]}} | {'Status'}"
    )
    print("=" * len(header))
    print(header)
    print("=" * len(header))

    passed = 0
    failed = 0

    for d in test_data:
        qty   = d.get("quantity", 1)
        tw    = d["weight"] * qty if d["weight"] >= 0 else d["weight"]  # giữ âm để lỗi
        result = engine.classify(d)

        status = "✅ PASS" if result == d["expected"] else "❌ FAIL"
        if result == d["expected"]:
            passed += 1
        else:
            failed += 1

        tw_display = f"{tw:.0f}kg" if d["weight"] > 0 else f"{tw}"

        print(
            f"{d['order_id']:<{w[0]}} | {tw_display:>{w[1]}} | {qty:>{w[2]}} | "
            f"{d.get('length',0):>{w[3]}} | {d.get('width',0):>{w[4]}} | "
            f"{d.get('height',0):>{w[5]}} | {d['distance']:>{w[6]}} | "
            f"{d['priority']:<{w[7]}} | {result:<{w[8]}} | {d['expected']:<{w[9]}} | {status}"
        )

    print("=" * len(header))
    print(f"Tổng: {len(test_data)} | ✅ PASS: {passed} | ❌ FAIL: {failed}")


if __name__ == "__main__":
    run_test()
