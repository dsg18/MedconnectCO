from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
import os

from .. import models, schemas, database
from ..auth_service import get_current_user
from ..pdf_service import generar_pdf_historia

router = APIRouter(prefix="/historias", tags=["historias clínicas"])


@router.post("/", response_model=schemas.HistoriaClinica, status_code=status.HTTP_201_CREATED)
def crear_historia(
    historia: schemas.HistoriaClinicaCreate,
    db: Session = Depends(database.get_db),
    current_user: models.Usuario = Depends(get_current_user),
):
    """
    Crea una nueva historia clínica y genera automáticamente su PDF.
    Solo los médicos pueden crear historias clínicas.
    """
    if current_user.rol != "medico":
        raise HTTPException(status_code=403, detail="Solo los médicos pueden crear historias clínicas")

    # Verificar que el hospital del médico esté aprobado
    if current_user.hospital_id:
        hospital = db.query(models.Hospital).filter(models.Hospital.id == current_user.hospital_id).first()
        if hospital and not hospital.aprobado:
            raise HTTPException(
                status_code=403,
                detail="Tu hospital aún no ha sido aprobado en la red nacional"
            )

    paciente = db.query(models.Paciente).filter(
        models.Paciente.documento == historia.paciente_documento
    ).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado con ese documento")

    db_historia = models.HistoriaClinica(
        paciente_id=paciente.id,
        medico_id=current_user.id,
        diagnostico=historia.diagnostico,
        tratamiento=historia.tratamiento,
    )
    db.add(db_historia)
    db.commit()
    db.refresh(db_historia)

    # ── Generar PDF vinculado a esta historia ─────────────────────────────────
    try:
        hospital_nombre = ""
        if current_user.hospital_id:
            h = db.query(models.Hospital).filter(models.Hospital.id == current_user.hospital_id).first()
            hospital_nombre = h.nombre if h else ""

        pdf_path = generar_pdf_historia(
            historia_id      = db_historia.id,
            paciente_doc     = paciente.documento,
            paciente_nombre  = paciente.nombre_completo,
            medico_username  = current_user.username,
            hospital_nombre  = hospital_nombre,
            diagnostico      = historia.diagnostico,
            tratamiento      = historia.tratamiento,
            fecha            = db_historia.fecha_creacion,
        )
        db_historia.pdf_path = pdf_path
        db.commit()
        db.refresh(db_historia)
    except Exception as e:
        # Si el PDF falla, la historia ya fue guardada — no se revierte
        print(f"[WARN] No se pudo generar el PDF de la historia {db_historia.id}: {e}")

    return db_historia


@router.get("/", response_model=List[schemas.HistoriaClinica])
def listar_historias(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(database.get_db),
    current_user: models.Usuario = Depends(get_current_user),
):
    """Lista historias clínicas. Solo admin y admin_clinica pueden listarlas."""
    if current_user.rol == "medico":
        raise HTTPException(
            status_code=403,
            detail="Los médicos no tienen acceso al listado de historias clínicas."
        )

    if current_user.rol == "admin":
        return db.query(models.HistoriaClinica).offset(skip).limit(limit).all()

    # admin_clinica: solo historias de médicos de su hospital
    medico_ids = [
        u.id for u in db.query(models.Usuario).filter(
            models.Usuario.hospital_id == current_user.hospital_id
        ).all()
    ]
    return (
        db.query(models.HistoriaClinica)
        .filter(models.HistoriaClinica.medico_id.in_(medico_ids))
        .offset(skip).limit(limit).all()
    )


@router.get("/paciente/{documento}", response_model=List[schemas.HistoriaClinica])
def historias_por_paciente(
    documento: str,
    db: Session = Depends(database.get_db),
    current_user: models.Usuario = Depends(get_current_user),
):
    """Obtiene todas las historias clínicas de un paciente por su documento."""
    paciente = db.query(models.Paciente).filter(models.Paciente.documento == documento).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")

    return (
        db.query(models.HistoriaClinica)
        .filter(models.HistoriaClinica.paciente_id == paciente.id)
        .all()
    )


@router.get("/{historia_id}/pdf")
def descargar_pdf_historia(
    historia_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.Usuario = Depends(get_current_user),
):
    """Descarga el PDF generado de una historia clínica."""
    historia = db.query(models.HistoriaClinica).filter(models.HistoriaClinica.id == historia_id).first()
    if not historia:
        raise HTTPException(status_code=404, detail="Historia clínica no encontrada")

    # Control de acceso
    if current_user.rol == "medico" and historia.medico_id != current_user.id:
        raise HTTPException(status_code=403, detail="No autorizado para descargar esta historia")

    if not historia.pdf_path or not os.path.exists(historia.pdf_path):
        raise HTTPException(status_code=404, detail="El PDF aún no está disponible para esta historia")

    return FileResponse(
        historia.pdf_path,
        media_type="application/pdf",
        filename=f"historia_clinica_{historia_id}.pdf",
    )


@router.get("/{historia_id}", response_model=schemas.HistoriaClinica)
def obtener_historia(
    historia_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.Usuario = Depends(get_current_user),
):
    """Obtiene una historia clínica por ID."""
    historia = db.query(models.HistoriaClinica).filter(models.HistoriaClinica.id == historia_id).first()
    if not historia:
        raise HTTPException(status_code=404, detail="Historia clínica no encontrada")

    if current_user.rol == "medico" and historia.medico_id != current_user.id:
        raise HTTPException(status_code=403, detail="No autorizado para ver esta historia")

    return historia


@router.put("/{historia_id}", response_model=schemas.HistoriaClinica)
def actualizar_historia(
    historia_id: int,
    datos: schemas.HistoriaClinicaBase,
    db: Session = Depends(database.get_db),
    current_user: models.Usuario = Depends(get_current_user),
):
    """Actualiza diagnóstico y tratamiento de una historia. Solo el médico que la creó."""
    historia = db.query(models.HistoriaClinica).filter(models.HistoriaClinica.id == historia_id).first()
    if not historia:
        raise HTTPException(status_code=404, detail="Historia clínica no encontrada")

    if current_user.rol == "medico" and historia.medico_id != current_user.id:
        raise HTTPException(status_code=403, detail="No autorizado para modificar esta historia")

    historia.diagnostico = datos.diagnostico
    historia.tratamiento = datos.tratamiento
    db.commit()
    db.refresh(historia)
    return historia
