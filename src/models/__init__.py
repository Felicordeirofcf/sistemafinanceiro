from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
import os

print("[INIT] Iniciando src/models/__init__.py")

# Carrega a URL do banco de dados
try:
    from src.config import DATABASE_URL
except ImportError:
    raise ImportError("[ERRO] Não foi possível importar DATABASE_URL de src.config")

# Verifica se DATABASE_URL está definida corretamente
if not DATABASE_URL or not isinstance(DATABASE_URL, str):
    raise ValueError("[ERRO] DATABASE_URL não está definida. Configure-a corretamente no Railway ou arquivo .env.")

print(f"[INIT] Usando DATABASE_URL: {DATABASE_URL}")

# Criação do engine SQLAlchemy com log detalhado (echo=True)
try:
    engine = create_engine(DATABASE_URL, echo=True, future=True)
    print("[INIT] Engine SQLAlchemy criado com sucesso.")
except Exception as e:
    print(f"[ERRO] Falha ao criar engine: {e}")
    raise

# Criação da sessão de banco de dados
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db_session = scoped_session(SessionLocal)

# Criação da base declarativa
Base = declarative_base()
Base.query = db_session.query_property()

# Testa conexão com o banco de dados
def test_connection():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            print("[INIT] Conexão com o banco de dados estabelecida com sucesso.")
    except Exception as e:
        print(f"[ERRO] Falha ao conectar ao banco de dados: {e}")
        raise

# Inicializa o banco de dados criando as tabelas
def init_db():
    print("[INIT] Iniciando criação de tabelas com init_db()")
    # Importa os modelos para que o SQLAlchemy reconheça as tabelas
    import src.models.user
    import src.models.transaction
    import src.models.category
    try:
        Base.metadata.create_all(bind=engine)
        print("[INIT] Tabelas criadas com sucesso.")
    except Exception as e:
        print(f"[ERRO] Falha ao criar as tabelas: {e}")
        raise

# Executa teste de conexão ao carregar o módulo
test_connection()
