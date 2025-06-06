# Correção do Erro no Sistema Financeiro

Este documento detalha a correção implementada para o erro `werkzeug.routing.exceptions.BuildError` que ocorria ao tentar adicionar uma nova transação no sistema financeiro.

## Problema Identificado

O erro `werkzeug.routing.exceptions.BuildError: Could not build url for endpoint 'transactions.add_transaction' with values ['ano', 'mes']. Did you mean 'transactions.add' instead?` indicava que o template Jinja2 `dashboard/index.html` estava tentando gerar uma URL para um endpoint chamado `transactions.add_transaction`, mas a rota definida no blueprint de transações (`src/routes/transactions.py`) era `transactions.add`.

Além disso, foi identificado que a aplicação não estava configurada para rodar localmente sem a variável de ambiente `DATABASE_URL` definida, o que impedia a execução para testes.

## Solução Implementada

Foram realizadas as seguintes alterações para corrigir os problemas:

1.  **Correção do Endpoint no Template Jinja2:**
    *   No arquivo `src/templates/dashboard/index.html`, a linha que gerava a URL para o formulário de transação foi alterada de `url_for('transactions.add_transaction', ...)` para `url_for('transactions.add', ...)`. Isso alinha a chamada no template com o nome do endpoint real definido no blueprint.

2.  **Configuração para Execução Local:**
    *   Foi criado um arquivo `src/config.py` para gerenciar as configurações da aplicação, incluindo `DATABASE_URL`, `SECRET_KEY` e credenciais do Google OAuth. Isso permite que a aplicação seja executada localmente usando um banco de dados SQLite padrão (`./test.db`) se a variável de ambiente `DATABASE_URL` não estiver definida.
    *   Os arquivos `src/models/__init__.py` e `src/main.py` foram atualizados para importar e utilizar as configurações do novo arquivo `src/config.py`.

## Como Rodar a Aplicação Localmente

Para rodar a aplicação localmente e verificar a correção, siga os passos abaixo:

1.  **Clone o Repositório (se ainda não o fez):**
    ```bash
    git clone https://github.com/Felicordeirofcf/sistemafinanceiro.git
    cd sistemafinanceiro
    ```

2.  **Instale as Dependências:**
    ```bash
    pip install -r requirements.txt --user
    ```
    *Nota: A opção `--user` é usada para evitar problemas de permissão.*

