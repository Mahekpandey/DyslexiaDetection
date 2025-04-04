import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib
import os

class DyslexiaPredictor:
    def predict(self, data):
        """
        Predict dyslexia probability based on reading performance
        
        Args:
            data (dict): Dictionary containing reading metrics
                - accuracy: float, percentage of words read correctly
                - words_per_minute: float, reading speed
                - total_words: int, total number of words in passage
                - correct_words: int, number of words read correctly
                - error_count: int, number of reading errors
        
        Returns:
            dict: Prediction results with keys:
                - prediction: bool, True if dyslexia predicted
                - probability: float, probability of dyslexia
        """
        try:
            # Extract features
            accuracy = data.get('accuracy', 0)
            wpm = data.get('words_per_minute', 0)
            error_rate = data.get('error_count', 0) / data.get('total_words', 1)
            
            # Simple threshold-based prediction
            # High probability of dyslexia if:
            # - Accuracy is below 85% OR
            # - Reading speed is below 100 wpm OR
            # - Error rate is above 20%
            probability = 0.0
            
            if accuracy < 85:
                probability += 0.4
            if wpm < 100:
                probability += 0.3
            if error_rate > 0.2:
                probability += 0.3
                
            # Normalize probability to 0-1 range
            probability = min(max(probability, 0.0), 1.0)
            
            return {
                'prediction': probability > 0.5,
                'probability': round(probability * 100, 2)
            }
            
        except Exception as e:
            print(f"Error in prediction: {str(e)}")
            return {
                'prediction': False,
                'probability': 0
            }

    def prepare_features(self, data):
        """Prepare features for model training"""
        features = []
        for item in data:
            features.append([
                item.get('accuracy', 0),
                item.get('words_per_minute', 0),
                item.get('error_count', 0) / item.get('total_words', 1)
            ])
        return np.array(features)

    def train(self, X, y):
        """Train the model with new data"""
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
        clf = RandomForestClassifier()
        clf.fit(X_train, y_train)
        return clf.score(X_train, y_train), clf.score(X_test, y_test)

class DyslexiaModel:
    def __init__(self):
        self.predictor = DyslexiaPredictor()
    
    def predict(self, data):
        """Make a prediction using the dyslexia predictor"""
        return self.predictor.predict(data)
    
    def train(self, data):
        """Train the model with new data"""
        # Prepare features and labels
        X = self.predictor.prepare_features(data)
        y = np.array([item.get('is_dyslexic', 0) for item in data])
        
        # Train the model
        train_score, test_score = self.predictor.train(X, y)
        return {
            'train_score': train_score,
            'test_score': test_score
        } 