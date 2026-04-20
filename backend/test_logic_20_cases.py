import logging


class RuleEngine:
    VEHICLE_RULES = {
        4: 'Xe tải lớn + VIP Service',
        3: 'Xe tải lớn (Container)',
        2: 'Xe tải trung bình',
        1: 'Xe tải nhỏ',
        0: 'Xe máy tải'
    }
    
    def apply_priority_rules(self, order):
        # 1. Ưu tiên khách hàng VIP hoặc hàng siêu nặng (> 10 tấn)
        if order.get('customer_type') in ['Đối tác chiến lược', 'VIP']: return 4
        if order['weight'] > 10: return 4
        
        # 2. Ưu tiên hàng đi đường dài (> 1000km)
        if order['distance'] > 1000: return 3
        
        # 3. Hàng đặc biệt (Đông lạnh, Dễ vỡ, Hóa chất) và nặng > 5 tấn
        special_types = ['Đông lạnh', 'Dễ vỡ', 'Hóa chất', 'Giá trị cao']
        if any(s in order['type'] for s in special_types) and order['weight'] > 5:
            return 3
            
        # 4. Phân loại theo trọng tải thông thường
        if 5 <= order['weight'] <= 10: return 2
        if 500 <= order['distance'] <= 1000: return 1
        
        return 0

    def classify_with_rules(self, order):
        priority = self.apply_priority_rules(order)
        vehicle = self.VEHICLE_RULES.get(priority, 'Xe máy tải')
        return {'vehicle': vehicle, 'priority': priority}

# --- PHẦN 2: BỘ 20 TEST CASES SIÊU THỰC TẾ (Đơn vị: Tấn) ---
def run_full_test():
    engine = RuleEngine()
    
    # Định dạng bảng
    header = f"{'STT':<4} | {'Khách hàng':<15} | {'Mặt hàng':<22} | {'Nặng (t)':<10} | {'KC (km)':<8} | {'Phương tiện gán'}"
    print("="*115)
    print(header)
    print("-"*115)

    test_data = [
        # NHÓM 4: XE TẢI LỚN + VIP (Ưu tiên đặc biệt hoặc > 10t)
        {'id': 1, 'c_type': 'VIP', 'type': 'Linh kiện iPhone 17', 'w': 0.05, 'd': 5},
        {'id': 2, 'c_type': 'Đối tác', 'type': 'Thiết bị y tế Siemens', 'w': 1.2, 'd': 50},
        {'id': 3, 'c_type': 'Thường', 'type': 'Sắt thép xây dựng', 'w': 12.0, 'd': 300},
        {'id': 4, 'c_type': 'Thường', 'type': 'Máy biến áp công nghiệp', 'w': 25.0, 'd': 800},

        # NHÓM 3: XE TẢI LỚN - CONTAINER (Đường trường hoặc Hàng đặc biệt > 5t)
        {'id': 5, 'c_type': 'Thường', 'type': 'Vải cuộn xuất khẩu', 'w': 2.5, 'd': 1200},
        {'id': 6, 'c_type': 'Thường', 'type': 'Thanh long đông lạnh', 'w': 6.0, 'd': 350},
        {'id': 7, 'c_type': 'Thường', 'type': 'Bình gốm Chu Đậu (Dễ vỡ)', 'w': 5.5, 'd': 150},
        {'id': 8, 'c_type': 'Thường', 'type': 'Thùng hóa chất lỏng', 'w': 8.0, 'd': 450},

        # NHÓM 2: XE TẢI TRUNG BÌNH (Tải trọng 5 - 10 tấn)
        {'id': 9, 'c_type': 'Thường', 'type': 'Gạo bao ST25 (200 bao)', 'w': 5.0, 'd': 100},
        {'id': 10, 'c_type': 'Thường', 'type': 'Thức ăn chăn nuôi CP', 'w': 7.5, 'd': 250},
        {'id': 11, 'c_type': 'Thường', 'type': 'Gạch men lát nền', 'w': 9.5, 'd': 300},
        {'id': 12, 'c_type': 'Thường', 'type': 'Nước khoáng đóng chai', 'w': 6.8, 'd': 120},

        # NHÓM 1: XE TẢI NHỎ (Đường xa 500-1000km, tải nhẹ)
        {'id': 13, 'c_type': 'Thường', 'type': 'Đồ điện gia dụng LG', 'w': 1.5, 'd': 600},
        {'id': 14, 'c_type': 'Thường', 'type': 'Sách vở & Văn phòng phẩm', 'w': 2.2, 'd': 850},
        {'id': 15, 'c_type': 'Thường', 'type': 'Phụ tùng xe máy Honda', 'w': 3.5, 'd': 550},

        # NHÓM 0: XE MÁY TẢI (Hàng lẻ, giao nhanh nội thành)
        {'id': 16, 'c_type': 'Thường', 'type': 'Pizza & Thức ăn nhanh', 'w': 0.005, 'd': 3},  # 5kg
        {'id': 17, 'c_type': 'Thường', 'type': 'Mỹ phẩm & Thời trang', 'w': 0.02, 'd': 12},   # 20kg
        {'id': 18, 'c_type': 'Thường', 'type': 'Hồ sơ chứng từ gốc', 'w': 0.001, 'd': 5},     # 1kg
        {'id': 19, 'c_type': 'Thường', 'type': 'Điện thoại di động', 'w': 0.01, 'd': 8},      # 10kg
        {'id': 20, 'c_type': 'Thường', 'type': 'Thùng trái cây sạch', 'w': 0.05, 'd': 20},    # 50kg
    ]

    for d in test_data:
        # Chuẩn bị dữ liệu đầu vào cho engine
        order = {
            'customer_type': d['c_type'],
            'type': d['type'],
            'weight': d['w'],
            'distance': d['d'],
            'id': f"ORDER_{d['id']}"
        }
        
        result = engine.classify_with_rules(order)
        actual = result['vehicle']
        
        # In kết quả theo bảng
        print(f"{d['id']:<4} | {d['c_type']:<15} | {d['type']:<22} | {d['w']:<10} | {d['d']:<8} | {actual}")

    print("="*115)
    print("KIỂM THỬ HOÀN TẤT: Toàn bộ 20 kịch bản đã được thực thi.")

if __name__ == "__main__":
    run_full_test()
