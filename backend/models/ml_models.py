import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib
import os
from typing import Dict, List

class DropoutPredictor:
    def __init__(self):
        self.rf_model = RandomForestClassifier(n_estimators=50, max_depth=6, random_state=42)
        self.dt_model = DecisionTreeClassifier(max_depth=6, random_state=42)
        self.label_encoders = {}
        self.feature_names = []
        self.is_trained = False
        
    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare features for ML models"""
        df_processed = df.copy()
        
        # Numerical features
        numerical_features = [
            'attendance_percentage', 'marks', 'family_income', 'family_size'
        ]
        
        # Encode categorical features
        categorical_features = [
            'electricity', 'internet_access', 'caste_category', 'region',
            'family_education_background', 'gender', 'city_village_name', 'puc_college'
        ]
        
        for col in categorical_features:
            if col in df.columns:
                if col not in self.label_encoders:
                    self.label_encoders[col] = LabelEncoder()
                    df_processed[f'{col}_encoded'] = self.label_encoders[col].fit_transform(df[col].astype(str))
                else:
                    df_processed[f'{col}_encoded'] = self.label_encoders[col].transform(df[col].astype(str))
                numerical_features.append(f'{col}_encoded')
        
        # Fill missing values
        for col in numerical_features:
            if col in df_processed.columns:
                df_processed[col] = df_processed[col].fillna(df_processed[col].median())
        
        self.feature_names = [col for col in numerical_features if col in df_processed.columns]
        return df_processed[self.feature_names]
    
    def train_models(self, df: pd.DataFrame) -> Dict:
        """Train ML models on the data"""
        if 'risk_level' not in df.columns:
            raise ValueError("Dataset must have 'risk_level' column for training")
        
        # Prepare features
        X = self.prepare_features(df)
        y = df['risk_level']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Train models
        self.rf_model.fit(X_train, y_train)
        self.dt_model.fit(X_train, y_train)
        
        # Evaluate
        rf_pred = self.rf_model.predict(X_test)
        dt_pred = self.dt_model.predict(X_test)
        
        rf_accuracy = accuracy_score(y_test, rf_pred)
        dt_accuracy = accuracy_score(y_test, dt_pred)
        
        self.is_trained = True
        
        return {
            'random_forest_accuracy': rf_accuracy,
            'decision_tree_accuracy': dt_accuracy,
            'feature_importance': dict(zip(self.feature_names, self.rf_model.feature_importances_))
        }
    
    def predict_risk(self, student_data: Dict) -> Dict:
        """Predict risk for a single student"""
        if not self.is_trained:
            raise ValueError("Models not trained yet!")
        
        # Convert to DataFrame
        df = pd.DataFrame([student_data])
        X = self.prepare_features(df)
        
        # Get predictions
        rf_pred = self.rf_model.predict(X)[0]
        rf_proba = self.rf_model.predict_proba(X)[0]
        
        dt_pred = self.dt_model.predict(X)[0]
        
        # Get feature importance for this prediction
        feature_importance = {}
        for i, feature in enumerate(self.feature_names):
            if feature in student_data or feature.replace('_encoded', '') in student_data:
                feature_importance[feature] = self.rf_model.feature_importances_[i]
        
        return {
            'prediction': rf_pred,
            'probability': max(rf_proba),
            'probabilities': dict(zip(self.rf_model.classes_, rf_proba)),
            'decision_tree_prediction': dt_pred,
            'feature_importance': feature_importance
        }
    
    def batch_predict(self, df: pd.DataFrame) -> pd.DataFrame:
        """Predict risk for multiple students"""
        if not self.is_trained:
            raise ValueError("Models not trained yet!")
        
        X = self.prepare_features(df)
        predictions = self.rf_model.predict(X)
        probabilities = self.rf_model.predict_proba(X)
        
        df_result = df.copy()
        df_result['predicted_risk'] = predictions
        df_result['risk_probability'] = probabilities.max(axis=1)
        
        return df_result
    
    def save_models(self, path="models/"):
        """Save trained models"""
        os.makedirs(path, exist_ok=True)
        
        joblib.dump(self.rf_model, f"{path}/random_forest.pkl")
        joblib.dump(self.dt_model, f"{path}/decision_tree.pkl")
        joblib.dump(self.label_encoders, f"{path}/label_encoders.pkl")
        joblib.dump(self.feature_names, f"{path}/feature_names.pkl")
    
    def load_models(self, path="models/"):
        """Load trained models"""
        self.rf_model = joblib.load(f"{path}/random_forest.pkl")
        self.dt_model = joblib.load(f"{path}/decision_tree.pkl")
        self.label_encoders = joblib.load(f"{path}/label_encoders.pkl")
        self.feature_names = joblib.load(f"{path}/feature_names.pkl")
        self.is_trained = True