from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from src.models import Base

class Category(Base):
    """Modelo de categoria para transações financeiras"""
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    nome = Column(String(50), nullable=False)
    tipo = Column(String(20), nullable=False)  # 'receita' ou 'despesa'
    cor = Column(String(7), default="#3498db")  # Cor em formato hexadecimal
    icone = Column(String(30), default="fa-tag")  # Ícone FontAwesome

    # Relacionamentos
    user = relationship("User", back_populates="categories")
    transacoes = relationship("Transaction", back_populates="categoria", cascade="all, delete", passive_deletes=True)

    def __repr__(self):
        return f"<Category {self.nome}>"

    def to_dict(self):
        """Converte o objeto Category em dicionário para uso em APIs"""
        return {
            "id": self.id,
            "nome": self.nome,
            "tipo": self.tipo,
            "cor": self.cor,
            "icone": self.icone
        }
