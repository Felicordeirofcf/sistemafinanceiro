from flask import Blueprint, render_template, redirect, url_for, flash, request, session, jsonify
from flask_login import login_required, current_user
import os
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from src.models import db_session
from src.models.transaction import Transaction
from src.models.google_calendar_auth import GoogleCalendarAuth

# Blueprint configuration
gcal_bp = Blueprint('gcal', __name__, url_prefix='/gcal')

# OAuth configurations from environment variables
SCOPES = ['https://www.googleapis.com/auth/calendar']
API_SERVICE_NAME = 'calendar'
API_VERSION = 'v3'
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")

@gcal_bp.route('/')
@login_required
def index():
    auth = GoogleCalendarAuth.query.filter_by(user_id=current_user.id).first()
    if not auth:
        return redirect(url_for("gcal.authorize"))
    return render_template('gcal/index.html', auth=auth)

@gcal_bp.route('/authorize')
@login_required
def authorize():
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

        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )
        session['state'] = state
        return redirect(authorization_url)

    except Exception as e:
        flash(f'Erro ao iniciar autorização: {str(e)}', 'danger')
        return redirect(url_for('gcal.index'))

@gcal_bp.route('/oauth2callback')
@login_required
def oauth2callback():
    state = session.get('state')
    if not state or state != request.args.get('state'):
        flash('Erro de validação de estado.', 'danger')
        return redirect(url_for('gcal.index'))

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
            state=state,
            redirect_uri=GOOGLE_REDIRECT_URI
        )

        flow.fetch_token(authorization_response=request.url)
        credentials = flow.credentials

        auth = GoogleCalendarAuth.query.filter_by(user_id=current_user.id).first()
        if not auth:
            auth = GoogleCalendarAuth(user_id=current_user.id)
            db_session.add(auth)

        auth.access_token = credentials.token
        auth.refresh_token = credentials.refresh_token
        auth.token_expiry = datetime.utcnow() + timedelta(seconds=credentials.expiry)

        calendar_service = build(API_SERVICE_NAME, API_VERSION, credentials=credentials)
        calendar_list = calendar_service.calendarList().list().execute()
        primary_calendar = next((cal for cal in calendar_list.get('items', []) if cal.get('primary')), None)

        if primary_calendar:
            auth.calendar_id = primary_calendar['id']

        db_session.commit()

        flash('Conta Google conectada com sucesso!', 'success')
        return redirect(url_for('gcal.sync_all'))

    except Exception as e:
        flash(f'Erro ao processar autorização: {str(e)}', 'danger')
        return redirect(url_for('gcal.index'))

