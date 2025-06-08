from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy.orm import relationship  # <-- IMPORTANTE
from src.models import Base

class User(Base, UserMixin):
    """Modelo de usuário para autenticação e relacionamento com dados financeiros"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(256), nullable=True)  # Suporte a login por senha ou OAuth
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # RELACIONAMENTO COM CATEGORIES
    categories = relationship("Category", back_populates="user")

    def __init__(self, username, email, password=None):
        self.username = username
        self.email = email
        if password:
            self.set_password(password)
        else:
            self.password_hash = None

    def set_password(self, password: str):
        """Cria o hash seguro da senha"""
        if password:
            self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Compara senha informada com o hash"""
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"
