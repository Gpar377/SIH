import pandas as pd
from backend.utils.file_processor import FileProcessor

# Test the file processor
fp = FileProcessor()

# Read the CSV file
df = pd.read_csv('test_student_data.csv')
print("Columns in CSV:", df.columns.tolist())
print("Required columns:", fp.required_columns)

# Test column detection
column_info = fp.detect_columns(df)
print("Column suggestions:", column_info['suggestions'])

# Test validation
validation = fp.validate_data(df)
print("Validation result:", validation)