# --- PHẦN 1: BỘ NÃO PHÂN LOẠI (RULE ENGINE) ĐÃ CHUẨN HÓA ---
class RuleEngine:
    VEHICLE_RULES = {
        4: 'xe_tai_lon_vip',
        3: 'xe_tai_lon_container',
        2: 'xe_tai_trung_binh',
        1: 'xe_tai_nho',
        0: 'xe_may_tai'
    }
    
    def apply_priority_rules(self, order):
        # Kiểm tra dữ liệu lỗi theo logic chuẩn
        if order['weight'] <= 0 or order['distance'] < 0:
            return -1 
            
        # Thống nhất giá trị so sánh: VIP, doi_tac
        if order.get('customer_type') in ['doi_tac', 'VIP']: return 4
        if order['weight'] > 10: return 4
        if order['distance'] > 1000: return 3
        
        # Thống nhất loại hàng hóa viết thường, không dấu
        special_types = ['dong_lanh', 'de_vo', 'gia_tri_cao', 'hoa_chat']
        if any(s in order['product_type'] for s in special_types) and order['weight'] > 5:
            return 3
            
        if 5 <= order['weight'] <= 10: return 2
        if 500 <= order['distance'] <= 1000: return 1
        return 0

    def classify(self, order):
        p = self.apply_priority_rules(order)
        if p == -1: return "LỖI: Dữ liệu không hợp lệ"
        return self.VEHICLE_RULES.get(p, 'xe_may_tai')

# --- PHẦN 2: BỘ 20 CASES KIỂM THỬ ĐÃ CHUẨN HÓA ---
def run_test():
    engine = RuleEngine()
    print("="*115)
    print(f"{'STT':<4} | {'Khách hàng':<10} | {'Loại hàng hóa':<20} | {'Nặng(t)':<8} | {'KC(km)':<8} | {'Kết quả'}")
    print("="*115)

    test_data = [
        # Nhóm 1: Hàng Đặc Biệt -> snake_case giá trị
        {'order_id': 'ORD_T1', 'customer_type': 'thuong', 'product_type': 'dong_lanh', 'weight': 6.5, 'distance': 100, 'priority': 'trung_binh'},
        {'order_id': 'ORD_T2', 'customer_type': 'thuong', 'product_type': 'dong_lanh', 'weight': 5.2, 'distance': 50, 'priority': 'trung_binh'},
        {'order_id': 'ORD_T3', 'customer_type': 'thuong', 'product_type': 'de_vo', 'weight': 7.0, 'distance': 200, 'priority': 'trung_binh'},
        {'order_id': 'ORD_T4', 'customer_type': 'thuong', 'product_type': 'hoa_chat', 'weight': 8.5, 'distance': 300, 'priority': 'nhanh'},

        # Nhóm 2: Khách VIP & Đối tác
        {'order_id': 'ORD_T5', 'customer_type': 'VIP', 'product_type': 'linh_kien_dien_tu', 'weight': 0.5, 'distance': 10, 'priority': 'nhanh'},
        {'order_id': 'ORD_T6', 'customer_type': 'doi_tac', 'product_type': 'nong_san', 'weight': 2.0, 'distance': 50, 'priority': 'nhanh'},
        {'order_id': 'ORD_T7', 'customer_type': 'thuong', 'product_type': 'do_gia_dung', 'weight': 15.0, 'distance': 200, 'priority': 'trung_binh'},

        # Nhóm 3: Đường dài
        {'order_id': 'ORD_T9', 'customer_type': 'thuong', 'product_type': 'my_pham', 'weight': 2.0, 'distance': 1500, 'priority': 'thap'},

        # Nhóm 7: TEST LỖI
        {'order_id': 'ORD_T18', 'customer_type': 'thuong', 'product_type': 'nong_san', 'weight': -5.0, 'distance': 100, 'priority': 'thap'},
        {'order_id': 'ORD_T19', 'customer_type': 'thuong', 'product_type': 'nong_san', 'weight': 0, 'distance': 50, 'priority': 'thap'},
    ]

    for d in test_data:
        # Gọi hàm classify với các key đã chuẩn hóa
        res = engine.classify({
            'customer_type': d['customer_type'], 
            'product_type': d['product_type'], 
            'weight': d['weight'], 
            'distance': d['distance']
        })
        print(f"{d['order_id']:<4} | {d['customer_type']:<10} | {d['product_type']:<20} | {d['weight']:<8} | {d['distance']:<8} | {res}")

if __name__ == "__main__":
    run_test()
