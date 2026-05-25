"""
run.py — Script de arranque del proyecto.
Ejecutar desde la raíz:  python run.py
"""
import subprocess
import sys
import os

ROOT = os.path.dirname(os.path.abspath(__file__))

def main():
    print("=" * 55)
    print("             MedConnectCo")
    print("=" * 55)

    # 1. Poblar BD si está vacía
    print("\n[1/2] Verificando base de datos...")
    sys.path.insert(0, ROOT)
    try:
        from backend.database import SessionLocal, engine, Base
        from backend import models
        Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        count = db.query(models.Usuario).count()
        db.close()
        if count == 0:
            print("      BD vacía → ejecutando seed...")
            from backend.seed import seed
            seed()
        else:
            print(f"      BD lista ({count} usuarios encontrados).")
    except Exception as e:
        print(f"      [WARN] No se pudo verificar la BD: {e}")

    # 2. Levantar servidor
    print("\n[2/2] Levantando servidor...")
    print()
    print("  Frontend : http://localhost:8000/app")
    print("  API Docs : http://localhost:8000/docs")
    print("  Health   : http://localhost:8000/")
    print()
    print("  Credenciales:")
    print("    admin     / admin123   (Administrador)")
    print("    dr_garcia / medico123  (Medico)")
    print()
    print("  Presiona Ctrl+C para detener el servidor.")
    print("=" * 55)
    print()

    subprocess.run([
        sys.executable, "-m", "uvicorn",
        "backend.main:app",
        "--reload",
        "--host", "127.0.0.1",
        "--port", "8000",
    ], cwd=ROOT)

if __name__ == "__main__":
    main()
