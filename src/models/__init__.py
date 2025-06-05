from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
import os

# Configuração do banco de dados
# Define o caminho absoluto para o banco de dados dentro do diretório src
src_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(src_dir) # Sobe um nível para /src
db_name = 'finance.db'
db_path = os.path.join(src_dir, db_name)
DATABASE_URL = os.getenv('DATABASE_URL') # Removido o fallback para SQLite

print(f"Usando DATABASE_URL: {DATABASE_URL}") # Log para depuração

engine = create_engine(DATABASE_URL)
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    """Inicializa o banco de dados e cria as tabelas"""
    import src.models.user
    import src.models.transaction
    import src.models.category
    Base.metadata.create_all(bind=engine)
