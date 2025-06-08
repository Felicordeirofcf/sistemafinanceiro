from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from dateutil.relativedelta import relativedelta

from src.models import db_session
from src.models.transaction import Transaction
from src.models.category import Category

transactions_bp = Blueprint("transactions", __name__, url_prefix="/transactions")

# ----------------------------- ADICIONAR TRANSAÇÃO -----------------------------

@transactions_bp.route("/delete/<int:id>", methods=["POST"])
@login_required
def delete(id):
    """Exclui uma transação"""
    transaction = Transaction.query.filter_by(id=id, user_id=current_user.id).first()

    if not transaction:
        return jsonify({"success": False, "message": "Transação não encontrada."}), 404

    is_recurring = transaction.is_recurring or transaction.parent_transaction_id
    delete_all_future = request.json.get("delete_all_future") if request.is_json else False

    if is_recurring and delete_all_future:
        parent_id = transaction.parent_transaction_id if transaction.parent_transaction_id else transaction.id

        today = datetime.now().date()
        future_transactions = Transaction.query.filter(
            Transaction.parent_transaction_id == parent_id,
            Transaction.data >= today
        ).all()

        for future in future_transactions:
            db_session.delete(future)

        if transaction.id == parent_id:
            db_session.delete(transaction)

        db_session.commit()
        return jsonify({"success": True, "message": "Todas as ocorrências futuras foram excluídas com sucesso!"})
    else:
        db_session.delete(transaction)
        db_session.commit()
        return jsonify({"success": True, "message": "Transação excluída com sucesso!"})
    return redirect(url_for("dashboard.index"))

# ----------------------------- EDITAR TRANSAÇÃO -----------------------------

@transactions_bp.route("/edit/<int:id>", methods=["POST"])
@login_required
def edit(id):
    """Edita uma transação existente"""
    transaction = Transaction.query.filter_by(id=id, user_id=current_user.id).first()

    if not transaction:
        flash("Transação não encontrada.", "danger")
        return redirect(url_for("dashboard.index"))

    descricao = request.form.get("descricao")
    valor_str = request.form.get("valor", "0").replace(".", "").replace(",", "")
    valor = int(valor_str) if valor_str.isdigit() else 0
    tipo = request.form.get("tipo")
    data = request.form.get("data")
    vencimento = request.form.get("vencimento") if tipo == "despesa" else None
    categoria_id = request.form.get("categoria_id")
    observacoes = request.form.get("observacoes", "")

    is_recurring = request.form.get("is_recurring") == "on"
    recurrence_frequency = request.form.get("recurrence_frequency")
    recurrence_end_date = request.form.get("recurrence_end_date")
    update_all_future = request.form.get("update_all_future") == "on"

    if not descricao or not valor or not tipo or not data:
        flash("Todos os campos obrigatórios devem ser preenchidos.", "danger")
        return redirect(url_for("dashboard.index"))

    if (transaction.is_recurring or transaction.parent_transaction_id) and update_all_future:
        parent_id = transaction.parent_transaction_id if transaction.parent_transaction_id else transaction.id
        parent = Transaction.query.get(parent_id)

        if parent:
            parent.descricao = descricao
            parent.valor = valor
            parent.tipo = tipo
            parent.categoria_id = categoria_id if categoria_id else None
            parent.observacoes = observacoes
            parent.is_recurring = is_recurring
            parent.recurrence_frequency = recurrence_frequency if is_recurring else None
            parent.recurrence_end_date = recurrence_end_date if is_recurring and recurrence_end_date else None

            today = datetime.now().strftime("%Y-%m-%d")
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
            flash("Todas as ocorrências futuras foram atualizadas com sucesso!", "success")
        else:
            flash("Transação pai não encontrada.", "danger")
    else:
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

        if is_recurring and tipo == "despesa" and not transaction.child_transactions:
            generate_recurring_transactions(transaction)

        flash("Transação atualizada com sucesso!", "success")

    return redirect(url_for("dashboard.index"))

# ----------------------------- EXCLUIR TRANSAÇÃO -----------------------------

