"""fix_db.py — Repara la base de datos: agrega dr_garcia y corrige historias con medico_id NULL."""
from passlib.context import CryptContext
import sqlite3

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
conn = sqlite3.connect("ehr.sqlite")

# 1. Insertar dr_garcia si no existe
existing = conn.execute("SELECT id FROM usuarios WHERE username='dr_garcia'").fetchone()
if not existing:
    hashed = pwd.hash("medico123")
    conn.execute(
        "INSERT INTO usuarios (username, hashed_password, rol, hospital_id) VALUES (?,?,?,?)",
        ("dr_garcia", hashed, "medico", 1)
    )
    conn.commit()
    garcia_id = conn.execute("SELECT id FROM usuarios WHERE username='dr_garcia'").fetchone()[0]
    print(f"[OK] dr_garcia creado con id: {garcia_id}")
else:
    garcia_id = existing[0]
    print(f"[OK] dr_garcia ya existe con id: {garcia_id}")

# 2. Corregir historias con medico_id NULL
n = conn.execute(
    "UPDATE historias_clinicas SET medico_id=? WHERE medico_id IS NULL",
    (garcia_id,)
).rowcount
conn.commit()
print(f"[OK] Historias con medico_id NULL corregidas: {n}")

print()
print("=== ESTADO FINAL ===")
print("USUARIOS:")
for r in conn.execute("SELECT id, username, rol, hospital_id FROM usuarios ORDER BY id"):
    print(f"  [{r[0]}] {r[1]:<15} rol={r[2]:<15} hospital_id={r[3]}")

print()
print("HOSPITALES:")
for r in conn.execute("SELECT id, nombre, aprobado FROM hospitales ORDER BY id"):
    print(f"  [{r[0]}] aprobado={r[2]}  {r[1]}")

print()
print("PACIENTES:")
for r in conn.execute("SELECT id, documento, nombre_completo FROM pacientes ORDER BY id"):
    print(f"  [{r[0]}] doc={r[1]:<12} {r[2]}")

print()
print("HISTORIAS:")
for r in conn.execute("SELECT id, paciente_id, medico_id, pdf_path FROM historias_clinicas ORDER BY id"):
    print(f"  [{r[0]}] paciente={r[1]} medico={r[2]} pdf={'SI' if r[3] else 'NO'}")

conn.close()
print()
print("[DONE] Base de datos reparada correctamente.")
