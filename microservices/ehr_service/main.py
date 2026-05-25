from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import httpx
import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.security import get_current_user_data
import models, schemas, database, pdf_generator

app = FastAPI(title="EHR Service")
models.Base.metadata.create_all(bind=database.engine)

# Configuración de URLs de otros servicios
PATIENT_SERVICE_URL = "http://localhost:8003"
HOSPITAL_SERVICE_URL = "http://localhost:8002"
AUDIT_SERVICE_URL = "http://localhost:8005"
NOTIFICATION_SERVICE_URL = "http://localhost:8006"

async def send_audit_log(usuario: str, accion: str, recurso: str, detalle: str):
    async with httpx.AsyncClient() as client:
        try:
            await client.post(AUDIT_SERVICE_URL + "/", json={
                "usuario": usuario,
                "accion": accion,
                "recurso": recurso,
                "detalle": detalle
            })
        except:
            pass # No bloqueamos si falla la auditoría en este prototipo

@app.get("/", response_model=list[schemas.HistoriaClinica])
def list_histories(db: Session = Depends(database.get_db), user: dict = Depends(get_current_user_data)):
    if user["rol"] == "admin":
        return db.query(models.HistoriaClinica).all()
    if user["rol"] in ("admin_clinica", "medico"):
        return db.query(models.HistoriaClinica).filter(models.HistoriaClinica.hospital_id == user["hospital_id"]).all()
    raise HTTPException(status_code=403)

@app.get("/paciente/{documento}", response_model=list[schemas.HistoriaClinica])
def list_histories_by_patient(documento: str, db: Session = Depends(database.get_db), user: dict = Depends(get_current_user_data)):
    # Lógica de seguridad: solo médicos de su hospital o admins
    query = db.query(models.HistoriaClinica).filter(models.HistoriaClinica.paciente_documento == documento)
    if user["rol"] != "admin":
        query = query.filter(models.HistoriaClinica.hospital_id == user["hospital_id"])
    return query.all()

@app.post("/", response_model=schemas.HistoriaClinica)
async def create_history(hc: schemas.HistoriaClinicaCreate, db: Session = Depends(database.get_db), user: dict = Depends(get_current_user_data)):
    if user["rol"] not in ("medico", "admin_clinica"):
        raise HTTPException(status_code=403, detail="Solo personal médico puede crear historias")
    
    # 1. Verificar si el paciente existe (Llamada al Patient Service)
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f"{PATIENT_SERVICE_URL}/{hc.paciente_documento}")
            if resp.status_code != 200:
                raise HTTPException(status_code=404, detail="El paciente no existe en el sistema nacional")
            paciente = resp.json()
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Servicio de Pacientes no disponible")

    # 2. Crear la historia en la DB local
    db_hc = models.HistoriaClinica(
        paciente_documento=hc.paciente_documento,
        medico_id=user.get("id", 0), # En un sistema real vendría del token
        hospital_id=user["hospital_id"],
        diagnostico=hc.diagnostico,
        tratamiento=hc.tratamiento
    )
    db.add(db_hc)
    db.commit()
    db.refresh(db_hc)

    # 3. Generar PDF de forma síncrona para este ejemplo
    pdf_data = {
        "paciente_nombre": paciente["nombre_completo"],
        "paciente_doc": hc.paciente_documento,
        "diagnostico": hc.diagnostico,
        "tratamiento": hc.tratamiento,
        "fecha": db_hc.fecha_creacion.strftime("%Y-%m-%d %H:%M"),
        "medico_nombre": user["sub"]
    }
    filename = pdf_generator.generar_pdf_historia(db_hc.id, pdf_data)
    db_hc.pdf_path = filename
    db.commit()
    
    # 4. Auditoría
    await send_audit_log(
        usuario=user["sub"],
        accion="CREATE",
        recurso="HistoriaClinica",
        detalle=f"Creada historia ID {db_hc.id} para paciente {hc.paciente_documento}"
    )

    # 5. Notificación al paciente
    async def notify_patient():
        async with httpx.AsyncClient() as client:
            try:
                await client.post(NOTIFICATION_SERVICE_URL + "/", json={
                    "usuario": hc.paciente_documento,
                    "mensaje": f"Se ha registrado una nueva historia clínica en el hospital {user.get('hospital_id', '')}."
                })
            except: pass
    
    asyncio.create_task(notify_patient())
    
    return db_hc

@app.get("/{historia_id}/pdf")
def download_pdf(historia_id: int, db: Session = Depends(database.get_db), user: dict = Depends(get_current_user_data)):
    hc = db.query(models.HistoriaClinica).filter(models.HistoriaClinica.id == historia_id).first()
    if not hc: raise HTTPException(status_code=404)
    
    # Seguridad básica
    if user["rol"] != "admin" and hc.hospital_id != user["hospital_id"]:
        raise HTTPException(status_code=403, detail="No tiene permiso para ver esta historia")

    if not hc.pdf_path: raise HTTPException(status_code=404, detail="PDF no generado")
    
    path = os.path.join("static/pdfs", hc.pdf_path)
    return FileResponse(path, filename=hc.pdf_path, media_type="application/pdf")
