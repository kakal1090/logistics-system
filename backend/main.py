import numpy as np
import pandas as pd
from typing import Dict, List, Any
import time
from knn_classifier import KNNClassifier
from rule_engine import RuleEngine
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OrderProcessingPipeline:
    """FLOW XỬ LÝ CHÍNH """
    
    # Mapping weight → label
    WEIGHT_LABELS = {
        0: 'Nhẹ',        # < 5t
        1: 'Trung bình', # 5-10t
        2: 'Nặng'        # > 10t
    }
    
    def __init__(self):
        self.knn_classifier = KNNClassifier()
        self.rule_engine = RuleEngine()
    
    def preprocess_order(self, raw_order: Dict[str, Any]) -> Dict[str, Any]:
        """Map INPUT format → internal format"""
        order = raw_order.copy()
        
        # Tính volume
        order['volume'] = (order['length'] * order['width'] * order['height']) / 1000000
        
        # Chuẩn hóa features cho KNN  
        order['weight_normalized'] = min(order['weight'] / 20.0, 1.0)
        order['distance_normalized'] = min(order['distance'] / 1500.0, 1.0)
        order['weight_distance_ratio'] = order['weight'] / max(order['distance'], 1)
        
        # Map customer_type từ priority input
        order['customer_type'] = 'VIP' if raw_order['priority'] == 'Nhanh' else 'Thường'
        
        # Map product_type
        product_map = {'De vo': 'Hàng dễ vỡ', 'Thuong': 'Hàng thường'}
        order['type'] = product_map.get(raw_order['product_type'], raw_order['product_type'])
        
        # Thêm id field cho internal
        order['id'] = raw_order['order_id']
        
        return order
    
    def get_weight_label(self, weight: float) -> str:
        """Label theo trọng lượng OUTPUT format"""
        if weight < 5:
            return 'Nhẹ'
        elif weight < 10:
            return 'Trung bình'
        return 'Nặng'
    
    def classify_hybrid(self, order: Dict[str, Any]) -> int:
        """Trả về priority number"""
        priority = self.rule_engine.apply_priority_rules(order)
        
        # KNN fallback nếu rule = 0 (default)
        if priority == 0:
            features = np.array([[
                order['weight_normalized'],
                order['distance_normalized'],
                order['weight_distance_ratio']
            ]])
            knn_priority, _ = self.knn_classifier.predict(features)
            priority = int(knn_priority[0])
        
        return priority
    
    def process_single_order(self, raw_order: Dict[str, Any]) -> Dict[str, Any]:
        """
        ✅ INPUT: raw_order (format frontend)
        ✅ OUTPUT: processed_result (format backend/socket)
        """
        start_time = time.time()
        order_id = raw_order['order_id']
        
        logger.info(f"\n🚀 Xử lý: {order_id} | Weight: {raw_order['weight']}t")
        
        # Preprocess
        order = self.preprocess_order(raw_order)
        
        # Phân loại
        priority = self.classify_hybrid(order)
        vehicle = self.rule_engine.VEHICLE_RULES[priority]
        weight_label = self.get_weight_label(raw_order['weight'])
        
        # Thời gian xử lý
        processed_time = f"{time.time() - start_time:.2f}s"
        
        # ✅ OUTPUT FORMAT CHÍNH THỨC
        result = {
            "order_id": order_id,
            "label": weight_label,
            "vehicle": vehicle,
            "processed_time": processed_time,
            "process_status": "Đã xử lý"
        }
        
        logger.info(f"✅ RESULT: {result}")
        return result
    
    def batch_process(self, orders: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [self.process_single_order(order) for order in orders]

# EXPORT cho Socket Server (Người 3)
def handle_new_order(raw_order: Dict[str, Any]) -> Dict[str, Any]:
    """Socket server gọi function này"""
    pipeline = OrderProcessingPipeline()
    return pipeline.process_single_order(raw_order)

# DEMO với format mới
if __name__ == "__main__":
    pipeline = OrderProcessingPipeline()
    
    # ✅ DEMO INPUT FORMAT FRONTEND
    demo_orders = [
        {
            "order_id": "ORD001",
            "customer_name": "Nguyen Van A",
            "phone": "0909123456",
            "email": "a@gmail.com",
            "address": "Quan 1 TP.HCM", 
            "product_type": "De vo",
            "weight": 12.5,
            "length": 50,
            "width": 40,
            "height": 30,
            "distance": 8,
            "priority": "Nhanh",
            "note": "Hang de vo"
        },
        {
            "order_id": "ORD002",
            "customer_name": "Tran Thi B",
            "phone": "0987654321",
            "email": "b@gmail.com",
            "address": "Quan 7 TP.HCM",
            "product_type": "Thuong",
            "weight": 3.2,
            "length": 30,
            "width": 20,
            "height": 25,
            "distance": 150,
            "priority": "Bình thường",
            "note": ""
        }
    ]
    
    # Chạy pipeline
    results = pipeline.batch_process(demo_orders)
    
    print("\n📊 OUTPUT FORMAT (Backend/Socket):")
    for result in results:
        print(result)
        print("-" * 50)
    
    # Lưu output
    pd.DataFrame(results).to_csv('output/processed_orders.csv', index=False)
