from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class RuleEngine:
    """Rule-based Engine """
    
    VEHICLE_RULES = {
        4: 'Xe tải lớn + VIP Service',
        3: 'Xe tải lớn (Container)',
        2: 'Xe tải trung bình',
        1: 'Xe tải nhỏ',
        0: 'Xe máy'
    }
    
    def __init__(self):
        pass
    
    def apply_priority_rules(self, order: Dict[str, Any]) -> int:
        """Áp dụng rules → trả về priority number"""
        
        # Rule 1: Priority input = "Nhanh" → VIP (Priority 4)
        if order.get('priority') == 'Nhanh':
            logger.info(f"🚀 Rule 1: {order['id']} - Priority 'Nhanh' → 4")
            return 4
        
        # Rule 2: Product_type = "De vo" + weight > 5t → Khẩn cấp (3)
        if order['product_type'] == 'De vo' and order['weight'] > 5:
            logger.info(f"📦 Rule 2: {order['id']} - 'De vo' + heavy → 3")
            return 3
        
        # Rule 3: Weight > 10t → VIP (4)
        if order['weight'] > 10:
            logger.info(f"⚖️ Rule 3: {order['id']} - {order['weight']}t > 10t → 4")
            return 4
        
        # Rule 4: Distance > 1000km → Khẩn cấp (3)
        if order['distance'] > 1000:
            logger.info(f"🗺️ Rule 4: {order['id']} - {order['distance']}km > 1000km → 3")
            return 3
        
        # Rule 5: Weight 5-10t → Ưu tiên 2
        if 5 <= order['weight'] <= 10:
            logger.info(f"⚖️ Rule 5: {order['id']} - Medium weight → 2")
            return 2
        
        # Rule 6: Volume lớn (> 0.05m³) → Ưu tiên 1
        volume = (order['length'] * order['width'] * order['height']) / 1000000
        if volume > 0.05:
            logger.info(f"📦 Rule 6: {order['id']} - Volume {volume:.2f}m³ → 1")
            return 1
        
        # Default: Thường (0)
        logger.info(f"➡️ Default: {order['id']} → 0")
        return 0
    
    def assign_vehicle(self, priority: int) -> str:
        """Gán xe theo priority"""
        vehicle = self.VEHICLE_RULES.get(priority, 'Xe tải nhỏ')
        logger.info(f"🚛 Vehicle: Priority {priority} → {vehicle}")
        return vehicle
    
    @staticmethod
    def get_priority_name(priority: int) -> str:
        """Tên priority (giữ lại cho logging)"""
        names = {0: 'Thường', 1: 'Ưu tiên 1', 2: 'Ưu tiên 2', 3: 'Khẩn cấp', 4: 'VIP'}
        return names.get(priority, 'Unknown')

# Test nhanh
if __name__ == "__main__":
    engine = RuleEngine()
    test_order = {
        "order_id": "ORD001",
        "product_type": "De vo",
        "weight": 12.5,
        "length": 50, "width": 40, "height": 30,
        "distance": 8,
        "priority": "Nhanh"
    }
    priority = engine.apply_priority_rules(test_order)
    vehicle = engine.assign_vehicle(priority)
    print(f"Priority: {priority}, Vehicle: {vehicle}")
