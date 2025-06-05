from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
import os

print("DEBUG: Iniciando src/models/__init__.py")

# Configuração do banco de dados
# Define o caminho absoluto para o banco de dados dentro do diretório src
src_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(src_dir) # Sobe um nível para /src
db_name = 'finance.db'
db_path = os.path.join(src_dir, db_name)

DATABASE_URL = os.getenv('DATABASE_URL')

print(f"DEBUG: DATABASE_URL obtida: {DATABASE_URL}")

# Adiciona uma verificação explícita para DATABASE_URL
if not DATABASE_URL:
    print("ERROR: DATABASE_URL environment variable is not set.")
    raise ValueError("DATABASE_URL environment variable is not set. Please configure it in Railway.")

print(f"DEBUG: Usando DATABASE_URL: {DATABASE_URL}") # Log para depuração

try:
    engine = create_engine(DATABASE_URL)
    print("DEBUG: Engine do SQLAlchemy criada com sucesso.")
except Exception as e:
    print(f"ERROR: Erro ao criar a engine do SQLAlchemy: {e}")
    raise

db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    """Inicializa o banco de dados e cria as tabelas"""
    print("DEBUG: Iniciando init_db()")
    import src.models.user
    import src.models.transaction
    import src.models.category
    try:
        Base.metadata.create_all(bind=engine)
        print("DEBUG: Base.metadata.create_all() executado com sucesso.")
    except Exception as e:
        print(f"ERROR: Erro ao criar tabelas no banco de dados: {e}")
        raise
    print("DEBUG: init_db() concluído.")
