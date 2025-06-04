from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta
import calendar
from dateutil.relativedelta import relativedelta
from src.models import db_session
from src.models.transaction import Transaction
from src.models.category import Category
from src.models.google_calendar_auth import GoogleCalendarAuth
from src.routes.gcal import sync_transaction

transactions_bp = Blueprint('transactions', __name__, url_prefix='/transactions')

@transactions_bp.route('/add', methods=['POST'])
@login_required
def add():
    """Adiciona uma nova transação"""
    if request.method == 'POST':
        descricao = request.form.get('descricao')
        valor_str = request.form.get('valor', '0').replace('.', '').replace(',', '')
        valor = int(valor_str) if valor_str.isdigit() else 0
        tipo = request.form.get('tipo')
        data = request.form.get('data')
        vencimento = request.form.get('vencimento') if tipo == 'despesa' else None
        categoria_id = request.form.get('categoria_id')
        observacoes = request.form.get('observacoes', '')
        
        # Campos de recorrência
        is_recurring = request.form.get('is_recurring') == 'on'
        recurrence_frequency = request.form.get('recurrence_frequency')
        recurrence_end_date = request.form.get('recurrence_end_date')
        
        if not descricao or not valor or not tipo or not data:
            flash('Todos os campos obrigatórios devem ser preenchidos.', 'danger')
            return redirect(url_for('dashboard.index'))
        
        # Cria a transação principal
        transaction = Transaction(
            user_id=current_user.id,
            descricao=descricao,
            valor=valor,
            tipo=tipo,
            data=data,
            vencimento=vencimento,
            pago=False if tipo == 'despesa' else True,
            categoria_id=categoria_id if categoria_id else None,
            observacoes=observacoes,
            is_recurring=is_recurring,
            recurrence_frequency=recurrence_frequency if is_recurring else None,
            recurrence_start_date=data if is_recurring else None,
            recurrence_end_date=recurrence_end_date if is_recurring and recurrence_end_date else None
        )
        
        db_session.add(transaction)
        db_session.commit()
        
        # Se for uma despesa recorrente, gera as próximas ocorrências
        if is_recurring and tipo == 'despesa':
            generate_recurring_transactions(transaction)
        
        # Verifica se o usuário tem integração com Google Calendar ativa
        auth = GoogleCalendarAuth.query.filter_by(user_id=current_user.id, sync_enabled=1).first()
        if auth and tipo == 'despesa':
            # Sincroniza a transação com o Google Calendar
            return redirect(url_for('gcal.sync_transaction', transaction_id=transaction.id))
        
        flash('Transação adicionada com sucesso!', 'success')
        return redirect(url_for('dashboard.index'))

@transactions_bp.route('/edit/<int:id>', methods=['POST'])
@login_required
def edit(id):
    """Edita uma transação existente"""
    transaction = Transaction.query.filter_by(id=id, user_id=current_user.id).first()
    
    if not transaction:
        flash('Transação não encontrada.', 'danger')
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        descricao = request.form.get('descricao')
        valor_str = request.form.get('valor', '0').replace('.', '').replace(',', '')
        valor = int(valor_str) if valor_str.isdigit() else 0
        tipo = request.form.get('tipo')
        data = request.form.get('data')
        vencimento = request.form.get('vencimento') if tipo == 'despesa' else None
        categoria_id = request.form.get('categoria_id')
        observacoes = request.form.get('observacoes', '')
        
        # Campos de recorrência
        is_recurring = request.form.get('is_recurring') == 'on'
        recurrence_frequency = request.form.get('recurrence_frequency')
        recurrence_end_date = request.form.get('recurrence_end_date')
        
        # Verifica se deve atualizar todas as ocorrências futuras
        update_all_future = request.form.get('update_all_future') == 'on'
        
        if not descricao or not valor or not tipo or not data:
            flash('Todos os campos obrigatórios devem ser preenchidos.', 'danger')
            return redirect(url_for('dashboard.index'))
        
        # Se for uma transação recorrente e o usuário quer atualizar todas as ocorrências futuras
        if (transaction.is_recurring or transaction.parent_transaction_id) and update_all_future:
            # Determina a transação pai
            parent_id = transaction.parent_transaction_id if transaction.parent_transaction_id else transaction.id
            parent = Transaction.query.get(parent_id)
            
            # Atualiza a transação pai
            if parent:
                parent.descricao = descricao
                parent.valor = valor
                parent.tipo = tipo
                parent.categoria_id = categoria_id if categoria_id else None
                parent.observacoes = observacoes
                parent.is_recurring = is_recurring
                parent.recurrence_frequency = recurrence_frequency if is_recurring else None
                parent.recurrence_end_date = recurrence_end_date if is_recurring and recurrence_end_date else None
                
                # Atualiza todas as ocorrências futuras
                today = datetime.now().strftime('%Y-%m-%d')
                future_transactions = Transaction.query.filter(
                    Transaction.parent_transaction_id == parent_id,
                    Transaction.data >= today
                ).all()
                
                for future in future_transactions:
                    future.descricao = descricao
                    future.valor = valor
                    future.tipo = tipo
                    future.categoria_id = categoria_id if categoria_id else None
                    future.observacoes = observacoes
                
                db_session.commit()
                flash('Todas as ocorrências futuras foram atualizadas com sucesso!', 'success')
            else:
                flash('Transação pai não encontrada.', 'danger')
        else:
            # Atualiza apenas a transação atual
            transaction.descricao = descricao
            transaction.valor = valor
            transaction.tipo = tipo
            transaction.data = data
            transaction.vencimento = vencimento
            transaction.categoria_id = categoria_id if categoria_id else None
            transaction.observacoes = observacoes
            transaction.is_recurring = is_recurring
            transaction.recurrence_frequency = recurrence_frequency if is_recurring else None
            transaction.recurrence_start_date = data if is_recurring else None
            transaction.recurrence_end_date = recurrence_end_date if is_recurring and recurrence_end_date else None
            
            db_session.commit()
            
            # Se for uma despesa recorrente e não tinha recorrência antes, gera as próximas ocorrências
            if is_recurring and tipo == 'despesa' and not transaction.child_transactions:
                generate_recurring_transactions(transaction)
            
            flash('Transação atualizada com sucesso!', 'success')
        
        # Verifica se o usuário tem integração com Google Calendar ativa
        auth = GoogleCalendarAuth.query.filter_by(user_id=current_user.id, sync_enabled=1).first()
        if auth and tipo == 'despesa':
            # Sincroniza a transação com o Google Calendar
            return redirect(url_for('gcal.sync_transaction', transaction_id=transaction.id))
        
        return redirect(url_for('dashboard.index'))

