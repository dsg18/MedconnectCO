from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import sys
import os

# Permitir importaciones de carpetas superiores
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.security import get_current_user_data

import models, schemas, database

app = FastAPI(title="Notification Service")

models.Base.metadata.create_all(bind=database.engine)

@app.post("/", response_model=schemas.Notification)
def create_notification(notif: schemas.NotificationCreate, db: Session = Depends(database.get_db)):
    db_notif = models.Notification(**notif.dict())
    db.add(db_notif)
    db.commit()
    db.refresh(db_notif)
    return db_notif

@app.get("/me", response_model=list[schemas.Notification])
def list_my_notifications(current_user: dict = Depends(get_current_user_data), db: Session = Depends(database.get_db)):
    # Los pacientes solo ven sus propias notificaciones
    return db.query(models.Notification).filter(models.Notification.usuario == current_user["sub"]).order_by(models.Notification.timestamp.desc()).all()

@app.put("/{notif_id}/read")
def mark_as_read(notif_id: int, current_user: dict = Depends(get_current_user_data), db: Session = Depends(database.get_db)):
    notif = db.query(models.Notification).filter(models.Notification.id == notif_id, models.Notification.usuario == current_user["sub"]).first()
    if not notif: raise HTTPException(status_code=404)
    notif.leido = True
    db.commit()
    return {"status": "ok"}
