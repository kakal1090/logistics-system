# --- PHẦN 1: BỘ NÃO PHÂN LOẠI (RULE ENGINE) ---
class RuleEngine:
    VEHICLE_RULES = {
        4: 'xe_tai_lon_vip',
        3: 'xe_tai_lon_container',
        2: 'xe_tai_trung_binh',
        1: 'xe_tai_nho',
        0: 'xe_may_tai'
    }
    
    def classify(self, order):
        # BẮT LỖI CHI TIẾT THEO TỪNG TRƯỜNG HỢP (Chỉ điểm lỗi)
        if order['weight'] < 0:
            return "LỖI: Trọng tải âm (-)"
        if order['weight'] == 0:
            return "LỖI: Trọng tải bằng 0"
        if order['distance'] < 0:
            return "LỖI: Khoảng cách âm (-)"
            
        # LOGIC PHÂN LOẠI
        p = 0
        if order.get('customer_type') in ['doi_tac', 'VIP'] or order['weight'] > 10:
            p = 4
        elif order['distance'] > 1000:
            p = 3
        else:
            specials = ['dong_lanh', 'de_vo', 'gia_tri_cao', 'hoa_chat']
            if any(s in order['product_type'] for s in specials) and order['weight'] > 5:
                p = 3
            elif 5 <= order['weight'] <= 10:
                p = 2
            elif 500 <= order['distance'] <= 1000:
                p = 1
        
        return self.VEHICLE_RULES.get(p, 'xe_may_tai')

# --- PHẦN 2: FULL 20 CASES KIỂM THỬ ---
def run_test():
    engine = RuleEngine()
    print("="*135)
    print(f"{'ID':<8} | {'Khách':<10} | {'Loại hàng':<18} | {'Nặng':<6} | {'KC':<6} | {'Ưu tiên':<10} | {'Kết quả máy test'}")
    print("="*135)

    test_data = [
        # Nhóm 1: Hàng Đặc Biệt
        {'order_id': 'ORD001', 'customer_type': 'thuong', 'product_type': 'dong_lanh', 'weight': 6.5, 'distance': 100, 'priority': 'trung_binh'},
        {'order_id': 'ORD002', 'customer_type': 'thuong', 'product_type': 'dong_lanh', 'weight': 5.2, 'distance': 50, 'priority': 'trung_binh'},
        {'order_id': 'ORD003', 'customer_type': 'thuong', 'product_type': 'de_vo', 'weight': 7.0, 'distance': 200, 'priority': 'trung_binh'},
        {'order_id': 'ORD004', 'customer_type': 'thuong', 'product_type': 'hoa_chat', 'weight': 8.5, 'distance': 300, 'priority': 'nhanh'},

        # Nhóm 2: Khách VIP / Đối tác
        {'order_id': 'ORD005', 'customer_type': 'VIP', 'product_type': 'linh_kien_dien_tu', 'weight': 0.5, 'distance': 10, 'priority': 'nhanh'},
        {'order_id': 'ORD006', 'customer_type': 'doi_tac', 'product_type': 'nong_san', 'weight': 2.0, 'distance': 50, 'priority': 'nhanh'},
        {'order_id': 'ORD007', 'customer_type': 'thuong', 'product_type': 'do_gia_dung', 'weight': 15.0, 'distance': 200, 'priority': 'trung_binh'},
        {'order_id': 'ORD008', 'customer_type': 'thuong', 'product_type': 'do_gia_dung', 'weight': 12.5, 'distance': 400, 'priority': 'trung_binh'},

        # Nhóm 3: Đường dài
        {'order_id': 'ORD009', 'customer_type': 'thuong', 'product_type': 'my_pham', 'weight': 2.0, 'distance': 1500, 'priority': 'thap'},
        {'order_id': 'ORD010', 'customer_type': 'thuong', 'product_type': 'do_gia_dung', 'weight': 1.5, 'distance': 1200, 'priority': 'thap'},

        # Nhóm 4: Hàng nặng (5-10 tấn)
        {'order_id': 'ORD011', 'customer_type': 'thuong', 'product_type': 'nong_san', 'weight': 6.0, 'distance': 100, 'priority': 'trung_binh'},
        {'order_id': 'ORD012', 'customer_type': 'thuong', 'product_type': 'nong_san', 'weight': 8.0, 'distance': 50, 'priority': 'trung_binh'},

        # Nhóm 5: Hàng nhẹ đường xa
        {'order_id': 'ORD013', 'customer_type': 'thuong', 'product_type': 'do_gia_dung', 'weight': 2.0, 'distance': 600, 'priority': 'thap'},
        {'order_id': 'ORD014', 'customer_type': 'thuong', 'product_type': 'do_gia_dung', 'weight': 1.0, 'distance': 800, 'priority': 'thap'},

        # Nhóm 6: Hàng tiêu dùng nhanh
        {'order_id': 'ORD015', 'customer_type': 'thuong', 'product_type': 'nong_san', 'weight': 0.02, 'distance': 5, 'priority': 'nhanh'},
        {'order_id': 'ORD016', 'customer_type': 'thuong', 'product_type': 'my_pham', 'weight': 0.1, 'distance': 10, 'priority': 'nhanh'},
        {'order_id': 'ORD017', 'customer_type': 'thuong', 'product_type': 'my_pham', 'weight': 0.05, 'distance': 20, 'priority': 'nhanh'},

        # Nhóm 7: KIỂM TRA LỖI (Dữ liệu sai)
        {'order_id': 'ORD018', 'customer_type': 'error', 'product_type': 'nong_san', 'weight': -5.0, 'distance': 100, 'priority': 'invalid'},
        {'order_id': 'ORD019', 'customer_type': 'error', 'product_type': 'nong_san', 'weight': 0, 'distance': 50, 'priority': 'invalid'},
        {'order_id': 'ORD020', 'customer_type': 'error', 'product_type': 'nong_san', 'weight': 1.0, 'distance': -10, 'priority': 'invalid'},
    ]

    for d in test_data:
        res = engine.classify(d)
        print(f"{d['order_id']:<8} | {d['customer_type']:<10} | {d['product_type']:<18} | {d['weight']:<6} | {d['distance']:<6} | {d['priority']:<10} | {res}")

if __name__ == "__main__":
    run_test()
