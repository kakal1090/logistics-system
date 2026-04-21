import os
import numpy as np
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
        self.knn = KNeighborsClassifier(
            n_neighbors=7,
            weights='distance',
            metric='euclidean'
        )
        self.is_trained = False
        self._load_model()

    def train(self, X_train, y_train, X_test=None, y_test=None):
        logger.info("Training KNN Classifier...")

        X_train_scaled = self.scaler.fit_transform(X_train)
        self.knn.fit(X_train_scaled, y_train)

        if X_test is not None and y_test is not None:
            X_test_scaled = self.scaler.transform(X_test)
            y_pred = self.knn.predict(X_test_scaled)
            accuracy = accuracy_score(y_test, y_pred)
            logger.info(f"KNN Accuracy: {accuracy:.2%}")
            logger.info(f"Classification Report:\n{classification_report(y_test, y_pred)}")

        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        joblib.dump(self.knn, self.model_path)
        joblib.dump(self.scaler, self.model_path.replace('.pkl', '_scaler.pkl'))

        self.is_trained = True
        logger.info("Model saved!")

    def predict(self, X):
        """Dự đoán label KNN"""
        if not self.is_trained:
            raise ValueError("Model chưa được train!")

        X_scaled = self.scaler.transform(X)
        predictions = self.knn.predict(X_scaled)
        probabilities = self.knn.predict_proba(X_scaled)

        return predictions, np.max(probabilities, axis=1)

    def _load_model(self):
        try:
            self.knn = joblib.load(self.model_path)
            self.scaler = joblib.load(self.model_path.replace('.pkl', '_scaler.pkl'))
            self.is_trained = True
            logger.info("Loaded pre-trained KNN model")
        except FileNotFoundError:
            logger.warning("No pre-trained model found. Need to train first.")
