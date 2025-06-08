from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from src.models import db_session
from src.models.transaction import Transaction
import smtplib
from email.message import EmailMessage
import os

alerts_bp = Blueprint("alerts", __name__, url_prefix="/alerts")

# 🔒 Função para envio de e-mails com fallback seguro
def enviar_email(destinatario, assunto, corpo_html):
    msg = EmailMessage()
    email_user = os.getenv("EMAIL_USER", "seu_email@gmail.com")
    email_pass = os.getenv("EMAIL_PASS", "sua_senha_de_app")

    msg["Subject"] = assunto
    msg["From"] = email_user
    msg["To"] = destinatario
    msg.set_content("Seu cliente de e-mail não suporta HTML.")
    msg.add_alternative(corpo_html, subtype="html")

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(email_user, email_pass)
            smtp.send_message(msg)
        return True
    except Exception as e:
        print(f"[ERRO] Falha ao enviar e-mail: {e}")
        return False


# 📅 Rota que retorna despesas com vencimento nos próximos 7 dias
@alerts_bp.route("/check")
@login_required
def check_alerts():
    try:
        hoje = datetime.now().date()
        limite = hoje + timedelta(days=7)

        despesas = Transaction.query.filter(
            Transaction.user_id == current_user.id,
            Transaction.tipo == "despesa",
            Transaction.pago == False,
            Transaction.vencimento >= hoje,
            Transaction.vencimento <= limite
        ).all()

        return jsonify({
            "alerts": [t.to_dict() for t in despesas],
            "count": len(despesas)
        })
    except Exception as e:
        print(f"[ERRO] check_alerts: {e}")
        return jsonify({"error": "Erro interno no servidor", "message": str(e)}), 500


# 📧 Rota que envia e-mail com as despesas próximas do vencimento
@alerts_bp.route("/send-email-alerts")
@login_required
def send_email_alerts():
    try:
        hoje = datetime.now().date()
        limite = hoje + timedelta(days=7)

        despesas = Transaction.query.filter(
            Transaction.user_id == current_user.id,
            Transaction.tipo == "despesa",
            Transaction.pago == False,
            Transaction.vencimento >= hoje,
            Transaction.vencimento <= limite
        ).all()

        if not despesas:
            flash("Não há despesas próximas do vencimento para notificar.", "info")
            return redirect(url_for("dashboard.index"))

        total = sum(t.valor for t in despesas)
        corpo = f"""
        <h2>🔔 Despesas a Vencer</h2>
        <p>Você tem <strong>{len(despesas)}</strong> despesa(s) próximas do vencimento.</p>
        <p><strong>Total:</strong> R$ {total:.2f}</p>
        <table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse;">
            <thead>
                <tr>
                    <th>Descrição</th>
                    <th>Valor (R$)</th>
                    <th>Vencimento</th>
                    <th>Categoria</th>
                </tr>
            </thead>
            <tbody>
        """

        for t in despesas:
            venc = t.vencimento.strftime("%d/%m/%Y")
            cat = t.categoria.nome if t.categoria else "Sem categoria"
            corpo += f"""
                <tr>
                    <td>{t.descricao}</td>
                    <td>{t.valor:.2f}</td>
                    <td>{venc}</td>
                    <td>{cat}</td>
                </tr>
            """

        corpo += "</tbody></table><p>Acesse o sistema para mais detalhes.</p>"

        if enviar_email(current_user.email, "📬 Alerta de Despesas", corpo):
            flash("E-mail de alerta enviado com sucesso!", "success")
        else:
            flash("Erro ao enviar e-mail. Verifique as credenciais ou permissões.", "danger")

    except Exception as e:
        print(f"[ERRO] send_email_alerts: {e}")
        flash(f"Erro ao enviar e-mail: {str(e)}", "danger")

    return redirect(url_for("dashboard.index"))


# ❌ Endpoint para "descartar" alerta no frontend (usado para UX)
@alerts_bp.route("/dismiss/<int:transaction_id>", methods=["POST"])
@login_required
def dismiss_alert(transaction_id):
    try:
        transaction = Transaction.query.filter_by(id=transaction_id, user_id=current_user.id).first()

        if not transaction:
            return jsonify({"success": False, "message": "Transação não encontrada"}), 404

        # Aqui futuramente você pode marcar como "alertado" ou "ignorado"
        return jsonify({"success": True})

    except Exception as e:
        print(f"[ERRO] dismiss_alert: {e}")
        return jsonify({"success": False, "message": str(e)}), 500
