import pandas as pd
import random

def knn_logic_real(weight, distance):
    # Logic phân loại sát thực tế Logistics
    if weight > 30:
        return "Xe Tải Hạng Nặng"
    elif weight > 10:
        if distance > 100:
            return "Xe Tải Hạng Nặng"
        return "Xe Tải Hạng Nhẹ"
    else: # weight <= 10
        if distance > 50:
            return "Xe Tải Hạng Nhẹ"
        return "Xe Máy"

def generate_real_logistics_data():
    cust_types = ['VIP', 'Thường', 'Đối tác']
    # Danh sách loại hàng thực tế
    prod_types = ['Linh kiện điện tử', 'Hàng đông lạnh', 'Hàng dễ vỡ', 'Nông sản', 'Mỹ phẩm', 'Đồ gia dụng']
    
    data = []
    for i in range(1, 501):
        # Tạo trọng lượng ngẫu nhiên từ 0.5kg đến 50kg
        w = round(random.uniform(0.5, 50.0), 2)
        
        # Tạo khoảng cách: hàng nặng thường đi xa, hàng nhẹ đi gần
        if w > 30:
            d = random.randint(50, 1000)
        else:
            d = random.randint(2, 200)
            
        result = knn_logic_real(w, d)
        
        data.append({
            'OrderID': i,
            'Product_Type': random.choice(prod_types),
            'Weight_kg': w,
            'Distance_km': d,
            'Vehicle_Type': result
        })
    
    df = pd.DataFrame(data)
    df.to_csv("data/orders_result_500.csv", index=False)
    
    print("-" * 50)
    print("🚀 ĐANG KHỞI TẠO 500 ĐƠN HÀNG LOGISTICS THỰC TẾ...")
    print(df.head(15)) # In 15 dòng để kiểm tra độ đa dạng
    print("-" * 50)
    print(f"✅ HOÀN TẤT! Đã lưu dữ liệu tại: data/orders_result_500.csv")

if __name__ == "__main__":
    generate_real_logistics_data()
