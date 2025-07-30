"""
Database migration script to add new fields to users table
This script adds: full_name, address, pin_code, updated_at fields
"""

import sqlite3
from datetime import datetime

def migrate_users_table():
    conn = sqlite3.connect('instance/parking2.db')
    cursor = conn.cursor()
    
    try:
        # Check if the new columns already exist
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Add full_name column if it doesn't exist
        if 'full_name' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN full_name VARCHAR(200)")
            print("Added full_name column")
        
        # Add address column if it doesn't exist
        if 'address' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN address TEXT")
            print("Added address column")
        
        # Add pin_code column if it doesn't exist
        if 'pin_code' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN pin_code VARCHAR(10)")
            print("Added pin_code column")
        
        # Add updated_at column if it doesn't exist
        if 'updated_at' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN updated_at DATETIME")
            print("Added updated_at column")
            
            # Set updated_at to current timestamp for existing users
            current_time = datetime.utcnow().isoformat()
            cursor.execute("UPDATE users SET updated_at = ? WHERE updated_at IS NULL", (current_time,))
            print("Updated existing users with current timestamp for updated_at")
        
        conn.commit()
        print("Migration completed successfully!")
        
    except Exception as e:
        print(f"Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_users_table()
