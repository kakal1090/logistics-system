from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class RuleEngine:
    """Rule-based Engine cho phân loại và gán phương tiện"""
    
    PRIORITY_RULES = {
        4: ['Đối tác chiến lược', 'VIP'],  # VIP
        3: ['distance > 1000km', 'weight > 10t & special'],  # Khẩn cấp
        2: ['weight 5-10t'],  # Ưu tiên 2
        1: ['distance 500-1000km'],  # Ưu tiên 1
        0: ['default']  # Thường
    }
    
    VEHICLE_RULES = {
        4: 'Xe tải lớn + VIP Service',
        3: 'Xe tải lớn (Container)',
        2: 'Xe tải trung bình',
        1: 'Xe tải nhỏ',
        0: 'Xe máy tải'
    }
    
    def __init__(self):
        pass
    
    def apply_priority_rules(self, order: Dict[str, Any]) -> int:
        """Áp dụng rule phân loại priority"""
        
        # Rule 1: Khách VIP/Đối tác chiến lược → Priority 4
        if order.get('customer_type') in ['Đối tác chiến lược', 'VIP']:
            logger.info(f"🚀 Rule VIP: {order['id']} → Priority 4")
            return 4
        
        # Rule 2: Trọng lượng > 10 tấn → Priority 4
        if order['weight'] > 10:
            logger.info(f"⚖️ Rule Heavy: {order['id']} ({order['weight']}t) → Priority 4")
            return 4
        
        # Rule 3: Khoảng cách > 1000km → Priority 3
        if order['distance'] > 1000:
            logger.info(f"🗺️ Rule Long Distance: {order['id']} ({order['distance']}km) → Priority 3")
            return 3
        
        # Rule 4: Hàng đặc biệt + weight > 5t → Priority 3
        special_types = ['Hàng dễ vỡ', 'Hàng đông lạnh', 'Hàng giá trị cao']
        if order['type'] in special_types and order['weight'] > 5:
            logger.info(f"📦 Rule Special: {order['id']} → Priority 3")
            return 3
        
        # Rule 5: Weight 5-10t → Priority 2
        if 5 <= order['weight'] <= 10:
            logger.info(f"⚖️ Rule Medium: {order['id']} → Priority 2")
            return 2
        
        # Rule 6: Distance 500-1000km → Priority 1
        if 500 <= order['distance'] <= 1000:
            logger.info(f"🗺️ Rule Medium Distance: {order['id']} → Priority 1")
            return 1
        
        # Default: Priority 0 (Thường)
        logger.info(f"➡️ Default Rule: {order['id']} → Priority 0")
        return 0
    
    def assign_vehicle(self, priority: int) -> str:
        """Gán phương tiện theo priority"""
        vehicle = self.VEHICLE_RULES.get(priority, 'Xe tải nhỏ')
        logger.info(f"🚛 Assigned: Priority {priority} → {vehicle}")
        return vehicle
    
    def classify_with_rules(self, order: Dict[str, Any]) -> Dict[str, Any]:
        """Phân loại hoàn chỉnh bằng rules"""
        priority = self.apply_priority_rules(order)
        vehicle = self.assign_vehicle(priority)
        
        return {
            'priority': priority,
            'priority_name': self.get_priority_name(priority),
            'vehicle': vehicle,
            'method': 'Rule-based'
        }
    
    @staticmethod
    def get_priority_name(priority: int) -> str:
        names = {0: 'Thường', 1: 'Ưu tiên 1', 2: 'Ưu tiên 2', 3: 'Khẩn cấp', 4: 'VIP'}
        return names.get(priority, 'Unknown')
