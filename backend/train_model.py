import pandas as pd
import random
import os


def build_label(total_weight):
    if total_weight < 200:
        return "Nhẹ"
    elif total_weight <= 1500:
        return "Trung bình"
    return "Nặng"


def assign_vehicle(label, total_weight, quantity, distance):
    if label == "Nhẹ":
        if total_weight < 15 and quantity <= 3 and distance <= 10:
            return "Xe máy"
        return "Xe tải van"

    if label == "Trung bình":
        return "Xe tải 1.5 tấn"

    if label == "Nặng":
        if total_weight <= 5000:
            return "Xe tải dưới 5 tấn"
        return "Xe đầu kéo / Container"

    return "Chưa xác định"


def generate_standard_logistics_data():
    os.makedirs("data", exist_ok=True)

    priorities = ["thuong", "nhanh", "hoa_toc"]
    data = []

    for i in range(1, 501):
        weight = round(random.uniform(1, 2000), 2)
        quantity = random.randint(1, 20)
        total_weight = round(weight * quantity, 2)

        length = round(random.uniform(10, 200), 2)
        width = round(random.uniform(10, 150), 2)
        height = round(random.uniform(10, 150), 2)
        volume = round(length * width * height, 2)

        distance = random.randint(1, 1500)
        priority = random.choice(priorities)

        label = build_label(total_weight)
        vehicle_type = assign_vehicle(label, total_weight, quantity, distance)

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
    print(df.head())


if __name__ == "__main__":
    generate_standard_logistics_data()
