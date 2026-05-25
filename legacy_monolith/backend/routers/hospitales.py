from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from .. import models, schemas, database
from ..auth_service import get_current_user

router = APIRouter(prefix="/hospitales", tags=["hospitales"])


@router.post("/", response_model=schemas.Hospital, status_code=status.HTTP_201_CREATED)
def crear_hospital(
    hospital: schemas.HospitalCreate,
    db: Session = Depends(database.get_db),
    current_user: models.Usuario = Depends(get_current_user),
):
    """Registra un nuevo hospital. Solo el admin del sistema puede hacerlo."""
    if current_user.rol != "admin":
        raise HTTPException(status_code=403, detail="Solo el administrador puede registrar hospitales")

    db_hospital = models.Hospital(**hospital.dict())
    db.add(db_hospital)
    db.commit()
    db.refresh(db_hospital)
    return db_hospital


@router.get("/", response_model=List[schemas.Hospital])
def listar_hospitales(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(database.get_db),
    current_user: models.Usuario = Depends(get_current_user),
):
    """Lista todos los hospitales registrados."""
    return db.query(models.Hospital).offset(skip).limit(limit).all()


@router.get("/{hospital_id}", response_model=schemas.Hospital)
def obtener_hospital(
    hospital_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.Usuario = Depends(get_current_user),
):
    """Obtiene un hospital por ID."""
    hospital = db.query(models.Hospital).filter(models.Hospital.id == hospital_id).first()
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital no encontrado")
    return hospital


@router.patch("/{hospital_id}/aprobar", response_model=schemas.Hospital)
def aprobar_hospital(
    hospital_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.Usuario = Depends(get_current_user),
):
    """Aprueba un hospital para que pueda operar en la red. Solo el admin del sistema."""
    if current_user.rol != "admin":
        raise HTTPException(status_code=403, detail="Solo el administrador puede aprobar hospitales")

    hospital = db.query(models.Hospital).filter(models.Hospital.id == hospital_id).first()
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital no encontrado")

    hospital.aprobado = True
    db.commit()
    db.refresh(hospital)
    return hospital


@router.delete("/{hospital_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_hospital(
    hospital_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.Usuario = Depends(get_current_user),
):
    """Elimina un hospital. Solo el admin del sistema."""
    if current_user.rol != "admin":
        raise HTTPException(status_code=403, detail="Solo el administrador puede eliminar hospitales")

    hospital = db.query(models.Hospital).filter(models.Hospital.id == hospital_id).first()
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital no encontrado")

    db.delete(hospital)
    db.commit()
