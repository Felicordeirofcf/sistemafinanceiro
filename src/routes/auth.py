from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import IntegrityError
from src.models import db_session
from src.models.user import User
from src.models.category import Category

from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import os

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

# Configurações OAuth
SCOPES = [
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
    'openid'
]
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        remember = bool(request.form.get("remember"))

        user = User.query.filter_by(username=username).first()
        if not user or not user.check_password(password):
            flash("Usuário ou senha incorretos.", "danger")
            return redirect(url_for("auth.login"))

        login_user(user, remember=remember)
        return redirect(url_for("dashboard.index"))

    return render_template("auth/login.html")


@auth_bp.route("/login/google")
def login_google():
    try:
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": GOOGLE_CLIENT_ID,
                    "client_secret": GOOGLE_CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [GOOGLE_REDIRECT_URI]
                }
            },
            scopes=SCOPES,
            redirect_uri=GOOGLE_REDIRECT_URI
        )

        authorization_url, state = flow.authorization_url()
        session['state'] = state
        return redirect(authorization_url)

    except Exception as e:
        flash(f"Erro ao iniciar login com Google: {e}", "danger")
        return redirect(url_for("auth.login"))


@auth_bp.route("/google/callback")
def google_callback():
    try:
        state = session.get('state')

        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": GOOGLE_CLIENT_ID,
                    "client_secret": GOOGLE_CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [GOOGLE_REDIRECT_URI]
                }
            },
            scopes=SCOPES,
            state=state,
            redirect_uri=GOOGLE_REDIRECT_URI
        )

        flow.fetch_token(authorization_response=request.url)
        credentials = flow.credentials

        request_session = google_requests.Request()
        id_info = id_token.verify_oauth2_token(
            credentials._id_token,
            request_session,
            GOOGLE_CLIENT_ID
        )

        email = id_info['email']
        name = id_info.get('name', 'Usuário Google')

        user = User.query.filter_by(email=email).first()
        if not user:
            # Cria usuário com senha em branco (gera um hash mesmo vazio)
            user = User(username=name, email=email, password="")
            db_session.add(user)
            db_session.commit()
            print(f"[GOOGLE] Novo usuário criado: {user.username} (ID: {user.id})")
        else:
            print(f"[GOOGLE] Usuário já existente: {user.username} (ID: {user.id})")

        login_user(user)
        print(f"[GOOGLE] Login realizado com sucesso: {user.username}")
        flash("Login com Google realizado com sucesso!", "success")
        return redirect(url_for("dashboard.index"))

    except Exception as e:
        print(f"[GOOGLE] Erro ao autenticar com Google: {e}")
        flash(f"Erro ao autenticar com Google: {e}", "danger")
        return redirect(url_for("auth.login"))


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        password_confirm = request.form.get("password_confirm")

        if not all([username, email, password, password_confirm]):
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
                flash("E-mail já está em uso.", "danger")
                return redirect(url_for("auth.register"))

            new_user = User(username=username, email=email, password=password)
            db_session.add(new_user)
            db_session.commit()

            flash("Conta criada com sucesso! Faça login para continuar.", "success")
            return redirect(url_for("auth.login"))

        except IntegrityError:
            db_session.rollback()
            flash("Erro ao criar a conta. Tente novamente.", "danger")
        except Exception as e:
            db_session.rollback()
            flash(f"Ocorreu um erro inesperado: {e}", "danger")

    return render_template("auth/register.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Você saiu do sistema.", "info")
    return redirect(url_for("auth.login"))
