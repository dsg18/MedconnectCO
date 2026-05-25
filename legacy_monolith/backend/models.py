from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
import datetime
from .database import Base

class Hospital(Base):
    __tablename__ = "hospitales"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    direccion = Column(String)
    aprobado = Column(Boolean, default=False)
    
    usuarios = relationship("Usuario", back_populates="hospital")

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    rol = Column(String) # admin, admin_clinica, medico
    hospital_id = Column(Integer, ForeignKey("hospitales.id"), nullable=True)
    creado_por = Column(String, nullable=True) # Username del creador

    hospital = relationship("Hospital", back_populates="usuarios")
    historias_creadas = relationship("HistoriaClinica", back_populates="medico")

class Paciente(Base):
    __tablename__ = "pacientes"

    id = Column(Integer, primary_key=True, index=True)
    documento = Column(String, unique=True, index=True)
    nombre_completo = Column(String)
    historias = relationship("HistoriaClinica", back_populates="paciente")

class HistoriaClinica(Base):
    __tablename__ = "historias_clinicas"

    id = Column(Integer, primary_key=True, index=True)
    paciente_id = Column(Integer, ForeignKey("pacientes.id"))
    medico_id = Column(Integer, ForeignKey("usuarios.id"))
    fecha_creacion = Column(DateTime, default=datetime.datetime.utcnow)
    diagnostico = Column(String)
    tratamiento = Column(String)
    pdf_path = Column(String, nullable=True)  # Ruta al PDF generado

    paciente = relationship("Paciente", back_populates="historias")
    medico = relationship("Usuario", back_populates="historias_creadas")
