from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from src.models import db_session
from src.models.transaction import Transaction
from src.models.category import Category

transactions_bp = Blueprint('transactions', __name__, url_prefix='/transactions')

@transactions_bp.route('/add', methods=['POST'])
@login_required
def add_transaction():
    """Adiciona uma nova transação"""
    if request.method == 'POST':
        tipo = request.form.get('tipo')
        valor = request.form.get('valor')
        data = request.form.get('data')
        descricao = request.form.get('descricao')
        categoria_id = request.form.get('categoria')
        
        # Validação dos campos
        if not all([tipo, valor, data, descricao, categoria_id]):
            flash('Todos os campos são obrigatórios!', 'danger')
            return redirect(url_for('dashboard.index', mes=request.args.get('mes'), ano=request.args.get('ano')))
        
        try:
            valor_float = float(valor)
            if valor_float <= 0:
                flash('O valor deve ser positivo.', 'danger')
                return redirect(url_for('dashboard.index', mes=request.args.get('mes'), ano=request.args.get('ano')))
        except ValueError:
            flash('Valor inválido!', 'danger')
            return redirect(url_for('dashboard.index', mes=request.args.get('mes'), ano=request.args.get('ano')))
        
        # Define 'pago' como True para receitas, False para despesas por padrão
        pago_status = True if tipo == 'receita' else False
        
        # Define vencimento igual à data para receitas
        vencimento = data if tipo == 'receita' else request.form.get('vencimento', data)
        
        # Cria a nova transação
        transaction = Transaction(
            user_id=current_user.id,
            tipo=tipo,
            valor=valor_float,
            data=data,
            descricao=descricao,
            categoria_id=categoria_id,
            pago=pago_status,
            vencimento=vencimento
        )
        
        db_session.add(transaction)
        db_session.commit()
        
        flash('Transação adicionada com sucesso!', 'success')
        
        # Redireciona para o mês da transação
        data_obj = datetime.strptime(data, "%Y-%m-%d")
        return redirect(url_for('dashboard.index', mes=data_obj.month, ano=data_obj.year))

@transactions_bp.route('/delete/<int:transaction_id>', methods=['POST'])
@login_required
def delete_transaction(transaction_id):
    """Exclui uma transação"""
    transaction = Transaction.query.filter_by(id=transaction_id, user_id=current_user.id).first()
    
    if transaction:
        data = transaction.data
        db_session.delete(transaction)
        db_session.commit()
        
        flash('Transação excluída com sucesso!', 'success')
        
        # Redireciona para o mês da transação
        data_obj = datetime.strptime(data, "%Y-%m-%d")
        return redirect(url_for('dashboard.index', mes=data_obj.month, ano=data_obj.year))
    
    flash('Transação não encontrada.', 'danger')
    return redirect(url_for('dashboard.index'))

@transactions_bp.route('/toggle_paid/<int:transaction_id>', methods=['POST'])
@login_required
def toggle_paid_status(transaction_id):
    """Altera o status de pagamento de uma transação"""
    transaction = Transaction.query.filter_by(id=transaction_id, user_id=current_user.id).first()
    
    if transaction and transaction.tipo == 'despesa':
        # Inverte o status de pagamento
        transaction.pago = not transaction.pago
        db_session.commit()
        
        status_text = 'paga' if transaction.pago else 'não paga'
        flash(f'Despesa marcada como {status_text}.', 'success')
        
        # Redireciona para o mês da transação
        data_obj = datetime.strptime(transaction.data, "%Y-%m-%d")
        return redirect(url_for('dashboard.index', mes=data_obj.month, ano=data_obj.year))
    
    elif transaction and transaction.tipo == 'receita':
        flash('Não é possível alterar o status de pagamento de receitas.', 'warning')
        
        # Redireciona para o mês da transação
        data_obj = datetime.strptime(transaction.data, "%Y-%m-%d")
        return redirect(url_for('dashboard.index', mes=data_obj.month, ano=data_obj.year))
    
    flash('Transação não encontrada.', 'danger')
    return redirect(url_for('dashboard.index'))

@transactions_bp.route('/search', methods=['GET'])
@login_required
def search_transactions():
    """Busca e filtra transações"""
    # Parâmetros de busca
    query = request.args.get('query', '')
    categoria = request.args.get('categoria', '')
    tipo = request.args.get('tipo', '')
    status = request.args.get('status', '')
    data_inicio = request.args.get('data_inicio', '')
    data_fim = request.args.get('data_fim', '')
    valor_min = request.args.get('valor_min', '')
    valor_max = request.args.get('valor_max', '')
    
    # Inicia a consulta base
    transactions_query = Transaction.query.filter_by(user_id=current_user.id)
    
    # Aplica os filtros
    if query:
        transactions_query = transactions_query.filter(Transaction.descricao.ilike(f'%{query}%'))
    
    if categoria and categoria != 'todas':
        transactions_query = transactions_query.filter(Transaction.categoria_id == categoria)
    
    if tipo and tipo != 'todos':
        transactions_query = transactions_query.filter(Transaction.tipo == tipo)
    
    if status:
        if status == 'pago':
            transactions_query = transactions_query.filter(Transaction.pago == True)
        elif status == 'nao_pago':
            transactions_query = transactions_query.filter(Transaction.pago == False)
    
    if data_inicio:
        transactions_query = transactions_query.filter(Transaction.data >= data_inicio)
    
    if data_fim:
        transactions_query = transactions_query.filter(Transaction.data <= data_fim)
    
    if valor_min:
        try:
            valor_min_float = float(valor_min)
            transactions_query = transactions_query.filter(Transaction.valor >= valor_min_float)
        except ValueError:
            pass
    
    if valor_max:
        try:
            valor_max_float = float(valor_max)
            transactions_query = transactions_query.filter(Transaction.valor <= valor_max_float)
        except ValueError:
            pass
    
    # Executa a consulta e ordena por data
    transactions = transactions_query.order_by(Transaction.data.desc()).all()
    
    # Converte para dicionário para retorno JSON
    transactions_list = [t.to_dict() for t in transactions]
    
    # Se for uma requisição AJAX, retorna JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'transactions': transactions_list,
            'count': len(transactions_list)
        })
    
    # Caso contrário, renderiza a página de resultados
    return render_template(
        'dashboard/search_results.html',
        transactions=transactions,
        query=query,
        categoria=categoria,
        tipo=tipo,
        status=status,
        data_inicio=data_inicio,
        data_fim=data_fim,
        valor_min=valor_min,
        valor_max=valor_max,
        categories=Category.query.filter_by(user_id=current_user.id).all()
    )
