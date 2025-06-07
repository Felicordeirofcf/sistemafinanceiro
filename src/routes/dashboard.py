from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from sqlalchemy import extract, distinct, or_, text

try:
    from src.models import db_session
    from src.models.transaction import Transaction
    from src.models.category import Category
except ImportError:
    from models import db_session
    from models.transaction import Transaction
    from models.category import Category

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")

@dashboard_bp.route("/")
@login_required
def index():
    """Rota principal do dashboard"""
    # Obtém o mês e ano atuais ou os selecionados via parâmetros
    now = datetime.now()
    selected_month = int(request.args.get("mes", now.month))
    selected_year = int(request.args.get("ano", now.year))
    
    # Obtém as transações do mês selecionado
    start_date = f"{selected_year}-{selected_month:02d}-01"
    
    # Calcula o último dia do mês
    if selected_month == 12:
        end_date = f"{selected_year + 1}-01-01"
    else:
        end_date = f"{selected_year}-{selected_month + 1:02d}-01"
    
    # Busca as transações do usuário no período selecionado
    transactions = Transaction.query.filter(
        Transaction.user_id == current_user.id,
        Transaction.data >= start_date,
        Transaction.data < end_date
    ).order_by(Transaction.data).all()
    
    # Calcula os totais
    total_receitas = sum(t.valor for t in transactions if t.tipo == "receita")
    total_despesas = sum(t.valor for t in transactions if t.tipo == "despesa")
    total_despesas_pagas = sum(t.valor for t in transactions if t.tipo == "despesa" and t.pago)
    total_despesas_pendentes = total_despesas - total_despesas_pagas
    saldo_mes = total_receitas - total_despesas_pagas
    
    # Obtém os anos disponíveis para o filtro - CORRIGIDO para SQLAlchemy 2.0+
    # Consulta direta para extrair anos distintos das datas de transações
    query = text("""
    SELECT DISTINCT TO_CHAR(transactions.data, 'YYYY') AS year
    FROM transactions
""")
years_data = db_session.execute(query).fetchall()

