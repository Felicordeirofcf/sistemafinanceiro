# Sistema Financeiro - Documentação

## Visão Geral

O Sistema Financeiro é uma aplicação web completa para gerenciamento de finanças pessoais, desenvolvida com Flask e tecnologias modernas de frontend. O sistema permite controlar receitas e despesas, visualizar dados em gráficos interativos, acompanhar transações em um calendário financeiro, receber alertas de vencimento e realizar buscas avançadas.

## Funcionalidades Principais

### 1. Autenticação e Segurança
- Sistema de login e registro de usuários
- Proteção de rotas para usuários autenticados
- Senhas criptografadas com hash seguro

### 2. Dashboard Interativo
- Resumo financeiro com cards informativos
- Gráficos de receitas x despesas
- Distribuição de gastos por categoria
- Visualização de saldo mensal

### 3. Calendário Financeiro
- Visualização de transações por data
- Marcação visual de receitas e despesas
- Detalhes ao clicar em cada lançamento
- Indicadores visuais de status de pagamento

### 4. Sistema de Alertas
- Notificações no sistema para vencimentos próximos
- Envio de e-mails para alertas de vencimento
- Visualização rápida de despesas pendentes

### 5. Filtros Avançados
- Busca por descrição
- Filtros por categoria, valor, período e status
- Visualização detalhada dos resultados de busca

### 6. Responsividade
- Layout adaptável para dispositivos móveis
- Menu colapsável em telas pequenas
- Visualização otimizada para touch

## Tecnologias Utilizadas

### Backend
- **Flask**: Framework web principal
- **SQLAlchemy**: ORM para interação com banco de dados
- **Flask-Login**: Gerenciamento de autenticação
- **Flask-WTF**: Validação de formulários
- **Flask-Mail**: Envio de alertas por e-mail

### Frontend
- **Bootstrap 5**: Framework CSS para responsividade
- **Chart.js**: Biblioteca para criação de gráficos
- **FullCalendar**: Biblioteca para calendário interativo
- **FontAwesome**: Ícones para melhorar a interface
- **SweetAlert2**: Notificações e alertas visuais
- **DataTables**: Para tabelas com filtros avançados

## Estrutura do Projeto

```
finance_app/
├── venv/                  # Ambiente virtual Python
├── src/                   # Código-fonte principal
│   ├── main.py            # Ponto de entrada da aplicação
│   ├── models/            # Modelos de dados
│   │   ├── __init__.py
│   │   ├── transaction.py # Modelo de transações
│   │   ├── category.py    # Modelo de categorias
│   │   └── user.py        # Modelo de usuários
│   ├── routes/            # Rotas da API
│   │   ├── __init__.py
│   │   ├── auth.py        # Rotas de autenticação
│   │   ├── dashboard.py   # Rotas para o dashboard
│   │   ├── transactions.py # Rotas para transações
│   │   └── alerts.py      # Rotas para alertas
│   ├── static/            # Arquivos estáticos
│   │   ├── css/           # Estilos CSS
│   │   ├── js/            # Scripts JavaScript
│   │   └── img/           # Imagens e ícones
│   └── templates/         # Templates HTML
│       ├── auth/          # Templates de autenticação
│       ├── dashboard/     # Templates do dashboard
│       └── components/    # Componentes reutilizáveis
├── requirements.txt       # Dependências do projeto
└── README.md              # Documentação
```

## Instruções de Instalação

### Requisitos
- Python 3.8 ou superior
- Pip (gerenciador de pacotes Python)
- Ambiente virtual (recomendado)

### Passos para Instalação Local

1. Clone o repositório ou descompacte o arquivo do projeto
```bash
git clone <url-do-repositorio> sistema_financeiro
cd sistema_financeiro
```

2. Crie e ative um ambiente virtual
```bash
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
```

3. Instale as dependências
```bash
pip install -r requirements.txt
```

4. Execute a aplicação
```bash
cd src
python main.py
```

5. Acesse a aplicação no navegador
```
http://localhost:5000
```

### Deploy em Produção

Para deploy em produção, recomendamos utilizar serviços como Render ou Railway:

1. Certifique-se de que o arquivo `requirements.txt` está atualizado:
```bash
pip freeze > requirements.txt
```

2. Configure as variáveis de ambiente necessárias:
   - `SECRET_KEY`: Chave secreta para segurança da aplicação
   - `DATABASE_URL`: URL de conexão com o banco de dados (PostgreSQL recomendado)
   - `MAIL_SERVER`, `MAIL_PORT`, `MAIL_USERNAME`, `MAIL_PASSWORD`: Configurações para envio de e-mail

3. Siga as instruções específicas da plataforma de deploy escolhida.

## Guia de Uso

### Primeiros Passos

1. **Registro e Login**
   - Crie uma conta com seu nome de usuário, e-mail e senha
   - Faça login com suas credenciais

2. **Dashboard**
   - Visualize o resumo financeiro do mês atual
   - Use o filtro de mês/ano para navegar entre períodos

3. **Adicionando Transações**
   - Use o formulário "Nova Transação" para adicionar receitas ou despesas
   - Preencha todos os campos obrigatórios
   - Para despesas, você pode definir a data de vencimento

4. **Gerenciando Transações**
   - Visualize suas transações na tabela ou no calendário
   - Marque despesas como pagas/não pagas usando o botão de status
   - Exclua transações quando necessário

5. **Usando o Calendário**
   - Clique em uma data para ver as transações daquele dia
   - Clique em uma transação no calendário para ver detalhes

6. **Alertas de Vencimento**
   - Verifique o ícone de sino para alertas de vencimentos próximos
   - Configure o envio de alertas por e-mail

7. **Busca Avançada**
   - Use a função de busca para filtrar transações por diversos critérios
   - Combine múltiplos filtros para resultados mais precisos

## Suporte e Contato

Para suporte ou dúvidas sobre o sistema, entre em contato através do e-mail: suporte@sistemafinanceiro.com.br

---

© 2025 Sistema Financeiro - Todos os direitos reservados
