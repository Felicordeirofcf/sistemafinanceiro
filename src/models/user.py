from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from src.models import Base

class User(Base, UserMixin):
    """Modelo de usuário para autenticação"""
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(256), nullable=True)  # Permitir login via Google
    created_at = Column(DateTime, default=func.now())

    def __init__(self, username, email, password=None):
        self.username = username
        self.email = email
        if password:
            self.set_password(password)
        else:
            self.password_hash = None

    def set_password(self, password):
        """Define a senha criptografada para o usuário"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifica se a senha fornecida corresponde à senha armazenada"""
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


