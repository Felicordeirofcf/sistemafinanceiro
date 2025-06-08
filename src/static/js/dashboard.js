document.addEventListener("DOMContentLoaded", function() {
    // Variável para controlar se os event listeners já foram registrados
    let eventListenersRegistered = false;

    // Função para formatar valor em moeda brasileira
    function formatCurrency(value) {
        if (value === null || value === undefined || value === '') return 'R$ 0,00';

        const numValue = typeof value === "string" ? parseFloat(value.replace(",", ".")) : value;
        if (isNaN(numValue)) return "R$ 0,00";

        return new Intl.NumberFormat("pt-BR", {
            style: "currency",
            currency: "BRL"
        }).format(numValue);
    }

    // Função para processar entrada de valor (aceita vírgula como decimal)
    function processCurrencyInput(inputValue) {
        if (!inputValue) return "";

        // Remove tudo exceto números, vírgula e ponto
        let cleaned = inputValue.replace(/[^\d.,]/g, "");

        // Se tem vírgula, usa como separador decimal
        if (cleaned.includes(",")) {
            // Remove pontos (milhares) e mantém apenas a vírgula
            cleaned = cleaned.replace(/\./g, "").replace(",", ".");
        }

        return cleaned;
    }

    // Aplicar formatação em campos de valor existentes na página
    function formatExistingValues() {
        // Formatar valores nas tabelas
        document.querySelectorAll(".currency-value").forEach(element => {
            const value = element.textContent || element.innerText;
            if (value && !value.includes("R$")) {
                element.textContent = formatCurrency(value);
            }
        });

        // Formatar valores nos cards de resumo
        document.querySelectorAll("[data-currency]").forEach(element => {
            const value = element.getAttribute("data-currency");
            if (value) {
                element.textContent = formatCurrency(value);
            }
        });
    }

    // Configurar campos de entrada de valor
    function setupCurrencyInputs() {
        const valorInputs = document.querySelectorAll("input[name=\"valor\"], #valor, #edit-valor");

        valorInputs.forEach(input => {
            // Remover listeners existentes para evitar duplicação
            input.removeEventListener("input", handleCurrencyInput);
            input.removeEventListener("blur", handleCurrencyBlur);
            input.removeEventListener("focus", handleCurrencyFocus);

            // Adicionar listeners
            input.addEventListener("input", handleCurrencyInput);
            input.addEventListener("blur", handleCurrencyBlur);
            input.addEventListener("focus", handleCurrencyFocus);

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
        if (input.setSelectionRange) {
            input.setSelectionRange(newCaretPos, newCaretPos);
        }
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
        const url = `/dashboard/dashboard_data?month=${month}&year=${year}`;
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
                console.error("Erro ao carregar dados do dashboard:", error);
                Swal.fire({
                    icon: "error",
                    title: "Erro",
                    text: "Não foi possível carregar os dados do dashboard. Tente novamente mais tarde."
                });
            });
    }

    // Função para atualizar a UI do dashboard
    function updateDashboardUI(data) {
        // Verificar e atualizar elementos dos cards de resumo
        const totalReceitas = document.getElementById("total-receitas");
        if (totalReceitas) {
            totalReceitas.textContent = formatCurrency(data.total_receitas);
        }
        
        const totalDespesas = document.getElementById("total-despesas");
        if (totalDespesas) {
            totalDespesas.textContent = formatCurrency(data.total_despesas);
        }
        
        const totalPendencias = document.getElementById("total-pendencias");
        if (totalPendencias) {
            totalPendencias.textContent = formatCurrency(data.total_pendencias);
        }
        
        const saldoAtual = document.getElementById("saldo-atual");
        if (saldoAtual) {
            saldoAtual.textContent = formatCurrency(data.saldo_atual);
        }

        // Atualizar tabela de transações
        const transactionsTableBody = document.getElementById("transactionsTableBody");
        if (transactionsTableBody) {
            transactionsTableBody.innerHTML = ""; // Limpar tabela existente
            data.transactions.forEach(transaction => {
                const row = transactionsTableBody.insertRow();
                row.innerHTML = `
                    <td>${transaction.data}</td>
                    <td>${transaction.descricao}</td>
                    <td>${transaction.categoria}</td>
                    <td class="currency-value">${formatCurrency(transaction.valor)}</td>
                    <td>${transaction.tipo === "receita" ? "Receita" : "Despesa"}</td>
                    <td>${transaction.status}</td>
                    <td>
                        <button class="btn btn-sm btn-primary edit-btn" data-id="${transaction.id}" data-type="${transaction.tipo}">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-sm btn-danger delete-btn" data-id="${transaction.id}" data-type="${transaction.tipo}">
                            <i class="fas fa-trash"></i>
                        </button>
                        ${transaction.tipo === "despesa" && transaction.status === "Pendente" ?
                            `<button class="btn btn-sm btn-success mark-paid-btn" data-id="${transaction.id}">
                                <i class="fas fa-check"></i>
                            </button>` : ""}
                    </td>
                `;
            });
        }

        // Atualizar título do período
        const currentMonthYear = document.getElementById("current-month-year");
        if (currentMonthYear) {
            currentMonthYear.textContent = data.current_month_year;
        }
    }

    // Variáveis globais para os gráficos
    let receitasDespesasChart;
    let categoriasDespesasChart;

    // Função para atualizar os gráficos
    function updateCharts(data) {
        // Gráfico de Receitas vs Despesas
        const ctxReceitasDespesas = document.getElementById("receitasDespesasChart");
        if (ctxReceitasDespesas) {
            const ctx = ctxReceitasDespesas.getContext("2d");
            if (receitasDespesasChart) {
                receitasDespesasChart.destroy();
            }
            receitasDespesasChart = new Chart(ctx, {
                type: "bar",
                data: {
                    labels: ["Receitas", "Despesas"],
                    datasets: [{
                        label: "Valor",
                        data: [data.total_receitas, data.total_despesas],
                        backgroundColor: ["#28a745", "#dc3545"],
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
        }

        // Gráfico de Despesas por Categoria
        const ctxCategoriasDespesas = document.getElementById("categoriasDespesasChart");
        if (ctxCategoriasDespesas) {
            const ctx = ctxCategoriasDespesas.getContext("2d");
            if (categoriasDespesasChart) {
                categoriasDespesasChart.destroy();
            }
            categoriasDespesasChart = new Chart(ctx, {
                type: "pie",
                data: {
                    labels: data.despesas_por_categoria.map(item => item.categoria),
                    datasets: [{
                        data: data.despesas_por_categoria.map(item => item.valor),
                        backgroundColor: [
                            "#007bff", "#dc3545", "#ffc107", "#28a745", "#6f42c1",
                            "#20c997", "#fd7e14", "#e83e8c", "#6610f2", "#6c757d"
                        ],
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    let label = context.label || "";
                                    if (label) {
                                        label += ": ";
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
    }

    // Variável global para o calendário
    let calendar;

    // Função para atualizar o calendário
    function updateCalendar(data) {
        const calendarEl = document.getElementById("calendar");
        if (calendarEl) {
            if (calendar) {
                calendar.destroy();
            }
            calendar = new FullCalendar.Calendar(calendarEl, {
                initialView: "dayGridMonth",
                locale: "pt-br",
                headerToolbar: {
                    left: "prev,next today",
                    center: "title",
                    right: "dayGridMonth,timeGridWeek,timeGridDay"
                },
                events: data.calendar_events.map(event => ({
                    title: `${event.descricao} - ${formatCurrency(event.valor)}`,
                    start: event.data,
                    color: event.tipo === "receita" ? "#28a745" : "#dc3545" // Verde para receita, vermelho para despesa
                })),
                eventClick: function(info) {
                    Swal.fire({
                        title: info.event.title,
                        html: `<p>Data: ${moment(info.event.start).format("DD/MM/YYYY")}</p>`,
                        icon: "info",
                        confirmButtonText: "Fechar"
                    });
                }
            });
            calendar.render();
        }
    }

    // Event Listeners para navegação de mês/ano
    const prevMonthBtn = document.getElementById("prevMonth");
    if (prevMonthBtn) {
        prevMonthBtn.addEventListener("click", function() {
            const currentMonthYear = document.getElementById("current-month-year").textContent.split("/");
            let month = parseInt(currentMonthYear[0]) - 1;
            let year = parseInt(currentMonthYear[1]);
            if (month < 1) {
                month = 12;
                year--;
            }
            loadDashboardData(month, year);
        });
    }

    const nextMonthBtn = document.getElementById("nextMonth");
    if (nextMonthBtn) {
        nextMonthBtn.addEventListener("click", function() {
            const currentMonthYear = document.getElementById("current-month-year").textContent.split("/");
            let month = parseInt(currentMonthYear[0]) + 1;
            let year = parseInt(currentMonthYear[1]);
            if (month > 12) {
                month = 1;
                year++;
            }
            loadDashboardData(month, year);
        });
    }

    // Configurar formulário de transação para AJAX
    function setupTransactionForm() {
        const form = document.getElementById("form-transacao");
        if (form) {
            form.addEventListener("submit", function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                // Obter dados do formulário
                const formData = new FormData(form);
                
                // Converter valor formatado para decimal
                const valorInput = document.getElementById("valor");
                if (valorInput && valorInput.value) {
                    const valorLimpo = processCurrencyInput(valorInput.value);
                    formData.set("valor", valorLimpo);
                }
                
                // Enviar via AJAX
                fetch(form.action, {
                    method: "POST",
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        Swal.fire({
                            icon: "success",
                            title: "Sucesso",
                            text: data.message,
                            timer: 2000,
                            showConfirmButton: false
                        });
                        
                        // Limpar formulário
                        form.reset();
                        
                        // Recarregar dados do dashboard
                        const currentMonth = new Date().getMonth() + 1;
                        const currentYear = new Date().getFullYear();
                        loadDashboardData(currentMonth, currentYear);
                    } else {
                        Swal.fire({
                            icon: "error",
                            title: "Erro",
                            text: data.message || "Erro ao adicionar transação"
                        });
                    }
                })
                .catch(error => {
                    console.error("Erro ao enviar formulário:", error);
                    Swal.fire({
                        icon: "error",
                        title: "Erro",
                        text: "Erro ao processar a solicitação"
                    });
                });
            });
        }
    }

    // Event Listeners para botões de ação na tabela (editar, excluir, marcar como pago)
    function setupTableEventListeners() {
        // Usar delegação de eventos para elementos dinâmicos
        $(document).on("click", ".edit-btn", function() {
            const id = $(this).data("id");
            const type = $(this).data("type");
            
            // Lógica para editar transação
            fetch(`/${type}/edit/${id}`)
                .then(response => response.json())
                .then(data => {
                    // Preencher modal de edição com os dados da transação
                    document.getElementById("edit-id").value = data.id;
                    document.getElementById("edit-type").value = data.tipo;
                    document.getElementById("edit-descricao").value = data.descricao;
                    document.getElementById("edit-valor").value = formatCurrency(data.valor);
                    document.getElementById("edit-data").value = data.data;
                    document.getElementById("edit-categoria").value = data.categoria;
                    
                    // Abrir modal
                    const editModal = new bootstrap.Modal(document.getElementById("editTransactionModal"));
                    editModal.show();
                })
                .catch(error => {
                    console.error("Erro ao carregar dados para edição:", error);
                    Swal.fire({
                        icon: "error",
                        title: "Erro",
                        text: "Erro ao carregar dados para edição"
                    });
                });
        });

        $(document).on("click", ".delete-btn", function() {
            const id = $(this).data("id");
            const type = $(this).data("type");
            
            Swal.fire({
                title: "Tem certeza?",
                text: "Esta ação não pode ser desfeita!",
                icon: "warning",
                showCancelButton: true,
                confirmButtonColor: "#d33",
                cancelButtonColor: "#3085d6",
                confirmButtonText: "Sim, excluir!",
                cancelButtonText: "Cancelar"
            }).then((result) => {
                if (result.isConfirmed) {
                    fetch(`/${type}/delete/${id}`, {
                        method: "DELETE"
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            Swal.fire({
                                icon: "success",
                                title: "Excluído!",
                                text: data.message,
                                timer: 2000,
                                showConfirmButton: false
                            });
                            
                            // Recarregar dados do dashboard
                            const currentMonth = new Date().getMonth() + 1;
                            const currentYear = new Date().getFullYear();
                            loadDashboardData(currentMonth, currentYear);
                        } else {
                            Swal.fire({
                                icon: "error",
                                title: "Erro",
                                text: data.message || "Erro ao excluir transação"
                            });
                        }
                    })
                    .catch(error => {
                        console.error("Erro ao excluir transação:", error);
                        Swal.fire({
                            icon: "error",
                            title: "Erro",
                            text: "Erro ao processar a solicitação"
                        });
                    });
                }
            });
        });

        $(document).on("click", ".mark-paid-btn", function() {
            const id = $(this).data("id");
            
            fetch(`/despesa/mark-paid/${id}`, {
                method: "POST"
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    Swal.fire({
                        icon: "success",
                        title: "Sucesso",
                        text: data.message,
                        timer: 2000,
                        showConfirmButton: false
                    });
                    
                    // Recarregar dados do dashboard
                    const currentMonth = new Date().getMonth() + 1;
                    const currentYear = new Date().getFullYear();
                    loadDashboardData(currentMonth, currentYear);
                } else {
                    Swal.fire({
                        icon: "error",
                        title: "Erro",
                        text: data.message || "Erro ao marcar como pago"
                    });
                }
            })
            .catch(error => {
                console.error("Erro ao marcar como pago:", error);
                Swal.fire({
                    icon: "error",
                    title: "Erro",
                    text: "Erro ao processar a solicitação"
                });
            });
        });
    }

    // Configurar filtros de mês/ano
    function setupFilters() {
        const filterButton = document.querySelector("button[type='submit']");
        if (filterButton) {
            filterButton.addEventListener("click", function(e) {
                e.preventDefault();
                
                const mesSelect = document.getElementById("mes");
                const anoSelect = document.getElementById("ano");
                
                if (mesSelect && anoSelect) {
                    const month = parseInt(mesSelect.value);
                    const year = parseInt(anoSelect.value);
                    
                    loadDashboardData(month, year);
                }
            });
        }
    }

    // Inicialização quando o DOM estiver carregado
    function init() {
        formatExistingValues();
        setupCurrencyInputs();
        setupTransactionForm();
        setupTableEventListeners();
        setupFilters();
        
        // Carregar dados iniciais do dashboard
        const currentMonth = new Date().getMonth() + 1;
        const currentYear = new Date().getFullYear();
        loadDashboardData(currentMonth, currentYear);
    }

    // Chamar inicialização
    init();
});

