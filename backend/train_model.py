import pandas as pd
import random
import os


def build_label(total_weight):
    """Phân loại dựa trên tổng khối lượng (weight × quantity)"""
    if total_weight < 200:
        return "Nhẹ"
    elif total_weight <= 1500:
        return "Trung bình"
    return "Nặng"


def assign_vehicle(label, total_weight, quantity, distance, length=0, width=0, height=0):
    """
    Rule base:
    - Xe máy      : kích thước ≤ 80×80×80 cm VÀ tổng KL < 100 kg
    - Xe tải      : Nhẹ / Trung bình không đủ điều kiện xe máy
    - Xe < 5 tấn  : Nặng và tổng KL ≤ 5000 kg
    - Xe đầu kéo  : Nặng và tổng KL > 5000 kg
    """
    fits_motorbike = (
        length <= 80 and width <= 80 and height <= 80 and total_weight < 100
    )

    if label == "Nhẹ":
        if fits_motorbike:
            return "Xe máy"
        return "Xe tải"

    if label == "Trung bình":
        return "Xe tải"

    if label == "Nặng":
        if total_weight <= 5000:
            return "Xe dưới 5 tấn"
        return "Xe đầu kéo / Container"

    return "Chưa xác định"


def generate_standard_logistics_data():
    os.makedirs("data", exist_ok=True)

    priorities = ["thuong", "nhanh", "hoa_toc"]
    data = []

    for i in range(1, 501):
        weight = round(random.uniform(1, 500), 2)
        quantity = random.randint(1, 20)
        total_weight = round(weight * quantity, 2)

        length = round(random.uniform(10, 200), 2)
        width = round(random.uniform(10, 150), 2)
        height = round(random.uniform(10, 150), 2)
        volume = round(length * width * height, 2)

        distance = random.randint(1, 1500)
        priority = random.choice(priorities)

        label = build_label(total_weight)
        vehicle_type = assign_vehicle(
            label, total_weight, quantity, distance,
            length=length, width=width, height=height
        )

        data.append({
            "order_id": f"ORD{i:03d}",
            "weight": weight,
            "quantity": quantity,
            "total_weight": total_weight,
            "length": length,
            "width": width,
            "height": height,
            "volume": volume,
            "distance": distance,
            "priority": priority,
            "label": label,
            "vehicle_type": vehicle_type,
            "note": "Giao hàng hệ thống"
        })

    df = pd.DataFrame(data)
    df.to_csv("data/orders_result_500.csv", index=False, encoding="utf-8-sig")

    print("✅ Đã tạo xong 500 dòng data chuẩn có gán nhãn")
    print(df["label"].value_counts())
    print(df["vehicle_type"].value_counts())
    print(df.head())


if __name__ == "__main__":
    generate_standard_logistics_data()
