from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from src.models import db_session
from src.models.user import User
from src.models.category import Category

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Rota para login de usuários"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        
        user = User.query.filter_by(username=username).first()
        
        # Verifica se o usuário existe e a senha está correta
        if not user or not user.check_password(password):
            flash('Usuário ou senha incorretos. Por favor, tente novamente.', 'danger')
            return redirect(url_for('auth.login'))
        
        # Realiza o login do usuário
        login_user(user, remember=remember)
        return redirect(url_for('dashboard.index'))
    
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Rota para registro de novos usuários"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')
        
        # Verifica se as senhas coincidem
        if password != password_confirm:
            flash('As senhas não coincidem.', 'danger')
            return redirect(url_for('auth.register'))
        
        # Verifica se o usuário já existe
        user_exists = User.query.filter_by(username=username).first()
        if user_exists:
            flash('Nome de usuário já está em uso.', 'danger')
            return redirect(url_for('auth.register'))
        
        # Verifica se o email já existe
        email_exists = User.query.filter_by(email=email).first()
        if email_exists:
            flash('Email já está em uso.', 'danger')
            return redirect(url_for('auth.register'))
        
        # Cria o novo usuário
        new_user = User(username=username, email=email, password=password)
        db_session.add(new_user)
        db_session.commit()
        
        # Atualiza as categorias padrão para o novo usuário
        categories = Category.query.filter_by(user_id=1).all()
        for cat in categories:
            new_cat = Category(
                user_id=new_user.id,
                nome=cat.nome,
                tipo=cat.tipo,
                cor=cat.cor,
                icone=cat.icone
            )
            db_session.add(new_cat)
        
        db_session.commit()
        
        flash('Conta criada com sucesso! Agora você pode fazer login.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """Rota para logout de usuários"""
    logout_user()
    flash('Você saiu do sistema.', 'info')
    return redirect(url_for('auth.login'))
