import joblib
import numpy as np
import os

class AGBPredictor:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.load_model()
    
    def load_model(self):
        """Load the trained model and scaler"""
        try:
            model_path = os.path.join(os.path.dirname(__file__), '../models/shcap_production_model_cleaned.pkl')
            scaler_path = os.path.join(os.path.dirname(__file__), '../models/shcap_production_scaler_cleaned.pkl')
            
            self.model = joblib.load(model_path)
            self.scaler = joblib.load(scaler_path)
            print(" AGB Model loaded successfully")
        except Exception as e:
            print(f" Error loading model: {e}")
    
    def predict(self, features):
        """Predict AGB for given features"""
        if self.model is None or self.scaler is None:
            raise Exception("Model not loaded")
        
        # Scale features
        features_scaled = self.scaler.transform([features])
        
        # Predict
        prediction = self.model.predict(features_scaled)[0]
        
        return max(0, prediction)  # Ensure non-negative biomass

# Global instance
agb_predictor = AGBPredictor()