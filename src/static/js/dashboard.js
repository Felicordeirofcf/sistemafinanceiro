document.addEventListener('DOMContentLoaded', function() {
    // Handle transaction type change (Receita/Despesa)
    const tipoReceita = document.getElementById('tipo-receita');
    const tipoDespesa = document.getElementById('tipo-despesa');
    const vencimentoGroup = document.getElementById('vencimento-group');
    const recorrenteGroup = document.getElementById('recorrente-group');

    function toggleVencimentoAndRecorrente() {
        if (tipoDespesa.checked) {
            vencimentoGroup.style.display = 'block';
            recorrenteGroup.style.display = 'block';
        } else {
            vencimentoGroup.style.display = 'none';
            recorrenteGroup.style.display = 'none';
        }
    }

    tipoReceita.addEventListener('change', toggleVencimentoAndRecorrente);
    tipoDespesa.addEventListener('change', toggleVencimentoAndRecorrente);

    // Initial call to set correct state
    toggleVencimentoAndRecorrente();

    // Handle recorrente checkbox change
    const recorrenteCheckbox = document.getElementById('recorrente');
    const frequenciaGroup = document.getElementById('frequencia-group');

    function toggleFrequencia() {
        if (recorrenteCheckbox.checked) {
            frequenciaGroup.style.display = 'block';
        } else {
            frequenciaGroup.style.display = 'none';
        }
    }

    recorrenteCheckbox.addEventListener('change', toggleFrequencia);

    // Initial call to set correct state
    toggleFrequencia();

    // Initialize DataTables for transactions table
    if ($.fn.DataTable) {
        $('#transactionsTable').DataTable({
            "language": {
                "url": "//cdn.datatables.net/plug-ins/1.13.4/i18n/pt-BR.json"
            },
            "order": [[2, "desc"]] // Order by Date (column 2) descending
        });
    }

    // Handle transaction form submission (AJAX)
    $('#form-transacao').on('submit', function(e) {
        e.preventDefault();
        const form = $(this);
        $.ajax({
            url: form.attr('action'),
            method: form.attr('method'),
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
                        location.reload(); // Reload page to update data
                    });
                } else {
                    Swal.fire({
                        icon: 'error',
                        title: 'Erro!',
                        text: response.message
                    });
                }
            },
            error: function(xhr) {
                Swal.fire({
                    icon: 'error',
                    title: 'Erro!',
                    text: 'Ocorreu um erro ao adicionar a transação.'
                });
            }
        });
    });

    // Handle delete transaction
    $(document).on('click', '.delete-btn', function() {
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

    // Handle pay transaction
    $(document).on('click', '.pay-btn', function() {
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
                    url: `/transactions/pay/${transactionId}`,
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

    // Handle edit transaction modal populate
    $(document).on('click', '.edit-btn', function() {
        const transactionId = $(this).data('id');
        $.ajax({
            url: `/transactions/get/${transactionId}`,
            method: 'GET',
            success: function(response) {
                if (response.success) {
                    const transaction = response.transaction;
                    $('#edit-transaction-id').val(transaction.id);
                    if (transaction.tipo === 'receita') {
                        $('#edit-tipo-receita').prop('checked', true);
                        $('#edit-vencimento-group').hide();
                        $('#edit-recorrente-group').hide();
                        $('#edit-frequencia-group').hide();
                    } else {
                        $('#edit-tipo-despesa').prop('checked', true);
                        $('#edit-vencimento-group').show();
                        $('#edit-recorrente-group').show();
                        if (transaction.is_recurring) {
                            $('#edit-recorrente').prop('checked', true);
                            $('#edit-frequencia-group').show();
                            $('#edit-frequencia').val(transaction.frequencia);
                        } else {
                            $('#edit-recorrente').prop('checked', false);
                            $('#edit-frequencia-group').hide();
                        }
                    }
                    $('#edit-valor').val(transaction.valor);
                    $('#edit-data').val(transaction.data);
                    $('#edit-vencimento').val(transaction.vencimento);
                    $('#edit-descricao').val(transaction.descricao);
                    $('#edit-categoria').val(transaction.categoria_id);
                    $('#edit-pago').prop('checked', transaction.pago);
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
                    text: 'Ocorreu um erro ao carregar os dados da transação.'
                });
            }
        });
    });

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
                    <p><strong>Valor:</strong> R$ ${(props.valor/100).toFixed(2).replace('.', ',')}</p>
                    <p><strong>Categoria:</strong> ${props.categoria}</p>
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
        $.ajax({
            url: `/dashboard/chart-data?mes={{ selected_month }}&ano={{ selected_year }}`,
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

                // Expense Chart (Despesas por Categoria)
                const expenseCtx = document.getElementById('expenseChart');
                if (expenseCtx) {
                    new Chart(expenseCtx, {
                        type: 'pie',
                        data: {
                            labels: response.expense_chart.map(item => item.name),
                            datasets: [{
                                data: response.expense_chart.map(item => item.value),
                                backgroundColor: response.expense_chart.map(item => item.color)
                            }]
                        },
                        options: {
                            responsive: true,
                            plugins: {
                                legend: {
                                    position: 'top',
                                },
                            }
                        }
                    });
                }

                // Income Chart (Receitas por Categoria)
                const incomeCtx = document.getElementById('incomeChart');
                if (incomeCtx) {
                    new Chart(incomeCtx, {
                        type: 'pie',
                        data: {
                            labels: response.income_chart.map(item => item.name),
                            datasets: [{
                                data: response.income_chart.map(item => item.value),
                                backgroundColor: response.income_chart.map(item => item.color)
                            }]
                        },
                        options: {
                            responsive: true,
                            plugins: {
                                legend: {
                                    position: 'top',
                                },
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

    loadChartData();

    // Fetch and display alerts
    function fetchAlerts() {
        $.ajax({
            url: '/alerts/upcoming_due',
            method: 'GET',
            success: function(response) {
                const alertsDropdown = $('#alerts-dropdown');
                const alertsBadge = $('#alerts-badge');
                alertsDropdown.find('.alert-item').remove(); // Clear previous alerts

                if (response.upcoming_due && response.upcoming_due.length > 0) {
                    alertsBadge.text(response.upcoming_due.length).show();
                    $('#no-alerts').hide();
                    response.upcoming_due.forEach(alert => {
                        alertsDropdown.append(`
                            <li><a class="dropdown-item alert-item" href="#">${alert.descricao} - R$ ${alert.valor.toFixed(2).replace('.', ',')} (Vence em: ${alert.vencimento})</a></li>
                        `);
                    });
                } else {
                    alertsBadge.hide();
                    $('#no-alerts').show();
                }
            },
            error: function() {
                console.error('Erro ao carregar alertas.');
            }
        });
    }

    fetchAlerts();

    // Initial setup for edit modal based on transaction type
    $(document).on('change', '#edit-tipo-receita, #edit-tipo-despesa', function() {
        if ($('#edit-tipo-despesa').is(':checked')) {
            $('#edit-vencimento-group').show();
            $('#edit-recorrente-group').show();
        } else {
            $('#edit-vencimento-group').hide();
            $('#edit-recorrente-group').hide();
            $('#edit-frequencia-group').hide(); // Hide frequency if not despesa
        }
    });

    $(document).on('change', '#edit-recorrente', function() {
        if ($(this).is(':checked')) {
            $('#edit-frequencia-group').show();
        } else {
            $('#edit-frequencia-group').hide();
        }
    });
});

