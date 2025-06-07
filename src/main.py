from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_login import LoginManager, current_user, login_required
from flask_mail import Mail
from dotenv import load_dotenv
import os
import sys
from datetime import datetime, timedelta
import sqlite3

print("DEBUG: Iniciando main.py")

# Carrega variáveis do arquivo .env automaticamente
load_dotenv()

# Configuração do caminho para importações
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Importação dos modelos e sessão do banco de dados
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

# Importa variáveis de ambiente do .env via os.getenv
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["GOOGLE_CLIENT_ID"] = os.getenv("GOOGLE_CLIENT_ID")
app.config["GOOGLE_CLIENT_SECRET"] = os.getenv("GOOGLE_CLIENT_SECRET")
app.config["GOOGLE_REDIRECT_URI"] = os.getenv("GOOGLE_REDIRECT_URI")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Configuração do Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME', 'seu_email@gmail.com')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD', 'sua_senha_de_app')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', 'seu_email@gmail.com')

mail = Mail(app)

print("DEBUG: Configurações do Flask aplicadas.")

# Configuração do Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"
login_manager.login_message = "Por favor, faça login para acessar esta página."

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Registro dos blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(transactions_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(alerts_bp)
app.register_blueprint(gcal_bp)

print("DEBUG: Blueprints registrados.")

# Rota principal
@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))
    return redirect(url_for("auth.login"))

# Finalização da sessão
@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

# Inicialização do banco
with app.app_context():
    print("DEBUG: Entrando no contexto da aplicação para inicializar o DB.")
    init_db()
    print("DEBUG: init_db() concluído.")
    print("Tabelas criadas ou já existentes no banco de dados.")

print("DEBUG: Preparando para executar a aplicação.")
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
print("DEBUG: Aplicação encerrada.")
