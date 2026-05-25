from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from .. import models, schemas, database
from ..auth_service import get_current_user, get_password_hash

router = APIRouter(prefix="/usuarios", tags=["usuarios"])


@router.get("/", response_model=List[schemas.Usuario])
def listar_usuarios(
    db: Session = Depends(database.get_db),
    current_user: models.Usuario = Depends(get_current_user),
):
    """
    Admin del sistema: ve todos los usuarios.
    Admin de clínica: ve solo los usuarios de su hospital.
    """
    if current_user.rol == "admin":
        return db.query(models.Usuario).all()
    if current_user.rol == "admin_clinica":
        return db.query(models.Usuario).filter(
            models.Usuario.hospital_id == current_user.hospital_id
        ).all()
    raise HTTPException(status_code=403, detail="No autorizado")


@router.post("/", response_model=schemas.Usuario, status_code=status.HTTP_201_CREATED)
def crear_usuario(
    user: schemas.UsuarioCreate,
    db: Session = Depends(database.get_db),
    current_user: models.Usuario = Depends(get_current_user),
):
    """
    Admin del sistema: puede crear cualquier usuario con cualquier rol.
    Admin de clínica: solo puede crear médicos dentro de su propio hospital.
    """
    if current_user.rol not in ("admin", "admin_clinica"):
        raise HTTPException(status_code=403, detail="No autorizado para crear usuarios")

    # Lógica de validación de hospital
    if current_user.rol == "admin":
        # Si el admin del sistema crea un admin de clínica o médico, el hospital_id es obligatorio
        if user.rol in ("admin_clinica", "medico") and not user.hospital_id:
            raise HTTPException(status_code=400, detail="Debe asociar este usuario a un hospital")
        final_hospital_id = user.hospital_id if user.rol != "admin" else None
    
    elif current_user.rol == "admin_clinica":
        if user.rol not in ("medico",):
            raise HTTPException(status_code=403, detail="Solo puede crear usuarios con rol médico")
        # El hospital se hereda automáticamente del admin que lo crea
        final_hospital_id = current_user.hospital_id

    existing = db.query(models.Usuario).filter(models.Usuario.username == user.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="El nombre de usuario ya existe")

    db_user = models.Usuario(
        username=user.username,
        hashed_password=get_password_hash(user.password),
        rol=user.rol,
        hospital_id=final_hospital_id,
        creado_por=current_user.username, # Registro de quién lo creó
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_usuario(
    usuario_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.Usuario = Depends(get_current_user),
):
    """
    Admin del sistema: puede eliminar cualquier usuario.
    Admin de clínica: solo puede eliminar usuarios de su hospital.
    """
    if current_user.rol not in ("admin", "admin_clinica"):
        raise HTTPException(status_code=403, detail="No autorizado")

    user = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="No puedes eliminarte a ti mismo")

    if current_user.rol == "admin_clinica" and user.hospital_id != current_user.hospital_id:
        raise HTTPException(status_code=403, detail="No autorizado: usuario pertenece a otro hospital")

    db.delete(user)
    db.commit()
