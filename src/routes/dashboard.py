from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from sqlalchemy import extract, distinct
from src.models import db_session
from src.models.transaction import Transaction
from src.models.category import Category

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/')
@login_required
def index():
    """Rota principal do dashboard"""
    # Obtém o mês e ano atuais ou os selecionados via parâmetros
    now = datetime.now()
    selected_month = int(request.args.get('mes', now.month))
    selected_year = int(request.args.get('ano', now.year))
    
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
    total_receitas = sum(t.valor for t in transactions if t.tipo == 'receita')
    total_despesas = sum(t.valor for t in transactions if t.tipo == 'despesa')
    total_despesas_pagas = sum(t.valor for t in transactions if t.tipo == 'despesa' and t.pago)
    total_despesas_pendentes = total_despesas - total_despesas_pagas
    saldo_mes = total_receitas - total_despesas_pagas
    
    # Obtém os anos disponíveis para o filtro - CORRIGIDO para SQLAlchemy 2.0+
    # Consulta direta para extrair anos distintos das datas de transações
    years_data = db_session.query(
        extract('year', Transaction.data)
    ).filter(
        Transaction.user_id == current_user.id
    ).distinct().all()
    
    available_years = set(year[0] for year in years_data if year[0])
    
    # Adiciona o ano atual se não estiver na lista
    current_year = now.year
    available_years.add(current_year)
    available_years = sorted(list(available_years), reverse=True)
    
    # Obtém o nome do mês
    month_names = [
        'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
        'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
    ]
    month_name = month_names[selected_month - 1] if 1 <= selected_month <= 12 else "Inválido"
    
    # Obtém as categorias do usuário
    categories = Category.query.filter_by(user_id=current_user.id).all()
    
    # Prepara dados para gráficos
    expense_by_category = {}
    income_by_category = {}
    
    for transaction in transactions:
        category_name = transaction.categoria.nome if transaction.categoria else "Sem categoria"
        
        if transaction.tipo == 'despesa':
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
        calendar_data.append({
            'id': transaction.id,
            'title': transaction.descricao,
            'start': transaction.data,
            'color': transaction.categoria.cor if transaction.categoria else '#3498db',
            'extendedProps': {
                'tipo': transaction.tipo,
                'valor': transaction.valor,
                'categoria': transaction.categoria.nome if transaction.categoria else "Sem categoria",
                'pago': transaction.pago,
                'icon': transaction.categoria.icone if transaction.categoria else 'fa-tag'
            }
        })
    
    # Verifica se há transações próximas do vencimento (para alertas)
    today = now.strftime("%Y-%m-%d")
    next_week = (now + timedelta(days=7)).strftime("%Y-%m-%d")
    
    upcoming_due = Transaction.query.filter(
        Transaction.user_id == current_user.id,
        Transaction.tipo == 'despesa',
        Transaction.pago == False,
        Transaction.vencimento >= today,
        Transaction.vencimento <= next_week
    ).order_by(Transaction.vencimento).all()
    
    return render_template(
        'dashboard/index.html',
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
        upcoming_due=upcoming_due
    )

@dashboard_bp.route('/chart-data')
@login_required
def chart_data():
    """Retorna dados para os gráficos em formato JSON"""
    # Obtém o mês e ano atuais ou os selecionados via parâmetros
    now = datetime.now()
    selected_month = int(request.args.get('mes', now.month))
    selected_year = int(request.args.get('ano', now.year))
    
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
        
        if transaction.tipo == 'despesa':
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
            'name': category,
            'value': value,
            'color': next((c.cor for c in Category.query.filter_by(
                user_id=current_user.id, nome=category
            ).all()), '#3498db')
        }
        for category, value in expense_by_category.items()
    ]
    
    income_chart_data = [
        {
            'name': category,
            'value': value,
            'color': next((c.cor for c in Category.query.filter_by(
                user_id=current_user.id, nome=category
            ).all()), '#2ecc71')
        }
        for category, value in income_by_category.items()
    ]
    
    # Dados para o gráfico de barras (receitas x despesas)
    bar_chart_data = {
        'labels': ['Receitas', 'Despesas'],
        'datasets': [
            {
                'data': [
                    sum(t.valor for t in transactions if t.tipo == 'receita'),
                    sum(t.valor for t in transactions if t.tipo == 'despesa')
                ],
                'backgroundColor': ['#2ecc71', '#e74c3c']
            }
        ]
    }
    
    return jsonify({
        'expense_chart': expense_chart_data,
        'income_chart': income_chart_data,
        'bar_chart': bar_chart_data
    })
