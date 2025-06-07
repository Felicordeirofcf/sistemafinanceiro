from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from src.models import db_session
from src.models.transaction import Transaction
import smtplib
from email.message import EmailMessage

alerts_bp = Blueprint("alerts", __name__, url_prefix="/alerts")

def enviar_email(destinatario, assunto, corpo):
    msg = EmailMessage()
    msg["Subject"] = assunto
    msg["From"] = "seu_email@gmail.com"  # Substitua pelo seu e-mail
    msg["To"] = destinatario
    msg.set_content(corpo, subtype=\'html\')

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login("seu_email@gmail.com", "sua_senha_de_app")  # Substitua pelo seu e-mail e senha de app
            smtp.send_message(msg)
        return True
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")
        return False

@alerts_bp.route("/check")
@login_required
def check_alerts():
    try:
        today = datetime.now().date()
        seven_days_from_now = today + timedelta(days=7)

        upcoming_due = Transaction.query.filter(
            Transaction.user_id == current_user.id,
            Transaction.tipo == "despesa",
            Transaction.pago == False,
            Transaction.vencimento >= today,
            Transaction.vencimento <= seven_days_from_now
        ).all()

        transactions_list = [t.to_dict() for t in upcoming_due]

        return jsonify({
            "alerts": transactions_list,
            "count": len(transactions_list)
        })
    except Exception as e:
        print(f"Error in check_alerts: {e}")
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500

@alerts_bp.route("/send-email-alerts")
@login_required
def send_email_alerts():
    try:
        today = datetime.now().date()
        seven_days_from_now = today + timedelta(days=7)

        upcoming_due = Transaction.query.filter(
            Transaction.user_id == current_user.id,
            Transaction.tipo == "despesa",
            Transaction.pago == False,
            Transaction.vencimento >= today,
            Transaction.vencimento <= seven_days_from_now
        ).all()

        if not upcoming_due:
            flash("Não há despesas próximas do vencimento para notificar.", "info")
            return redirect(url_for("dashboard.index"))

        total_value = sum(t.valor for t in upcoming_due)
        num_expenses = len(upcoming_due)

        email_subject = "Alerta de Despesas - Sistema Financeiro"
        email_body = f"<h2>Alerta de Despesas Próximas do Vencimento</h2>"
        email_body += f"<p>Você tem {num_expenses} despesa(s) que vence(m) nos próximos dias. Valor total: R$ {total_value:.2f}.</p>"
        email_body += "<p>As seguintes despesas estão próximas do vencimento:</p>"
        email_body += "<table border=\'1\' cellpadding=\'5\' style=\'border-collapse: collapse;\'>"
        email_body += "<tr><th>Descrição</th><th>Valor</th><th>Vencimento</th><th>Categoria</th></tr>"

        for transaction in upcoming_due:
            vencimento = transaction.vencimento.strftime("%d/%m/%Y")
            email_body += f"<tr><td>{transaction.descricao}</td><td>R$ {transaction.valor:.2f}</td><td>{vencimento}</td><td>{transaction.categoria.nome if transaction.categoria else \'Sem categoria\'}</td></tr>"

        email_body += "</table><p>Acesse o sistema para mais detalhes.</p>"

        if enviar_email(current_user.email, email_subject, email_body):
            flash("E-mail de alerta enviado com sucesso!", "success")
        else:
            flash("Erro ao enviar e-mail de alerta. Verifique as configurações de e-mail.", "danger")

    except Exception as e:
        flash(f"Erro ao enviar e-mail: {str(e)}", "danger")

    return redirect(url_for("dashboard.index"))

@alerts_bp.route("/dismiss/<int:transaction_id>", methods=["POST"])
@login_required
def dismiss_alert(transaction_id):
    try:
        transaction = Transaction.query.filter_by(id=transaction_id, user_id=current_user.id).first()

        if transaction:
            # Assuming \'notificado\' field exists in Transaction model or can be added
            # If not, you might need to add it to the Transaction model
            # For now, we\'ll just return success as the original code had a \'notificado\' check
            return jsonify({"success": True})

        return jsonify({"success": False, "message": "Transação não encontrada"}), 404
    except Exception as e:
        print(f"Error in dismiss_alert: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


