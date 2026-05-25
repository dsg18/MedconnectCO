from sqlalchemy import Column, Integer, String, DateTime, Boolean
import datetime
from database import Base

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    usuario = Column(String, index=True) # El documento del paciente
    mensaje = Column(String)
    leido = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
