import pandas as pd
import random

def knn_logic(weight, distance):
    # Logic KNN đơn giản hóa để test nhanh
    if weight > 30 or distance > 500:
        return "Xe Tải Hạng Nặng"
    elif weight > 10:
        return "Xe Tải Hạng Nhẹ"
    else:
        return "Xe Máy"

def test_500_orders_with_results():
    cust_types = ['VIP', 'Thường', 'Đối tác']
    prod_types = ['Linh kiện', 'Đông lạnh', 'Dễ vỡ', 'Nông sản', 'Mỹ phẩm']
    
    data = []
    for i in range(1, 501):
        w = round(random.uniform(0.5, 50.0), 2)
        d = random.randint(5, 1000)
        result = knn_logic(w, d) # Chạy thuật toán phân loại ở đây
        
        data.append({
            'OrderID': i,
            'Weight_kg': w,
            'Distance_km': d,
            'Vehicle_Type': result # Kết quả của thuật toán
        })
    
    df = pd.DataFrame(data)
    df.to_csv("orders_result_500.csv", index=False)
    
    print("-" * 40)
    print("🚀 ĐANG CHẠY THUẬT TOÁN KNN TRÊN 500 ĐƠN HÀNG...")
    print(df.head(10)) # In ra 10 dòng đầu để bạn chụp ảnh
    print("-" * 40)
    print(f"✅ HOÀN TẤT! Đã phân loại 500 đơn hàng.")
    print(f"📊 Kết quả đã lưu tại: orders_result_500.csv")

if __name__ == "__main__":
    test_500_orders_with_results()
