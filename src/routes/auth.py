from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from src.models import db_session
from src.models.user import User
from src.models.category import Category
from sqlalchemy.exc import IntegrityError

from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import os
import json

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

CLIENT_SECRETS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'client_secret.json')
SCOPES = ['https://www.googleapis.com/auth/userinfo.email', 'https://www.googleapis.com/auth/userinfo.profile', 'openid']
REDIRECT_URI = "http://localhost:5000/auth/google/callback"  # ajuste conforme necessário

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        remember = True if request.form.get("remember") else False

        user = User.query.filter_by(username=username).first()
        if not user or not user.check_password(password):
            flash("Usuário ou senha incorretos. Por favor, tente novamente.", "danger")
            return redirect(url_for("auth.login"))

        login_user(user, remember=remember)
        return redirect(url_for("dashboard.index"))

    return render_template("auth/login.html")

@auth_bp.route("/login/google")
def login_google():
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )
    authorization_url, state = flow.authorization_url()
    session['state'] = state
    return redirect(authorization_url)

@auth_bp.route("/auth/google/callback")
def google_callback():
    state = session.get('state')
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        state=state,
        redirect_uri=REDIRECT_URI
    )
    flow.fetch_token(authorization_response=request.url)

    credentials = flow.credentials
    request_session = google_requests.Request()
    id_info = id_token.verify_oauth2_token(credentials._id_token, request_session)

    email = id_info['email']
    name = id_info.get('name', 'Usuário Google')

    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(email=email, nome=name)
        db_session.add(user)
        db_session.commit()

    login_user(user)
    flash('Login com Google realizado com sucesso!', 'success')
    return redirect(url_for('dashboard.index'))

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        password_confirm = request.form.get("password_confirm")

        if not username or not email or not password or not password_confirm:
            flash("Todos os campos são obrigatórios.", "danger")
            return redirect(url_for("auth.register"))

        if password != password_confirm:
            flash("As senhas não coincidem.", "danger")
            return redirect(url_for("auth.register"))

        try:
            if User.query.filter_by(username=username).first():
                flash("Nome de usuário já está em uso.", "danger")
                return redirect(url_for("auth.register"))

            if User.query.filter_by(email=email).first():
                flash("Email já está em uso.", "danger")
                return redirect(url_for("auth.register"))

            new_user = User(username=username, email=email, password=password)
            db_session.add(new_user)
            db_session.commit()

            flash("Conta criada com sucesso! Agora você pode fazer login.", "success")
            return redirect(url_for("auth.login"))

        except IntegrityError:
            db_session.rollback()
            flash("Erro ao criar a conta. Por favor, tente novamente.", "danger")
            return redirect(url_for("auth.register"))
        except Exception as e:
            db_session.rollback()
            flash(f"Ocorreu um erro inesperado: {e}", "danger")
            return redirect(url_for("auth.register"))

    return render_template("auth/register.html")

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Você saiu do sistema.", "info")
    return redirect(url_for("auth.login"))