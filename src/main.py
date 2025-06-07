from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_login import LoginManager, current_user, login_required
from flask_mail import Mail
import os
import sys
from datetime import datetime, timedelta
import sqlite3

# DEBUG: Iniciando a aplicação
print("DEBUG: Iniciando main.py")

# Carrega variáveis do arquivo .env localmente (ignorado no Railway)
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("DEBUG: Variáveis do .env carregadas.")
except ImportError:
    print("DEBUG: python-dotenv não encontrado. Prosseguindo sem carregar .env")

# Ajuste de caminho para imports do projeto
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Importação dos módulos e rotas
try:
    from src.models import db_session, init_db
    from src.models.user import User
    from src.models.transaction import Transaction
    from src.models.category import Category
    from src.models.google_calendar_auth import GoogleCalendarAuth

    from src.routes.auth import auth_bp
    from src.routes.transactions import transactions_bp
    from src.routes.dashboard import dashboard_bp
    from src.routes.alerts import alerts_bp
    from src.routes.gcal import gcal_bp
except ImportError:
    from models import db_session, init_db
    from models.user import User
    from models.transaction import Transaction
    from models.category import Category
    from models.google_calendar_auth import GoogleCalendarAuth

    from routes.auth import auth_bp
    from routes.transactions import transactions_bp
    from routes.dashboard import dashboard_bp
    from routes.alerts import alerts_bp
    from routes.gcal import gcal_bp

print("DEBUG: Modelos e rotas importados.")

# Criação da aplicação Flask
app = Flask(__name__)

# Configurações principais com variáveis de ambiente
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.config["GOOGLE_CLIENT_ID"] = os.getenv("GOOGLE_CLIENT_ID")
app.config["GOOGLE_CLIENT_SECRET"] = os.getenv("GOOGLE_CLIENT_SECRET")
app.config["GOOGLE_REDIRECT_URI"] = os.getenv("GOOGLE_REDIRECT_URI")

# ✅ Configurações de sessão seguras para ambiente HTTPS + OAuth
app.config["SESSION_COOKIE_SAMESITE"] = "None"
app.config["SESSION_COOKIE_SECURE"] = True
app.config["REMEMBER_COOKIE_DURATION"] = timedelta(days=7)

# Configuração do e-mail (opcional)
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME", "seu_email@gmail.com")
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD", "sua_senha_de_app")
app.config["MAIL_DEFAULT_SENDER"] = os.getenv("MAIL_DEFAULT_SENDER", "seu_email@gmail.com")

mail = Mail(app)

print("DEBUG: Configurações aplicadas com sucesso.")

# Configuração do login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"
login_manager.login_message = "Por favor, faça login para acessar esta página."

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Registro de rotas (blueprints)
app.register_blueprint(auth_bp)
app.register_blueprint(transactions_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(alerts_bp)
app.register_blueprint(gcal_bp)

print("DEBUG: Blueprints registrados.")

# Rota raiz
@app.route("/")
def index():
    print(f"[ROOT] Usuário autenticado? {current_user.is_authenticated}")
    if current_user.is_authenticated:
        print(f"[ROOT] Redirecionando para dashboard de: {current_user.username}")
        return redirect(url_for("dashboard.index"))
    return redirect(url_for("auth.login"))

# Encerramento da sessão do banco após cada requisição
@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

# Inicialização do banco de dados
with app.app_context():
    print("DEBUG: Inicializando banco de dados.")
    init_db()
    print("DEBUG: init_db() concluído com sucesso.")

# Execução local
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

print("DEBUG: Aplicação finalizada.")
