import subprocess
import time
import sys
import os

# Puertos y comandos
SERVICES = [
    {"name": "Auth Service",      "dir": "auth_service",     "port": 8001},
    {"name": "Hospital Service",  "dir": "hospital_service", "port": 8002},
    {"name": "Patient Service",   "dir": "patient_service",  "port": 8003},
    {"name": "EHR Service",       "dir": "ehr_service",      "port": 8004},
    {"name": "Audit Service",     "dir": "audit_service",    "port": 8005},
    {"name": "Notification Service", "dir": "notification_service", "port": 8006},
    {"name": "API Gateway",       "dir": "gateway",          "port": 8000},
]

processes = []

print("Iniciando MedConnectCo en modo Microservicios...")

base_dir = os.path.join(os.getcwd(), "microservices")

try:
    for service in SERVICES:
        print(f"Arrancando {service['name']} en puerto {service['port']}...")
        cwd = os.path.join(base_dir, service['dir'])
        
        # Ejecutar uvicorn
        p = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", str(service['port'])],
            cwd=cwd
        )
        processes.append(p)
        time.sleep(1) # Esperar un segundo entre arranques

    print("\nTodos los servicios estan en ejecucion.")
    print("Frontend disponible en: http://localhost:8000")
    print("Para detener todo, presiona CTRL+C")

    # Mantener el script vivo
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print("\n🛑 Deteniendo servicios...")
    for p in processes:
        p.terminate()
    print("👋 ¡Adiós!")
