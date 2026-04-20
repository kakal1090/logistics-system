from Demo.rule_engine import assign_vehicle

def run_20_test_cases():
    print("="*80)
    print(f"{'STT':<4} | {'Phân loại':<10} | {'Cân nặng':<8} | {'Khoảng cách':<10} | {'Kết quả thực tế'}")
    print("="*80)

    # Danh sách 20 cases kiểm thử chi tiết
    test_data = [
        # Nhóm 1: Hàng Nhẹ (Mốc quan trọng: 15kg và 10km)
        ('Nhẹ', 2, 2, 'Xe máy'),
        ('Nhẹ', 14.9, 5, 'Xe máy'),
        ('Nhẹ', 5, 9.9, 'Xe máy'),
        ('Nhẹ', 15, 5, 'Xe Tải Van'),      # Biên cân nặng
        ('Nhẹ', 5, 10, 'Xe Tải Van'),     # Biên khoảng cách
        ('Nhẹ', 20, 15, 'Xe Tải Van'),
        ('Nhẹ', 10, 12, 'Xe Tải Van'),
        
        # Nhóm 2: Xe tải 1.5 tấn (Mốc <= 1500kg)
        ('Nặng', 500, 10, 'Xe tải 1.5 tấn'),
        ('Nặng', 1000, 20, 'Xe tải 1.5 tấn'),
        ('Nặng', 1500, 50, 'Xe tải 1.5 tấn'), # Mốc biên 1500
        
        # Nhóm 3: Xe tải 5 tấn (1500 < w <= 5000)
        ('Nặng', 1501, 30, 'Xe tải 5 tấn'),   # Vừa chớm qua 1.5 tấn
        ('Nặng', 3000, 40, 'Xe tải 5 tấn'),
        ('Nặng', 4500, 10, 'Xe tải 5 tấn'),
        ('Nặng', 5000, 100, 'Xe tải 5 tấn'),  # Mốc biên 5000
        
        # Nhóm 4: Xe Container (> 5000kg)
        ('Nặng', 5001, 20, 'Xe Đầu kéo / Container'),
        ('Nặng', 6000, 150, 'Xe Đầu kéo / Container'),
        ('Nặng', 10000, 200, 'Xe Đầu kéo / Container'),
        ('Nặng', 15000, 300, 'Xe Đầu kéo / Container'),
        
        # Nhóm 5: Các trường hợp đặc biệt
        ('Nặng', 100, 1, 'Xe tải 1.5 tấn'),   # Nặng nhưng nhẹ cân
        ('Nhẹ', 1, 0.5, 'Xe máy'),            # Siêu nhẹ, siêu gần
    ]

    pass_count = 0
    for i, (label, weight, dist, expected) in enumerate(test_data, 1):
        actual = assign_vehicle(label, weight, dist)
        
        # Kiểm tra xem code của Nhi chạy có khớp với mong đợi không
        status = "PASS" if actual == expected else "FAIL"
        if status == "PASS": pass_count += 1
        
        print(f"{i:<4} | {label:<10} | {weight:<8} | {dist:<10} | {actual:<25} | {status}")

    print("="*80)
    print(f"KẾT QUẢ TỔNG HỢP: {pass_count}/20 TRƯỜNG HỢP CHẠY ĐÚNG.")
    print("="*80)

if __name__ == "__main__":
    run_20_test_cases()
