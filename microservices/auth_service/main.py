from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
import sys
import os

# Permitir importaciones de carpetas superiores
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.security import (
    verify_password, get_password_hash, create_access_token, 
    get_current_user_data, ACCESS_TOKEN_EXPIRE_MINUTES
)

import models, schemas, database

app = FastAPI(title="Auth Service", version="1.0.0")

models.Base.metadata.create_all(bind=database.engine)

@app.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = db.query(models.Usuario).filter(models.Usuario.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password): 
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    
    access_token = create_access_token(
        data={"sub": user.username, "rol": user.rol, "hospital_id": user.hospital_id}
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/me", response_model=schemas.Usuario)
def read_users_me(current_user: dict = Depends(get_current_user_data), db: Session = Depends(database.get_db)):
    user = db.query(models.Usuario).filter(models.Usuario.username == current_user["sub"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user

@app.get("/", response_model=list[schemas.Usuario])
def list_users(current_user: dict = Depends(get_current_user_data), db: Session = Depends(database.get_db)):
    if current_user["rol"] == "admin":
        return db.query(models.Usuario).all()
    if current_user["rol"] == "admin_clinica":
        return db.query(models.Usuario).filter(models.Usuario.hospital_id == current_user["hospital_id"]).all()
    raise HTTPException(status_code=403, detail="No autorizado")

@app.post("/register", response_model=schemas.Usuario)
@app.post("/", response_model=schemas.Usuario)
def register(user: schemas.UsuarioCreate, db: Session = Depends(database.get_db), current_user: dict = Depends(get_current_user_data)):
    if current_user["rol"] not in ("admin", "admin_clinica"):
        raise HTTPException(status_code=403, detail="No autorizado")

    final_hospital_id = user.hospital_id
    if current_user["rol"] == "admin_clinica":
        final_hospital_id = current_user["hospital_id"]
        if user.rol != "medico":
            raise HTTPException(status_code=403, detail="Solo puede crear médicos")

    db_user = models.Usuario(
        username=user.username,
        hashed_password=get_password_hash(user.password),
        rol=user.rol,
        hospital_id=final_hospital_id,
        creado_por=current_user["sub"]
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/register_patient", response_model=schemas.Usuario)
def register_patient(user: schemas.UsuarioCreate, db: Session = Depends(database.get_db), current_user: dict = Depends(get_current_user_data)):
    # Los médicos y admins pueden registrar pacientes
    if current_user["rol"] not in ("admin", "admin_clinica", "medico"):
        raise HTTPException(status_code=403, detail="No autorizado")

    if user.rol != "paciente":
        raise HTTPException(status_code=400, detail="Solo se permiten registros de pacientes")

    db_user = models.Usuario(
        username=user.username,
        hashed_password=get_password_hash(user.password),
        rol="paciente",
        hospital_id=user.hospital_id,
        creado_por=current_user["sub"]
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(database.get_db), current_user: dict = Depends(get_current_user_data)):
    user = db.query(models.Usuario).filter(models.Usuario.id == user_id).first()
    if not user: raise HTTPException(status_code=404)
    if current_user["rol"] == "admin" or (current_user["rol"] == "admin_clinica" and user.hospital_id == current_user["hospital_id"]):
        db.delete(user)
        db.commit()
        return {"detail": "Usuario eliminado"}
    raise HTTPException(status_code=403)
