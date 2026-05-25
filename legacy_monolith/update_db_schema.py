import sqlite3
import os

db_path = "ehr.sqlite"

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if creado_por column exists
    cursor.execute("PRAGMA table_info(usuarios)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if "creado_por" not in columns:
        print("Adding column 'creado_por' to 'usuarios' table...")
        cursor.execute("ALTER TABLE usuarios ADD COLUMN creado_por TEXT")
        conn.commit()
        print("Column added successfully.")
    else:
        print("Column 'creado_por' already exists.")
        
    conn.close()
else:
    print("Database file not found. It will be created with the new schema when the server starts.")
