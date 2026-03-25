import sqlite3
import os

def migrate():
    db_path = 'dietengine.db'
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='exercises'")
        if not cursor.fetchone():
            print("Table 'exercises' does not exist yet.")
            return

        # Check for column
        cursor.execute("PRAGMA table_info(exercises)")
        columns = [c[1] for c in cursor.fetchall()]
        
        if 'location_type' not in columns:
            print("Adding 'location_type' column to 'exercises' table...")
            cursor.execute("ALTER TABLE exercises ADD COLUMN location_type TEXT DEFAULT 'Any'")
            conn.commit()
            print("Migration successful.")
        else:
            print("Column 'location_type' already exists.")
            
    except Exception as e:
        print(f"Migration failed: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
