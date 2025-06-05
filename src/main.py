from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_login import LoginManager, current_user, login_required
import os
import sys
from datetime import datetime, timedelta
import sqlite3

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

# Criação da aplicação Flask
app = Flask(__name__)

# Configuração do Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return db_session.query(User).get(int(user_id))

# Registro dos blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(transactions_bp, url_prefix='/transactions')
app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
app.register_blueprint(alerts_bp, url_prefix='/alerts')
app.register_blueprint(gcal_bp, url_prefix='/gcal')

# Configuração do tratamento de requisições
@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

# Inicialização do banco de dados e criação das categorias padrão
with app.app_context():
    # Inicializa o banco de dados
    init_db()
    print("Tabelas criadas ou já existentes no banco de dados.")
    
    # Verifica se já existem categorias padrão
    if Category.query.count() == 0:
        print("Criando categorias padrão...")
        default_categories = [
            Category(name='Alimentação', type='expense'),
            Category(name='Transporte', type='expense'),
            Category(name='Salário', type='income'),
            Category(name='Lazer', type='expense'),
            Category(name='Educação', type='expense'),
            Category(name='Saúde', type='expense'),
            Category(name='Moradia', type='expense'),
            Category(name='Investimento', type='income'),
            Category(name='Outros', type='expense')
        ]
        db_session.add_all(default_categories)
        db_session.commit()
        print("Categorias padrão criadas com sucesso.")

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.dashboard'))
    return redirect(url_for('auth.login'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=os.getenv('PORT', 5000))