@transactions_bp.route('/delete/<int:id>')
@login_required
def delete(id):
    """Exclui uma transação"""
    transaction = Transaction.query.filter_by(id=id, user_id=current_user.id).first()
    
    if not transaction:
        flash('Transação não encontrada.', 'danger')
        return redirect(url_for('dashboard.index'))
    
    # Verifica se é uma transação recorrente
    is_recurring = transaction.is_recurring or transaction.parent_transaction_id
    
    # Pergunta se deve excluir todas as ocorrências futuras
    delete_all_future = request.args.get('delete_all_future') == 'true'
    
    # Se for uma transação recorrente e o usuário quer excluir todas as ocorrências futuras
    if is_recurring and delete_all_future:
        # Determina a transação pai
        parent_id = transaction.parent_transaction_id if transaction.parent_transaction_id else transaction.id
        
        # Exclui todas as ocorrências futuras
        today = datetime.now().strftime('%Y-%m-%d')
        future_transactions = Transaction.query.filter(
            Transaction.parent_transaction_id == parent_id,
            Transaction.data >= today
        ).all()
        
        for future in future_transactions:
            # Exclui evento do Google Calendar se existir
            delete_gcal_event(future)
            db_session.delete(future)
        
        # Se a transação atual for a pai, também a exclui
        if transaction.id == parent_id:
            delete_gcal_event(transaction)
            db_session.delete(transaction)
        
        db_session.commit()
        flash('Todas as ocorrências futuras foram excluídas com sucesso!', 'success')
    else:
        # Exclui apenas a transação atual
        delete_gcal_event(transaction)
        db_session.delete(transaction)
        db_session.commit()
        flash('Transação excluída com sucesso!', 'success')
    
    return redirect(url_for('dashboard.index'))

@transactions_bp.route('/toggle_status/<int:id>')
@login_required
def toggle_status(id):
    """Alterna o status de pagamento de uma transação"""
    transaction = Transaction.query.filter_by(id=id, user_id=current_user.id).first()
    
    if not transaction:
        flash('Transação não encontrada.', 'danger')
        return redirect(url_for('dashboard.index'))
    
    # Inverte o status de pagamento
    transaction.pago = not transaction.pago
    db_session.commit()
    
    # Verifica se o usuário tem integração com Google Calendar ativa
    auth = GoogleCalendarAuth.query.filter_by(user_id=current_user.id, sync_enabled=1).first()
    if auth and transaction.tipo == 'despesa':
        # Sincroniza a transação com o Google Calendar
        return redirect(url_for('gcal.sync_transaction', transaction_id=transaction.id))
    
    status = "paga" if transaction.pago else "pendente"
    flash(f'Transação marcada como {status}.', 'success')
    return redirect(url_for('dashboard.index'))

