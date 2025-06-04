from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from src.models import Base

class Transaction(Base):
    """Modelo de transação financeira"""
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    tipo = Column(String(20), nullable=False)  # 'receita' ou 'despesa'
    valor = Column(Float, nullable=False)
    data = Column(String(10), nullable=False)  # Formato YYYY-MM-DD
    descricao = Column(String(200), nullable=False)
    categoria_id = Column(Integer, ForeignKey('categories.id'), nullable=False)
    pago = Column(Boolean, default=False)
    vencimento = Column(String(10), nullable=True)  # Formato YYYY-MM-DD
    notificado = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())

    # Relacionamentos
    user = relationship("User", backref="transactions")
    categoria = relationship("Category", backref="transactions")

    def __repr__(self):
        return f'<Transaction {self.descricao}: R${self.valor:.2f}>'
    
    def to_dict(self):
        """Converte o objeto para um dicionário"""
        return {
            'id': self.id,
            'tipo': self.tipo,
            'valor': self.valor,
            'data': self.data,
            'descricao': self.descricao,
            'categoria': self.categoria.nome if self.categoria else None,
            'categoria_id': self.categoria_id,
            'pago': self.pago,
            'vencimento': self.vencimento,
            'cor': self.categoria.cor if self.categoria else '#3498db',
            'icone': self.categoria.icone if self.categoria else 'fa-tag'
        }
