from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import IntegrityError
from src.models import db_session
from src.models.user import User
from src.models.category import Category

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()

        if user:
            print(f"[DEBUG] Usuário encontrado: {user.username}")
        else:
            print(f"[DEBUG] Usuário não encontrado: {username}")

        if user and check_password_hash(user.password_hash, password):
            login_user(user, remember='remember' in request.form)
            print(f"[DEBUG] Login bem-sucedido: {username}")
            return redirect(url_for("dashboard.index"))
        else:
            flash("Credenciais inválidas", "danger")

    return render_template("auth/login.html")

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


