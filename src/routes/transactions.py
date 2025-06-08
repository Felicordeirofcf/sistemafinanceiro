from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from dateutil.relativedelta import relativedelta

from src.models import db_session
from src.models.transaction import Transaction
from src.models.category import Category

transactions_bp = Blueprint("transactions", __name__, url_prefix="/transactions")

# ----------------------------- ADICIONAR TRANSAÇÃO -----------------------------

@transactions_bp.route("/add", methods=["POST"])
@login_required
def add():
    try:
        descricao = request.form.get("descricao")
        valor_str = request.form.get("valor", "0")
        
        # Processar valor no formato brasileiro (R$ 100,59 ou 100,59)
        if valor_str:
            # Remover símbolos de moeda e espaços
            valor_str = valor_str.replace("R$", "").replace(" ", "").strip()
            # Substituir vírgula por ponto para conversão
            valor_str = valor_str.replace(",", ".")
            try:
                valor = float(valor_str) if valor_str else 0
            except ValueError:
                valor = 0
        else:
            valor = 0
        tipo = request.form.get("tipo")
        data_str = request.form.get("data")
        vencimento_str = request.form.get("vencimento") if tipo == "despesa" else None
        categoria_id = request.form.get("categoria_id")
        observacoes = request.form.get("observacoes", "")

        data = datetime.strptime(data_str, "%Y-%m-%d").date() if data_str else None
        vencimento = datetime.strptime(vencimento_str, "%Y-%m-%d").date() if vencimento_str else None

        is_recurring = request.form.get("is_recurring") == "on"
        recurrence_frequency = request.form.get("recurrence_frequency")
        recurrence_end_date_str = request.form.get("recurrence_end_date")
        recurrence_end_date = datetime.strptime(recurrence_end_date_str, "%Y-%m-%d").date() if recurrence_end_date_str else None

        if not descricao or not valor or not tipo or not data:
            return jsonify({"success": False, "message": "Campos obrigatórios faltando."}), 400

        transaction = Transaction(
            user_id=current_user.id,
            descricao=descricao,
            valor=valor,
            tipo=tipo,
            data=data,
            vencimento=vencimento,
            pago=False if tipo == "despesa" else True,
            categoria_id=categoria_id if categoria_id else None,
            observacoes=observacoes,
            is_recurring=is_recurring,
            recurrence_frequency=recurrence_frequency if is_recurring else None,
            recurrence_start_date=data if is_recurring else None,
            recurrence_end_date=recurrence_end_date if is_recurring else None
        )

        db_session.add(transaction)
        db_session.commit()

        # Gerar transações recorrentes imediatamente após criar a transação principal
        if is_recurring and tipo == "despesa":
            generate_recurring_transactions(transaction)

        return jsonify({"success": True, "message": "Transação adicionada com sucesso!"})

    except Exception as e:
        return jsonify({"success": False, "message": f"Erro ao adicionar transação: {str(e)}"}), 500


# ----------------------------- EXCLUIR TRANSAÇÃO -----------------------------

@transactions_bp.route("/delete/<int:id>", methods=["POST"])
@login_required
def delete(id):
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
        return jsonify({"success": True, "message": "Ocorrências futuras excluídas com sucesso."})
    else:
        db_session.delete(transaction)
        db_session.commit()
        return jsonify({"success": True, "message": "Transação excluída com sucesso."})


# ----------------------------- EDITAR TRANSAÇÃO -----------------------------

