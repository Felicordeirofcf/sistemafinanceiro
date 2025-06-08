# 💰 Sistema Financeiro

Um sistema completo de controle financeiro pessoal desenvolvido em Python Flask, com interface moderna e funcionalidades avançadas para gestão de receitas, despesas e planejamento financeiro.

## 🚀 Funcionalidades Principais

### 📊 Dashboard Interativo
- **Resumo Financeiro**: Cards com totais de receitas, despesas, pendências e saldo
- **Gráficos Dinâmicos**: Visualização de receitas vs despesas com Chart.js
- **Calendário Financeiro**: Visualização mensal de transações com FullCalendar.js
- **Filtros por Período**: Navegação por mês/ano com atualização automática

### 💳 Gestão de Transações
- **Cadastro Intuitivo**: Formulário moderno com validações em tempo real
- **Tipos de Transação**: Receitas e despesas com campos específicos
- **Valores em Real**: Formatação automática em moeda brasileira (R$ 100,59)
- **Datas Flexíveis**: Data da transação e vencimento para despesas
- **Status de Pagamento**: Controle de despesas pagas/pendentes

### 🔄 Transações Recorrentes
- **Geração Automática**: Criação de transações futuras por 12 meses
- **Frequências Variadas**: Mensal, bimestral, trimestral, semestral e anual
- **Controle de Período**: Data final opcional para limitação
- **Gestão Inteligente**: Evita duplicações e permite edição individual

### ✏️ Edição e Controle
- **Modal de Edição**: Interface simplificada para alteração de dados
- **Exclusão Segura**: Confirmação com SweetAlert2
- **Marcar como Pago**: Botão rápido para atualização de status
- **Validações**: Verificação de campos obrigatórios e formatos

### 🎨 Interface e Experiência
- **Design Responsivo**: Bootstrap 5 com layout adaptável
- **Ícones Modernos**: Font Awesome para melhor visualização
- **Feedback Visual**: Alertas e notificações com SweetAlert2
- **Navegação Intuitiva**: Menu organizado e acesso rápido

## 🛠️ Tecnologias Utilizadas

### Backend
- **Python 3.11+**: Linguagem principal
- **Flask**: Framework web minimalista
- **SQLAlchemy**: ORM para banco de dados
- **Flask-Login**: Sistema de autenticação
- **Werkzeug**: Utilitários web e segurança

### Frontend
- **HTML5/CSS3**: Estrutura e estilização
- **Bootstrap 5**: Framework CSS responsivo
- **JavaScript ES6+**: Interatividade e validações
- **jQuery**: Manipulação DOM e AJAX
- **Chart.js**: Gráficos interativos
- **FullCalendar.js**: Calendário de eventos
- **DataTables**: Tabelas avançadas
- **SweetAlert2**: Alertas e modais elegantes
- **Font Awesome**: Biblioteca de ícones

### Banco de Dados
- **SQLite**: Banco local para desenvolvimento
- **PostgreSQL**: Suporte para produção
- **Migrações**: Controle de versão do schema

## 📁 Estrutura do Projeto

```
sistemafinanceiro/
├── src/
│   ├── __init__.py
│   ├── main.py                 # Aplicação principal
│   ├── config.py              # Configurações
│   ├── models/                # Modelos de dados
│   │   ├── user.py           # Modelo de usuário
│   │   ├── transaction.py    # Modelo de transação
│   │   └── category.py       # Modelo de categoria
│   ├── routes/               # Rotas da aplicação
│   │   ├── auth.py          # Autenticação
│   │   ├── dashboard.py     # Dashboard principal
│   │   ├── transactions.py  # Gestão de transações
│   │   └── alerts.py        # Sistema de alertas
│   ├── templates/           # Templates HTML
│   │   ├── dashboard/       # Templates do dashboard
│   │   └── auth/           # Templates de autenticação
│   └── static/             # Arquivos estáticos
│       ├── css/           # Estilos customizados
│       ├── js/            # Scripts JavaScript
│       └── images/        # Imagens e ícones
├── requirements.txt        # Dependências Python
└── README.md              # Documentação
```

## 🔧 Funcionalidades Técnicas

### Autenticação e Segurança
- Sistema de login/logout seguro
- Hash de senhas com Werkzeug
- Sessões protegidas
- Validação de formulários

### Processamento de Dados
- Formatação automática de moeda brasileira
- Validação de entrada com vírgula decimal
- Cálculos financeiros precisos
- Agregações por período

### Interface Avançada
- AJAX para operações sem reload
- Validação em tempo real
- Feedback visual imediato
- Responsividade completa

### Gestão de Estado
- Filtros persistentes por sessão
- Navegação por períodos
- Atualização automática de dados
- Cache inteligente

## 💡 Recursos Especiais

### 🇧🇷 Localização Brasileira
- Formatação de moeda em Real (R$)
- Separador decimal com vírgula
- Datas no formato brasileiro
- Interface em português

### 📱 Responsividade
- Layout adaptável para mobile
- Touch-friendly para dispositivos móveis
- Navegação otimizada para tablets
- Performance em diferentes resoluções

### 🔄 Automação
- Geração automática de transações recorrentes
- Cálculos automáticos de saldos
- Atualização em tempo real
- Sincronização de dados

### 📈 Relatórios e Análises
- Gráficos de receitas vs despesas
- Análise de despesas fixas vs variáveis
- Calendário visual de transações
- Resumos por período

## 🎯 Casos de Uso

### Controle Pessoal
- Gestão de salário e gastos mensais
- Controle de contas a pagar
- Planejamento de despesas recorrentes
- Acompanhamento de metas financeiras

### Planejamento Familiar
- Orçamento doméstico
- Controle de despesas compartilhadas
- Planejamento de gastos anuais
- Gestão de emergências

### Pequenos Negócios
- Controle de fluxo de caixa
- Gestão de receitas e despesas
- Planejamento financeiro
- Relatórios para tomada de decisão

## 🔮 Funcionalidades Futuras

### Em Desenvolvimento
- Categorização avançada de transações
- Relatórios em PDF
- Backup automático
- Integração com bancos

### Planejado
- App mobile nativo
- Múltiplas contas
- Metas de economia
- Alertas inteligentes

## 📊 Métricas do Sistema

### Performance
- Carregamento rápido (< 2s)
- Interface responsiva
- Operações em tempo real
- Otimização de consultas

### Usabilidade
- Interface intuitiva
- Feedback visual claro
- Navegação simplificada
- Acessibilidade básica

### Confiabilidade
- Validações robustas
- Tratamento de erros
- Backup de dados
- Segurança de sessão

---

## 🏆 Diferenciais

✅ **Interface Moderna**: Design clean e profissional  
✅ **Experiência Brasileira**: Formatação e localização nativas  
✅ **Automação Inteligente**: Transações recorrentes automáticas  
✅ **Feedback Visual**: Alertas e validações em tempo real  
✅ **Responsividade Total**: Funciona em qualquer dispositivo  
✅ **Performance Otimizada**: Carregamento rápido e operações fluidas  

**Sistema Financeiro** - Sua ferramenta completa para controle financeiro pessoal! 💰📊

