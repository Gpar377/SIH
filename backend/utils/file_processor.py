import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import io
import os

class FileProcessor:
    def __init__(self):
        self.supported_formats = ['.csv', '.xlsx', '.xls']
        self.required_columns = [
            'student_id', 'name', 'attendance_percentage', 'marks'
        ]
        self.optional_columns = [
            'department', 'semester', 'family_income', 'family_size',
            'region', 'electricity', 'internet_access', 'distance_from_college'
        ]
        
    def read_file(self, file_content: bytes, filename: str) -> pd.DataFrame:
        """Read uploaded file and return DataFrame"""
        file_ext = os.path.splitext(filename)[1].lower()
        
        if file_ext not in self.supported_formats:
            raise ValueError(f"Unsupported file format. Supported: {self.supported_formats}")
        
        try:
            if file_ext == '.csv':
                df = pd.read_csv(io.BytesIO(file_content))
            else:  # Excel files
                df = pd.read_excel(io.BytesIO(file_content))
            
            return df
        except Exception as e:
            raise ValueError(f"Error reading file: {str(e)}")
    
    def detect_columns(self, df: pd.DataFrame) -> Dict:
        """Detect and suggest column mappings"""
        user_columns = df.columns.tolist()
        suggestions = {}
        
        # Column mapping suggestions based on common patterns
        mapping_patterns = {
            'student_id': ['id', 'student_id', 'roll_no', 'enrollment', 'student_no'],
            'name': ['name', 'student_name', 'full_name', 'student'],
            'attendance_percentage': ['attendance_percentage', 'attendance', 'attend', 'attendance_percent', 'attendance%'],
            'marks': ['marks', 'theory_marks', 'score', 'grade', 'percentage'],
            'department': ['department', 'dept', 'branch', 'course'],
            'semester': ['semester', 'sem', 'year', 'class'],
            'family_income': ['income', 'family_income', 'annual_income'],
            'family_size': ['family_size', 'family_members', 'household_size'],
            'region': ['region', 'area', 'location', 'urban_rural'],
            'electricity': ['electricity', 'power', 'electric'],
            'internet_access': ['internet', 'internet_access', 'wifi'],
            'distance_from_college': ['distance', 'commute', 'travel_distance']
        }
        
        for system_col, patterns in mapping_patterns.items():
            for user_col in user_columns:
                if user_col.lower() in [p.lower() for p in patterns]:
                    suggestions[user_col] = system_col
                    break
        
        return {
            'user_columns': user_columns,
            'suggestions': suggestions,
            'required_mappings': self.required_columns,
            'optional_mappings': self.optional_columns
        }
    
    def apply_column_mapping(self, df: pd.DataFrame, mappings: Dict) -> pd.DataFrame:
        """Apply user-defined column mappings"""
        df_mapped = df.copy()
        
        # Rename columns based on mappings
        rename_dict = {user_col: system_col for user_col, system_col in mappings.items() if user_col in df.columns}
        df_mapped = df_mapped.rename(columns=rename_dict)
        
        return df_mapped
    
    def validate_data(self, df: pd.DataFrame) -> Dict:
        """Validate the processed data"""
        validation_results = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'stats': {}
        }
        
        # Check required columns
        missing_required = [col for col in self.required_columns if col not in df.columns]
        if missing_required:
            validation_results['is_valid'] = False
            validation_results['errors'].append(f"Missing required columns: {missing_required}")
        
        # Validate data types and ranges
        if 'attendance_percentage' in df.columns:
            invalid_attendance = df[(df['attendance_percentage'] < 0) | (df['attendance_percentage'] > 100)]
            if not invalid_attendance.empty:
                validation_results['warnings'].append(f"{len(invalid_attendance)} rows have invalid attendance values")
        
        if 'marks' in df.columns:
            invalid_marks = df[(df['marks'] < 0) | (df['marks'] > 100)]
            if not invalid_marks.empty:
                validation_results['warnings'].append(f"{len(invalid_marks)} rows have invalid marks")
        
        if 'family_income' in df.columns:
            negative_income = df[df['family_income'] < 0]
            if not negative_income.empty:
                validation_results['warnings'].append(f"{len(negative_income)} rows have negative family income")
        
        # Generate statistics
        validation_results['stats'] = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'missing_values': df.isnull().sum().to_dict(),
            'data_types': df.dtypes.astype(str).to_dict()
        }
        
        return validation_results
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize the data"""
        df_clean = df.copy()
        
        # Generate student_id if missing
        if 'student_id' not in df_clean.columns or df_clean['student_id'].isnull().any():
            df_clean['student_id'] = df_clean.index.map(lambda x: f"STU_{x:04d}")
        
        # Clean numerical columns
        numerical_columns = ['attendance_percentage', 'marks', 'family_income', 'family_size', 'distance_from_college']
        for col in numerical_columns:
            if col in df_clean.columns:
                df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
        
        # Standardize categorical columns
        if 'region' in df_clean.columns:
            df_clean['region'] = df_clean['region'].str.title()
        
        if 'electricity' in df_clean.columns:
            df_clean['electricity'] = df_clean['electricity'].map({
                'yes': 'Regular', 'no': 'Irregular', 'regular': 'Regular', 
                'irregular': 'Irregular', 1: 'Regular', 0: 'Irregular'
            }).fillna(df_clean['electricity'])
        
        if 'internet_access' in df_clean.columns:
            df_clean['internet_access'] = df_clean['internet_access'].map({
                'yes': 'Yes', 'no': 'No', 1: 'Yes', 0: 'No'
            }).fillna(df_clean['internet_access'])
        
        # Fill missing values with defaults
        defaults = {
            'department': 'General',
            'semester': 1,
            'family_income': 200000,
            'family_size': 4,
            'region': 'Urban',
            'electricity': 'Regular',
            'internet_access': 'Yes',
            'distance_from_college': 10,
            'age': 18,
            'batch_year': 2024
        }
        
        for col, default_value in defaults.items():
            if col in df_clean.columns:
                df_clean[col] = df_clean[col].fillna(default_value)
        
        return df_clean
    
    def get_sample_data(self, df: pd.DataFrame, n_rows: int = 5) -> List[Dict]:
        """Get sample rows for preview"""
        sample_df = df.head(n_rows)
        return sample_df.to_dict('records')