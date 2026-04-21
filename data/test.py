import pandas as pd
import random
import os

def build_label(weight):
    if weight < 200:
        return "Nhẹ"
    elif weight < 1000:
        return "Trung bình"
    return "Nặng"

def assign_vehicle(label, product_type, weight, distance):
    if product_type == "dong_lanh":
        return "Xe lạnh"

    if product_type == "de_vo":
        if weight < 200:
            return "Xe Tải Van"
        return "Xe tải 1.5 tấn"

    if label == "Nhẹ":
        if weight < 15 and distance < 10:
            return "Xe máy"
        return "Xe Tải Van"
    elif label == "Trung bình":
        return "Xe tải 1.5 tấn"
    else:
        if weight <= 5000:
            return "Xe tải 5 tấn"
        return "Xe Đầu kéo / Container"

def generate_standard_logistics_data():
    cust_types = ["VIP", "thuong", "doi_tac"]
    prod_types = [
        "linh_kien_dien_tu",
        "dong_lanh",
        "de_vo",
        "nong_san",
        "my_pham",
        "do_gia_dung",
        "tieu_chuan",
        "cong_kenh",
        "nguy_hiem",
        "hang_tieu_dung"
    ]
    priorities = ["thuong", "nhanh", "hoa_toc"]

    data = []

    if not os.path.exists("data"):
        os.makedirs("data")

    for i in range(1, 501):
        weight = round(random.uniform(1, 3000), 2)
        distance = random.randint(2, 1500)

        length = round(random.uniform(10, 200), 2)
        width = round(random.uniform(10, 150), 2)
        height = round(random.uniform(10, 150), 2)

        customer = random.choice(cust_types)
        product_type = random.choice(prod_types)
        priority = "nhanh" if customer == "VIP" else random.choice(priorities)

        label = build_label(weight)
        vehicle_type = assign_vehicle(label, product_type, weight, distance)

        data.append({
            "order_id": f"ORD{i:03d}",
            "customer_type": customer,
            "product_type": product_type,
            "weight": weight,
            "length": length,
            "width": width,
            "height": height,
            "distance": distance,
            "priority": priority,
            "label": label,
            "vehicle_type": vehicle_type,
            "note": "Giao hàng hệ thống"
        })

    df = pd.DataFrame(data)
    file_path = "data/orders_result_500.csv"
    df.to_csv(file_path, index=False, encoding="utf-8-sig")

    print("✅ Đã tạo xong 500 dòng data chuẩn")
    print(df.head(10))
    print(f"📁 File: {file_path}")

if __name__ == "__main__":
    generate_standard_logistics_data()
