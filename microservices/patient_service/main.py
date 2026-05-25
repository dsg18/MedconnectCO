from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import sys
import os
import httpx

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.security import get_current_user_data
import models, schemas, database

app = FastAPI(title="Patient Service")
models.Base.metadata.create_all(bind=database.engine)

AUDIT_SERVICE_URL = "http://localhost:8005"
AUTH_SERVICE_URL = "http://localhost:8001"

async def send_audit_log(usuario: str, accion: str, recurso: str, detalle: str):
    async with httpx.AsyncClient() as client:
        try:
            await client.post(AUDIT_SERVICE_URL + "/", json={
                "usuario": usuario,
                "accion": accion,
                "recurso": recurso,
                "detalle": detalle
            })
        except: pass

@app.get("/", response_model=list[schemas.Paciente])
def list_patients(db: Session = Depends(database.get_db)):
    return db.query(models.Paciente).all()

@app.get("/{documento}", response_model=schemas.Paciente)
def get_patient(documento: str, db: Session = Depends(database.get_db)):
    p = db.query(models.Paciente).filter(models.Paciente.documento == documento).first()
    if not p: raise HTTPException(status_code=404, detail="Paciente no encontrado")
    return p

@app.post("/", response_model=schemas.Paciente)
async def create_patient(p: schemas.PacienteCreate, db: Session = Depends(database.get_db), user: dict = Depends(get_current_user_data)):
    # Solo médicos y admins pueden registrar pacientes
    if user["rol"] not in ("admin", "admin_clinica", "medico"): raise HTTPException(status_code=403)
    
    if not p.consentimiento:
        raise HTTPException(status_code=400, detail="Debe aceptar el consentimiento informado para registrar al paciente")

    existing = db.query(models.Paciente).filter(models.Paciente.documento == p.documento).first()
    if existing: raise HTTPException(status_code=400, detail="Paciente ya registrado")
    
    db_p = models.Paciente(**p.dict())
    db.add(db_p)
    db.commit()
    db.refresh(db_p)
    
    # Auditoría síncrona/asíncrona (usamos await porque FastAPI lo permite)
    import asyncio
    asyncio.create_task(send_audit_log(
        usuario=user["sub"],
        accion="CREATE",
        recurso="Paciente",
        detalle=f"Registrado paciente {p.documento}"
    ))

    # 2. Registrar usuario en Auth Service (para que el paciente pueda entrar)
    async def register_auth_user():
        async with httpx.AsyncClient() as client:
            try:
                # Usamos el PIN de 4 dígitos como password
                await client.post(AUTH_SERVICE_URL + "/register_patient", 
                    json={
                        "username": p.documento,
                        "password": p.pin,
                        "rol": "paciente",
                        "hospital_id": user.get("hospital_id")
                    },
                    headers={"Authorization": f"Bearer {user['token_original']}"}
                )
            except: pass
    
    asyncio.create_task(register_auth_user())
    
    return db_p

@app.post("/{documento}/condiciones", response_model=schemas.CondicionCronica)
async def add_condition(documento: str, cond: schemas.CondicionCronicaCreate, db: Session = Depends(database.get_db), user: dict = Depends(get_current_user_data)):
    # Solo médicos pueden registrar enfermedades crónicas
    if user["rol"] != "medico": raise HTTPException(status_code=403, detail="Solo los médicos pueden registrar antecedentes")
    
    patient = db.query(models.Paciente).filter(models.Paciente.documento == documento).first()
    if not patient: raise HTTPException(status_code=404, detail="Paciente no encontrado")
    
    db_cond = models.CondicionCronica(**cond.dict(), paciente_id=patient.id)
    db.add(db_cond)
    db.commit()
    db.refresh(db_cond)
    
    # Auditoría
    import asyncio
    asyncio.create_task(send_audit_log(
        usuario=user["sub"],
        accion="CREATE",
        recurso="CondicionCronica",
        detalle=f"Registrada condición {cond.nombre} para paciente {documento}"
    ))
    
    return db_cond
