import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib
import os

class SimpleMLModel:
    def __init__(self):
        self.model = None
        self.model_path = "dropout_model.pkl"
        
    def create_sample_data(self):
        """Create sample training data"""
        np.random.seed(42)
        n_samples = 1000
        
        # Generate features
        attendance = np.random.normal(75, 15, n_samples)
        marks = np.random.normal(70, 20, n_samples)
        fees_due = np.random.exponential(15000, n_samples)
        
        # Create target based on logical rules
        dropout_risk = []
        for i in range(n_samples):
            score = 0
            if attendance[i] < 60: score += 2
            elif attendance[i] < 75: score += 1
            
            if marks[i] < 50: score += 2
            elif marks[i] < 65: score += 1
            
            if fees_due[i] > 25000: score += 2
            elif fees_due[i] > 15000: score += 1
            
            # 0=Low, 1=Medium, 2=High, 3=Critical
            if score >= 5: dropout_risk.append(3)
            elif score >= 3: dropout_risk.append(2)
            elif score >= 1: dropout_risk.append(1)
            else: dropout_risk.append(0)
        
        return pd.DataFrame({
            'attendance_percentage': attendance,
            'marks': marks,
            'fees_due': fees_due,
            'risk_level': dropout_risk
        })
    
    def train_model(self):
        """Train the ML model"""
        print("Training ML model...")
        
        # Create sample data
        df = self.create_sample_data()
        
        # Prepare features
        X = df[['attendance_percentage', 'marks', 'fees_due']]
        y = df['risk_level']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Train model
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.model.fit(X_train, y_train)
        
        # Calculate accuracy
        accuracy = self.model.score(X_test, y_test)
        print(f"Model accuracy: {accuracy:.2%}")
        
        # Save model
        joblib.dump(self.model, self.model_path)
        print(f"Model saved to {self.model_path}")
        
        return accuracy
    
    def load_model(self):
        """Load existing model"""
        if os.path.exists(self.model_path):
            self.model = joblib.load(self.model_path)
            print("Model loaded successfully")
            return True
        return False
    
    def predict_risk(self, attendance, marks, fees_due):
        """Predict dropout risk"""
        if self.model is None:
            if not self.load_model():
                self.train_model()
        
        # Prepare input
        features = np.array([[attendance, marks, fees_due]])
        
        # Predict
        risk_level = self.model.predict(features)[0]
        risk_probability = self.model.predict_proba(features)[0]
        
        # Convert to readable format
        risk_labels = ['Low', 'Medium', 'High', 'Critical']
        
        return {
            'risk_level': risk_labels[risk_level],
            'risk_score': float(risk_probability[risk_level] * 100),
            'probabilities': {
                'Low': float(risk_probability[0] * 100),
                'Medium': float(risk_probability[1] * 100),
                'High': float(risk_probability[2] * 100),
                'Critical': float(risk_probability[3] * 100)
            }
        }
    
    def batch_predict(self, students_df):
        """Predict risk for multiple students"""
        if self.model is None:
            if not self.load_model():
                self.train_model()
        
        results = []
        for _, student in students_df.iterrows():
            attendance = student.get('attendance_percentage', 75)
            marks = student.get('marks', 70)
            fees_due = student.get('fees_due', 10000)
            
            prediction = self.predict_risk(attendance, marks, fees_due)
            results.append({
                'student_id': student.get('student_id', ''),
                'risk_level': prediction['risk_level'],
                'risk_score': prediction['risk_score']
            })
        
        return results

# Global instance
ml_model = SimpleMLModel()

if __name__ == "__main__":
    # Train model if run directly
    ml_model.train_model()
    
    # Test prediction
    test_result = ml_model.predict_risk(45, 35, 25000)
    print(f"Test prediction: {test_result}")