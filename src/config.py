import os

# Carrega do .env (se estiver rodando localmente)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # Ignora se não estiver disponível

# Configurações do banco de dados
DATABASE_URL = os.getenv("DATABASE_URL")

# Chave secreta da aplicação Flask
SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret-key")
