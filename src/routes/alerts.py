from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from src.models import db_session
from src.models.transaction import Transaction
from flask_mail import Mail, Message
import os

alerts_bp = Blueprint(\'alerts\', __name__, url_prefix=\'/alerts\')

# Configuração do Flask-Mail
mail = Mail()

@alerts_bp.route(\'/check\')
@login_required
def check_alerts():
    """Verifica transações próximas do vencimento e exibe alertas"""
    try:
        today = datetime.now().strftime(\"%Y-%m-%d\")
        next_days = (datetime.now() + timedelta(days=2)).strftime(\"%Y-%m-%d\")
        
        # Busca despesas não pagas com vencimento nos próximos 2 dias
        upcoming_due = Transaction.query.filter(
            Transaction.user_id == current_user.id,
            Transaction.tipo == \'despesa\',
            Transaction.pago == False,
            Transaction.vencimento >= today,
            Transaction.vencimento <= next_days,
            Transaction.notificado == False  # Apenas as que ainda não foram notificadas
        ).all()
        
        # Marca as transações como notificadas
        for transaction in upcoming_due:
            transaction.notificado = True
        
        db_session.commit()
        
        # Retorna as transações para exibição no frontend
        transactions_list = [t.to_dict() for t in upcoming_due]
        
        return jsonify({
            \'alerts\': transactions_list,
            \'count\': len(transactions_list)
        })
    except Exception as e:
        # Log the error for debugging
        print(f"Error in check_alerts: {e}")
        # Return a JSON error response
        return jsonify({\'error\': \'Internal Server Error\', \'message\': str(e)}), 500

@alerts_bp.route(\'/send-email\')
@login_required
def send_email_alerts():
    """Envia alertas por e-mail para despesas próximas do vencimento"""
    # Verifica se o serviço de e-mail está configurado
    if not mail.app:
        flash(\'Serviço de e-mail não configurado.\', \'warning\')
        return redirect(url_for(\'dashboard.index\'))
    
    try:
        today = datetime.now().strftime(\"%Y-%m-%d\")
        next_days = (datetime.now() + timedelta(days=2)).strftime(\"%Y-%m-%d\")
        
        # Busca despesas não pagas com vencimento nos próximos 2 dias
        upcoming_due = Transaction.query.filter(
            Transaction.user_id == current_user.id,
            Transaction.tipo == \'despesa\',
            Transaction.pago == False,
            Transaction.vencimento >= today,
            Transaction.vencimento <= next_days
        ).all()
        
        if not upcoming_due:
            flash(\'Não há despesas próximas do vencimento para notificar.\', \'info\')
            return redirect(url_for(\'dashboard.index\'))
        
        # Prepara o conteúdo do e-mail
        email_content = "<h2>Alerta de Despesas Próximas do Vencimento</h2>"
        email_content += "<p>As seguintes despesas estão próximas do vencimento:</p>"
        email_content += "<table border=\'1\' cellpadding=\'5\' style=\'border-collapse: collapse;\'>"
        email_content += "<tr><th>Descrição</th><th>Valor</th><th>Vencimento</th><th>Categoria</th></tr>"
        
        for transaction in upcoming_due:
            vencimento = datetime.strptime(transaction.vencimento, \"%Y-%m-%d\").strftime(\"%d/%m/%Y\")
            email_content += f"<tr>"
            email_content += f"<td>{transaction.descricao}</td>"
            email_content += f"<td>R$ {transaction.valor:.2f}</td>"
            email_content += f"<td>{vencimento}</td>"
            email_content += f"<td>{transaction.categoria.nome if transaction.categoria else \'Sem categoria\'}</td>"
            email_content += f"</tr>"
        
        email_content += "</table>"
        email_content += "<p>Acesse o sistema para mais detalhes.</p>"
        
        # Envia o e-mail
        msg = Message(
            "Alerta de Despesas - Sistema Financeiro",
            recipients=[current_user.email],
            html=email_content
        )
        mail.send(msg)
        flash(\'E-mail de alerta enviado com sucesso!\', \'success\')
    except Exception as e:
        flash(f\'Erro ao enviar e-mail: {str(e)}\', \'danger\')
    
    return redirect(url_for(\'dashboard.index\'))

@alerts_bp.route(\'/dismiss/<int:transaction_id>\', methods=[\'POST\'])
@login_required
def dismiss_alert(transaction_id):
    """Marca um alerta como visualizado"""
    try:
        transaction = Transaction.query.filter_by(id=transaction_id, user_id=current_user.id).first()
        
        if transaction:
            transaction.notificado = True
            db_session.commit()
            return jsonify({\'success\': True})
        
        return jsonify({\'success\': False, \'message\': \'Transação não encontrada\'}), 404
    except Exception as e:
        print(f"Error in dismiss_alert: {e}")
        return jsonify({\'success\': False, \'message\': str(e)}), 500


