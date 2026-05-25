"""
seed.py — Pobla la base de datos con datos de prueba.
Ejecutar desde la raíz del proyecto:
    python -m backend.seed
"""
import sys
import os

# Asegurar que el paquete backend sea importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import SessionLocal, engine, Base
from backend import models
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Evitar duplicados
        if db.query(models.Usuario).count() > 0:
            print("[WARN] La base de datos ya tiene datos. Saltando seed.")
            return

        # ── Hospitales ────────────────────────────────────────────────────────
        h1 = models.Hospital(nombre="Hospital General de Medellín", direccion="Calle 10 #45-12, Medellín", aprobado=True)
        h2 = models.Hospital(nombre="Clínica San Rafael Bogotá",   direccion="Carrera 50 #22-80, Bogotá",  aprobado=True)
        h3 = models.Hospital(nombre="Centro Médico del Norte",     direccion="Av. Norte #5-15, Barranquilla", aprobado=False)
        db.add_all([h1, h2, h3])
        db.flush()

        # ── Usuarios ──────────────────────────────────────────────────────────
        admin = models.Usuario(
            username="admin",
            hashed_password=pwd_context.hash("admin123"),
            rol="admin",
            hospital_id=None,
        )
        admin_clinica = models.Usuario(
            username="admin_hgm",
            hashed_password=pwd_context.hash("clinica123"),
            rol="admin_clinica",
            hospital_id=None,  # se asigna después del flush
        )
        medico1 = models.Usuario(
            username="dr_garcia",
            hashed_password=pwd_context.hash("medico123"),
            rol="medico",
            hospital_id=None,
        )
        medico2 = models.Usuario(
            username="dra_lopez",
            hashed_password=pwd_context.hash("medico123"),
            rol="medico",
            hospital_id=None,
        )
        db.add_all([admin, admin_clinica, medico1, medico2])
        db.flush()

        # Asignar hospitales ahora que tenemos IDs
        admin_clinica.hospital_id = h1.id
        medico1.hospital_id = h1.id
        medico2.hospital_id = h2.id
        db.flush()

        # ── Pacientes ─────────────────────────────────────────────────────────
        p1 = models.Paciente(documento="10234567", nombre_completo="Carlos Andrés Ríos Montoya")
        p2 = models.Paciente(documento="20456789", nombre_completo="María Fernanda Castro Gómez")
        p3 = models.Paciente(documento="30891234", nombre_completo="Luis Felipe Moreno Zapata")
        db.add_all([p1, p2, p3])
        db.flush()

        # ── Historias Clínicas ────────────────────────────────────────────────
        db.add_all([
            models.HistoriaClinica(
                paciente_id=p1.id, medico_id=medico1.id,
                diagnostico="Hipertensión arterial grado II",
                tratamiento="Losartán 50 mg c/24h. Control en 1 mes.",
            ),
            models.HistoriaClinica(
                paciente_id=p1.id, medico_id=medico2.id,
                diagnostico="Diabetes mellitus tipo 2 — compensada",
                tratamiento="Metformina 850 mg c/12h. Dieta hipocalórica.",
            ),
            models.HistoriaClinica(
                paciente_id=p2.id, medico_id=medico1.id,
                diagnostico="Rinitis alérgica crónica",
                tratamiento="Loratadina 10 mg c/24h. Evitar alérgenos.",
            ),
            models.HistoriaClinica(
                paciente_id=p3.id, medico_id=medico2.id,
                diagnostico="Lumbalgia mecánica inespecífica",
                tratamiento="Ibuprofeno 400 mg c/8h x 5 días. Fisioterapia.",
            ),
        ])

        db.commit()
        print("[OK] Seed completado exitosamente.")
        print()
        print("Usuarios creados:")
        print("  admin     / admin123   (rol: admin — Administrador del sistema)")
        print("  admin_hgm / clinica123 (rol: admin_clinica — Hospital General de Medellín)")
        print("  dr_garcia / medico123  (rol: medico — Hospital General de Medellín)")
        print("  dra_lopez / medico123  (rol: medico — Clínica San Rafael Bogotá)")

    except Exception as e:
        db.rollback()
        print(f"[ERROR] Error durante el seed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
