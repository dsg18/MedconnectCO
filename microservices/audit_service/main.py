# pyrefly: ignore [missing-import]
from fastapi import FastAPI, Depends, HTTPException
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
import sys
import os

# Permitir importaciones de carpetas superiores
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.security import get_current_user_data

import models, schemas, database

app = FastAPI(title="Audit Service", version="1.0.0")

models.Base.metadata.create_all(bind=database.engine)

@app.post("/", response_model=schemas.AuditLog)
def create_log(log: schemas.AuditLogCreate, db: Session = Depends(database.get_db)):
    db_log = models.AuditLog(**log.dict())
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

@app.get("/", response_model=list[schemas.AuditLog])
def list_logs(db: Session = Depends(database.get_db), current_user: dict = Depends(get_current_user_data)):
    # Solo administradores pueden ver la auditoría
    if current_user["rol"] != "admin":
        raise HTTPException(status_code=403, detail="No autorizado")
    return db.query(models.AuditLog).order_by(models.AuditLog.timestamp.desc()).all()
