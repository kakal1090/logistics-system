import pandas as pd
import random
import os

def knn_logic_standard(weight, distance):
  
    if weight > 30:
        return "xe_tai_hang_nang"
    elif weight > 10:
        return "xe_tai_hang_nhe" if distance <= 100 else "xe_tai_hang_nang"
    else:
        return "xe_may" if distance <= 50 else "xe_tai_hang_nhe"

def generate_standard_logistics_data():
    # 1. CHUẨN HÓA DANH MỤC: 
    cust_types = ['VIP', 'thuong', 'doi_tac']
    prod_types = ['linh_kien_dien_tu', 'dong_lanh', 'de_vo', 'nong_san', 'my_pham', 'do_gia_dung']
    priorities = ['nhanh', 'trung_binh', 'thap']
    
    data = []
    
   
    if not os.path.exists('data'):
        os.makedirs('data')

    for i in range(1, 501):
        # Tạo trọng lượng và khoảng cách ngẫu nhiên
        w = round(random.uniform(0.5, 50.0), 2)
        d = random.randint(2, 1000)
        
        # Chạy thuật toán phân loại
        v_type = knn_logic_standard(w, d)
        
        # Chọn khách hàng ngẫu nhiên
        customer = random.choice(cust_types)
        
        # 2. CHUẨN HÓA KEY & DATA
        data.append({
            'order_id': f"ORD{i:03d}",         # Định dạng chuẩn: ORD001, ORD002...
            'customer_type': customer,
            'product_type': random.choice(prod_types),
            'weight': w,
            'distance': d,
            # Logic Priority: Khách VIP luôn ưu tiên Giao nhanh
            'priority': 'nhanh' if customer == 'VIP' else random.choice(['trung_binh', 'thap']),
            'vehicle_type': v_type,
            'note': 'Giao hàng hệ thống'
        })
    
    # Tạo DataFrame
    df = pd.DataFrame(data)
    
    # 3. XUẤT FILE: Dùng utf-8-sig để mở Excel không bị lỗi font
    file_path = "data/orders_result_500.csv"
    df.to_csv(file_path, index=False, encoding='utf-8-sig')
    
    print("-" * 60)
    print("🚀 ĐÃ HOÀN TẤT CHUẨN HÓA 500 ĐƠN HÀNG")
    print(df.head(15)) # In 15 dòng để check format cột và dữ liệu
    print("-" * 60)
    print(f"✅ File sạch đã sẵn sàng tại: {file_path}")

if __name__ == "__main__":
    generate_standard_logistics_data()
