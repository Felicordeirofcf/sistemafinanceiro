from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
import os

print("DEBUG: Iniciando src/models/__init__.py")

# Carrega DATABASE_URL do src.config
from src.config import DATABASE_URL

# Verificação da variável de ambiente
if not DATABASE_URL:
    raise ValueError("DATABASE_URL não está definida. Configure-a no Railway ou no .env.")

print(f"DEBUG: Usando DATABASE_URL: {DATABASE_URL}")

# Criação do engine com a URL do banco (PostgreSQL esperado)
try:
    engine = create_engine(DATABASE_URL, echo=True, future=True)
    print(f"DEBUG: Engine do SQLAlchemy criada com sucesso.")
except Exception as e:
    print(f"ERROR: Falha ao criar engine: {e}")
    raise

# Sessão do banco
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

# Base declarativa
Base = declarative_base()
Base.query = db_session.query_property()

# Teste de conexão para diagnóstico
def test_connection():
    try:
        with engine.connect() as connection:
            result = connection.execute("SELECT 1;")
            print("DEBUG: Conexão com banco estabelecida com sucesso.")
    except Exception as e:
        print(f"ERROR: Falha ao conectar ao banco: {e}")
        raise

# Inicialização do banco e criação de tabelas
def init_db():
    print("DEBUG: Iniciando init_db()")
    import src.models.user
    import src.models.transaction
    import src.models.category
    try:
        Base.metadata.create_all(bind=engine)
        print("DEBUG: Tabelas criadas com sucesso.")
    except Exception as e:
        print(f"ERROR: Falha na criação das tabelas: {e}")
        raise

# Executa teste no momento do carregamento
test_connection()
