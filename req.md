<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - Sistema Financeiro</title>
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Font Awesome -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <!-- FullCalendar -->
    <link href="https://cdn.jsdelivr.net/npm/fullcalendar@5.11.3/main.min.css" rel="stylesheet">
    <!-- DataTables -->
    <link href="https://cdn.datatables.net/1.13.4/css/dataTables.bootstrap5.min.css" rel="stylesheet">
    <!-- SweetAlert2 -->
    <link href="https://cdn.jsdelivr.net/npm/sweetalert2@11.7.5/dist/sweetalert2.min.css" rel="stylesheet">
    <!-- Custom CSS -->
    <link rel="stylesheet" href="{{ url_for('static', filename='css/dashboard.css') }}">
</head>
<body>
    <!-- Navbar -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary sticky-top">
        <div class="container-fluid">
            <a class="navbar-brand" href="{{ url_for('dashboard.index') }}">
                <i class="fas fa-wallet me-2"></i>Sistema Financeiro
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav me-auto">
                    <li class="nav-item">
                        <a class="nav-link active" href="{{ url_for('dashboard.index') }}">
                            <i class="fas fa-chart-pie me-1"></i>Dashboard
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="#" data-bs-toggle="modal" data-bs-target="#searchModal">
                            <i class="fas fa-search me-1"></i>Busca Avançada
                        </a>
                    </li>
                </ul>
                <ul class="navbar-nav">
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle" href="#" id="alertsDropdown" role="button" data-bs-toggle="dropdown" aria-expanded="false">
                            <i class="fas fa-bell me-1"></i>
                            <span class="badge bg-danger" id="alerts-badge" style="display: none;">0</span>
                        </a>
                        <ul class="dropdown-menu dropdown-menu-end" aria-labelledby="alertsDropdown" id="alerts-dropdown">
                            <li><h6 class="dropdown-header">Alertas de Vencimento</h6></li>
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="dropdown-item text-center" id="no-alerts">Nenhum alerta no momento</a></li>
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="dropdown-item text-center" href="{{ url_for('alerts.send_email_alerts') }}">Enviar alertas por e-mail</a></li>
                        </ul>
                    </li>
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle" href="#" id="userDropdown" role="button" data-bs-toggle="dropdown" aria-expanded="false">
                            <i class="fas fa-user-circle me-1"></i>{{ current_user.username }}
                        </a>
                        <ul class="dropdown-menu dropdown-menu-end" aria-labelledby="userDropdown">
                            <li><a class="dropdown-item" href="#"><i class="fas fa-cog me-2"></i>Configurações</a></li>
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="dropdown-item" href="{{ url_for('auth.logout') }}"><i class="fas fa-sign-out-alt me-2"></i>Sair</a></li>
                        </ul>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <!-- Conteúdo Principal -->
    <div class="container-fluid py-4">
        <!-- Mensagens Flash -->
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }} alert-dismissible fade show" role="alert">
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}

        <!-- Filtro de Mês/Ano -->
        <div class="card shadow-sm mb-4">
            <div class="card-body">
                <form action="{{ url_for('dashboard.index') }}" method="get" class="row g-3 align-items-center">
                    <div class="col-md-4">
                        <label for="mes" class="form-label">Mês</label>
                        <select class="form-select" id="mes" name="mes">
                            <option value="1" {% if selected_month == 1 %}selected{% endif %}>Janeiro</option>
                            <option value="2" {% if selected_month == 2 %}selected{% endif %}>Fevereiro</option>
                            <option value="3" {% if selected_month == 3 %}selected{% endif %}>Março</option>
                            <option value="4" {% if selected_month == 4 %}selected{% endif %}>Abril</option>
                            <option value="5" {% if selected_month == 5 %}selected{% endif %}>Maio</option>
                            <option value="6" {% if selected_month == 6 %}selected{% endif %}>Junho</option>
                            <option value="7" {% if selected_month == 7 %}selected{% endif %}>Julho</option>
                            <option value="8" {% if selected_month == 8 %}selected{% endif %}>Agosto</option>
                            <option value="9" {% if selected_month == 9 %}selected{% endif %}>Setembro</option>
                            <option value="10" {% if selected_month == 10 %}selected{% endif %}>Outubro</option>
                            <option value="11" {% if selected_month == 11 %}selected{% endif %}>Novembro</option>
                            <option value="12" {% if selected_month == 12 %}selected{% endif %}>Dezembro</option>
                        </select>
                    </div>
                    <div class="col-md-4">
                        <label for="ano" class="form-label">Ano</label>
                        <select class="form-select" id="ano" name="ano">
                            {% for year in available_years %}
                                <option value="{{ year }}" {% if selected_year == year %}selected{% endif %}>{{ year }}</option>
                            {% endfor %}
                        </select>
                    </div>
                    <div class="col-md-4 d-flex align-items-end">
                        <button type="submit" class="btn btn-primary w-100">
                            <i class="fas fa-filter me-2"></i>Filtrar
                        </button>
                    </div>
                </form>
            </div>
        </div>

        <!-- Cards de Resumo -->
        <div class="row mb-4">
            <div class="col-md-3">
                <div class="card shadow-sm h-100 border-left-primary">
                    <div class="card-body">
                        <div class="row no-gutters align-items-center">
                            <div class="col mr-2">
                                <div class="text-xs font-weight-bold text-primary text-uppercase mb-1">Receitas</div>
                                <div class="h5 mb-0 font-weight-bold text-gray-800">R$ {{ "%.2f"|format(total_receitas) }}</div>
                            </div>
                            <div class="col-auto">
                                <i class="fas fa-money-bill-wave fa-2x text-gray-300"></i>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card shadow-sm h-100 border-left-danger">
                    <div class="card-body">
                        <div class="row no-gutters align-items-center">
                            <div class="col mr-2">
                                <div class="text-xs font-weight-bold text-danger text-uppercase mb-1">Despesas Totais</div>
                                <div class="h5 mb-0 font-weight-bold text-gray-800">R$ {{ "%.2f"|format(total_despesas) }}</div>
                            </div>
                            <div class="col-auto">
                                <i class="fas fa-credit-card fa-2x text-gray-300"></i>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card shadow-sm h-100 border-left-warning">
                    <div class="card-body">
                        <div class="row no-gutters align-items-center">
                            <div class="col mr-2">
                                <div class="text-xs font-weight-bold text-warning text-uppercase mb-1">Despesas Pendentes</div>
                                <div class="h5 mb-0 font-weight-bold text-gray-800">R$ {{ "%.2f"|format(total_despesas_pendentes) }}</div>
                            </div>
                            <div class="col-auto">
                                <i class="fas fa-clock fa-2x text-gray-300"></i>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card shadow-sm h-100 border-left-success">
                    <div class="card-body">
                        <div class="row no-gutters align-items-center">
                            <div class="col mr-2">
                                <div class="text-xs font-weight-bold text-success text-uppercase mb-1">Saldo do Mês</div>
                                <div class="h5 mb-0 font-weight-bold text-gray-800">R$ {{ "%.2f"|format(saldo_mes) }}</div>
                            </div>
                            <div class="col-auto">
                                <i class="fas fa-wallet fa-2x text-gray-300"></i>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Gráficos e Calendário -->
        <div class="row mb-4">
            <!-- Gráficos -->
            <div class="col-lg-6">
                <div class="card shadow-sm mb-4">
                    <div class="card-header py-3 d-flex flex-row align-items-center justify-content-between">
                        <h6 class="m-0 font-weight-bold">Receitas x Despesas</h6>
                    </div>
                    <div class="card-body">
                        <div class="chart-container">
                            <canvas id="barChart"></canvas>
                        </div>
                    </div>
                </div>
                <div class="row">
                    <div class="col-md-6">
                        <div class="card shadow-sm mb-4">
                            <div class="card-header py-3 d-flex flex-row align-items-center justify-content-between">
                                <h6 class="m-0 font-weight-bold">Despesas por Categoria</h6>
                            </div>
                            <div class="card-body">
                                <div class="chart-container">
                                    <canvas id="expenseChart"></canvas>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="card shadow-sm mb-4">
                            <div class="card-header py-3 d-flex flex-row align-items-center justify-content-between">
                                <h6 class="m-0 font-weight-bold">Receitas por Categoria</h6>
                            </div>
                            <div class="card-body">
                                <div class="chart-container">
                                    <canvas id="incomeChart"></canvas>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Calendário -->
            <div class="col-lg-6">
                <div class="card shadow-sm">
                    <div class="card-header py-3 d-flex flex-row align-items-center justify-content-between">
                        <h6 class="m-0 font-weight-bold">Calendário Financeiro</h6>
                    </div>
                    <div class="card-body">
                        <div id="calendar"></div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Formulário de Nova Transação e Lista de Transações -->
        <div class="row">
            <!-- Formulário de Nova Transação -->
            <div class="col-lg-4">
                <div class="card shadow-sm mb-4">
                    <div class="card-header py-3">
                        <h6 class="m-0 font-weight-bold">Nova Transação</h6>
                    </div>
                    <div class="card-body">
                        <form id="form-transacao" action="{{ url_for("transactions.add", mes=selected_month, ano=selected_year) }}" method="post">               <div class="mb-3">
                                <label class="form-label">Tipo:</label>
                                <div class="form-check form-check-inline">
                                    <input class="form-check-input" type="radio" id="tipo-receita" name="tipo" value="receita" checked>
                                    <label class="form-check-label" for="tipo-receita">Receita</label>
                                </div>
                                <div class="form-check form-check-inline">
                                    <input class="form-check-input" type="radio" id="tipo-despesa" name="tipo" value="despesa">
                                    <label class="form-check-label" for="tipo-despesa">Despesa</label>
                                </div>
                            </div>
                            <div class="mb-3">
                                <label for="valor" class="form-label">Valor (R$):</label>
                                <input type="number" class="form-control" id="valor" name="valor" step="0.01" required>
                            </div>
                            <div class="mb-3">
                                <label for="data" class="form-label">Data:</label>
                                <input type="date" class="form-control" id="data" name="data" required value="{{ today_date }}">
                            </div>
                            <div class="mb-3" id="vencimento-group" style="display: none;">
                                <label for="vencimento" class="form-label">Data de Vencimento:</label>
                                <input type="date" class="form-control" id="vencimento" name="vencimento" value="{{ today_date }}">
                            </div>
                            <div class="mb-3">
                                <label for="descricao" class="form-label">Descrição:</label>
                                <input type="text" class="form-control" id="descricao" name="descricao" required>
                            </div>
                            <div class="mb-3">
                                <label for="categoria" class="form-label">Categoria:</label>
                                <select class="form-select" id="categoria" name="categoria" required>
                                    <optgroup label="Receitas" id="receitas-group">
                                        {% for category in categories %}
                                            {% if category.tipo == 'receita' %}
                                                <option value="{{ category.id }}" data-icon="{{ category.icone }}">{{ category.nome }}</option>
                                            {% endif %}
                                        {% endfor %}
                                    </optgroup>
                                    <optgroup label="Despesas" id="despesas-group" style="display: none;">
                                        {% for category in categories %}
                                            {% if category.tipo == 'despesa' %}
                                                <option value="{{ category.id }}" data-icon="{{ category.icone }}">{{ category.nome }}</option>
                                            {% endif %}
                                        {% endfor %}
                                    </optgroup>
                                </select>
                            </div>
                            <div class="d-grid">
                                <button type="submit" class="btn btn-primary">
                                    <i class="fas fa-plus-circle me-2"></i>Adicionar Transação
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
            
            <!-- Lista de Transações -->
            <div class="col-lg-8">
                <div class="card shadow-sm mb-4">
                    <div class="card-header py-3 d-flex flex-row align-items-center justify-content-between">
                        <h6 class="m-0 font-weight-bold">Transações de {{ selected_month_str }}/{{ selected_year }}</h6>
                    </div>
                    <div class="card-body">
                        <div class="table-responsive">
                            <table class="table table-hover" id="transactionsTable">
                                <thead>
                                    <tr>
                                        <th>Descrição</th>
                                        <th>Categoria</th>
                                        <th>Data</th>
                                        <th>Valor</th>
                                        <th>Status</th>
                                        <th>Ações</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {% for transaction in transactions %}
                                        <tr class="{% if transaction.tipo == 'receita' %}table-success{% elif transaction.tipo == 'despesa' and transaction.pago %}table-info{% elif transaction.tipo == 'despesa' and not transaction.pago %}table-warning{% endif %}">
                                            <td>{{ transaction.descricao }}</td>
                                            <td>
                                                <i class="fas {{ transaction.categoria.icone }}" style="color: {{ transaction.categoria.cor }}"></i>
                                                {{ transaction.categoria.nome }}
                                            </td>
                                            <td>{{ transaction.data }}</td>
                                            <td>R$ {{ "%.2f"|format(transaction.valor) }}</td>
                                            <td>
                                                {% if transaction.tipo == 'receita' %}
                                                    <span class="badge bg-success">Receita</span>
                                                {% elif transaction.tipo == 'despesa' and transaction.pago %}
                                                    <span class="badge bg-info">Paga</span>
                                                {% elif transaction.tipo == 'despesa' and not transaction.pago %}
                                                    <span class="badge bg-warning text-dark">Pendente</span>
                                                {% endif %}
                                            </td>
                                            <td>
                                                <div class="btn-group" role="group">
                                                    {% if transaction.tipo == 'despesa' %}
                                                        <form action="{{ url_for('transactions.toggle_paid_status', transaction_id=transaction.id) }}" method="post" style="display: inline;">
                                                            <button type="submit" class="btn btn-sm {% if transaction.pago %}btn-warning{% else %}btn-info{% endif %}" title="{{ 'Marcar como não paga' if transaction.pago else 'Marcar como paga' }}">
                                                                <i class="fas {% if transaction.pago %}fa-times-circle{% else %}fa-check-circle{% endif %}"></i>
                                                            </button>
                                                        </form>
                                                    {% endif %}
                                                    <form action="{{ url_for('transactions.delete_transaction', transaction_id=transaction.id) }}" method="post" style="display: inline;" onsubmit="return confirm('Tem certeza que deseja excluir esta transação?');">
                                                        <button type="submit" class="btn btn-sm btn-danger" title="Excluir">
                                                            <i class="fas fa-trash"></i>
                                                        </button>
                                                    </form>
                                                </div>
                                            </td>
                                        </tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Modal de Busca Avançada -->
    <div class="modal fade" id="searchModal" tabindex="-1" aria-labelledby="searchModalLabel" aria-hidden="true">
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="searchModalLabel">Busca Avançada</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <form id="searchForm" action="{{ url_for('transactions.search_transactions') }}" method="get">
                        <div class="row mb-3">
                            <div class="col-md-12">
                                <label for="query" class="form-label">Descrição:</label>
                                <input type="text" class="form-control" id="query" name="query" placeholder="Buscar por descrição...">
                            </div>
                        </div>
                        <div class="row mb-3">
                            <div class="col-md-4">
                                <label for="categoria" class="form-label">Categoria:</label>
                                <select class="form-select" id="search-categoria" name="categoria">
                                    <option value="todas">Todas</option>
                                    <optgroup label="Receitas">
                                        {% for category in categories %}
                                            {% if category.tipo == 'receita' %}
                                                <option value="{{ category.id }}">{{ category.nome }}</option>
                                            {% endif %}
                                        {% endfor %}
                                    </optgroup>
                                    <optgroup label="Despesas">
                                        {% for category in categories %}
                                            {% if category.tipo == 'despesa' %}
                                                <option value="{{ category.id }}">{{ category.nome }}</option>
                                            {% endif %}
                                        {% endfor %}
                                    </optgroup>
                                </select>
                            </div>
                            <div class="col-md-4">
                                <label for="tipo" class="form-label">Tipo:</label>
                                <select class="form-select" id="tipo" name="tipo">
                                    <option value="todos">Todos</option>
                                    <option value="receita">Receitas</option>
                                    <option value="despesa">Despesas</option>
                                </select>
                            </div>
                            <div class="col-md-4">
                                <label for="status" class="form-label">Status:</label>
                                <select class="form-select" id="status" name="status">
                                    <option value="">Todos</option>
                                    <option value="pago">Pagas</option>
                                    <option value="nao_pago">Não Pagas</option>
                                </select>
                            </div>
                        </div>
                        <div class="row mb-3">
                            <div class="col-md-6">
                                <label for="data_inicio" class="form-label">Data Início:</label>
                                <input type="date" class="form-control" id="data_inicio" name="data_inicio">
                            </div>
                            <div class="col-md-6">
                                <label for="data_fim" class="form-label">Data Fim:</label>
                                <input type="date" class="form-control" id="data_fim" name="data_fim">
                            </div>
                        </div>
                        <div class="row mb-3">
                            <div class="col-md-6">
                                <label for="valor_min" class="form-label">Valor Mínimo:</label>
                                <input type="number" class="form-control" id="valor_min" name="valor_min" step="0.01">
                            </div>
                            <div class="col-md-6">
                                <label for="valor_max" class="form-label">Valor Máximo:</label>
                                <input type="number" class="form-control" id="valor_max" name="valor_max" step="0.01">
                            </div>
                        </div>
                    </form>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Fechar</button>
                    <button type="submit" form="searchForm" class="btn btn-primary">Buscar</button>
                </div>
            </div>
        </div>
    </div>

    <!-- Modal de Detalhes da Transação (Calendário) -->
    <div class="modal fade" id="transactionModal" tabindex="-1" aria-labelledby="transactionModalLabel" aria-hidden="true">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="transactionModalLabel">Detalhes da Transação</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body" id="transactionModalBody">
                    <!-- Conteúdo preenchido via JavaScript -->
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Fechar</button>
                    <button type="button" class="btn btn-danger" id="deleteTransactionBtn">Excluir</button>
                    <button type="button" class="btn btn-info" id="togglePaidBtn">Alterar Status</button>
                </div>
            </div>
        </div>
    </div>

    <!-- Scripts -->
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/fullcalendar@5.11.3/main.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/fullcalendar@5.11.3/locales-all.min.js"></script>
    <script src="https://cdn.datatables.net/1.13.4/js/jquery.dataTables.min.js"></script>
    <script src="https://cdn.datatables.net/1.13.4/js/dataTables.bootstrap5.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11.7.5/dist/sweetalert2.all.min.js"></script>
    
    <script>
        // Inicialização do DataTables
        $(document).ready(function() {
            $('#transactionsTable').DataTable({
                language: {
                    url: '//cdn.datatables.net/plug-ins/1.13.4/i18n/pt-BR.json'
                },
                order: [[2, 'desc']], // Ordena por data (coluna 2) decrescente
                responsive: true
            });
            
            // Alterna entre categorias de receita e despesa
            $('input[name="tipo"]').change(function() {
                if ($(this).val() === 'receita') {
                    $('#receitas-group').show();
                    $('#despesas-group').hide();
                    $('#vencimento-group').hide();
                    // Seleciona a primeira opção de receita
                    $('#categoria').val($('#receitas-group option:first').val());
                } else {
                    $('#receitas-group').hide();
                    $('#despesas-group').show();
                    $('#vencimento-group').show();
                    // Seleciona a primeira opção de despesa
                    $('#categoria').val($('#despesas-group option:first').val());
                }
            });
            
            // Verifica alertas ao carregar a página
            checkAlerts();
        });
        
        // Gráficos
        fetch('{{ url_for("dashboard.chart_data", mes=selected_month, ano=selected_year) }}')
            .then(response => response.json())
            .then(data => {
                // Gráfico de barras (Receitas x Despesas)
                const barCtx = document.getElementById('barChart').getContext('2d');
                new Chart(barCtx, {
                    type: 'bar',
                    data: {
                        labels: data.bar_chart.labels,
                        datasets: [{
                            label: 'Valor (R$)',
                            data: data.bar_chart.datasets[0].data,
                            backgroundColor: data.bar_chart.datasets[0].backgroundColor,
                            borderColor: data.bar_chart.datasets[0].backgroundColor,
                            borderWidth: 1
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                display: false
                            },
                            tooltip: {
                                callbacks: {
                                    label: function(context) {
                                        return `R$ ${context.raw.toFixed(2)}`;
                                    }
                                }
                            }
                        },
                        scales: {
                            y: {
                                beginAtZero: true,
                                ticks: {
                                    callback: function(value) {
                                        return `R$ ${value.toFixed(2)}`;
                                    }
                                }
                            }
                        }
                    }
                });
                
                // Gráfico de pizza (Despesas por Categoria)
                const expenseCtx = document.getElementById('expenseChart').getContext('2d');
                new Chart(expenseCtx, {
                    type: 'pie',
                    data: {
                        labels: data.expense_chart.map(item => item.name),
                        datasets: [{
                            data: data.expense_chart.map(item => item.value),
                            backgroundColor: data.expense_chart.map(item => item.color),
                            borderWidth: 1
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                position: 'bottom',
                                labels: {
                                    boxWidth: 12
                                }
                            },
                            tooltip: {
                                callbacks: {
                                    label: function(context) {
                                        const label = context.label || '';
                                        const value = context.raw || 0;
                                        const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                        const percentage = Math.round((value / total) * 100);
                                        return `${label}: R$ ${value.toFixed(2)} (${percentage}%)`;
                                    }
                                }
                            }
                        }
                    }
                });
                
                // Gráfico de pizza (Receitas por Categoria)
                const incomeCtx = document.getElementById('incomeChart').getContext('2d');
                new Chart(incomeCtx, {
                    type: 'pie',
                    data: {
                        labels: data.income_chart.map(item => item.name),
                        datasets: [{
                            data: data.income_chart.map(item => item.value),
                            backgroundColor: data.income_chart.map(item => item.color),
                            borderWidth: 1
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                position: 'bottom',
                                labels: {
                                    boxWidth: 12
                                }
                            },
                            tooltip: {
                                callbacks: {
                                    label: function(context) {
                                        const label = context.label || '';
                                        const value = context.raw || 0;
                                        const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                        const percentage = Math.round((value / total) * 100);
                                        return `${label}: R$ ${value.toFixed(2)} (${percentage}%)`;
                                    }
                                }
                            }
                        }
                    }
                });
            });
        
        // Calendário
        document.addEventListener('DOMContentLoaded', function() {
            const calendarEl = document.getElementById('calendar');
            const calendar = new FullCalendar.Calendar(calendarEl, {
                initialView: 'dayGridMonth',
                locale: 'pt-br',
                headerToolbar: {
                    left: 'prev,next today',
                    center: 'title',
                    right: 'dayGridMonth,listMonth'
                },
                events: {{ calendar_data|tojson }},
                eventClick: function(info) {
                    const event = info.event;
                    const props = event.extendedProps;
                    
                    // Preenche o modal com os detalhes da transação
                    let modalContent = `
                        <div class="transaction-details">
                            <div class="mb-3">
                                <h5><i class="fas ${props.icon}" style="color: ${event.backgroundColor}"></i> ${event.title}</h5>
                            </div>
                            <div class="mb-2">
                                <strong>Tipo:</strong> ${props.tipo === 'receita' ? 'Receita' : 'Despesa'}
                            </div>
                            <div class="mb-2">
                                <strong>Valor:</strong> R$ ${props.valor.toFixed(2)}
                            </div>
                            <div class="mb-2">
                                <strong>Data:</strong> ${event.start.toLocaleDateString('pt-BR')}
                            </div>
                            <div class="mb-2">
                                <strong>Categoria:</strong> ${props.categoria}
                            </div>`;
                    
                    if (props.tipo === 'despesa') {
                        modalContent += `
                            <div class="mb-2">
                                <strong>Status:</strong> ${props.pago ? 'Paga' : 'Não Paga'}
                            </div>`;
                    }
                    
                    modalContent += `</div>`;
                    
                    document.getElementById('transactionModalBody').innerHTML = modalContent;
                    
                    // Configura os botões de ação
                    const deleteBtn = document.getElementById('deleteTransactionBtn');
                    const toggleBtn = document.getElementById('togglePaidBtn');
                    
                    deleteBtn.onclick = function() {
                        if (confirm('Tem certeza que deseja excluir esta transação?')) {
                            const form = document.createElement('form');
                            form.method = 'POST';
                            form.action = `/transactions/delete/${event.id}`;
                            document.body.appendChild(form);
                            form.submit();
                        }
                    };
                    
                    if (props.tipo === 'despesa') {
                        toggleBtn.style.display = 'block';
                        toggleBtn.textContent = props.pago ? 'Marcar como Não Paga' : 'Marcar como Paga';
                        toggleBtn.onclick = function() {
                            const form = document.createElement('form');
                            form.method = 'POST';
                            form.action = `/transactions/toggle_paid/${event.id}`;
                            document.body.appendChild(form);
                            form.submit();
                        };
                    } else {
                        toggleBtn.style.display = 'none';
                    }
                    
                    // Abre o modal
                    const transactionModal = new bootstrap.Modal(document.getElementById('transactionModal'));
                    transactionModal.show();
                }
            });
            calendar.render();
        });
        
        // Verificação de alertas
        function checkAlerts() {
            fetch('{{ url_for("alerts.check_alerts") }}')
                .then(response => response.json())
                .then(data => {
                    const alertsCount = data.alerts.length;
                    const alertsBadge = document.getElementById('alerts-badge');
                    const alertsDropdown = document.getElementById('alerts-dropdown');
                    const noAlerts = document.getElementById('no-alerts');
                    
                    if (alertsCount > 0) {
                        // Atualiza o badge
                        alertsBadge.textContent = alertsCount;
                        alertsBadge.style.display = 'inline-block';
                        
                        // Limpa o dropdown
                        noAlerts.style.display = 'none';
                        
                        // Adiciona os alertas ao dropdown
                        data.alerts.forEach(alert => {
                            const li = document.createElement('li');
                            const a = document.createElement('a');
                            a.className = 'dropdown-item';
                            a.href = '#';
                            
                            const vencimento = new Date(alert.vencimento);
                            const hoje = new Date();
                            const diffDias = Math.ceil((vencimento - hoje) / (1000 * 60 * 60 * 24));
                            
                            a.innerHTML = `
                                <div class="d-flex w-100 justify-content-between">
                                    <h6 class="mb-1">${alert.descricao}</h6>
                                    <small class="text-danger">Vence em ${diffDias} dia(s)</small>
                                </div>
                                <p class="mb-1">R$ ${alert.valor.toFixed(2)}</p>
                                <small>${alert.categoria}</small>
                            `;
                            
                            a.onclick = function() {
                                // Marca o alerta como visualizado
                                fetch(`/alerts/dismiss/${alert.id}`, {
                                    method: 'POST'
                                });
                                
                                // Exibe detalhes da transação
                                Swal.fire({
                                    title: 'Despesa Próxima do Vencimento',
                                    html: `
                                        <div class="text-start">
                                            <p><strong>Descrição:</strong> ${alert.descricao}</p>
                                            <p><strong>Valor:</strong> R$ ${alert.valor.toFixed(2)}</p>
                                            <p><strong>Vencimento:</strong> ${new Date(alert.vencimento).toLocaleDateString('pt-BR')}</p>
                                            <p><strong>Categoria:</strong> ${alert.categoria}</p>
                                        </div>
                                    `,
                                    icon: 'warning',
                                    showCancelButton: true,
                                    confirmButtonText: 'Marcar como Paga',
                                    cancelButtonText: 'Fechar'
                                }).then((result) => {
                                    if (result.isConfirmed) {
                                        const form = document.createElement('form');
                                        form.method = 'POST';
                                        form.action = `/transactions/toggle_paid/${alert.id}`;
                                        document.body.appendChild(form);
                                        form.submit();
                                    }
                                });
                            };
                            
                            li.appendChild(a);
                            alertsDropdown.insertBefore(li, alertsDropdown.querySelector('hr'));
                        });
                        
                        // Notifica o usuário
                        Swal.fire({
                            title: 'Alertas de Vencimento',
                            text: `Você tem ${alertsCount} despesa(s) próxima(s) do vencimento!`,
                            icon: 'warning',
                            confirmButtonText: 'Ver Detalhes'
                        });
                    } else {
                        alertsBadge.style.display = 'none';
                        noAlerts.style.display = 'block';
                    }
                });
        }
    </script>
</body>
</html>