@gcal_bp.route('/disconnect')
@login_required
def disconnect():
    auth = GoogleCalendarAuth.query.filter_by(user_id=current_user.id).first()

    if auth:
        try:
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
    auth = GoogleCalendarAuth.query.filter_by(user_id=current_user.id).first()
    
    if not auth or not auth.sync_enabled:
        flash('Sincronização com Google Calendar não está habilitada.', 'warning')
        return redirect(url_for('dashboard.index'))
    
    transaction = Transaction.query.filter_by(id=transaction_id, user_id=current_user.id).first()
    
    if not transaction:
        flash('Transação não encontrada.', 'danger')
        return redirect(url_for('dashboard.index'))
    
    try:
        credentials = Credentials(
            token=auth.access_token,
            refresh_token=auth.refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=GOOGLE_CLIENT_ID,
            client_secret=GOOGLE_CLIENT_SECRET,
            scopes=SCOPES
        )
        
        calendar_service = build(API_SERVICE_NAME, API_VERSION, credentials=credentials)

        data_evento = (transaction.vencimento or transaction.data).strftime('%Y-%m-%d')

        event = {
            'summary': transaction.descricao,
            'description': f"Valor: R$ {transaction.valor:.2f} | Categoria: {transaction.categoria.nome if transaction.categoria else 'Sem categoria'} | Tipo: {transaction.tipo.capitalize()}",
            'start': {
                'dateTime': f"{data_evento}T09:00:00",
                'timeZone': 'America/Sao_Paulo'
            },
            'end': {
                'dateTime': f"{data_evento}T10:00:00",
                'timeZone': 'America/Sao_Paulo'
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 2880},
                    {'method': 'popup', 'minutes': 1440}
                ]
            }
        }

        event_id = getattr(transaction, 'gcal_event_id', None)

        if event_id:
            calendar_service.events().update(
                calendarId=auth.calendar_id,
                eventId=event_id,
                body=event
            ).execute()
            flash('Evento atualizado no Google Calendar.', 'success')
        else:
            created_event = calendar_service.events().insert(
                calendarId=auth.calendar_id,
                body=event
            ).execute()
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
    auth = GoogleCalendarAuth.query.filter_by(user_id=current_user.id).first()
    
    if not auth or not auth.sync_enabled:
        flash('Sincronização com Google Calendar não está habilitada.', 'warning')
        return redirect(url_for('gcal.index'))
    
    transactions = Transaction.query.filter_by(
        user_id=current_user.id,
        tipo='despesa'
    ).all()
    
    if not transactions:
        flash('Nenhuma despesa encontrada para sincronizar.', 'info')
        return redirect(url_for('gcal.index'))
    
    try:
        credentials = Credentials(
            token=auth.access_token,
            refresh_token=auth.refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=GOOGLE_CLIENT_ID,
            client_secret=GOOGLE_CLIENT_SECRET,
            scopes=SCOPES
        )
        
        calendar_service = build(API_SERVICE_NAME, API_VERSION, credentials=credentials)

        synced_count = 0

        for transaction in transactions:
            try:
                data_evento = (transaction.vencimento or transaction.data).strftime('%Y-%m-%d')

                event = {
                    'summary': transaction.descricao,
                    'description': f"Valor: R$ {transaction.valor:.2f} | Categoria: {transaction.categoria.nome if transaction.categoria else 'Sem categoria'} | Tipo: {transaction.tipo.capitalize()}",
                    'start': {
                        'dateTime': f"{data_evento}T09:00:00",
                        'timeZone': 'America/Sao_Paulo'
                    },
                    'end': {
                        'dateTime': f"{data_evento}T10:00:00",
                        'timeZone': 'America/Sao_Paulo'
                    },
                    'reminders': {
                        'useDefault': False,
                        'overrides': [
                            {'method': 'email', 'minutes': 2880},
                            {'method': 'popup', 'minutes': 1440}
                        ]
                    }
                }

                event_id = getattr(transaction, 'gcal_event_id', None)

                if event_id:
                    calendar_service.events().update(
                        calendarId=auth.calendar_id,
                        eventId=event_id,
                        body=event
                    ).execute()
                else:
                    created_event = calendar_service.events().insert(
                        calendarId=auth.calendar_id,
                        body=event
                    ).execute()
                    transaction.gcal_event_id = created_event['id']
                
                synced_count += 1
            except Exception:
                continue
        
        db_session.commit()
        flash(f'{synced_count} despesas sincronizadas com Google Calendar.', 'success')
        return redirect(url_for('gcal.index'))
    except Exception as e:
        flash(f'Erro ao sincronizar com Google Calendar: {str(e)}', 'danger')
        return redirect(url_for('gcal.index'))

@gcal_bp.route('/toggle_sync')
@login_required
def toggle_sync():
    auth = GoogleCalendarAuth.query.filter_by(user_id=current_user.id).first()
    
    if not auth:
        flash('Nenhuma conta Google conectada.', 'warning')
        return redirect(url_for('gcal.index'))
    
    auth.sync_enabled = 0 if auth.sync_enabled else 1
    db_session.commit()
    
    status = "ativada" if auth.sync_enabled else "desativada"
    flash(f'Sincronização com Google Calendar {status}.', 'success')
    
    return redirect(url_for('gcal.index'))
