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
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'chave-secreta-temporaria')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///finance.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configuração do Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Por favor, faça login para acessar esta página.'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Registro dos blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(transactions_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(alerts_bp)
app.register_blueprint(gcal_bp)  # Novo blueprint para Google Calendar

# Rota principal - redireciona para o dashboard
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    return redirect(url_for('auth.login'))

# Encerramento da sessão do banco de dados ao finalizar a requisição
@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

# Inicialização do banco de dados e criação das categorias padrão
with app.app_context():
    # Inicializa o banco de dados
    # init_db()
    Base.metadata.create_all(bind=engine)
    print("Tabelas criadas ou já existentes no banco de dados.")
    
    # Verifica se já existem categorias padrão
    if Category.query.count() == 0:
        # Categorias padrão para despesas
        despesas = [
            {'nome': 'Alimentação', 'tipo': 'despesa', 'cor': '#e74c3c', 'icone': 'fa-utensils'},
            {'nome': 'Transporte', 'tipo': 'despesa', 'cor': '#3498db', 'icone': 'fa-car'},
            {'nome': 'Moradia', 'tipo': 'despesa', 'cor': '#9b59b6', 'icone': 'fa-home'},
            {'nome': 'Lazer', 'tipo': 'despesa', 'cor': '#f39c12', 'icone': 'fa-gamepad'},
            {'nome': 'Saúde', 'tipo': 'despesa', 'cor': '#2ecc71', 'icone': 'fa-medkit'},
            {'nome': 'Educação', 'tipo': 'despesa', 'cor': '#1abc9c', 'icone': 'fa-book'},
            {'nome': 'Outros', 'tipo': 'despesa', 'cor': '#95a5a6', 'icone': 'fa-tag'}
        ]
        
        # Categorias padrão para receitas
        receitas = [
            {'nome': 'Salário', 'tipo': 'receita', 'cor': '#2ecc71', 'icone': 'fa-money-bill'},
            {'nome': 'Freelance', 'tipo': 'receita', 'cor': '#3498db', 'icone': 'fa-laptop'},
            {'nome': 'Investimentos', 'tipo': 'receita', 'cor': '#f39c12', 'icone': 'fa-chart-line'},
            {'nome': 'Outros', 'tipo': 'receita', 'cor': '#95a5a6', 'icone': 'fa-tag'}
        ]
        
        # Adiciona categorias padrão ao banco de dados
        for cat in despesas + receitas:
            category = Category(
                user_id=1,  # ID temporário, será atualizado quando o usuário se registrar
                nome=cat['nome'],
                tipo=cat['tipo'],
                cor=cat['cor'],
                icone=cat['icone']
            )
            db_session.add(category)
        
        db_session.commit()

# Execução da aplicação
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