@transactions_bp.route("/edit/<int:id>", methods=["POST"])
@login_required
def edit(id):
    transaction = Transaction.query.filter_by(id=id, user_id=current_user.id).first()
    if not transaction:
        return jsonify({"success": False, "message": "Transação não encontrada."}), 404

    try:
        descricao = request.form.get("descricao")
        valor_str = request.form.get("valor", "0").replace(".", "").replace(",", "")
        valor = int(valor_str) if valor_str.isdigit() else 0
        tipo = request.form.get("tipo")
        data_str = request.form.get("data")
        vencimento_str = request.form.get("vencimento") if tipo == "despesa" else None
        categoria_id = request.form.get("categoria_id")
        observacoes = request.form.get("observacoes", "")

        data = datetime.strptime(data_str, "%Y-%m-%d").date()
        vencimento = datetime.strptime(vencimento_str, "%Y-%m-%d").date() if vencimento_str else None

        is_recurring = request.form.get("is_recurring") == "on"
        recurrence_frequency = request.form.get("recurrence_frequency")
        recurrence_end_date_str = request.form.get("recurrence_end_date")
        recurrence_end_date = datetime.strptime(recurrence_end_date_str, "%Y-%m-%d").date() if recurrence_end_date_str else None
        update_all_future = request.form.get("update_all_future") == "on"

        if not descricao or not valor or not tipo or not data:
            return jsonify({"success": False, "message": "Campos obrigatórios faltando."}), 400

        if (transaction.is_recurring or transaction.parent_transaction_id) and update_all_future:
            parent_id = transaction.parent_transaction_id if transaction.parent_transaction_id else transaction.id
            parent = Transaction.query.get(parent_id)

            if parent:
                parent.descricao = descricao
                parent.valor = valor
                parent.tipo = tipo
                parent.categoria_id = categoria_id or None
                parent.observacoes = observacoes
                parent.is_recurring = is_recurring
                parent.recurrence_frequency = recurrence_frequency if is_recurring else None
                parent.recurrence_end_date = recurrence_end_date if is_recurring else None

                today = datetime.now().date()
                future_transactions = Transaction.query.filter(
                    Transaction.parent_transaction_id == parent_id,
                    Transaction.data >= today
                ).all()

                for future in future_transactions:
                    future.descricao = descricao
                    future.valor = valor
                    future.tipo = tipo
                    future.categoria_id = categoria_id or None
                    future.observacoes = observacoes

                db_session.commit()
                return jsonify({"success": True, "message": "Ocorrências futuras atualizadas."})
        else:
            transaction.descricao = descricao
            transaction.valor = valor
            transaction.tipo = tipo
            transaction.data = data
            transaction.vencimento = vencimento
            transaction.categoria_id = categoria_id or None
            transaction.observacoes = observacoes
            transaction.is_recurring = is_recurring
            transaction.recurrence_frequency = recurrence_frequency if is_recurring else None
            transaction.recurrence_start_date = data if is_recurring else None
            transaction.recurrence_end_date = recurrence_end_date if is_recurring else None

            db_session.commit()

            if is_recurring and tipo == "despesa" and not transaction.child_transactions:
                generate_recurring_transactions(transaction)

            return jsonify({"success": True, "message": "Transação atualizada."})

    except Exception as e:
        return jsonify({"success": False, "message": f"Erro ao editar: {str(e)}"}), 500


# ----------------------------- TOGGLE STATUS -----------------------------

@transactions_bp.route("/toggle_status/<int:id>", methods=["POST"])
@login_required
def toggle_status(id):
    transaction = Transaction.query.filter_by(id=id, user_id=current_user.id).first()

    if not transaction:
        return jsonify({"success": False, "message": "Transação não encontrada."}), 404

    transaction.pago = not transaction.pago
    db_session.commit()

    status = "paga" if transaction.pago else "pendente"
    return jsonify({"success": True, "message": f"Transação marcada como {status}."})


# ----------------------------- MARCAR COMO PAGO -----------------------------

@transactions_bp.route("/pay/<int:id>", methods=["POST"])
@login_required
def pay(id):
    transaction = Transaction.query.filter_by(id=id, user_id=current_user.id).first()

    if not transaction:
        return jsonify({"success": False, "message": "Transação não encontrada."}), 404

    if transaction.tipo != "despesa":
        return jsonify({"success": False, "message": "Apenas despesas podem ser marcadas como pagas."}), 400

    transaction.pago = True
    db_session.commit()

    return jsonify({"success": True, "message": "Despesa marcada como paga."})


# ----------------------------- OBTER TRANSAÇÃO -----------------------------

