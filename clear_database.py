from models.database import Database

def clear_all_data():
    """Clear all student data from database"""
    db = Database()
    
    try:
        # Clear all students
        db.cursor.execute("DELETE FROM students")
        db.conn.commit()
        
        print("✅ All student data cleared from database")
        print("Database is now empty and ready for new data")
        
        # Show count to confirm
        db.cursor.execute("SELECT COUNT(*) FROM students")
        count = db.cursor.fetchone()[0]
        print(f"Current student count: {count}")
        
    except Exception as e:
        print(f"Error clearing database: {e}")

if __name__ == "__main__":
    clear_all_data()