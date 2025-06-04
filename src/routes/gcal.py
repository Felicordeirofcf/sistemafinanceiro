from flask import Blueprint, render_template, redirect, url_for, flash, request, session, jsonify
from flask_login import login_required, current_user
import os
import json
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from src.models import db_session
from src.models.transaction import Transaction
from src.models.google_calendar_auth import GoogleCalendarAuth

# Configuração do Blueprint
gcal_bp = Blueprint('gcal', __name__, url_prefix='/gcal')

# Configurações do OAuth
CLIENT_SECRETS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'client_secret.json')
SCOPES = ['https://www.googleapis.com/auth/calendar']
API_SERVICE_NAME = 'calendar'
API_VERSION = 'v3'

# Verificar se o arquivo de credenciais existe
if not os.path.exists(CLIENT_SECRETS_FILE):
    # Criar um arquivo de exemplo para orientar o usuário
    with open(CLIENT_SECRETS_FILE, 'w') as f:
        f.write(json.dumps({
            "web": {
                "client_id": "SEU_CLIENT_ID_AQUI",
                "project_id": "SEU_PROJECT_ID_AQUI",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_secret": "SEU_CLIENT_SECRET_AQUI",
                "redirect_uris": ["http://localhost:5000/gcal/oauth2callback"]
            }
        }, indent=4))

@gcal_bp.route('/')
@login_required
def index():
    """Página principal de configuração do Google Calendar"""
    # Verifica se o usuário já está autenticado
    auth = GoogleCalendarAuth.query.filter_by(user_id=current_user.id).first()
    
    return render_template(
        'gcal/index.html',
        auth=auth
    )

@gcal_bp.route('/authorize')
@login_required
def authorize():
    """Inicia o fluxo de autorização OAuth"""
    # Cria o fluxo de autorização usando o arquivo de credenciais
    try:
        flow = Flow.from_client_secrets_file(
            CLIENT_SECRETS_FILE,
            scopes=SCOPES,
            redirect_uri=url_for('gcal.oauth2callback', _external=True)
        )
        
        # Gera a URL de autorização
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'  # Força a exibição da tela de consentimento para obter refresh_token
        )
        
        # Armazena o estado na sessão para validação posterior
        session['state'] = state
        
        # Redireciona para a URL de autorização
        return redirect(authorization_url)
    except Exception as e:
        flash(f'Erro ao iniciar autorização: {str(e)}', 'danger')
        return redirect(url_for('gcal.index'))

@gcal_bp.route('/oauth2callback')
@login_required
def oauth2callback():
    """Callback para processar a resposta da autorização OAuth"""
    # Verifica o estado para prevenir ataques CSRF
    state = session.get('state')
    if not state or state != request.args.get('state'):
        flash('Erro de validação de estado. Tente novamente.', 'danger')
        return redirect(url_for('gcal.index'))
    
    try:
        # Cria o fluxo de autorização
        flow = Flow.from_client_secrets_file(
            CLIENT_SECRETS_FILE,
            scopes=SCOPES,
            state=state,
            redirect_uri=url_for('gcal.oauth2callback', _external=True)
        )
        
        # Processa a resposta da autorização
        flow.fetch_token(authorization_response=request.url)
        credentials = flow.credentials
        
        # Armazena as credenciais no banco de dados
        auth = GoogleCalendarAuth.query.filter_by(user_id=current_user.id).first()
        if not auth:
            auth = GoogleCalendarAuth(user_id=current_user.id)
            db_session.add(auth)
        
        auth.access_token = credentials.token
        auth.refresh_token = credentials.refresh_token
        auth.token_expiry = datetime.utcnow() + timedelta(seconds=credentials.expiry)
        
        # Obtém o ID do calendário principal do usuário
        calendar_service = build(API_SERVICE_NAME, API_VERSION, credentials=credentials)
        calendar_list = calendar_service.calendarList().list().execute()
        primary_calendar = next((cal for cal in calendar_list.get('items', []) if cal.get('primary')), None)
        
        if primary_calendar:
            auth.calendar_id = primary_calendar['id']
        
        db_session.commit()
        
        flash('Conta Google conectada com sucesso!', 'success')
        
        # Sincroniza as transações existentes
        return redirect(url_for('gcal.sync_all'))
    except Exception as e:
        flash(f'Erro ao processar autorização: {str(e)}', 'danger')
        return redirect(url_for('gcal.index'))

