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
        let cleaned = inputValue.replace(/[^\d,\.]/g, '');
        
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
        });
    }

    function handleCurrencyInput(e) {
        let value = e.target.value;
        
        // Permitir apenas números, vírgula e ponto
        value = value.replace(/[^\d,\.]/g, '');
        
        // Limitar a uma vírgula ou ponto
        const commaCount = (value.match(/,/g) || []).length;
        const dotCount = (value.match(/\./g) || []).length;
        
        if (commaCount > 1) {
            value = value.replace(/,(?=.*,)/g, '');
        }
        if (dotCount > 1) {
            value = value.replace(/\.(?=.*\.)/g, '');
        }
        
        e.target.value = value;
    }

    function handleCurrencyBlur(e) {
        let value = e.target.value;
        if (value.includes(',')) {
            // Se tem vírgula, converte para ponto para compatibilidade com HTML5
            e.target.value = value.replace(',', '.');
        }
    }

    function handleCurrencyFocus(e) {
        let value = e.target.value;
        if (value.includes('.') && !value.includes(',')) {
            e.target.value = value.replace('.', ',');
        }
    }

    const tipoReceita = document.getElementById('tipo-receita');
    const tipoDespesa = document.getElementById('tipo-despesa');
    const vencimentoGroup = document.getElementById('vencimento-group');
    const recorrenteGroup = document.getElementById('recorrente-group');
    const recorrenteCheckbox = document.getElementById('recorrente');
    const frequenciaGroup = document.getElementById('frequencia-group');
    const dataFimGroup = document.getElementById('data-fim-group');
    const pagoGroup = document.getElementById('pago-group');

    function toggleVencimentoAndRecorrente() {
        if (tipoDespesa && tipoDespesa.checked) {
            if (vencimentoGroup) vencimentoGroup.style.display = 'block';
            if (recorrenteGroup) recorrenteGroup.style.display = 'block';
            if (pagoGroup) pagoGroup.style.display = 'block';
        } else {
            if (vencimentoGroup) vencimentoGroup.style.display = 'none';
            if (recorrenteGroup) recorrenteGroup.style.display = 'none';
            if (pagoGroup) pagoGroup.style.display = 'none';
            // Reset campos quando muda para receita
            if (recorrenteCheckbox) recorrenteCheckbox.checked = false;
            toggleFrequencia();
        }
    }

    function toggleFrequencia() {
        if (recorrenteCheckbox && recorrenteCheckbox.checked) {
            if (frequenciaGroup) frequenciaGroup.style.display = 'block';
            if (dataFimGroup) dataFimGroup.style.display = 'block';
        } else {
            if (frequenciaGroup) frequenciaGroup.style.display = 'none';
            if (dataFimGroup) dataFimGroup.style.display = 'none';
        }
    }

    // Event listeners para campos de tipo
    if (tipoReceita) tipoReceita.addEventListener('change', toggleVencimentoAndRecorrente);
    if (tipoDespesa) tipoDespesa.addEventListener('change', toggleVencimentoAndRecorrente);
    if (recorrenteCheckbox) recorrenteCheckbox.addEventListener('change', toggleFrequencia);

    // Inicializar estado
    toggleVencimentoAndRecorrente();
    toggleFrequencia();

    // Configurar formatação de moeda
    formatExistingValues();
    setupCurrencyInputs();

    // Inicializar DataTables de forma mais robusta
    function initializeDataTable() {
        try {
            const tableElement = document.getElementById('transactionsTable');
            if (!tableElement) {
                console.log('Tabela transactionsTable não encontrada');
                return;
            }

            // Destruir DataTable existente se houver
            if ($.fn.DataTable && $.fn.DataTable.isDataTable('#transactionsTable')) {
                $('#transactionsTable').DataTable().clear().destroy();
                $('#transactionsTable').empty();
            }
            
            // Aguardar um momento para garantir que a destruição foi completa
            setTimeout(() => {
                try {
                    const $table = $('#transactionsTable');
                    
                    // Verificar se a tabela ainda existe após possível destruição
                    if ($table.length === 0) {
                        console.log('Tabela não existe mais após destruição');
                        return;
                    }

                    const headerCols = $table.find('thead th').length;
                    const bodyRows = $table.find('tbody tr').length;
                    
                    console.log(`Tabela encontrada - Colunas: ${headerCols}, Linhas: ${bodyRows}`);
                    
                    // Só inicializar se a tabela tem estrutura válida
                    if (headerCols >= 4) { // Mínimo de 4 colunas esperadas
                        // Verificar se há dados reais (não apenas mensagem de "nenhum registro")
                        const hasRealData = bodyRows > 0 && $table.find('tbody tr td[colspan]').length === 0;
                        
                        const config = {
                            destroy: true, // Permitir reinicialização
                            language: {
                                url: "//cdn.datatables.net/plug-ins/1.13.4/i18n/pt-BR.json"
                            },
                            columnDefs: [
                                { orderable: false, targets: -1 } // Última coluna (ações) não ordenável
                            ],
                            responsive: true,
                            pageLength: 10,
                            lengthMenu: [[10, 25, 50, -1], [10, 25, 50, "Todos"]],
                            info: hasRealData,
                            paging: hasRealData,
                            searching: hasRealData,
                            autoWidth: false
                        };
                        
                        // Só definir ordenação se há dados reais
                        if (hasRealData && headerCols >= 2) {
                            config.order = [[1, 'desc']]; // Ordenar por segunda coluna (data)
                        }
                        
                        $table.DataTable(config);
                        console.log('DataTable inicializado com sucesso');
                        
                    } else {
                        console.log('Estrutura da tabela inválida para DataTable');
                    }
                } catch (innerError) {
                    console.warn('Erro na inicialização interna do DataTable:', innerError);
                }
            }, 100);
            
        } catch (error) {
            console.warn('Erro ao inicializar DataTable:', error);
        }
    }

    // Função única para submissão do formulário
    async function submitTransactionForm(e) {
        e.preventDefault();
        e.stopPropagation();
        
        const form = e.target;
        const submitBtn = form.querySelector('button[type="submit"]');
        
        // Verificar se já está processando para evitar dupla submissão
        if (submitBtn.disabled) {
            return false;
        }
        
        // Validações customizadas
        const valorInput = document.getElementById('valor');
        let valor = valorInput ? valorInput.value.replace(',', '.') : '';
        const descricaoInput = document.getElementById('descricao');
        const descricao = descricaoInput ? descricaoInput.value.trim() : '';
        
        let isValid = true;
        
        // Validar valor
        if (!valor || parseFloat(valor) <= 0) {
            if (valorInput) valorInput.classList.add('is-invalid');
            isValid = false;
        } else {
            if (valorInput) {
                valorInput.classList.remove('is-invalid');
                // Garantir que o valor seja enviado com ponto decimal
                valorInput.value = valor;
            }
        }
        
        // Validar descrição
        if (!descricao) {
            if (descricaoInput) descricaoInput.classList.add('is-invalid');
            isValid = false;
        } else {
            if (descricaoInput) descricaoInput.classList.remove('is-invalid');
        }
        
        if (!isValid) {
            Swal.fire({
                icon: 'warning',
                title: 'Campos obrigatórios',
                text: 'Por favor, preencha todos os campos obrigatórios corretamente.'
            });
            return false;
        }
        
        // Desabilitar botão durante envio
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Adicionando...';

        try {
            const formData = new FormData(form);
            
            const response = await fetch(form.action, {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            
            if (data.success) {
                Swal.fire({
                    icon: 'success',
                    title: 'Sucesso!',
                    text: data.message,
                    showConfirmButton: false,
                    timer: 1500
                }).then(() => {
                    // Limpar formulário
                    form.reset();
                    // Resetar data para hoje
                    const dataInput = document.getElementById('data');
                    const vencimentoInput = document.getElementById('vencimento');
                    if (dataInput) dataInput.value = new Date().toISOString().split('T')[0];
                    if (vencimentoInput) vencimentoInput.value = new Date().toISOString().split('T')[0];
                    // Resetar visibilidade dos campos
                    toggleVencimentoAndRecorrente();
                    toggleFrequencia();
                    // Recarregar página para atualizar dados
                    location.reload();
                });
            } else {
                Swal.fire({
                    icon: 'error',
                    title: 'Erro!',
                    text: data.message
                });
            }
        } catch (error) {
            console.error('Erro ao enviar formulário:', error);
            Swal.fire({
                icon: 'error',
                title: 'Erro!',
                text: 'Erro ao adicionar a transação. Tente novamente.'
            });
        } finally {
            // Reabilitar botão
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="fas fa-plus-circle me-2"></i>Adicionar Transação';
        }
        
        return false;
    }

    // Registrar event listeners apenas uma vez
    function registerEventListeners() {
        if (eventListenersRegistered) {
            return;
        }
        
        // Event listener para o formulário de transação
        const form = document.getElementById('form-transacao');
        if (form) {
            // Remover listeners existentes
            form.removeEventListener('submit', submitTransactionForm);
            // Adicionar listener único
            form.addEventListener('submit', submitTransactionForm);
        }

        // Event listeners para ações da tabela (usando delegação de eventos)
        $(document).off('click', '.delete-btn').on('click', '.delete-btn', function() {
            const transactionId = $(this).data('id');
            Swal.fire({
                title: 'Tem certeza?',
                text: "Você não poderá reverter isso!",
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#3085d6',
                cancelButtonColor: '#d33',
                confirmButtonText: 'Sim, deletar!',
                cancelButtonText: 'Cancelar'
            }).then((result) => {
                if (result.isConfirmed) {
                    $.ajax({
                        url: `/transactions/delete/${transactionId}`,
                        method: 'POST',
                        success: function(response) {
                            if (response.success) {
                                Swal.fire(
                                    'Deletado!',
                                    'A transação foi deletada.',
                                    'success'
                                ).then(() => {
                                    location.reload();
                                });
                            } else {
                                Swal.fire(
                                    'Erro!',
                                    response.message,
                                    'error'
                                );
                            }
                        },
                        error: function() {
                            Swal.fire(
                                'Erro!',
                                'Ocorreu um erro ao deletar a transação.',
                                'error'
                            );
                        }
                    });
                }
            });
        });

        $(document).off('click', '.pay-btn').on('click', '.pay-btn', function() {
            const transactionId = $(this).data('id');
            Swal.fire({
                title: 'Marcar como pago?',
                text: "Esta despesa será marcada como paga.",
                icon: 'info',
                showCancelButton: true,
                confirmButtonColor: '#3085d6',
                cancelButtonColor: '#d33',
                confirmButtonText: 'Sim, marcar como pago!',
                cancelButtonText: 'Cancelar'
            }).then((result) => {
                if (result.isConfirmed) {
                    $.ajax({
                        url: `/transactions/toggle_status/${transactionId}`,
                        method: 'POST',
                        success: function(response) {
                            if (response.success) {
                                Swal.fire(
                                    'Pago!',
                                    'A despesa foi marcada como paga.',
                                    'success'
                                ).then(() => {
                                    location.reload();
                                });
                            } else {
                                Swal.fire(
                                    'Erro!',
                                    response.message,
                                    'error'
                                );
                            }
                        },
                        error: function() {
                            Swal.fire(
                                'Erro!',
                                'Ocorreu um erro ao marcar a despesa como paga.',
                                'error'
                            );
                        }
                    });
                }
            });
        });

        eventListenersRegistered = true;
    }

    // Aguardar carregamento completo antes de inicializar
    $(document).ready(function() {
        setTimeout(function() {
            initializeDataTable();
            formatExistingValues();
            registerEventListeners();
        }, 300);
    });

    // Aguardar carregamento da janela
    $(window).on('load', function() {
        setTimeout(function() {
            initializeDataTable();
            formatExistingValues();
        }, 200);
    });

    // Handle edit transaction modal populate
    $(document).on('click', '.edit-btn', function() {
        const transactionId = $(this).data('id');
        
        // Mostrar loading
        Swal.fire({
            title: 'Carregando...',
            text: 'Buscando dados da transação',
            allowOutsideClick: false,
            didOpen: () => {
                Swal.showLoading();
            }
        });
        
        $.ajax({
            url: `/transactions/get/${transactionId}`,
            method: 'GET',
            success: function(response) {
                Swal.close();
                
                if (response.success) {
                    const transaction = response.transaction;
                    
                    // Preencher campos básicos
                    $('#edit-transaction-id').val(transaction.id);
                    $('#edit-valor').val(transaction.valor);
                    $('#edit-data').val(transaction.data);
                    $('#edit-descricao').val(transaction.descricao);
                    
                    // Configurar tipo de transação
                    if (transaction.tipo === 'receita') {
                        $('#edit-tipo-receita').prop('checked', true);
                        $('#edit-vencimento-group').hide();
                        $('#edit-pago-group').hide();
                        $('#edit-recorrente-group').hide();
                        $('#edit-frequencia-group').hide();
                    } else {
                        $('#edit-tipo-despesa').prop('checked', true);
                        $('#edit-vencimento-group').show();
                        $('#edit-pago-group').show();
                        $('#edit-recorrente-group').show();
                        
                        // Preencher campos específicos de despesa
                        $('#edit-vencimento').val(transaction.vencimento || transaction.data);
                        $('#edit-pago').prop('checked', transaction.pago);
                        
                        // Configurar recorrência
                        if (transaction.is_recurring) {
                            $('#edit-recorrente').prop('checked', true);
                            $('#edit-frequencia-group').show();
                            $('#edit-frequencia').val(transaction.frequencia || 'mensal');
                        } else {
                            $('#edit-recorrente').prop('checked', false);
                            $('#edit-frequencia-group').hide();
                        }
                    }
                    
                    // Adicionar event listeners para o modal
                    setupEditModalListeners();
                    
                } else {
                    Swal.fire({
                        icon: 'error',
                        title: 'Erro!',
                        text: response.message || 'Erro ao carregar dados da transação'
                    });
                }
            },
            error: function(xhr, status, error) {
                Swal.close();
                Swal.fire({
                    icon: 'error',
                    title: 'Erro!',
                    text: 'Erro ao carregar os dados da transação. Tente novamente.'
                });
            }
        });
    });

    // Configurar listeners do modal de edição
    function setupEditModalListeners() {
        // Controlar visibilidade dos campos baseado no tipo
        $('#edit-tipo-receita, #edit-tipo-despesa').off('change').on('change', function() {
            if ($('#edit-tipo-despesa').is(':checked')) {
                $('#edit-vencimento-group').show();
                $('#edit-pago-group').show();
                $('#edit-recorrente-group').show();
            } else {
                $('#edit-vencimento-group').hide();
                $('#edit-pago-group').hide();
                $('#edit-recorrente-group').hide();
                $('#edit-frequencia-group').hide();
                $('#edit-recorrente').prop('checked', false);
            }
        });

        // Controlar visibilidade da frequência
        $('#edit-recorrente').off('change').on('change', function() {
            if ($(this).is(':checked')) {
                $('#edit-frequencia-group').show();
            } else {
                $('#edit-frequencia-group').hide();
            }
        });
    }

    // Handle edit form submission
    $('#save-edit-btn').on('click', function() {
        const form = $('#edit-form-transacao');
        const transactionId = $('#edit-transaction-id').val();
        $.ajax({
            url: `/transactions/edit/${transactionId}`,
            method: 'POST',
            data: form.serialize(),
            success: function(response) {
                if (response.success) {
                    Swal.fire({
                        icon: 'success',
                        title: 'Sucesso!',
                        text: response.message,
                        showConfirmButton: false,
                        timer: 1500
                    }).then(() => {
                        $('#editTransactionModal').modal('hide');
                        location.reload();
                    });
                } else {
                    Swal.fire({
                        icon: 'error',
                        title: 'Erro!',
                        text: response.message
                    });
                }
            },
            error: function() {
                Swal.fire({
                    icon: 'error',
                    title: 'Erro!',
                    text: 'Ocorreu um erro ao salvar as alterações.'
                });
            }
        });
    });

    // FullCalendar initialization
    var calendarEl = document.getElementById('calendar');
    if (calendarEl) {
        var calendar = new FullCalendar.Calendar(calendarEl, {
            initialView: 'dayGridMonth',
            locale: 'pt-br',
            headerToolbar: {
                left: 'prev,next today',
                center: 'title',
                right: 'dayGridMonth,timeGridWeek,timeGridDay,listMonth'
            },
            events: function(fetchInfo, successCallback, failureCallback) {
                $.ajax({
                    url: `/dashboard/calendar-data?mes=${new Date().getMonth() + 1}&ano=${new Date().getFullYear()}`,
                    method: 'GET',
                    success: function(response) {
                        const events = response.calendar_data.map(event => ({
                            id: event.id,
                            title: event.title,
                            start: event.start,
                            color: event.color,
                            extendedProps: event.extendedProps
                        }));
                        successCallback(events);
                    },
                    error: function() {
                        failureCallback();
                        Swal.fire({
                            icon: 'error',
                            title: 'Erro!',
                            text: 'Ocorreu um erro ao carregar os eventos do calendário.'
                        });
                    }
                });
            },
            eventClick: function(info) {
                const event = info.event;
                const props = event.extendedProps;
                let details = `
                    <p><strong>Tipo:</strong> ${props.tipo === 'receita' ? 'Receita' : 'Despesa'}</p>
                    <p><strong>Valor:</strong> R$ ${(props.valor).toFixed(2).replace('.', ',')}</p>
                    <p><strong>Data:</strong> ${new Date(event.start).toLocaleDateString('pt-BR')}</p>
                `;
                if (props.tipo === 'despesa') {
                    details += `<p><strong>Status:</strong> ${props.pago ? 'Pago' : 'Pendente'}</p>`;
                }
                if (props.is_recurring) {
                    details += `<p><strong>Recorrente:</strong> Sim</p>`;
                }

                Swal.fire({
                    title: event.title,
                    html: details,
                    icon: 'info',
                    confirmButtonText: 'Fechar'
                });
            }
        });
        calendar.render();
    }

    // Chart.js initialization
    function loadChartData() {
        const currentMonth = new Date().getMonth() + 1;
        const currentYear = new Date().getFullYear();
        
        $.ajax({
            url: `/dashboard/chart-data?mes=${currentMonth}&ano=${currentYear}`,
            method: 'GET',
            success: function(response) {
                // Bar Chart (Receitas x Despesas)
                const barCtx = document.getElementById('barChart');
                if (barCtx) {
                    new Chart(barCtx, {
                        type: 'bar',
                        data: response.bar_chart,
                        options: {
                            responsive: true,
                            plugins: {
                                legend: { display: false }
                            }
                        }
                    });
                }
            },
            error: function() {
                Swal.fire({
                    icon: 'error',
                    title: 'Erro!',
                    text: 'Ocorreu um erro ao carregar os dados dos gráficos.'
                });
            }
        });
    }

    // Load chart data on page load
    loadChartData();
});

