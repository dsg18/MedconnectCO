from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from .. import models, schemas, database
from ..auth_service import get_current_user

router = APIRouter(prefix="/pacientes", tags=["pacientes"])


@router.post("/", response_model=schemas.Paciente, status_code=status.HTTP_201_CREATED)
def registrar_paciente(
    paciente: schemas.PacienteCreate,
    db: Session = Depends(database.get_db),
    current_user: models.Usuario = Depends(get_current_user),
):
    """Registra un nuevo paciente. Médicos y admins pueden hacerlo."""
    if current_user.rol not in ("medico", "admin", "admin_clinica"):
        raise HTTPException(status_code=403, detail="No autorizado para registrar pacientes")

    existente = db.query(models.Paciente).filter(models.Paciente.documento == paciente.documento).first()
    if existente:
        raise HTTPException(status_code=400, detail="Ya existe un paciente con ese documento")

    db_paciente = models.Paciente(**paciente.dict())
    db.add(db_paciente)
    db.commit()
    db.refresh(db_paciente)
    return db_paciente


@router.get("/", response_model=List[schemas.Paciente])
def listar_pacientes(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(database.get_db),
    current_user: models.Usuario = Depends(get_current_user),
):
    """Lista todos los pacientes registrados."""
    return db.query(models.Paciente).offset(skip).limit(limit).all()


@router.get("/{documento}", response_model=schemas.PacienteDetalle)
def buscar_paciente_por_documento(
    documento: str,
    db: Session = Depends(database.get_db),
    current_user: models.Usuario = Depends(get_current_user),
):
    """Busca un paciente por número de documento e incluye sus historias clínicas."""
    paciente = db.query(models.Paciente).filter(models.Paciente.documento == documento).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    return paciente


@router.put("/{documento}", response_model=schemas.Paciente)
def actualizar_paciente(
    documento: str,
    datos: schemas.PacienteCreate,
    db: Session = Depends(database.get_db),
    current_user: models.Usuario = Depends(get_current_user),
):
    """Actualiza los datos de un paciente."""
    if current_user.rol not in ("medico", "admin", "admin_clinica"):
        raise HTTPException(status_code=403, detail="No autorizado")

    paciente = db.query(models.Paciente).filter(models.Paciente.documento == documento).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")

    paciente.nombre_completo = datos.nombre_completo
    paciente.documento = datos.documento
    db.commit()
    db.refresh(paciente)
    return paciente
