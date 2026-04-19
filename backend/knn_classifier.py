import numpy as np
import pandas as pd
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report
import joblib
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KNNClassifier:
    """KNN Classifier cho phân loại đơn hàng vận tải"""
    
    def __init__(self, model_path='models/knn_model.pkl'):
        self.model_path = model_path
        self.scaler = StandardScaler()
        self.knn = KNeighborsClassifier(n_neighbors=5, weights='distance', metric='euclidean')
        self.is_trained = False
        self._load_model()
    
    def train(self, X_train: np.ndarray, y_train: np.ndarray, X_test: np.ndarray = None, y_test: np.ndarray = None):
        """Huấn luyện KNN"""
        logger.info(" Training KNN Classifier...")
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        
        # Train model
        self.knn.fit(X_train_scaled, y_train)
        
        # Test nếu có test data
        if X_test is not None and y_test is not None:
            X_test_scaled = self.scaler.transform(X_test)
            y_pred = self.knn.predict(X_test_scaled)
            accuracy = accuracy_score(y_test, y_pred)
            logger.info(f" KNN Accuracy: {accuracy:.2%}")
            logger.info(f"Classification Report:\n{classification_report(y_test, y_pred)}")
        
        # Save model
        joblib.dump(self.knn, self.model_path)
        joblib.dump(self.scaler, self.model_path.replace('.pkl', '_scaler.pkl'))
        self.is_trained = True
        logger.info(" Model saved!")
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Dự đoán priority"""
        if not self.is_trained:
            raise ValueError("Model chưa được train!")
        
        X_scaled = self.scaler.transform(X)
        predictions = self.knn.predict(X_scaled)
        probabilities = self.knn.predict_proba(X_scaled)
        
        return predictions, np.max(probabilities, axis=1)
    
    def _load_model(self):
        """Load pre-trained model"""
        try:
            self.knn = joblib.load(self.model_path)
            self.scaler = joblib.load(self.model_path.replace('.pkl', '_scaler.pkl'))
            self.is_trained = True
            logger.info(" Loaded pre-trained KNN model")
        except FileNotFoundError:
            logger.warning("❌ No pre-trained model found. Need to train first.")
