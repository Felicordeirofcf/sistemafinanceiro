from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_login import LoginManager, current_user, login_required
import os
from datetime import datetime, timedelta

# DEBUG: Iniciando a aplicação
print("DEBUG: Iniciando main.py")

# Carrega variáveis do arquivo .env localmente (ignorado no Railway)
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("DEBUG: Variáveis do .env carregadas.")
except ImportError:
    print("DEBUG: python-dotenv não encontrado. Prosseguindo sem carregar .env")

# Importação dos módulos e rotas
from models import db_session, init_db
from models.user import User
from models.transaction import Transaction
from models.category import Category

from routes.auth import auth_bp
from routes.transactions import transactions_bp
from routes.dashboard import dashboard_bp
from routes.alerts import alerts_bp

print("DEBUG: Modelos e rotas importados.")

# Criação da aplicação Flask
app = Flask(__name__)

# Configurações principais com variáveis de ambiente
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# ✅ Configurações de sessão seguras para ambiente HTTPS + OAuth
app.config["SESSION_COOKIE_SAMESITE"] = "None"
app.config["SESSION_COOKIE_SECURE"] = True
app.config["REMEMBER_COOKIE_DURATION"] = timedelta(days=7)

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


