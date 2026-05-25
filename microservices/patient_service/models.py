from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Paciente(Base):
    __tablename__ = "pacientes"
    id = Column(Integer, primary_key=True, index=True)
    documento = Column(String, unique=True, index=True)
    nombre_completo = Column(String)
    fecha_expedicion = Column(String)
    fecha_nacimiento = Column(String)
    pin = Column(String) 
    consentimiento = Column(Boolean, default=False)
    
    condiciones = relationship("CondicionCronica", back_populates="paciente")

class CondicionCronica(Base):
    __tablename__ = "condiciones_cronicas"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String) # Ej: Diabetes, Hipertensión
    fecha_diagnostico = Column(String)
    paciente_id = Column(Integer, ForeignKey("pacientes.id"))
    
    paciente = relationship("Paciente", back_populates="condiciones")
