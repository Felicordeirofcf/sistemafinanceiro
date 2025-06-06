import os

# Configurações do banco de dados
# DATABASE_URL = 'postgresql://postgres:WOBJFhAuvKGKURZOInheKDQWPQwYDgxz@postgres.railway.internal:5432/railway'
DATABASE_URL = 'sqlite:///../test.db'

# Configurações do Google OAuth
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
GOOGLE_REDIRECT_URI = os.environ.get('GOOGLE_REDIRECT_URI')

# Chave secreta para sessões do Flask
SECRET_KEY = 'bc132d7da14069340f332a6d814071b57cee8b9a3322a516'


