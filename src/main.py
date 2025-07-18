from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_login import LoginManager, current_user, login_required
import os
from datetime import datetime, timedelta

# DEBUG: Iniciando a aplicação
print("DEBUG: Iniciando main.py")

# Carrega variáveis do .env localmente (ignorado no Railway)
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("DEBUG: Variáveis do .env carregadas.")
except ImportError:
    print("DEBUG: python-dotenv não encontrado. Prosseguindo sem carregar .env")

# Importações dos modelos e rotas
from src.models import db_session, init_db
from src.models.user import User
from src.models.transaction import Transaction
from src.models.category import Category

from src.routes.auth import auth_bp
from src.routes.transactions import transactions_bp
from src.routes.dashboard import dashboard_bp
from src.routes.alerts import alerts_bp

print("DEBUG: Modelos e rotas importados.")

# Criação da aplicação Flask
app = Flask(__name__)

# Configurações principais com variáveis de ambiente
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "supersecretkey")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///banco.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Configurações seguras de sessão
app.config["SESSION_COOKIE_SAMESITE"] = "None"
app.config["SESSION_COOKIE_SECURE"] = True
app.config["REMEMBER_COOKIE_DURATION"] = timedelta(days=7)

print("DEBUG: Configurações aplicadas com sucesso.")

# Gerenciador de login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"
login_manager.login_message = "Por favor, faça login para acessar esta página."

@login_manager.user_loader
def load_user(user_id):
    return db_session.query(User).get(int(user_id))

# Registro de blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(transactions_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(alerts_bp)

print("DEBUG: Blueprints registrados.")

# Rota principal
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
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)

print("DEBUG: Aplicação finalizada.")
