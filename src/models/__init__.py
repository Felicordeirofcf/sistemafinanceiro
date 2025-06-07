from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
import os

print("DEBUG: Iniciando src/models/__init__.py")

# Carrega DATABASE_URL do arquivo de configuração
from src.config import DATABASE_URL

# Verifica se a variável de ambiente está definida
if not DATABASE_URL:
    raise ValueError("DATABASE_URL não está definida. Configure-a no Railway ou no .env.")

print(f"DEBUG: Usando DATABASE_URL: {DATABASE_URL}")

# Criação do engine SQLAlchemy com echo=True para log detalhado
try:
    engine = create_engine(DATABASE_URL, echo=True, future=True)
    print("DEBUG: Engine do SQLAlchemy criada com sucesso.")
except Exception as e:
    print(f"ERROR: Falha ao criar engine: {e}")
    raise

# Criação da sessão do banco
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

# Criação da base declarativa
Base = declarative_base()
Base.query = db_session.query_property()

# Função de teste de conexão segura
def test_connection():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            print("DEBUG: Conexão com banco estabelecida com sucesso.")
    except Exception as e:
        print(f"ERROR: Falha ao conectar ao banco: {e}")
        raise

# Inicializa o banco de dados criando as tabelas
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

# Executa o teste de conexão ao carregar o módulo
test_connection()


