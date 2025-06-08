from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Text, Date
from sqlalchemy.orm import relationship
from models import Base

class Transaction(Base):
    """Modelo para transações financeiras"""
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    descricao = Column(String(255), nullable=False)
    valor = Column(Integer, nullable=False)  # Valor em centavos
    tipo = Column(String(50), nullable=False)  # 'receita' ou 'despesa'
    data = Column(Date, nullable=False)  # Alterado para tipo Date
    vencimento = Column(Date, nullable=True)  # Alterado para tipo Date
    pago = Column(Boolean, default=False)
    categoria_id = Column(Integer, ForeignKey('categories.id'), nullable=True)
    gcal_event_id = Column(String(255), nullable=True)  # ID do evento no Google Calendar
    observacoes = Column(Text, nullable=True)
    
    # Campos para despesas recorrentes
    is_recurring = Column(Boolean, default=False)  # Indica se é uma despesa recorrente
    recurrence_frequency = Column(String(50), nullable=True)  # mensal, trimestral, semestral, anual
    recurrence_start_date = Column(Date, nullable=True)  # Alterado para tipo Date
    recurrence_end_date = Column(Date, nullable=True)  # Alterado para tipo Date (opcional)
    parent_transaction_id = Column(Integer, ForeignKey('transactions.id'), nullable=True)  # ID da transação original
    
    # Relacionamentos
    categoria = relationship("Category", back_populates="transacoes")
    child_transactions = relationship("Transaction", 
                                     foreign_keys=[parent_transaction_id],
                                     backref="parent_transaction",
                                     remote_side=[id])

    def __repr__(self):
        return f'<Transaction {self.descricao} {self.valor}>'
