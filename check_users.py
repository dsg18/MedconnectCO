import sqlite3
import os

db_path = "microservices/auth_service/auth.db"
conn = sqlite3.connect(db_path)
c = conn.cursor()
c.execute("SELECT username, rol FROM usuarios")
users = c.fetchall()
print("Usuarios en Auth Service:")
for u in users:
    print(f"User: {u[0]}, Rol: {u[1]}")
conn.close()
