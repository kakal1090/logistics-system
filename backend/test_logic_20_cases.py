# --- PHẦN 1: BỘ NÃO PHÂN LOẠI (RULE ENGINE) ---
class RuleEngine:
    VEHICLE_RULES = {
        4: 'Xe tải lớn + VIP Service',
        3: 'Xe tải lớn (Container)',
        2: 'Xe tải trung bình',
        1: 'Xe tải nhỏ',
        0: 'Xe máy tải'
    }
    
    def apply_priority_rules(self, order):
        # Kiểm tra dữ liệu lỗi trước khi xử lý
        if order['weight'] <= 0 or order['distance'] < 0:
            return -1 # Mã lỗi cho dữ liệu không hợp lệ
            
        if order.get('customer_type') in ['Đối tác chiến lược', 'VIP']: return 4
        if order['weight'] > 10: return 4
        if order['distance'] > 1000: return 3
        
        # Rule hàng đặc biệt (Phải nặng trên 5 tấn mới đi Container)
        special_types = ['Đông lạnh', 'Dễ vỡ', 'Giá trị cao', 'Hóa chất']
        if any(s in order['type'] for s in special_types) and order['weight'] > 5:
            return 3
            
        if 5 <= order['weight'] <= 10: return 2
        if 500 <= order['distance'] <= 1000: return 1
        return 0

    def classify(self, order):
        p = self.apply_priority_rules(order)
        if p == -1: return "LỖI: Dữ liệu không hợp lệ"
        return self.VEHICLE_RULES.get(p, 'Xe máy tải')

# --- PHẦN 2: BỘ 20 CASES KIỂM THỬ CHUYÊN SÂU  ---
def run_test():
    engine = RuleEngine()
    print("="*115)
    print(f"{'STT':<4} | {'Khách hàng':<15} | {'Loại hàng hóa':<22} | {'Nặng(t)':<8} | {'KC(km)':<8} | {'Kết quả máy test'}")
    print("="*115)

    test_data = [
        # Nhóm 1: Hàng Đặc Biệt (Đông lạnh, Dễ vỡ...) -> Xe Container
        {'id': 1, 'c_type': 'Thường', 'type': 'Tôm hùm ĐÔNG LẠNH', 'w': 6.5, 'd': 100},
        {'id': 2, 'c_type': 'Thường', 'type': 'Vắc xin ĐÔNG LẠNH', 'w': 5.2, 'd': 50},
        {'id': 3, 'c_type': 'Thường', 'type': 'Gốm sứ DỄ VỠ', 'w': 7.0, 'd': 200},
        {'id': 4, 'c_type': 'Thường', 'type': 'Hóa chất NGUY HIỂM', 'w': 8.5, 'd': 300},

        # Nhóm 2: Khách VIP & Hàng siêu nặng -> Xe VIP Service
        {'id': 5, 'c_type': 'VIP', 'type': 'Linh kiện điện tử', 'w': 0.5, 'd': 10},
        {'id': 6, 'c_type': 'Đối tác', 'type': 'Nông sản xuất khẩu', 'w': 2.0, 'd': 50},
        {'id': 7, 'c_type': 'Thường', 'type': 'Máy công nghiệp', 'w': 15.0, 'd': 200},
        {'id': 8, 'c_type': 'Thường', 'type': 'Sắt thép Hòa Phát', 'w': 12.5, 'd': 400},

        # Nhóm 3: Đường dài (> 1000km) -> Xe Container
        {'id': 9, 'c_type': 'Thường', 'type': 'Giày da xuất khẩu', 'w': 2.0, 'd': 1500},
        {'id': 10, 'c_type': 'Thường', 'type': 'Hàng gia dụng', 'w': 1.5, 'd': 1200},

        # Nhóm 4: Hàng nặng thông thường (5 - 10 tấn) -> Xe trung bình
        {'id': 11, 'c_type': 'Thường', 'type': 'Gạo bao ST25', 'w': 6.0, 'd': 100},
        {'id': 12, 'c_type': 'Thường', 'type': 'Nước giải khát', 'w': 8.0, 'd': 50},

        # Nhóm 5: Hàng nhẹ đường xa (500-1000km) -> Xe tải nhỏ
        {'id': 13, 'c_type': 'Thường', 'type': 'Phụ tùng máy móc', 'w': 2.0, 'd': 600},
        {'id': 14, 'c_type': 'Thường', 'type': 'Văn phòng phẩm', 'w': 1.0, 'd': 800},

        # Nhóm 6: Hàng tiêu dùng nhanh -> Xe máy
        {'id': 15, 'c_type': 'Thường', 'type': 'Thực phẩm giao nhanh', 'w': 0.02, 'd': 5},
        {'id': 16, 'c_type': 'Thường', 'type': 'Mỹ phẩm Hanayuki', 'w': 0.1, 'd': 10},
        {'id': 17, 'c_type': 'Thường', 'type': 'Quần áo Shopee', 'w': 0.05, 'd': 20},

        # Nhóm 7: TEST LỖI (Dữ liệu không hợp lệ) 
        {'id': 18, 'c_type': 'Thường', 'type': 'Sai lệch trọng tải', 'w': -5.0, 'd': 100}, # Cân âm
        {'id': 19, 'c_type': 'Thường', 'type': 'Chưa khai báo trọng tải', 'w': 0, 'd': 50},       # Cân bằng 0
        {'id': 20, 'c_type': 'Thường', 'type': 'Lỗi định vị', 'w': 1.0, 'd': -10},  # KC âm
    ]

    for d in test_data:
        res = engine.classify({'customer_type': d['c_type'], 'type': d['type'], 'weight': d['w'], 'distance': d['d']})
        print(f"{d['id']:<4} | {d['c_type']:<15} | {d['type']:<22} | {d['w']:<8} | {d['d']:<8} | {res}")

if __name__ == "__main__":
    run_test()
