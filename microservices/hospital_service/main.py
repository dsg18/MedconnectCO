from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.security import get_current_user_data
import models, schemas, database

app = FastAPI(title="Hospital Service")
models.Base.metadata.create_all(bind=database.engine)

@app.get("/", response_model=list[schemas.Hospital])
def list_hospitals(db: Session = Depends(database.get_db)):
    return db.query(models.Hospital).all()

@app.get("/{hospital_id}", response_model=schemas.Hospital)
def get_hospital(hospital_id: int, db: Session = Depends(database.get_db)):
    h = db.query(models.Hospital).filter(models.Hospital.id == hospital_id).first()
    if not h: raise HTTPException(status_code=404)
    return h

@app.post("/", response_model=schemas.Hospital)
def create_hospital(h: schemas.HospitalCreate, db: Session = Depends(database.get_db), user: dict = Depends(get_current_user_data)):
    if user["rol"] != "admin": raise HTTPException(status_code=403)
    db_h = models.Hospital(**h.dict())
    db.add(db_h)
    db.commit()
    db.refresh(db_h)
    return db_h

@app.patch("/{hospital_id}/aprobar")
def approve_hospital(hospital_id: int, db: Session = Depends(database.get_db), user: dict = Depends(get_current_user_data)):
    if user["rol"] != "admin": raise HTTPException(status_code=403)
    h = db.query(models.Hospital).filter(models.Hospital.id == hospital_id).first()
    if not h: raise HTTPException(status_code=404)
    h.aprobado = True
    db.commit()
    return {"detail": "Hospital aprobado"}

@app.delete("/{hospital_id}")
def delete_hospital(hospital_id: int, db: Session = Depends(database.get_db), user: dict = Depends(get_current_user_data)):
    if user["rol"] != "admin": raise HTTPException(status_code=403)
    h = db.query(models.Hospital).filter(models.Hospital.id == hospital_id).first()
    if not h: raise HTTPException(status_code=404)
    db.delete(h)
    db.commit()
    return {"detail": "Hospital eliminado"}