@gcal_bp.route('/disconnect')
@login_required
def disconnect():
    """Desconecta a conta Google"""
    auth = GoogleCalendarAuth.query.filter_by(user_id=current_user.id).first()
    
    if auth:
        try:
            # Revoga o token de acesso
            credentials = Credentials(
                token=auth.access_token,
                refresh_token=auth.refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=json.load(open(CLIENT_SECRETS_FILE))['web']['client_id'],
                client_secret=json.load(open(CLIENT_SECRETS_FILE))['web']['client_secret'],
                scopes=SCOPES
            )
            
            # Remove do banco de dados
            db_session.delete(auth)
            db_session.commit()
            
            flash('Conta Google desconectada com sucesso!', 'success')
        except Exception as e:
            flash(f'Erro ao desconectar conta: {str(e)}', 'danger')
    else:
        flash('Nenhuma conta Google conectada.', 'warning')
    
    return redirect(url_for('gcal.index'))

@gcal_bp.route('/sync/<int:transaction_id>')
@login_required
def sync_transaction(transaction_id):
    """Sincroniza uma transação específica com o Google Calendar"""
    auth = GoogleCalendarAuth.query.filter_by(user_id=current_user.id).first()
    
    if not auth or not auth.sync_enabled:
        flash('Sincronização com Google Calendar não está habilitada.', 'warning')
        return redirect(url_for('dashboard.index'))
    
    transaction = Transaction.query.filter_by(id=transaction_id, user_id=current_user.id).first()
    
    if not transaction:
        flash('Transação não encontrada.', 'danger')
        return redirect(url_for('dashboard.index'))
    
    try:
        # Cria as credenciais
        credentials = Credentials(
            token=auth.access_token,
            refresh_token=auth.refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=json.load(open(CLIENT_SECRETS_FILE))['web']['client_id'],
            client_secret=json.load(open(CLIENT_SECRETS_FILE))['web']['client_secret'],
            scopes=SCOPES
        )
        
        # Cria o serviço do Calendar
        calendar_service = build(API_SERVICE_NAME, API_VERSION, credentials=credentials)
        
        # Prepara o evento
        event = {
            'summary': transaction.descricao,
            'description': f"Valor: R$ {transaction.valor:.2f} | Categoria: {transaction.categoria.nome if transaction.categoria else 'Sem categoria'} | Tipo: {transaction.tipo.capitalize()}",
            'start': {
                'date': transaction.vencimento if transaction.vencimento else transaction.data
            },
            'end': {
                'date': transaction.vencimento if transaction.vencimento else transaction.data
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 2880},  # 2 dias antes
                    {'method': 'popup', 'minutes': 1440}   # 1 dia antes
                ]
            }
        }
        
        # Verifica se a transação já tem um evento associado
        event_id = getattr(transaction, 'gcal_event_id', None)
        
        if event_id:
            # Atualiza o evento existente
            calendar_service.events().update(
                calendarId=auth.calendar_id,
                eventId=event_id,
                body=event
            ).execute()
            flash('Evento atualizado no Google Calendar.', 'success')
        else:
            # Cria um novo evento
            created_event = calendar_service.events().insert(
                calendarId=auth.calendar_id,
                body=event
            ).execute()
            
            # Armazena o ID do evento
            transaction.gcal_event_id = created_event['id']
            db_session.commit()
            
            flash('Evento criado no Google Calendar.', 'success')
        
        return redirect(url_for('dashboard.index'))
    except Exception as e:
        flash(f'Erro ao sincronizar com Google Calendar: {str(e)}', 'danger')
        return redirect(url_for('dashboard.index'))

