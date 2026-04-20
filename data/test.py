import pandas as pd
import random
import os

def create_and_test_500_orders():
    cust_types = ['VIP', 'Thường', 'Đối tác']
    prod_types = ['Linh kiện điện tử', 'Hàng ĐÔNG LẠNH', 'Gốm sứ DỄ VỠ', 'Nông sản ST25', 'Mỹ phẩm', 'Sắt thép']
    
    data = []
    for i in range(1, 501):
        data.append({
            'id': i,
            'customer_type': random.choice(cust_types),
            'product_type': random.choice(prod_types),
            'weight': round(random.uniform(0.1, 50.0), 2),
            'distance': random.randint(5, 1500)
        })
    
    df = pd.DataFrame(data)
    # Lưu file ngay tại thư mục đang đứng để tránh lỗi folder data
    file_name = "orders_final_500.csv"
    df.to_csv(file_name, index=False)
    
    print("-" * 30)
    print(f"✅ Đã tạo thành công file: {file_name}")
    print(f"📊 Tổng cộng: {len(df)} đơn hàng đã được chuẩn hóa.")
    print("🚀 Dữ liệu đã sẵn sàng cho báo cáo và demo!")
    print("-" * 30)

if __name__ == "__main__":
    create_and_test_500_orders()