@transactions_bp.route("/delete/<int:id>")
@login_required
def delete(id):
    """Exclui uma transação"""
    transaction = Transaction.query.filter_by(id=id, user_id=current_user.id).first()

    if not transaction:
        flash("Transação não encontrada.", "danger")
        return redirect(url_for("dashboard.index"))

    is_recurring = transaction.is_recurring or transaction.parent_transaction_id
    delete_all_future = request.args.get("delete_all_future") == "true"

    if is_recurring and delete_all_future:
        parent_id = transaction.parent_transaction_id if transaction.parent_transaction_id else transaction.id

        today = datetime.now().strftime("%Y-%m-%d")
        future_transactions = Transaction.query.filter(
            Transaction.parent_transaction_id == parent_id,
            Transaction.data >= today
        ).all()

        for future in future_transactions:
            db_session.delete(future)

        if transaction.id == parent_id:
            db_session.delete(transaction)

        db_session.commit()
        flash("Todas as ocorrências futuras foram excluídas com sucesso!", "success")
    else:
        db_session.delete(transaction)
        db_session.commit()
        flash("Transação excluída com sucesso!", "success")

    return redirect(url_for("dashboard.index"))

# ----------------------------- TOGGLE STATUS -----------------------------

@transactions_bp.route("/toggle_status/<int:id>")
@login_required
def toggle_status(id):
    """Alterna o status de pagamento de uma transação"""
    transaction = Transaction.query.filter_by(id=id, user_id=current_user.id).first()

    if not transaction:
        flash("Transação não encontrada.", "danger")
        return redirect(url_for("dashboard.index"))

    transaction.pago = not transaction.pago
    db_session.commit()

    status = "paga" if transaction.pago else "pendente"
    flash(f"Transação marcada como {status}.", "success")
    return redirect(url_for("dashboard.index"))

# ----------------------------- TRANSAÇÕES RECORRENTES -----------------------------

@transactions_bp.route("/recurring")
@login_required
def recurring():
    """Exibe todas as despesas recorrentes"""
    recurring_transactions = Transaction.query.filter_by(
        user_id=current_user.id,
        is_recurring=True,
        parent_transaction_id=None
    ).order_by(Transaction.data.desc()).all()

    categories = Category.query.filter_by(user_id=current_user.id).all()

    return render_template(
        "dashboard/recurring.html",
        transactions=recurring_transactions,
        categories=categories
    )

@transactions_bp.route("/generate_recurring")
@login_required
def generate_recurring():
    """Gera as próximas ocorrências de todas as despesas recorrentes"""
    recurring_transactions = Transaction.query.filter_by(
        user_id=current_user.id,
        is_recurring=True,
        parent_transaction_id=None
    ).all()

    count = 0
    for transaction in recurring_transactions:
        count += generate_recurring_transactions(transaction)

    flash(f"{count} novas ocorrências de despesas recorrentes foram geradas.", "success")
    return redirect(url_for("transactions.recurring"))

def generate_recurring_transactions(transaction, limit=12):
    """Gera as próximas ocorrências de uma despesa recorrente"""
    if not transaction.is_recurring or transaction.tipo != "despesa":
        return 0

    start_date = datetime.strptime(transaction.recurrence_start_date or transaction.data, "%Y-%m-%d")
    end_date = None
    if transaction.recurrence_end_date:
        end_date = datetime.strptime(transaction.recurrence_end_date, "%Y-%m-%d")

    frequency_months = {
        "mensal": 1,
        "bimestral": 2,
        "trimestral": 3,
        "semestral": 6,
        "anual": 12
    }.get(transaction.recurrence_frequency, 1)

    existing_dates = set(child.data for child in transaction.child_transactions)

    count = 0
    current_date = start_date

    for _ in range(limit):
        current_date += relativedelta(months=frequency_months)
        if end_date and current_date > end_date:
            break

        date_str = current_date.strftime("%Y-%m-%d")
        if date_str in existing_dates:
            continue

        new_transaction = Transaction(
            user_id=transaction.user_id,
            descricao=transaction.descricao,
            valor=transaction.valor,
            tipo=transaction.tipo,
            data=date_str,
            vencimento=date_str,
            pago=False,
            categoria_id=transaction.categoria_id,
            observacoes=transaction.observacoes,
            parent_transaction_id=transaction.id
        )

        db_session.add(new_transaction)
        count += 1

    db_session.commit()
    return count

# ----------------------------- ROTA OPCIONAL: CARREGAR MODAL -----------------------------

@transactions_bp.route("/modal")
@login_required
def transaction_modal():
    """Carrega o modal de transação com categorias do usuário"""
    categories = Category.query.filter_by(user_id=current_user.id).all()
    return render_template("components/transaction_modal.html", categories=categories)
