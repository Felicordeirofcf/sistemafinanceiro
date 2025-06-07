from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from sqlalchemy import or_, text

try:
    from src.models import db_session
    from src.models.transaction import Transaction
    from src.models.category import Category
except ImportError:
    from models import db_session
    from models.transaction import Transaction
    from models.category import Category

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")

# Função utilitária para range de datas do mês
def get_date_range(year, month):
    start = f"{year}-{month:02d}-01"
    end = f"{year + 1}-01-01" if month == 12 else f"{year}-{month + 1:02d}-01"
    return start, end

@dashboard_bp.route("/")
@login_required
def index():
    now = datetime.now()
    selected_month = int(request.args.get("mes", now.month))
    selected_year = int(request.args.get("ano", now.year))

    start_date, end_date = get_date_range(selected_year, selected_month)

    transactions = Transaction.query.filter(
        Transaction.user_id == current_user.id,
        Transaction.data >= start_date,
        Transaction.data < end_date
    ).order_by(Transaction.data).all()

    total_receitas = sum(t.valor for t in transactions if t.tipo == "receita")
    total_despesas = sum(t.valor for t in transactions if t.tipo == "despesa")
    total_despesas_pagas = sum(t.valor for t in transactions if t.tipo == "despesa" and t.pago)
    total_despesas_pendentes = total_despesas - total_despesas_pagas
    saldo_mes = total_receitas - total_despesas_pagas

    query = text("""
        SELECT DISTINCT TO_CHAR(CAST(transactions.data AS DATE), 'YYYY') AS year
        FROM transactions
        WHERE user_id = :user_id
    """)
    years_data = db_session.execute(query, {"user_id": current_user.id}).fetchall()
    available_years = {year[0] for year in years_data if year[0]}
    available_years.add(str(now.year))
    available_years = sorted(list(available_years), reverse=True)

    month_names = [
        "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
        "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
    ]
    month_name = month_names[selected_month - 1] if 1 <= selected_month <= 12 else f"Mês {selected_month}"

    categories = Category.query.filter_by(user_id=current_user.id).all()
    category_colors = {c.nome: c.cor for c in categories}
    category_icons = {c.nome: c.icone for c in categories}

    expense_by_category = {}
    income_by_category = {}
    calendar_data = []

    for transaction in transactions:
        cat = transaction.categoria
        category_name = cat.nome if cat else "Sem categoria"
        if transaction.tipo == "despesa":
            expense_by_category[category_name] = expense_by_category.get(category_name, 0) + transaction.valor
        elif transaction.tipo == "receita":
            income_by_category[category_name] = income_by_category.get(category_name, 0) + transaction.valor

        color = cat.cor if cat else "#3498db"
        icon = cat.icone if cat else "fa-tag"
        title_prefix = "🔄 " if transaction.is_recurring or transaction.parent_transaction_id else ""
        calendar_data.append({
            "id": transaction.id,
            "title": title_prefix + transaction.descricao,
            "start": transaction.data,
            "color": color,
            "extendedProps": {
                "tipo": transaction.tipo,
                "valor": transaction.valor,
                "categoria": category_name,
                "pago": transaction.pago,
                "icon": icon,
                "is_recurring": transaction.is_recurring or transaction.parent_transaction_id is not None
            }
        })

    today = now.strftime("%Y-%m-%d")
    next_week = (now + timedelta(days=7)).strftime("%Y-%m-%d")
    upcoming_due = Transaction.query.filter(
        Transaction.user_id == current_user.id,
        Transaction.tipo == "despesa",
        Transaction.pago.is_(False),
        Transaction.vencimento >= today,
        Transaction.vencimento <= next_week
    ).order_by(Transaction.vencimento).all()

    recurring_count = Transaction.query.filter(
        Transaction.user_id == current_user.id,
        Transaction.is_recurring.is_(True),
        Transaction.parent_transaction_id.is_(None)
    ).count()

    return render_template(
        "dashboard/index.html",
        transactions=transactions,
        total_receitas=total_receitas,
        total_despesas=total_despesas,
        total_despesas_pagas=total_despesas_pagas,
        total_despesas_pendentes=total_despesas_pendentes,
        saldo_mes=saldo_mes,
        selected_month=selected_month,
        selected_year=selected_year,
        selected_month_str=month_name,
        available_years=available_years,
        current_year=now.year,
        today_date=today,
        categories=categories,
        expense_by_category=expense_by_category,
        income_by_category=income_by_category,
        calendar_data=calendar_data,
        upcoming_due=upcoming_due,
        recurring_count=recurring_count
    )