@transactions_bp.route('/recurring')
@login_required
def recurring():
    """Exibe todas as despesas recorrentes"""
    # Busca todas as transações recorrentes (apenas as principais)
    recurring_transactions = Transaction.query.filter_by(
        user_id=current_user.id,
        is_recurring=True,
        parent_transaction_id=None
    ).order_by(Transaction.data.desc()).all()
    
    # Obtém as categorias do usuário
    categories = Category.query.filter_by(user_id=current_user.id).all()
    
    return render_template(
        'dashboard/recurring.html',
        transactions=recurring_transactions,
        categories=categories
    )

@transactions_bp.route('/generate_recurring')
@login_required
def generate_recurring():
    """Gera as próximas ocorrências de todas as despesas recorrentes"""
    # Busca todas as transações recorrentes (apenas as principais)
    recurring_transactions = Transaction.query.filter_by(
        user_id=current_user.id,
        is_recurring=True,
        parent_transaction_id=None
    ).all()
    
    count = 0
    for transaction in recurring_transactions:
        count += generate_recurring_transactions(transaction)
    
    flash(f'{count} novas ocorrências de despesas recorrentes foram geradas.', 'success')
    return redirect(url_for('transactions.recurring'))

def generate_recurring_transactions(transaction, limit=12):
    """Gera as próximas ocorrências de uma despesa recorrente"""
    if not transaction.is_recurring or transaction.tipo != 'despesa':
        return 0
    
    # Determina a data de início
    start_date = datetime.strptime(transaction.recurrence_start_date or transaction.data, '%Y-%m-%d')
    
    # Determina a data de término (se houver)
    end_date = None
    if transaction.recurrence_end_date:
        end_date = datetime.strptime(transaction.recurrence_end_date, '%Y-%m-%d')
    
    # Determina a frequência em meses
    frequency_months = {
        'mensal': 1,
        'bimestral': 2,
        'trimestral': 3,
        'semestral': 6,
        'anual': 12
    }.get(transaction.recurrence_frequency, 1)
    
    # Busca as ocorrências já existentes
    existing_dates = set()
    for child in transaction.child_transactions:
        existing_dates.add(child.data)
    
    # Gera as próximas ocorrências
    count = 0
    current_date = start_date
    
    # Limita a 12 ocorrências futuras ou até a data de término
    for _ in range(limit):
        # Avança para a próxima data
        current_date = current_date + relativedelta(months=frequency_months)
        
        # Verifica se ultrapassou a data de término
        if end_date and current_date > end_date:
            break
        
        # Formata a data para string
        date_str = current_date.strftime('%Y-%m-%d')
        
        # Verifica se já existe uma ocorrência nesta data
        if date_str in existing_dates:
            continue
        
        # Cria uma nova ocorrência
        new_transaction = Transaction(
            user_id=transaction.user_id,
            descricao=transaction.descricao,
            valor=transaction.valor,
            tipo=transaction.tipo,
            data=date_str,
            vencimento=date_str,  # Usa a mesma data como vencimento
            pago=False,
            categoria_id=transaction.categoria_id,
            observacoes=transaction.observacoes,
            parent_transaction_id=transaction.id
        )
        
        db_session.add(new_transaction)
        count += 1
    
    db_session.commit()
    return count

def delete_gcal_event(transaction):
    """Exclui o evento do Google Calendar associado a uma transação"""
    # Verifica se há um evento do Google Calendar associado
    event_id = getattr(transaction, 'gcal_event_id', None)
    auth = GoogleCalendarAuth.query.filter_by(user_id=transaction.user_id, sync_enabled=1).first()
    
    # Se houver evento associado e integração ativa, exclui o evento
    if event_id and auth:
        try:
            from google.oauth2.credentials import Credentials
            from googleapiclient.discovery import build
            import json
            import os
            
            # Caminho para o arquivo de credenciais
            CLIENT_SECRETS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'client_secret.json')
            
            # Cria as credenciais
            credentials = Credentials(
                token=auth.access_token,
                refresh_token=auth.refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=json.load(open(CLIENT_SECRETS_FILE))['web']['client_id'],
                client_secret=json.load(open(CLIENT_SECRETS_FILE))['web']['client_secret'],
                scopes=['https://www.googleapis.com/auth/calendar']
            )
            
            # Cria o serviço do Calendar
            calendar_service = build('calendar', 'v3', credentials=credentials)
            
            # Exclui o evento
            calendar_service.events().delete(
                calendarId=auth.calendar_id,
                eventId=event_id
            ).execute()
            
            return True
        except Exception as e:
            # Apenas registra o erro, mas não impede a exclusão da transação
            print(f"Erro ao excluir evento do Google Calendar: {str(e)}")
    
    return False
