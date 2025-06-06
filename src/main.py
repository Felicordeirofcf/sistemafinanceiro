from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_login import LoginManager, current_user, login_required
import os
import sys
from datetime import datetime, timedelta
import sqlite3

print("DEBUG: Iniciando main.py")

# Configuração do caminho para importações
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Função para verificar e atualizar o esquema do banco de dados
# Esta função deve ser executada ANTES de qualquer importação de modelos


# Executa a migração do banco ANTES de importar os modelos
# Isso garante que as colunas existam antes de qualquer consulta ORM


# Importação dos modelos e sessão do banco de dados
try:
    from src.models import db_session, init_db
    from src.models.user import User
    from src.models.transaction import Transaction
    from src.models.category import Category
    from src.models.google_calendar_auth import GoogleCalendarAuth

    # Importação das rotas
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

    # Importação das rotas
    from routes.auth import auth_bp
    from routes.transactions import transactions_bp
    from routes.dashboard import dashboard_bp
    from routes.alerts import alerts_bp
    from routes.gcal import gcal_bp

print("DEBUG: Modelos e rotas importados.")

# Criação da aplicação Flask
app = Flask(__name__)
from src.config import SECRET_KEY, DATABASE_URL, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI

app.config["SECRET_KEY"] = SECRET_KEY
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["GOOGLE_CLIENT_ID"] = GOOGLE_CLIENT_ID
app.config["GOOGLE_CLIENT_SECRET"] = GOOGLE_CLIENT_SECRET
app.config["GOOGLE_REDIRECT_URI"] = GOOGLE_REDIRECT_URI

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

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
app.register_blueprint(gcal_bp)  # Novo blueprint para Google Calendar

print("DEBUG: Blueprints registrados.")

# Rota principal - redireciona para o dashboard
@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))
    return redirect(url_for("auth.login"))

# Encerramento da sessão do banco de dados ao finalizar a requisição
@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

# Inicialização do banco de dados e criação das categorias padrão
with app.app_context():
    print("DEBUG: Entrando no contexto da aplicação para inicializar o DB.")
    # Inicializa o banco de dados
    init_db()
    print("DEBUG: init_db() concluído.")
    print("Tabelas criadas ou já existentes no banco de dados.")
    
    # A lógica de criação de categorias padrão foi removida daqui
    # para evitar o erro ForeignKeyViolation, pois ela dependia de um
    # user_id fixo que pode não existir no momento da inicialização.
    # As categorias devem ser criadas após o registro do usuário
    # ou por um processo de seed de dados separado.

print("DEBUG: Preparando para executar a aplicação.")
# Execução da aplicação
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
print("DEBUG: Aplicação encerrada.")