@dashboard_bp.route("/chart-data")
@login_required
def chart_data():
    now = datetime.now()
    selected_month = int(request.args.get("mes", now.month))
    selected_year = int(request.args.get("ano", now.year))

    start_date, end_date = get_date_range(selected_year, selected_month)

    transactions = Transaction.query.filter(
        Transaction.user_id == current_user.id,
        Transaction.data >= start_date,
        Transaction.data < end_date
    ).all()

    categories = Category.query.filter_by(user_id=current_user.id).all()
    category_colors = {c.nome: c.cor for c in categories}

    expense_by_category = {}
    income_by_category = {}

    for transaction in transactions:
        category_name = transaction.categoria.nome if transaction.categoria else "Sem categoria"
        if transaction.tipo == "despesa":
            expense_by_category[category_name] = expense_by_category.get(category_name, 0) + transaction.valor
        elif transaction.tipo == "receita":
            income_by_category[category_name] = income_by_category.get(category_name, 0) + transaction.valor

    expense_chart_data = [
        {"name": cat, "value": val, "color": category_colors.get(cat, "#3498db")}
        for cat, val in expense_by_category.items()
    ]

    income_chart_data = [
        {"name": cat, "value": val, "color": category_colors.get(cat, "#2ecc71")}
        for cat, val in income_by_category.items()
    ]

    bar_chart_data = {
        "labels": ["Receitas", "Despesas"],
        "datasets": [
            {
                "data": [
                    sum(t.valor for t in transactions if t.tipo == "receita"),
                    sum(t.valor for t in transactions if t.tipo == "despesa")
                ],
                "backgroundColor": ["#2ecc71", "#e74c3c"]
            }
        ]
    }

    fixed_expenses = sum(t.valor for t in transactions if t.tipo == "despesa" and (t.is_recurring or t.parent_transaction_id))
    variable_expenses = sum(t.valor for t in transactions if t.tipo == "despesa" and not (t.is_recurring or t.parent_transaction_id))

    fixed_vs_variable_data = {
        "labels": ["Despesas Fixas", "Despesas Variáveis"],
        "datasets": [
            {
                "data": [fixed_expenses, variable_expenses],
                "backgroundColor": ["#9b59b6", "#f39c12"]
            }
        ]
    }

    return jsonify({
        "expense_chart": expense_chart_data,
        "income_chart": income_chart_data,
        "bar_chart": bar_chart_data,
        "fixed_vs_variable_chart": fixed_vs_variable_data
    })

@dashboard_bp.route("/search", methods=["GET", "POST"])
@login_required
def search():
    if request.method == "POST":
        termo = request.form.get("termo", "")
        categoria_id_str = request.form.get("categoria_id")
        tipo = request.form.get("tipo")
        data_inicio = request.form.get("data_inicio")
        data_fim = request.form.get("data_fim")
        valor_min_str = request.form.get("valor_min", "").replace(".", "").replace(",", ".")
        valor_max_str = request.form.get("valor_max", "").replace(".", "").replace(",", ".")
        status = request.form.get("status")
        is_recurring = request.form.get("is_recurring")

        query = Transaction.query.filter(Transaction.user_id == current_user.id)

        if termo:
            query = query.filter(Transaction.descricao.ilike(f"%{termo}%"))

        if categoria_id_str:
            try:
                categoria_id = int(categoria_id_str)
                query = query.filter(Transaction.categoria_id == categoria_id)
            except (ValueError, TypeError):
                pass

        if tipo:
            query = query.filter(Transaction.tipo == tipo)

        if data_inicio:
            query = query.filter(Transaction.data >= data_inicio)

        if data_fim:
            query = query.filter(Transaction.data <= data_fim)

        if valor_min_str:
            try:
                valor_min = float(valor_min_str)
                query = query.filter(Transaction.valor >= valor_min)
            except:
                pass

        if valor_max_str:
            try:
                valor_max = float(valor_max_str)
                query = query.filter(Transaction.valor <= valor_max)
            except:
                pass

        if status:
            if status == "pago":
                query = query.filter(Transaction.pago == True)
            elif status == "pendente":
                query = query.filter(Transaction.pago == False)

        if is_recurring:
            if is_recurring == "sim":
                query = query.filter(or_(Transaction.is_recurring == True, Transaction.parent_transaction_id != None))
            elif is_recurring == "nao":
                query = query.filter(Transaction.is_recurring == False, Transaction.parent_transaction_id == None)

        transactions = query.order_by(Transaction.data.desc()).all()
        categories = Category.query.filter_by(user_id=current_user.id).all()

        return render_template(
            "dashboard/search_results.html",
            transactions=transactions,
            categories=categories,
            search_params={
                "termo": termo,
                "categoria_id": categoria_id_str,
                "tipo": tipo,
                "data_inicio": data_inicio,
                "data_fim": data_fim,
                "valor_min": valor_min_str,
                "valor_max": valor_max_str,
                "status": status,
                "is_recurring": is_recurring
            }
        )

    return redirect(url_for("dashboard.index"))
