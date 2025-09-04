# IFPE - Sistemas Distribuídos
# Protótipo: Sistema de Notificações em Tempo Real de Pedidos

## Discente: Heitor Fidelis
## Docente: Luciano de Souza Cabral

## Tecnologias Utilizadas

- **Python 3.12**
- **FastAPI** – framework web assíncrono
- **aio_pika** – cliente assíncrono para RabbitMQ
- **RabbitMQ** – broker de mensagens
- **Tailwind CSS** – estilização do front-end
- **HTML + JavaScript** – interface de acompanhamento dos pedidos
- **Docker** - Containerização do RabbitMQ e aplicação

### Descrição da arquitetura

1. **Front-End**
   - Conecta ao backend via **WebSocket**.
   - Exibe em tempo real o status dos pedidos.
   - Permite simular vários pedidos com delays configuráveis.

2. **Backend (FastAPI)**
   - Recebe requisições de simulação de pedidos (`/simulate`).
   - Publica mensagens no **RabbitMQ** com status dos pedidos.
   - Escuta as mensagens do RabbitMQ e envia via WebSocket para todos os clientes conectados.

3. **RabbitMQ**
   - Fila de mensagens durável (`order_updates`) para garantir que nenhuma mensagem seja perdida.

## Funcionalidades

- Conexão **WebSocket** em tempo real.
- Simulação de múltiplos pedidos com **delays configuráveis**.
- Atualização de tabela de pedidos em tempo real.
- Filtragem de pedidos pelo **Order ID**.
- Exibição de status coloridos:
  - **Preparado** → amarelo
  - **Enviado** → azul
  - **Entregue** → verde

## Como executar o protótipo localmente

### 1. Clonar o repositório

```bash
git clone https://github.com/hfidelis/distributed-systems-ifpe
cd distributed-systems-ifpe/notification-prototype
```

### Via Docker (recomendado)
```bash
docker compose build app
docker compose up -d
```

### Ou manualmente:

### 1. Instalar dependências

```bash
cd app
pip install -r requirements.txt
```

### 2. Rodar o RabbitMQ
Via Docker (recomendado):

```bash
cd ..
docker compose up rabbitmq -d
```
Acesse o painel de controle do RabbitMQ em `http://localhost:15672` (usuário: `guest`, senha: `guest`).

### 3. Rodar o servidor FastAPI

```bash
cd app
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 4. Acessar a aplicação
Abra o navegador e acesse `http://localhost:8000` para ver a interface de acompanhamento dos pedidos.

