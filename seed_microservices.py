import sys
import os
import sqlite3

# Carpeta base de microservicios
BASE_DIR = os.path.join(os.getcwd(), "microservices")

def seed_auth():
    print("Poblando Auth Service...")
    db_path = os.path.join(BASE_DIR, "auth_service", "auth.db")
    from microservices.common.security import get_password_hash
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY, username TEXT UNIQUE, hashed_password TEXT, rol TEXT, hospital_id INTEGER, creado_por TEXT)")
    
    users = [
        ('admin', get_password_hash('admin123'), 'admin', None, 'Sistema'),
        ('admin_medellin', get_password_hash('clinica123'), 'admin_clinica', 1, 'admin'),
        ('dr_perez', get_password_hash('medico123'), 'medico', 1, 'admin_medellin'),
    ]
    
    patients_auth = [
        ('10203040', get_password_hash('1234'), 'paciente', 1, 'Sistema'),
        ('50607080', get_password_hash('4321'), 'paciente', 1, 'Sistema'),
    ]
    
    for u in users + patients_auth:
        try:
            c.execute("INSERT INTO usuarios (username, hashed_password, rol, hospital_id, creado_por) VALUES (?,?,?,?,?)", u)
        except sqlite3.IntegrityError: pass
    
    conn.commit()
    conn.close()

def seed_hospitals():
    print("Poblando Hospital Service...")
    db_path = os.path.join(BASE_DIR, "hospital_service", "hospitals.db")
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS hospitales (id INTEGER PRIMARY KEY, nombre TEXT, direccion TEXT, aprobado BOOLEAN)")
    
    hospitals = [
        (1, 'Hospital General de Medellín', 'Carrera 48 # 32-102', 1),
        (2, 'Clínica Valle del Lili', 'Av. Simón Bolívar, Cali', 0),
    ]
    for h in hospitals:
        try:
            c.execute("INSERT INTO hospitales (id, nombre, direccion, aprobado) VALUES (?,?,?,?)", h)
        except sqlite3.IntegrityError: pass
    conn.commit()
    conn.close()

def seed_patients():
    print("Poblando Patient Service...")
    db_path = os.path.join(BASE_DIR, "patient_service", "patients.db")
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Crear tablas
    c.execute("""
        CREATE TABLE IF NOT EXISTS pacientes (
            id INTEGER PRIMARY KEY, 
            documento TEXT UNIQUE, 
            nombre_completo TEXT, 
            fecha_expedicion TEXT,
            fecha_nacimiento TEXT,
            pin TEXT,
            consentimiento BOOLEAN DEFAULT 0
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS condiciones_cronicas (
            id INTEGER PRIMARY KEY,
            nombre TEXT,
            fecha_diagnostico TEXT,
            paciente_id INTEGER,
            FOREIGN KEY(paciente_id) REFERENCES pacientes(id)
        )
    """)
    
    patients = [
        ('10203040', 'Juan David Gómez', '2015-05-10', '1990-01-20', '1234', 1),
        ('50607080', 'María Camila López', '2018-08-15', '1985-03-12', '4321', 1),
    ]
    for p in patients:
        try:
            c.execute("INSERT INTO pacientes (documento, nombre_completo, fecha_expedicion, fecha_nacimiento, pin, consentimiento) VALUES (?,?,?,?,?,?)", p)
        except sqlite3.IntegrityError: pass
        
    # Añadir condiciones de ejemplo
    condiciones = [
        ('Hipertensión Arterial', '2020-01-01', 1),
        ('Diabetes Tipo 2', '2021-06-15', 2),
    ]
    for co in condiciones:
        try:
            c.execute("INSERT INTO condiciones_cronicas (nombre, fecha_diagnostico, paciente_id) VALUES (?,?,?)", co)
        except sqlite3.IntegrityError: pass

    conn.commit()
    conn.close()

if __name__ == "__main__":
    seed_auth()
    seed_hospitals()
    seed_patients()
    print("\nBases de datos de microservicios pobladas.")
