from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
import os

print("[INIT] Iniciando src/models/__init__.py")

# Carrega a URL do banco
try:
    from src.config import DATABASE_URL
except ImportError:
    raise ImportError("[INIT][ERRO] Não foi possível importar DATABASE_URL de config.")

# Validação da URL
if not DATABASE_URL or not isinstance(DATABASE_URL, str):
    raise ValueError("[INIT][ERRO] DATABASE_URL não está definida ou é inválida.")

print(f"[INIT] Usando DATABASE_URL: {DATABASE_URL}")

# Criação do engine com echo para log SQL (desative em produção se necessário)
try:
    engine = create_engine(DATABASE_URL, echo=True, future=True)
    print("[INIT] Engine SQLAlchemy criado com sucesso.")
except Exception as e:
    print(f"[INIT][ERRO] Falha ao criar engine: {e}")
    raise

# Sessão de banco de dados
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db_session = scoped_session(SessionLocal)

# Base declarativa
Base = declarative_base()
Base.query = db_session.query_property()

# Teste de conexão
def test_connection():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            print("[INIT] Conexão com o banco estabelecida com sucesso.")
    except Exception as e:
        print(f"[INIT][ERRO] Conexão falhou: {e}")
        raise

# Inicialização das tabelas
def init_db():
    print("[INIT] Iniciando criação de tabelas com init_db()")
    try:
        import models.user
        import models.transaction
        import models.category
        Base.metadata.create_all(bind=engine)
        print("[INIT] Tabelas criadas com sucesso.")
    except Exception as e:
        print(f"[INIT][ERRO] Falha ao criar tabelas: {e}")
        raise

# Executa conexão ao iniciar o módulo
test_connection()
