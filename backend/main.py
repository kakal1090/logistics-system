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
    """FLOW XỬ LÝ CHÍNH: Input → Output"""
    
    def __init__(self):
        self.knn_classifier = KNNClassifier()
        self.rule_engine = RuleEngine()
    
    def preprocess_order(self, raw_order: Dict[str, Any]) -> Dict[str, Any]:
        """Chuẩn hóa order cho KNN"""
        order = raw_order.copy()
        
        # Tính features
        order['weight_normalized'] = order['weight'] / 20.0  # Max 20t
        order['distance_normalized'] = order['distance'] / 1500.0  # Max 1500km
        order['weight_distance_ratio'] = order['weight'] / max(order['distance'], 1)
        
        return order
    
    def classify_hybrid(self, order: Dict[str, Any]) -> Dict[str, Any]:
        """Hybrid classification: Rule → KNN fallback"""
        
        # BƯỚC 1: Thử Rule-based trước
        rule_result = self.rule_engine.classify_with_rules(order)
        
        if rule_result['priority'] > 0:  # Rule đã phân loại (không phải default 0)
            return rule_result
        
        # BƯỚC 2: KNN fallback cho trường hợp phức tạp
        logger.info(f"🤖 Rule không xác định → Chuyển KNN: {order['id']}")
        
        features = np.array([[
            order['weight_normalized'],
            order['distance_normalized'],
            order['weight_distance_ratio']
        ]])
        
        knn_priority, confidence = self.knn_classifier.predict(features)
        vehicle = self.rule_engine.assign_vehicle(knn_priority)
        
        return {
            'priority': int(knn_priority),
            'priority_name': self.rule_engine.get_priority_name(knn_priority),
            'vehicle': vehicle,
            'method': f'KNN (confidence: {confidence[0]:.2%})'
        }
    
    def process_single_order(self, raw_order: Dict[str, Any]) -> Dict[str, Any]:
        """
        PIPELINE ĐẦY ĐỦ CHO 1 ĐƠN HÀNG
        Input: raw_order → Output: processed_order
        """
        order_id = raw_order['id']
        logger.info(f"\n{'='*50}")
        logger.info(f"🚀 Bắt đầu xử lý đơn hàng: {order_id}")
        
        # BƯỚC 1: Nhận đơn
        order = raw_order.copy()
        order['status'] = '📥 Nhận đơn'
        order['step'] = 1
        order['timestamp'] = time.strftime('%H:%M:%S')
        logger.info(f"✅ Bước 1: Nhận đơn {order_id}")
        
        # BƯỚC 2: Xác nhận (giả lập)
        order['status'] = '✅ Đã xác nhận'
        order['step'] = 2
        logger.info(f"✅ Bước 2: Xác nhận đơn {order_id}")
        time.sleep(0.5)
        
        # BƯỚC 3: Preprocess
        order = self.preprocess_order(order)
        order['status'] = '🔄 Đang phân loại...'
        order['step'] = 3
        logger.info(f"🔄 Bước 3: Chuẩn hóa features")
        
        # BƯỚC 4: Phân loại Hybrid (Rule + KNN)
        classification = self.classify_hybrid(order)
        order.update(classification)
        order['status'] = f'🎯 Đã phân loại ({classification["method"]})'
        order['step'] = 4
        logger.info(f"🎯 Bước 4: Phân loại → {classification['priority_name']}")
        
        # BƯỚC 5: Gán phương tiện
        order['status'] = f'🚛 Gán xe: {classification["vehicle"]}'
        order['step'] = 5
        logger.info(f"🚛 Bước 5: Gán phương tiện")
        time.sleep(0.3)
        
        # BƯỚC 6: Hoàn thành
        order['status'] = '🏁 Hoàn thành'
        order['step'] = 6
        order['completed_at'] = time.strftime('%H:%M:%S')
        logger.info(f"🏁 Bước 6: Hoàn thành xử lý {order_id}")
        
        logger.info(f"{'='*50}")
        return order
    
    def batch_process(self, orders: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Xử lý batch nhiều đơn hàng"""
        results = []
        for order in orders:
            result = self.process_single_order(order)
            results.append(result)
        return results

# DEMO CHẠY
if __name__ == "__main__":
    pipeline = OrderProcessingPipeline()
    
    # Demo data input
    demo_orders = [
        {'id': 'ORD001', 'weight': 12.5, 'distance': 800, 'type': 'Hàng thường', 'customer_type': None},
        {'id': 'ORD002', 'weight': 3.2, 'distance': 150, 'type': 'Hàng dễ vỡ', 'customer_type': 'Đối tác chiến lược'},
        {'id': 'ORD003', 'weight': 6.8, 'distance': 1200, 'type': 'Hàng đông lạnh', 'customer_type': None},
        {'id': 'ORD004', 'weight': 2.1, 'distance': 45, 'type': 'Hàng thường', 'customer_type': None},
        {'id': 'ORD005', 'weight': 7.5, 'distance': 600, 'type': 'Hàng thường', 'customer_type': None},
    ]
    
    # Chạy pipeline
    results = pipeline.batch_process(demo_orders)
    
    # Xuất kết quả
    df_results = pd.DataFrame(results)
    print("\n📊 KẾT QUẢ XỬ LÝ:")
    print(df_results[['id', 'priority_name', 'vehicle', 'method', 'status']].to_string(index=False))
    
    # Lưu file output
    df_results.to_csv('output/processed_orders.csv', index=False)
    print(f"\n💾 Kết quả đã lưu: output/processed_orders.csv")