available_years = set(year[0] for year in years_data if year[0])
    
    # Adiciona o ano atual se não estiver na lista
    current_year = now.year
    available_years.add(current_year)
    available_years = sorted(list(available_years), reverse=True)
    
    # Obtém o nome do mês
    month_names = [
        "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
        "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
    ]
    month_name = month_names[selected_month - 1] if 1 <= selected_month <= 12 else "Inválido"
    
    # Obtém as categorias do usuário
    categories = Category.query.filter_by(user_id=current_user.id).all()
    
    # Prepara dados para gráficos
    expense_by_category = {}
    income_by_category = {}
    
    for transaction in transactions:
        category_name = transaction.categoria.nome if transaction.categoria else "Sem categoria"
        
        if transaction.tipo == "despesa":
            if category_name in expense_by_category:
                expense_by_category[category_name] += transaction.valor
            else:
                expense_by_category[category_name] = transaction.valor
        else:
            if category_name in income_by_category:
                income_by_category[category_name] += transaction.valor
            else:
                income_by_category[category_name] = transaction.valor
    
    # Prepara dados para o calendário
    calendar_data = []
    for transaction in transactions:
        # Determina a cor e ícone com base no tipo e status
        color = transaction.categoria.cor if transaction.categoria else "#3498db"
        icon = transaction.categoria.icone if transaction.categoria else "fa-tag"
        
        # Adiciona indicador visual para despesas recorrentes
        title_prefix = "🔄 " if transaction.is_recurring or transaction.parent_transaction_id else ""
        
        calendar_data.append({
            "id": transaction.id,
            "title": title_prefix + transaction.descricao,
            "start": transaction.data,
            "color": color,
            "extendedProps": {
                "tipo": transaction.tipo,
                "valor": transaction.valor,
                "categoria": transaction.categoria.nome if transaction.categoria else "Sem categoria",
                "pago": transaction.pago,
                "icon": icon,
                "is_recurring": transaction.is_recurring or transaction.parent_transaction_id is not None
            }
        })
    
    # Verifica se há transações próximas do vencimento (para alertas)
    today = now.strftime("%Y-%m-%d")
    next_week = (now + timedelta(days=7)).strftime("%Y-%m-%d")
    
    upcoming_due = Transaction.query.filter(
        Transaction.user_id == current_user.id,
        Transaction.tipo == "despesa",
        Transaction.pago == False,
        Transaction.vencimento >= today,
        Transaction.vencimento <= next_week
    ).order_by(Transaction.vencimento).all()
    
    # Obtém o total de despesas fixas/recorrentes
    recurring_count = Transaction.query.filter(
        Transaction.user_id == current_user.id,
        Transaction.is_recurring == True,
        Transaction.parent_transaction_id == None
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
        today_date=now.strftime("%Y-%m-%d"),
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
    """Retorna dados para os gráficos em formato JSON"""
    # Obtém o mês e ano atuais ou os selecionados via parâmetros
    now = datetime.now()
    selected_month = int(request.args.get("mes", now.month))
    selected_year = int(request.args.get("ano", now.year))
    
    # Obtém as transações do mês selecionado
    start_date = f"{selected_year}-{selected_month:02d}-01"
    
    # Calcula o último dia do mês
    if selected_month == 12:
        end_date = f"{selected_year + 1}-01-01"
    else:
        end_date = f"{selected_year}-{selected_month + 1:02d}-01"
    
    # Busca as transações do usuário no período selecionado
    transactions = Transaction.query.filter(
        Transaction.user_id == current_user.id,
        Transaction.data >= start_date,
        Transaction.data < end_date
    ).all()
    
    # Prepara dados para gráficos
    expense_by_category = {}
    income_by_category = {}
    
    for transaction in transactions:
        category_name = transaction.categoria.nome if transaction.categoria else "Sem categoria"
        
        if transaction.tipo == "despesa":
            if category_name in expense_by_category:
                expense_by_category[category_name] += transaction.valor
            else:
                expense_by_category[category_name] = transaction.valor
        else:
            if category_name in income_by_category:
                income_by_category[category_name] += transaction.valor
            else:
                income_by_category[category_name] = transaction.valor
    
    # Formata os dados para o gráfico de pizza
    expense_chart_data = [
        {
            "name": category,
            "value": value,
            "color": next((c.cor for c in Category.query.filter_by(
                user_id=current_user.id, nome=category
            ).all()), "#3498db")
        }
        for category, value in expense_by_category.items()
    ]
    
    income_chart_data = [
        {
            "name": category,
            "value": value,
            "color": next((c.cor for c in Category.query.filter_by(
                user_id=current_user.id, nome=category
            ).all()), "#2ecc71")
        }
        for category, value in income_by_category.items()
    ]
    
    # Dados para o gráfico de barras (receitas x despesas)
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
    
    # Dados para o gráfico de despesas fixas vs variáveis
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
    """Busca transações com filtros avançados"""
    if request.method == "POST":
        # Obtém os parâmetros de busca
        termo = request.form.get("termo", "")
        categoria_id = request.form.get("categoria_id")
        tipo = request.form.get("tipo")
        data_inicio = request.form.get("data_inicio")
        data_fim = request.form.get("data_fim")
        valor_min_str = request.form.get("valor_min", "").replace(".", "").replace(",", "")
        valor_max_str = request.form.get("valor_max", "").replace(".", "").replace(",", "")
        status = request.form.get("status")
        is_recurring = request.form.get("is_recurring")
        
        # Constrói a consulta base
        query = Transaction.query.filter(Transaction.user_id == current_user.id)
        
        # Aplica os filtros
        if termo:
            query = query.filter(Transaction.descricao.ilike(f"%{termo}%"))
        
        if categoria_id:
            query = query.filter(Transaction.categoria_id == categoria_id)
        
        if tipo:
            query = query.filter(Transaction.tipo == tipo)
        
        if data_inicio:
            query = query.filter(Transaction.data >= data_inicio)
        
        if data_fim:
            query = query.filter(Transaction.data <= data_fim)
        
        if valor_min_str and valor_min_str.isdigit():
            valor_min = int(valor_min_str)
            query = query.filter(Transaction.valor >= valor_min)
        
        if valor_max_str and valor_max_str.isdigit():
            valor_max = int(valor_max_str)
            query = query.filter(Transaction.valor <= valor_max)
        
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
        
        # Executa a consulta
        transactions = query.order_by(Transaction.data.desc()).all()
        
        # Obtém as categorias do usuário para o formulário de busca
        categories = Category.query.filter_by(user_id=current_user.id).all()
        
        return render_template(
            "dashboard/search_results.html",
            transactions=transactions,
            categories=categories,
            search_params={
                "termo": termo,
                "categoria_id": categoria_id,
                "tipo": tipo,
                "data_inicio": data_inicio,
                "data_fim": data_fim,
                "valor_min": valor_min_str,
                "valor_max": valor_max_str,
                "status": status,
                "is_recurring": is_recurring
            }
        )
    
    # Se for GET, redireciona para o dashboard
    return redirect(url_for("dashboard.index"))


