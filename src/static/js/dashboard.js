document.addEventListener('DOMContentLoaded', function() {
    // Variável para controlar se os event listeners já foram registrados
    let eventListenersRegistered = false;

    // Função para formatar valor em moeda brasileira
    function formatCurrency(value) {
        if (value === null || value === undefined || value === '') return 'R$ 0,00';

        const numValue = typeof value === 'string' ? parseFloat(value.replace(',', '.')) : value;
        if (isNaN(numValue)) return 'R$ 0,00';

        return new Intl.NumberFormat('pt-BR', {
            style: 'currency',
            currency: 'BRL'
        }).format(numValue);
    }

    // Função para processar entrada de valor (aceita vírgula como decimal)
    function processCurrencyInput(inputValue) {
        if (!inputValue) return '';

        // Remove tudo exceto números, vírgula e ponto
        let cleaned = inputValue.replace(/[^\d.,]/g, '');

        // Se tem vírgula, usa como separador decimal
        if (cleaned.includes(',')) {
            // Remove pontos (milhares) e mantém apenas a vírgula
            cleaned = cleaned.replace(/\./g, '').replace(',', '.');
        }

        return cleaned;
    }

    // Aplicar formatação em campos de valor existentes na página
    function formatExistingValues() {
        // Formatar valores nas tabelas
        document.querySelectorAll('.currency-value').forEach(element => {
            const value = element.textContent || element.innerText;
            if (value && !value.includes('R$')) {
                element.textContent = formatCurrency(value);
            }
        });

        // Formatar valores nos cards de resumo
        document.querySelectorAll('[data-currency]').forEach(element => {
            const value = element.getAttribute('data-currency');
            if (value) {
                element.textContent = formatCurrency(value);
            }
        });
    }

    // Configurar campos de entrada de valor
    function setupCurrencyInputs() {
        const valorInputs = document.querySelectorAll('input[name="valor"], #valor, #edit-valor');

        valorInputs.forEach(input => {
            // Remover listeners existentes para evitar duplicação
            input.removeEventListener('input', handleCurrencyInput);
            input.removeEventListener('blur', handleCurrencyBlur);
            input.removeEventListener('focus', handleCurrencyFocus);

            // Adicionar listeners
            input.addEventListener('input', handleCurrencyInput);
            input.addEventListener('blur', handleCurrencyBlur);
            input.addEventListener('focus', handleCurrencyFocus);

            // Formatar valor inicial se existir
            if (input.value) {
                input.value = formatCurrency(processCurrencyInput(input.value));
            }
        });
    }

    // Handlers para os eventos de input e blur
    function handleCurrencyInput(event) {
        const input = event.target;
        const caretPos = input.selectionStart;
        const oldValue = input.value;

        let cleaned = processCurrencyInput(oldValue);
        input.value = cleaned;

        // Ajustar a posição do cursor
        const newCaretPos = caretPos - (oldValue.length - cleaned.length);
        input.setSelectionRange(newCaretPos, newCaretPos);
    }

    function handleCurrencyBlur(event) {
        const input = event.target;
        input.value = formatCurrency(processCurrencyInput(input.value));
    }

    function handleCurrencyFocus(event) {
        const input = event.target;
        input.value = processCurrencyInput(input.value);
    }

    // Função para carregar dados do dashboard via AJAX
    function loadDashboardData(month, year) {
        const url = `/dashboard_data?month=${month}&year=${year}`;
        fetch(url)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                updateDashboardUI(data);
                updateCharts(data);
                updateCalendar(data);
                formatExistingValues(); // Reaplicar formatação após carregar novos dados
                setupCurrencyInputs(); // Reconfigurar inputs após carregar novos dados
            })
            .catch(error => {
                console.error('Erro ao carregar dados do dashboard:', error);
                Swal.fire({
                    icon: 'error',
                    title: 'Erro',
                    text: 'Não foi possível carregar os dados do dashboard. Tente novamente mais tarde.'
                });
            });
    }

    // Função para atualizar a UI do dashboard
    function updateDashboardUI(data) {
        document.getElementById('total-receitas').textContent = formatCurrency(data.total_receitas);
        document.getElementById('total-despesas').textContent = formatCurrency(data.total_despesas);
        document.getElementById('total-pendencias').textContent = formatCurrency(data.total_pendencias);
        document.getElementById('saldo-atual').textContent = formatCurrency(data.saldo_atual);

        // Atualizar tabela de transações
        const transactionsTableBody = document.getElementById('transactions-table-body');
        transactionsTableBody.innerHTML = ''; // Limpar tabela existente
        data.transactions.forEach(transaction => {
            const row = transactionsTableBody.insertRow();
            row.innerHTML = `
                <td>${transaction.data}</td>
                <td>${transaction.descricao}</td>
                <td>${transaction.categoria}</td>
                <td class="currency-value">${formatCurrency(transaction.valor)}</td>
                <td>${transaction.tipo === 'receita' ? 'Receita' : 'Despesa'}</td>
                <td>${transaction.status}</td>
                <td>
                    <button class="btn btn-sm btn-primary edit-btn" data-id="${transaction.id}" data-type="${transaction.tipo}">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-sm btn-danger delete-btn" data-id="${transaction.id}" data-type="${transaction.tipo}">
                        <i class="fas fa-trash"></i>
                    </button>
                    ${transaction.tipo === 'despesa' && transaction.status === 'Pendente' ?
                        `<button class="btn btn-sm btn-success mark-paid-btn" data-id="${transaction.id}">
                            <i class="fas fa-check"></i>
                        </button>` : ''}
                </td>
            `;
        });

        // Atualizar título do período
        document.getElementById('current-month-year').textContent = data.current_month_year;
    }

    // Variáveis globais para os gráficos
    let receitasDespesasChart;
    let categoriasDespesasChart;

    // Função para atualizar os gráficos
    function updateCharts(data) {
        // Gráfico de Receitas vs Despesas
        const ctxReceitasDespesas = document.getElementById('receitasDespesasChart').getContext('2d');
        if (receitasDespesasChart) {
            receitasDespesasChart.destroy();
        }
        receitasDespesasChart = new Chart(ctxReceitasDespesas, {
            type: 'bar',
            data: {
                labels: ['Receitas', 'Despesas'],
                datasets: [{
                    label: 'Valor',
                    data: [data.total_receitas, data.total_despesas],
                    backgroundColor: ['#28a745', '#dc3545'],
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return formatCurrency(value);
                            }
                        }
                    }
                },
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return formatCurrency(context.raw);
                            }
                        }
                    }
                }
            }
        });

        // Gráfico de Despesas por Categoria
        const ctxCategoriasDespesas = document.getElementById('categoriasDespesasChart').getContext('2d');
        if (categoriasDespesasChart) {
            categoriasDespesasChart.destroy();
        }
        categoriasDespesasChart = new Chart(ctxCategoriasDespesas, {
            type: 'pie',
            data: {
                labels: data.despesas_por_categoria.map(item => item.categoria),
                datasets: [{
                    data: data.despesas_por_categoria.map(item => item.valor),
                    backgroundColor: [
                        '#007bff', '#dc3545', '#ffc107', '#28a745', '#6f42c1',
                        '#20c997', '#fd7e14', '#e83e8c', '#6610f2', '#6c757d'
                    ],
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                let label = context.label || '';
                                if (label) {
                                    label += ': ';
                                }
                                label += formatCurrency(context.raw);
                                return label;
                            }
                        }
                    }
                }
            }
        });
    }

    // Variável global para o calendário
    let calendar;

    // Função para atualizar o calendário
    function updateCalendar(data) {
        const calendarEl = document.getElementById('calendar');
        if (calendar) {
            calendar.destroy();
        }
        calendar = new FullCalendar.Calendar(calendarEl, {
            initialView: 'dayGridMonth',
            locale: 'pt-br',
            headerToolbar: {
                left: 'prev,next today',
                center: 'title',
                right: 'dayGridMonth,timeGridWeek,timeGridDay'
            },
            events: data.calendar_events.map(event => ({
                title: `${event.descricao} - ${formatCurrency(event.valor)}`,
                start: event.data,
                color: event.tipo === 'receita' ? '#28a745' : '#dc3545' // Verde para receita, vermelho para despesa
            })),
            eventClick: function(info) {
                Swal.fire({
                    title: info.event.title,
                    html: `<p>Data: ${moment(info.event.start).format('DD/MM/YYYY')}</p>`,
                    icon: 'info',
                    confirmButtonText: 'Fechar'
                });
            }
        });
        calendar.render();
    }

    // Event Listeners para navegação de mês/ano
    document.getElementById('prevMonth').addEventListener('click', function() {
        const currentMonthYear = document.getElementById('current-month-year').textContent.split('/');
        let month = parseInt(currentMonthYear[0]) - 1;
        let year = parseInt(currentMonthYear[1]);
        if (month < 1) {
            month = 12;
            year--;
        }
        loadDashboardData(month, year);
    });

    document.getElementById('nextMonth').addEventListener('click', function() {
        const currentMonthYear = document.getElementById('current-month-year').textContent.split('/');
        let month = parseInt(currentMonthYear[0]) + 1;
        let year = parseInt(currentMonthYear[1]);
        if (month > 12) {
            month = 1;
            year++;
        }
        loadDashboardData(month, year);
    });

    // Event Listeners para botões de ação na tabela (editar, excluir, marcar como pago)
    document.getElementById('transactions-table-body').addEventListener('click', function(event) {
        const target = event.target;
        const button = target.closest('button');

        if (button) {
            const id = button.dataset.id;
            const type = button.dataset.type;

            if (button.classList.contains('edit-btn')) {
                // Lógica para editar transação
                fetch(`/${type}/edit/${id}`)
                    .then(response => response.json())
                    .then(data => {
                        // Preencher modal de edição com os dados da transação
                        document.getElementById('edit-id').value = data.id;
                        document.getElementById('edit-type').value = data.tipo;
                        document.getElementById('edit-descricao').value = data.descricao;
                        document.getElementById('edit-valor').value = formatCurrency(data.valor);
                        document.getElementById('edit-data').value = data.data;
                        document.getElementById('edit-categoria').value = data.categoria;
                        document.getElementById('edit-vencimento-group').style.display = data.tipo === 'despesa' ? 'block' : 'none';
                        document.getElementById('edit-vencimento').value = data.data_vencimento || '';
                        document.getElementById('edit-status-group').style.display = data.tipo === 'despesa' ? 'block' : 'none';
                        document.getElementById('edit-status').value = data.status || 'Pendente';
                        document.getElementById('edit-recorrente-group').style.display = 'none'; // Esconder para edição individual
                        document.getElementById('edit-frequencia-group').style.display = 'none';
                        document.getElementById('edit-data-final-group').style.display = 'none';

                        // Abrir modal
                        const editModal = new bootstrap.Modal(document.getElementById('editTransactionModal'));
                        editModal.show();
                    })
                    .catch(error => {
                        console.error('Erro ao carregar dados para edição:', error);
                        Swal.fire({
                            icon: 'error',
                            title: 'Erro',
                            text: 'Não foi possível carregar os dados para edição.'
                        });
                    });
            } else if (button.classList.contains('delete-btn')) {
                // Lógica para excluir transação
                Swal.fire({
                    title: 'Tem certeza?',
                    text: "Você não poderá reverter isso!",
                    icon: 'warning',
                    showCancelButton: true,
                    confirmButtonColor: '#3085d6',
                    cancelButtonColor: '#d33',
                    confirmButtonText: 'Sim, excluir!',
                    cancelButtonText: 'Cancelar'
                }).then((result) => {
                    if (result.isConfirmed) {
                        fetch(`/${type}/delete/${id}`, {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify({ id: id, tipo: type })
                        })
                        .then(response => {
                            if (!response.ok) {
                                throw new Error(`HTTP error! status: ${response.status}`);
                            }
                            return response.json();
                        })
                        .then(data => {
                            if (data.success) {
                                Swal.fire(
                                    'Excluído!',
                                    'Sua transação foi excluída.',
                                    'success'
                                );
                                // Recarregar dados do dashboard
                                const currentMonthYear = document.getElementById('current-month-year').textContent.split('/');
                                loadDashboardData(parseInt(currentMonthYear[0]), parseInt(currentMonthYear[1]));
                            } else {
                                Swal.fire(
                                    'Erro!',
                                    data.message || 'Não foi possível excluir a transação.',
                                    'error'
                                );
                            }
                        })
                        .catch(error => {
                            console.error('Erro ao excluir transação:', error);
                            Swal.fire(
                                'Erro!',
                                'Não foi possível excluir a transação. Tente novamente.',
                                'error'
                            );
                        });
                    }
                });
            } else if (button.classList.contains('mark-paid-btn')) {
                // Lógica para marcar despesa como paga
                Swal.fire({
                    title: 'Marcar como Paga?',
                    text: "Esta despesa será marcada como paga.",
                    icon: 'info',
                    showCancelButton: true,
                    confirmButtonColor: '#3085d6',
                    cancelButtonColor: '#d33',
                    confirmButtonText: 'Sim, marcar como paga!',
                    cancelButtonText: 'Cancelar'
                }).then((result) => {
                    if (result.isConfirmed) {
                        fetch(`/despesa/marcar_paga/${id}`, {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify({ id: id })
                        })
                        .then(response => {
                            if (!response.ok) {
                                throw new Error(`HTTP error! status: ${response.status}`);
                            }
                            return response.json();
                        })
                        .then(data => {
                            if (data.success) {
                                Swal.fire(
                                    'Marcada!',
                                    'Despesa marcada como paga.',
                                    'success'
                                );
                                // Recarregar dados do dashboard
                                const currentMonthYear = document.getElementById('current-month-year').textContent.split('/');
                                loadDashboardData(parseInt(currentMonthYear[0]), parseInt(currentMonthYear[1]));
                            } else {
                                Swal.fire(
                                    'Erro!',
                                    data.message || 'Não foi possível marcar a despesa como paga.',
                                    'error'
                                );
                            }
                        })
                        .catch(error => {
                            console.error('Erro ao marcar despesa como paga:', error);
                            Swal.fire(
                                'Erro!',
                                'Não foi possível marcar a despesa como paga. Tente novamente.',
                                'error'
                            );
                        });
                    }
                });
            }
        }
    });

    // Lógica para o formulário de adição/edição de transações
    document.getElementById('transactionForm').addEventListener('submit', function(event) {
        event.preventDefault();

        const form = event.target;
        const formData = new FormData(form);
        const jsonData = {};

        for (let [key, value] of formData.entries()) {
            jsonData[key] = value;
        }

        // Processar o valor antes de enviar
        jsonData['valor'] = processCurrencyInput(jsonData['valor']);

        const isEdit = jsonData['id'] !== '';
        const url = isEdit ? `/${jsonData['tipo']}/edit/${jsonData['id']}` : '/add_transaction';
        const method = 'POST';

        fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(jsonData)
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => { throw new Error(err.message || `HTTP error! status: ${response.status}`); });
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                Swal.fire({
                    icon: 'success',
                    title: 'Sucesso!',
                    text: data.message
                });
                // Fechar modal e recarregar dados
                const modalElement = document.getElementById('addTransactionModal') || document.getElementById('editTransactionModal');
                const modal = bootstrap.Modal.getInstance(modalElement);
                if (modal) {
                    modal.hide();
                }
                form.reset();
                const currentMonthYear = document.getElementById('current-month-year').textContent.split('/');
                loadDashboardData(parseInt(currentMonthYear[0]), parseInt(currentMonthYear[1]));
            } else {
                Swal.fire({
                    icon: 'error',
                    title: 'Erro!',
                    text: data.message || 'Ocorreu um erro ao salvar a transação.'
                });
            }
        })
        .catch(error => {
            console.error('Erro ao salvar transação:', error);
            Swal.fire({
                icon: 'error',
                title: 'Erro!',
                text: error.message || 'Não foi possível salvar a transação. Verifique os dados e tente novamente.'
            });
        });
    });

    // Lógica para o formulário de transações recorrentes
    document.getElementById('recorrenteForm').addEventListener('submit', function(event) {
        event.preventDefault();

        const form = event.target;
        const formData = new FormData(form);
        const jsonData = {};

        for (let [key, value] of formData.entries()) {
            jsonData[key] = value;
        }

        // Processar o valor antes de enviar
        jsonData['valor'] = processCurrencyInput(jsonData['valor']);

        fetch('/add_recorrente', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(jsonData)
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => { throw new Error(err.message || `HTTP error! status: ${response.status}`); });
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                Swal.fire({
                    icon: 'success',
                    title: 'Sucesso!',
                    text: data.message
                });
                // Fechar modal e recarregar dados
                const modalElement = document.getElementById('addRecorrenteModal');
                const modal = bootstrap.Modal.getInstance(modalElement);
                if (modal) {
                    modal.hide();
                }
                form.reset();
                const currentMonthYear = document.getElementById('current-month-year').textContent.split('/');
                loadDashboardData(parseInt(currentMonthYear[0]), parseInt(currentMonthYear[1]));
            } else {
                Swal.fire({
                    icon: 'error',
                    title: 'Erro!',
                    text: data.message || 'Ocorreu um erro ao salvar a transação recorrente.'
                });
            }
        })
        .catch(error => {
            console.error('Erro ao salvar transação recorrente:', error);
            Swal.fire({
                icon: 'error',
                title: 'Erro!',
                text: error.message || 'Não foi possível salvar a transação recorrente. Verifique os dados e tente novamente.'
            });
        });
    });

    // Lógica para alternar campos de despesa/receita no modal de adição
    document.getElementById('tipo').addEventListener('change', function() {
        const tipo = this.value;
        document.getElementById('vencimento-group').style.display = tipo === 'despesa' ? 'block' : 'none';
        document.getElementById('status-group').style.display = tipo === 'despesa' ? 'block' : 'none';
        document.getElementById('recorrente-group').style.display = 'block'; // Sempre visível para nova transação
        document.getElementById('frequencia-group').style.display = document.getElementById('recorrente').checked ? 'block' : 'none';
        document.getElementById('data-final-group').style.display = document.getElementById('recorrente').checked ? 'block' : 'none';
    });

    // Lógica para alternar campos de recorrência
    document.getElementById('recorrente').addEventListener('change', function() {
        const isRecorrente = this.checked;
        document.getElementById('frequencia-group').style.display = isRecorrente ? 'block' : 'none';
        document.getElementById('data-final-group').style.display = isRecorrente ? 'block' : 'none';
    });

    // Lógica para alternar campos de despesa/receita no modal de edição
    document.getElementById('edit-tipo').addEventListener('change', function() {
        const tipo = this.value;
        document.getElementById('edit-vencimento-group').style.display = tipo === 'despesa' ? 'block' : 'none';
        document.getElementById('edit-status-group').style.display = tipo === 'despesa' ? 'block' : 'none';
    });

    // Inicialização
    function initializeDashboard() {
        if (!eventListenersRegistered) {
            // Carregar dados iniciais para o mês e ano atuais
            const today = new Date();
            loadDashboardData(today.getMonth() + 1, today.getFullYear());
            formatExistingValues();
            setupCurrencyInputs();
            eventListenersRegistered = true;
        }
    }

    // Chamar a inicialização quando o DOM estiver completamente carregado
    initializeDashboard();
});