@transactions_bp.route("/get/<int:id>", methods=["GET"])
@login_required
def get_transaction(id):
    transaction = Transaction.query.filter_by(id=id, user_id=current_user.id).first()

    if not transaction:
        return jsonify({"success": False, "message": "Transação não encontrada."}), 404

    try:
        # Tratamento seguro de datas
        data_str = None
        if transaction.data:
            if isinstance(transaction.data, str):
                data_str = transaction.data
            else:
                data_str = transaction.data.strftime("%Y-%m-%d")
        
        vencimento_str = None
        if transaction.vencimento:
            if isinstance(transaction.vencimento, str):
                vencimento_str = transaction.vencimento
            else:
                vencimento_str = transaction.vencimento.strftime("%Y-%m-%d")

        transaction_data = {
            "id": transaction.id,
            "descricao": transaction.descricao or "",
            "valor": float(transaction.valor) if transaction.valor else 0,
            "tipo": transaction.tipo or "receita",
            "data": data_str,
            "vencimento": vencimento_str,
            "pago": bool(transaction.pago),
            "categoria_id": transaction.categoria_id,
            "observacoes": transaction.observacoes or "",
            "is_recurring": bool(transaction.is_recurring),
            "frequencia": transaction.recurrence_frequency or "mensal"
        }

        return jsonify({"success": True, "transaction": transaction_data})
    
    except Exception as e:
        return jsonify({"success": False, "message": f"Erro ao processar dados da transação: {str(e)}"}), 500


# ----------------------------- TRANSAÇÕES RECORRENTES -----------------------------

@transactions_bp.route("/recurring")
@login_required
def recurring():
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
    recurring_transactions = Transaction.query.filter_by(
        user_id=current_user.id,
        is_recurring=True,
        parent_transaction_id=None
    ).all()

    count = 0
    for transaction in recurring_transactions:
        count += generate_recurring_transactions(transaction)

    flash(f"{count} novas ocorrências geradas.", "success")
    return redirect(url_for("transactions.recurring"))


def generate_recurring_transactions(transaction, months_ahead=12):
    """
    Gera transações recorrentes para os próximos meses especificados.
    
    Args:
        transaction: Transação base para gerar as recorrências
        months_ahead: Número de meses à frente para gerar (padrão: 12)
    
    Returns:
        int: Número de transações geradas
    """
    if not transaction.is_recurring or transaction.tipo != "despesa":
        return 0

    start_date = transaction.recurrence_start_date or transaction.data
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
    elif isinstance(start_date, datetime):
        start_date = start_date.date()
    
    end_date = transaction.recurrence_end_date
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
    elif isinstance(end_date, datetime):
        end_date = end_date.date()

    frequency_months = {
        "mensal": 1,
        "bimestral": 2,
        "trimestral": 3,
        "semestral": 6,
        "anual": 12
    }.get(transaction.recurrence_frequency, 1)

    # Buscar transações filhas existentes
    existing_transactions = Transaction.query.filter_by(
        parent_transaction_id=transaction.id
    ).all()
    existing_dates = set(t.data for t in existing_transactions)

    count = 0
    current_date = datetime.combine(start_date, datetime.min.time())
    
    # Calcular data limite (12 meses à frente ou data final definida pelo usuário)
    max_date = datetime.now().date() + relativedelta(months=months_ahead)
    if end_date and end_date < max_date:
        max_date = end_date

    # Gerar transações até atingir a data limite
    while True:
        current_date += relativedelta(months=frequency_months)
        next_date = current_date.date()
        
        # Verificar se a data limite foi atingida
        if next_date > max_date:
            break

        # Verificar se já existe uma transação para esta data
        if next_date in existing_dates:
            continue

        # Criar nova transação recorrente
        new_transaction = Transaction(
            user_id=transaction.user_id,
            descricao=transaction.descricao,
            valor=transaction.valor,
            tipo=transaction.tipo,
            data=next_date,
            vencimento=next_date,  # Para despesas recorrentes, vencimento = data
            pago=False,  # Sempre criar como não pago
            categoria_id=transaction.categoria_id,
            observacoes=transaction.observacoes,
            parent_transaction_id=transaction.id,
            is_recurring=False,  # Transações filhas não são recorrentes
            recurrence_frequency=None,
            recurrence_start_date=None,
            recurrence_end_date=None
        )

        db_session.add(new_transaction)
        count += 1

    if count > 0:
        db_session.commit()

    return count


# ----------------------------- MODAL DE TRANSAÇÃO -----------------------------

@transactions_bp.route("/modal")
@login_required
def transaction_modal():
    categories = Category.query.filter_by(user_id=current_user.id).all()
    return render_template("components/transaction_modal.html", categories=categories)
