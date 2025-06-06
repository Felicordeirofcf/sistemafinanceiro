import os

# Configurações do banco de dados
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///./test.db')

# Configurações do Google OAuth
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
GOOGLE_REDIRECT_URI = os.environ.get('GOOGLE_REDIRECT_URI')

# Chave secreta para sessões do Flask
SECRET_KEY = os.environ.get('SECRET_KEY', 'uma_chave_secreta_muito_segura')


