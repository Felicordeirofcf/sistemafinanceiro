from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.sql import func
from src.models import Base

class GoogleCalendarAuth(Base):
    """Modelo para armazenar dados de autenticação do Google Calendar"""
    __tablename__ = 'google_calendar_auth'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, unique=True)
    access_token = Column(Text, nullable=True)
    refresh_token = Column(Text, nullable=True)
    token_expiry = Column(DateTime, nullable=True)
    calendar_id = Column(String(255), nullable=True)  # ID do calendário principal ou selecionado
    sync_enabled = Column(Integer, default=1)  # 1=habilitado, 0=desabilitado
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f'<GoogleCalendarAuth user_id={self.user_id}>'
