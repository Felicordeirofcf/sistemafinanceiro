# Guia de Integração com Google Calendar

## Visão Geral
A integração com o Google Calendar permite que suas despesas sejam automaticamente sincronizadas como eventos no seu calendário Google, facilitando o acompanhamento de vencimentos e evitando atrasos.

## Funcionalidades
- **Sincronização automática**: Cada despesa é criada como um evento no Google Calendar
- **Lembretes personalizados**: Receba notificações 2 dias antes por email e 1 dia antes por popup
- **Atualização dinâmica**: Alterações nas despesas são refletidas automaticamente no calendário
- **Visualização integrada**: Veja suas contas junto com seus outros compromissos pessoais

## Configuração Inicial

### 1. Criar projeto no Google Cloud Console
1. Acesse [Google Cloud Console](https://console.cloud.google.com/)
2. Crie um novo projeto
3. Habilite a Google Calendar API
4. Configure a tela de consentimento OAuth
5. Crie credenciais OAuth 2.0 para aplicativo web
6. Adicione a URL de redirecionamento: `https://seu-dominio.onrender.com/gcal/oauth2callback`
7. Baixe o arquivo JSON de credenciais

### 2. Configurar o arquivo de credenciais
1. Renomeie o arquivo baixado para `client_secret.json`
2. Substitua o arquivo de exemplo em `src/client_secret.json` pelo seu arquivo real
3. Certifique-se de que o arquivo contém seu client_id e client_secret corretos

### 3. Configurar variáveis de ambiente no Render
1. No painel do Render, vá para seu serviço web
2. Acesse a seção "Environment"
3. Adicione a variável `GOOGLE_APPLICATION_CREDENTIALS` com o valor `/opt/render/project/src/client_secret.json`

## Como usar

### Conectar sua conta Google
1. Acesse a página "Integração Google Calendar" no menu do sistema
2. Clique no botão "Conectar com Google"
3. Siga as instruções para autorizar o acesso ao seu calendário
4. Após autorização, você retornará ao sistema automaticamente

### Gerenciar a sincronização
- **Ativar/Pausar**: Use o botão na página de integração para ativar ou pausar a sincronização
- **Sincronizar manualmente**: Clique em "Sincronizar Agora" para forçar a sincronização de todas as despesas
- **Desconectar**: Use o botão "Desconectar Conta" para remover a integração

## Comportamento da sincronização

### Novas despesas
- Quando uma nova despesa é criada, um evento é automaticamente adicionado ao seu Google Calendar
- O evento é criado na data de vencimento da despesa
- O título do evento é a descrição da despesa
- A descrição do evento inclui o valor e a categoria

### Edição de despesas
- Quando uma despesa é editada, o evento correspondente no calendário é atualizado
- Alterações na data, valor, descrição ou categoria são refletidas no evento

### Exclusão de despesas
- Quando uma despesa é excluída, o evento correspondente no calendário também é removido

### Marcação de pagamento
- Quando uma despesa é marcada como paga, o evento no calendário é atualizado para refletir o status

## Solução de problemas

### Erro de autenticação
- Verifique se o arquivo `client_secret.json` está correto e atualizado
- Tente desconectar e reconectar sua conta Google

### Eventos não aparecem no calendário
- Verifique se a sincronização está ativada na página de integração
- Clique em "Sincronizar Agora" para forçar a sincronização
- Verifique se você tem permissões de escrita no calendário selecionado

### Erro ao conectar conta Google
- Verifique se a URL de redirecionamento no Google Cloud Console está correta
- Certifique-se de que a API do Google Calendar está habilitada no projeto
