from sqlalchemy import Column, Integer, String, DateTime
import datetime
from database import Base

class HistoriaClinica(Base):
    __tablename__ = "historias_clinicas"
    id = Column(Integer, primary_key=True, index=True)
    paciente_documento = Column(String, index=True) # Enlace lógico
    medico_id = Column(Integer) # ID del médico en el auth_service
    hospital_id = Column(Integer) # ID del hospital en el hospital_service
    fecha_creacion = Column(DateTime, default=datetime.datetime.utcnow)
    diagnostico = Column(String)
    tratamiento = Column(String)
    pdf_path = Column(String, nullable=True)
