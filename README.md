# RabbitCRUD - Sistema de CRUD com RabbitMQ e MongoDB

Sistema completo de CRUD (Create, Read, Update, Delete) usando Flask, MongoDB e RabbitMQ, com monitoramento em tempo real e geração automática de dados.

## 🏗️ Arquitetura

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│     API     │───▶│  RabbitMQ   │───▶│   Worker    │
│   (Flask)   │    │  (Message   │    │ (Processor) │
│             │    │   Broker)   │    │             │
└─────────────┘    └─────────────┘    └─────────────┘
       │                                        │
       ▼                                        ▼
┌─────────────┐                        ┌─────────────┐
│  MongoDB    │◀───────────────────────│  MongoDB    │
│ (Database)  │                        │ (Database)  │
└─────────────┘                        └─────────────┘
       │
       ▼
┌─────────────┐
│   Monitor   │
│ (Dashboard) │
└─────────────┘
```

## 🚀 Funcionalidades

- **API REST** completa com Flask
- **Banco de dados** MongoDB
- **Message Broker** RabbitMQ
- **Worker** para processamento assíncrono
- **Monitor em tempo real** com dashboard web
- **Gerador de dados** automático
- **Testes automatizados** com pytest
- **CI/CD** com GitHub Actions

## 📋 Pré-requisitos

- Python 3.8+
- Docker e Docker Compose
- Git

## 🛠️ Instalação

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/RabbitCRUD.git
cd RabbitCRUD
```

### 2. Instale as dependências

```bash
pip install -r requirements.txt
pip install -r api/requirements.txt
pip install -r worker/requirements.txt
pip install -r data_generator/requirements.txt
```

### 3. Inicie os serviços Docker

```bash
docker-compose -f docker-services.yml up -d
```

## 🎯 Como Executar

### Opção 1: Execução Manual

1. **Inicie o Worker:**
```bash
cd worker
python worker.py
```

2. **Inicie a API:**
```bash
cd api
python app.py
```

3. **Inicie o Monitor (opcional):**
```bash
python realtime_monitor.py
```

4. **Gere dados de teste:**
```bash
cd data_generator
python generator_local.py
```

### Opção 2: Script Automatizado

```bash
python docker-services.py start
```

## 📡 Endpoints da API

### Health Check
```http
GET /health
```

### Usuários

#### Listar todos os usuários
```http
GET /api/users
```

#### Criar usuário
```http
POST /api/users
Content-Type: application/json

{
  "name": "João Silva",
  "email": "joao@example.com",
  "value": 100
}
```

#### Atualizar usuário
```http
PUT /api/users/{name}
Content-Type: application/json

{
  "email": "novo@example.com",
  "value": 200
}
```

#### Deletar usuário
```http
DELETE /api/users/{name}
```

#### Limpar todos os usuários
```http
DELETE /api/clear-all
```

## 🌐 URLs Disponíveis

- **API**: http://localhost:5000
- **Monitor em Tempo Real**: http://localhost:8000
- **RabbitMQ Management**: http://localhost:15672 (guest/guest)
- **MongoDB**: mongodb://localhost:27017

## 🧪 Testes

Execute os testes automatizados:

```bash
pytest tests/ -v
```

### Testes disponíveis:
- `test_api.py` - Testes da API REST
- `test_repository.py` - Testes do repositório MongoDB

## 📊 Monitoramento

O sistema inclui um dashboard de monitoramento em tempo real que mostra:

- Lista de usuários no banco
- Histórico de operações
- Estatísticas de uso
- Controles para gerar e limpar dados

Acesse: http://localhost:8000

## 🔧 Configuração

### Variáveis de Ambiente

As configurações estão em `api/config.py` e `worker/config.py`:

```python
MONGO_URI = "mongodb://localhost:27017"
RABBITMQ_HOST = "localhost"
QUEUE_NAME = "user_operations"
```

### Docker Services

Os serviços externos (MongoDB e RabbitMQ) são gerenciados via Docker:

```yaml
# docker-services.yml
services:
  mongo:
    image: mongo:latest
    ports:
      - "27017:27017"
  
  rabbitmq:
    image: rabbitmq:3-management
    ports:
      - "5672:5672"
      - "15672:15672"
```

## 🏃‍♂️ Geração de Dados

O gerador de dados cria usuários aleatórios e executa operações CRUD:

```bash
cd data_generator
python generator_local.py
```

Funcionalidades:
- Criação de usuários com dados aleatórios
- Atualização de usuários existentes
- Exclusão de usuários
- Operações contínuas com delay configurável

## 🐳 Docker

### Serviços Externos
```bash
# Iniciar MongoDB e RabbitMQ
docker-compose -f docker-services.yml up -d

# Parar serviços
docker-compose -f docker-services.yml down
```

### Gerenciamento de Serviços
```bash
# Verificar status
docker ps

# Ver logs
docker-compose -f docker-services.yml logs

# Reiniciar serviços
docker-compose -f docker-services.yml restart
```

## 📁 Estrutura do Projeto

```
RabbitCRUD/
├── api/                    # API Flask
│   ├── controllers/        # Controladores REST
│   ├── models/            # Modelos Pydantic
│   ├── repositories/      # Camada de dados
│   ├── services/          # Lógica de negócio
│   └── messaging/         # Producer RabbitMQ
├── worker/                # Worker de processamento
│   ├── processing/        # Handler de mensagens
│   ├── repositories/      # Repositório do worker
│   └── monitoring/        # Publisher de monitoramento
├── data_generator/        # Gerador de dados
├── tests/                 # Testes automatizados
├── realtime_monitor.py    # Dashboard de monitoramento
├── docker-services.yml    # Serviços Docker
└── requirements.txt       # Dependências principais
```

## 🔄 Fluxo de Dados

1. **Cliente** faz requisição para a **API**
2. **API** valida dados e publica mensagem no **RabbitMQ**
3. **Worker** consome mensagem e processa no **MongoDB**
4. **Monitor** exibe dados em tempo real
5. **Gerador** cria dados de teste automaticamente

## 🛡️ Tratamento de Erros

- Validação de dados com Pydantic
- Tratamento de erros de serialização JSON
- Conversão automática de ObjectId para string
- Logs detalhados para debugging

## 🚀 Deploy

### Desenvolvimento
```bash
python docker-services.py start
cd api && python app.py
cd worker && python worker.py
```

### Produção
Use um servidor WSGI como Gunicorn:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 api.app:app
```

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 👥 Autores

- Hercules Freitas - *Desenvolvimento inicial* - [herculesfj](https://github.com/herculesfj)

## 🙏 Agradecimentos

- Flask para a API web
- MongoDB para o banco de dados
- RabbitMQ para o message broker
- Pytest para os testes
- Docker para containerização
