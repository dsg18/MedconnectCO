from sqlalchemy import Column, Integer, String, DateTime
import datetime
from database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    usuario = Column(String, index=True)
    accion = Column(String) # CREATE, UPDATE, DELETE, LOGIN
    recurso = Column(String) # Paciente, Historia, Hospital
    detalle = Column(String)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