@gcal_bp.route('/sync_all')
@login_required
def sync_all():
    """Sincroniza todas as transações com o Google Calendar"""
    auth = GoogleCalendarAuth.query.filter_by(user_id=current_user.id).first()
    
    if not auth or not auth.sync_enabled:
        flash('Sincronização com Google Calendar não está habilitada.', 'warning')
        return redirect(url_for('gcal.index'))
    
    # Obtém todas as transações do tipo despesa (apenas despesas são sincronizadas)
    transactions = Transaction.query.filter_by(
        user_id=current_user.id,
        tipo='despesa'
    ).all()
    
    if not transactions:
        flash('Nenhuma despesa encontrada para sincronizar.', 'info')
        return redirect(url_for('gcal.index'))
    
    try:
        # Cria as credenciais
        credentials = Credentials(
            token=auth.access_token,
            refresh_token=auth.refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=json.load(open(CLIENT_SECRETS_FILE))['web']['client_id'],
            client_secret=json.load(open(CLIENT_SECRETS_FILE))['web']['client_secret'],
            scopes=SCOPES
        )
        
        # Cria o serviço do Calendar
        calendar_service = build(API_SERVICE_NAME, API_VERSION, credentials=credentials)
        
        # Contador de eventos sincronizados
        synced_count = 0
        
        for transaction in transactions:
            try:
                # Prepara o evento
                event = {
                    'summary': transaction.descricao,
                    'description': f"Valor: R$ {transaction.valor:.2f} | Categoria: {transaction.categoria.nome if transaction.categoria else 'Sem categoria'} | Tipo: {transaction.tipo.capitalize()}",
                    'start': {
                        'date': transaction.vencimento if transaction.vencimento else transaction.data
                    },
                    'end': {
                        'date': transaction.vencimento if transaction.vencimento else transaction.data
                    },
                    'reminders': {
                        'useDefault': False,
                        'overrides': [
                            {'method': 'email', 'minutes': 2880},  # 2 dias antes
                            {'method': 'popup', 'minutes': 1440}   # 1 dia antes
                        ]
                    }
                }
                
                # Verifica se a transação já tem um evento associado
                event_id = getattr(transaction, 'gcal_event_id', None)
                
                if event_id:
                    # Atualiza o evento existente
                    calendar_service.events().update(
                        calendarId=auth.calendar_id,
                        eventId=event_id,
                        body=event
                    ).execute()
                else:
                    # Cria um novo evento
                    created_event = calendar_service.events().insert(
                        calendarId=auth.calendar_id,
                        body=event
                    ).execute()
                    
                    # Armazena o ID do evento
                    transaction.gcal_event_id = created_event['id']
                
                synced_count += 1
            except Exception as e:
                # Continua para a próxima transação em caso de erro
                continue
        
        # Salva todas as alterações
        db_session.commit()
        
        flash(f'{synced_count} despesas sincronizadas com Google Calendar.', 'success')
        return redirect(url_for('gcal.index'))
    except Exception as e:
        flash(f'Erro ao sincronizar com Google Calendar: {str(e)}', 'danger')
        return redirect(url_for('gcal.index'))

@gcal_bp.route('/toggle_sync')
@login_required
def toggle_sync():
    """Ativa/desativa a sincronização com o Google Calendar"""
    auth = GoogleCalendarAuth.query.filter_by(user_id=current_user.id).first()
    
    if not auth:
        flash('Nenhuma conta Google conectada.', 'warning')
        return redirect(url_for('gcal.index'))
    
    # Inverte o estado de sincronização
    auth.sync_enabled = 0 if auth.sync_enabled else 1
    db_session.commit()
    
    status = "ativada" if auth.sync_enabled else "desativada"
    flash(f'Sincronização com Google Calendar {status}.', 'success')
    
    return redirect(url_for('gcal.index'))
