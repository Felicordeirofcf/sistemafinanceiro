from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from src.models import db_session
from src.models.transaction import Transaction
from flask_mail import Mail, Message
from src.models.google_calendar_auth import GoogleCalendarAuth
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import os
import json

alerts_bp = Blueprint('alerts', __name__, url_prefix='/alerts')

mail = Mail()

@alerts_bp.route('/check')
@login_required
def check_alerts():
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        next_days = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")

        upcoming_due = Transaction.query.filter(
            Transaction.user_id == current_user.id,
            Transaction.tipo == 'despesa',
            Transaction.pago == False,
            Transaction.vencimento >= today,
            Transaction.vencimento <= next_days,
            getattr(Transaction, 'notificado', False) == False
        ).all()

        for transaction in upcoming_due:
            if hasattr(transaction, 'notificado'):
                transaction.notificado = True

        db_session.commit()

        transactions_list = [t.to_dict() for t in upcoming_due]

        return jsonify({
            'alerts': transactions_list,
            'count': len(transactions_list)
        })
    except Exception as e:
        print(f"Error in check_alerts: {e}")
        return jsonify({'error': 'Internal Server Error', 'message': str(e)}), 500

@alerts_bp.route('/send-email')
@login_required
def send_email_alerts():
    if not mail.app:
        flash('Serviço de e-mail não configurado.', 'warning')
        return redirect(url_for('dashboard.index'))

    try:
        today = datetime.now().strftime("%Y-%m-%d")
        next_days = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")

        upcoming_due = Transaction.query.filter(
            Transaction.user_id == current_user.id,
            Transaction.tipo == 'despesa',
            Transaction.pago == False,
            Transaction.vencimento >= today,
            Transaction.vencimento <= next_days
        ).all()

        if not upcoming_due:
            flash('Não há despesas próximas do vencimento para notificar.', 'info')
            return redirect(url_for('dashboard.index'))

        email_content = "<h2>Alerta de Despesas Próximas do Vencimento</h2>"
        email_content += "<p>As seguintes despesas estão próximas do vencimento:</p>"
        email_content += "<table border='1' cellpadding='5' style='border-collapse: collapse;'>"
        email_content += "<tr><th>Descrição</th><th>Valor</th><th>Vencimento</th><th>Categoria</th></tr>"

        auth = GoogleCalendarAuth.query.filter_by(user_id=current_user.id, sync_enabled=True).first()

        for transaction in upcoming_due:
            vencimento = datetime.strptime(transaction.vencimento, "%Y-%m-%d").strftime("%d/%m/%Y")
            email_content += f"<tr><td>{transaction.descricao}</td><td>R$ {transaction.valor:.2f}</td><td>{vencimento}</td><td>{transaction.categoria.nome if transaction.categoria else 'Sem categoria'}</td></tr>"

            if auth:
                criar_evento_google_calendar(transaction, auth)

        email_content += "</table><p>Acesse o sistema para mais detalhes.</p>"

        msg = Message(
            "Alerta de Despesas - Sistema Financeiro",
            recipients=[current_user.email],
            html=email_content
        )
        mail.send(msg)
        flash('E-mail de alerta enviado com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao enviar e-mail: {str(e)}', 'danger')

    return redirect(url_for('dashboard.index'))

@alerts_bp.route('/dismiss/<int:transaction_id>', methods=['POST'])
@login_required
def dismiss_alert(transaction_id):
    try:
        transaction = Transaction.query.filter_by(id=transaction_id, user_id=current_user.id).first()

        if transaction and hasattr(transaction, 'notificado'):
            transaction.notificado = True
            db_session.commit()
            return jsonify({'success': True})

        return jsonify({'success': False, 'message': 'Transação não encontrada ou sem campo notificado'}), 404
    except Exception as e:
        print(f"Error in dismiss_alert: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

def criar_evento_google_calendar(transaction, auth):
    try:
        with open("client_secret.json") as f:
            secrets = json.load(f)["web"]

        credentials = Credentials(
            token=auth.access_token,
            refresh_token=auth.refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=secrets["client_id"],
            client_secret=secrets["client_secret"],
            scopes=["https://www.googleapis.com/auth/calendar"]
        )

        service = build("calendar", "v3", credentials=credentials)

        evento = {
            "summary": f"[Despesa] {transaction.descricao}",
            "description": f"Valor: R$ {transaction.valor:.2f}\nCategoria: {transaction.categoria.nome if transaction.categoria else 'Sem categoria'}",
            "start": {"date": transaction.vencimento},
            "end": {"date": transaction.vencimento},
            "reminders": {
                "useDefault": False,
                "overrides": [
                    {"method": "email", "minutes": 2880},
                    {"method": "popup", "minutes": 1440}
                ]
            }
        }

        service.events().insert(calendarId=auth.calendar_id, body=evento).execute()
        print(f"✅ Evento criado para '{transaction.descricao}'")
    except Exception as e:
        print(f"⚠️ Erro ao criar evento no Google Calendar: {e}")
