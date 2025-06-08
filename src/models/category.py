from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from src.models import Base

class Category(Base):
    """Modelo de categoria para transações (removido do uso ativo)"""
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    nome = Column(String(50), nullable=False)
    tipo = Column(String(20), nullable=False)  # 'receita' ou 'despesa'
    cor = Column(String(7), default='#3498db')  # Formato hexadecimal (#RRGGBB)
    icone = Column(String(30), default='fa-tag')  # Ícone FontAwesome

    # As relações abaixo podem ser mantidas apenas por compatibilidade com o banco
    user = relationship("User", back_populates="categories")
    transacoes = relationship("Transaction", back_populates="categoria")

    def __repr__(self):
        return f'<Category {self.nome}>'

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'tipo': self.tipo,
            'cor': self.cor,
            'icone': self.icone
        }
