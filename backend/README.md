# Multi-Agent NF-e System - Backend

Sistema multi-agente de IA para processamento de notas fiscais eletrônicas (NF-e) usando CrewAI, GPT-4o-mini e Supabase.

## � Índiice

- [Visão Geral](#visão-geral)
- [Arquitetura](#arquitetura)
- [Requisitos](#requisitos)
- [Instalação](#instalação)
- [Configuração](#configuração)
- [Executando a Aplicação](#executando-a-aplicação)
- [API Endpoints](#api-endpoints)
- [Sistema de Agentes](#sistema-de-agentes)
- [Sistema de Memória](#sistema-de-memória)
- [Processamento em Lote](#processamento-em-lote)
- [Testes](#testes)
- [Troubleshooting](#troubleshooting)

## 🎯 Visão Geral

O Multi-Agent NF-e System é uma aplicação backend construída em Python que utiliza **CrewAI** para orquestrar três agentes especializados baseados em GPT-4o-mini. Os agentes trabalham em equipe para:

- **Processar notas fiscais eletrônicas** em lote a partir de arquivos XML
- **Responder perguntas** dos usuários através de chat interativo com linguagem natural
- **Consultar dados** no banco de dados Supabase PostgreSQL
- **Manter contexto** conversacional com memória RAG (Retrieval-Augmented Generation)

### Principais Funcionalidades

✅ **Chat Interativo**: Faça perguntas em linguagem natural sobre suas notas fiscais  
✅ **Processamento em Lote**: Importe múltiplos XMLs de NF-e automaticamente  
✅ **Multi-Agente**: Três agentes especializados trabalhando em conjunto  
✅ **Memória Contextual**: Sistema RAG com busca semântica para manter contexto  
✅ **API REST**: Interface completa para integração com frontend  
✅ **Logging Estruturado**: Rastreamento detalhado de todas as operações  

## 🏗️ Arquitetura

### Componentes Principais

```
┌─────────────┐
│   Frontend  │
└──────┬──────┘
       │ HTTP
┌──────▼──────────────────────────────────────┐
│         FastAPI REST API                    │
│  ┌────────────┐      ┌──────────────────┐  │
│  │ Chat Route │      │ Batch Route      │  │
│  └─────┬──────┘      └────────┬─────────┘  │
└────────┼─────────────────────┼─────────────┘
         │                     │
    ┌────▼─────────────────────▼────┐
    │     Sistema de Agentes        │
    │  ┌──────────────────────────┐ │
    │  │   Coordenador (Manager)  │ │
    │  └────┬──────────────┬──────┘ │
    │       │              │         │
    │  ┌────▼────┐   ┌────▼────┐   │
    │  │   SQL   │   │ Conversa│   │
    │  │Specialist│   │Specialist│   │
    │  └─────────┘   └─────────┘   │
    └───────────────────────────────┘
         │              │
    ┌────▼──────┐  ┌───▼────────┐
    │  Memória  │  │  Supabase  │
    │  (RAG)    │  │ PostgreSQL │
    └───────────┘  └────────────┘
```

### Agentes CrewAI

1. **Coordenador** (Manager)
   - Analisa intenção das mensagens
   - Delega tarefas aos agentes especializados
   - Gerencia fluxo de comunicação

2. **SQL Specialist**
   - Gera consultas SQL otimizadas
   - Executa queries no Supabase
   - Retorna dados estruturados

3. **Conversation Specialist**
   - Formata respostas em linguagem natural
   - Mantém tom profissional e amigável
   - Responde perguntas gerais sobre o sistema

## 📦 Requisitos

### Software Necessário

- **Python 3.12.x** (recomendado para melhor compatibilidade)
- **pip** (gerenciador de pacotes Python)
- **Conta OpenAI** com API key
- **Projeto Supabase** configurado

### Dependências Principais

- `crewai>=0.80.0` - Framework multi-agente
- `fastapi>=0.104.0` - Framework web
- `openai>=1.0.0` - Cliente OpenAI
- `chromadb>=0.4.0` - Banco vetorial para RAG
- `psycopg2-binary>=2.9.9` - Driver PostgreSQL

Veja `requirements.txt` para lista completa.

## 🚀 Instalação

### 1. Clone o Repositório

```bash
git clone <repository-url>
cd backend
```

### 2. Crie um Ambiente Virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Instale as Dependências

```bash
pip install -r requirements.txt
```

### 4. Verifique a Instalação

```bash
python -c "import crewai; print(f'CrewAI version: {crewai.__version__}')"
```

## ⚙️ Configuração

### 1. Crie o Arquivo .env

Copie o arquivo de exemplo e configure suas credenciais:

```bash
cp .env.example .env
```

### 2. Configure as Variáveis de Ambiente

Edite o arquivo `.env` com suas credenciais:

```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_MODEL=gpt-4o-mini
OPENAI_TEMPERATURE=0.7

# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-supabase-service-role-key-here

# Application Configuration
APP_ENV=development
LOG_LEVEL=INFO

# Chat Memory Configuration
MAX_CHAT_HISTORY=4

# Batch Processing Configuration
XML_FOLDER=xml_nf
MAX_CONCURRENT_UPLOADS=5

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
```

### 3. Obtenha suas Credenciais

#### OpenAI API Key

1. Acesse [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Faça login ou crie uma conta
3. Clique em "Create new secret key"
4. Copie a chave e cole em `OPENAI_API_KEY`

#### Supabase Credentials

1. Acesse [https://supabase.com/dashboard](https://supabase.com/dashboard)
2. Selecione seu projeto
3. Vá em **Settings** → **API**
4. Copie:
   - **URL**: Cole em `SUPABASE_URL`
   - **service_role key**: Cole em `SUPABASE_SERVICE_KEY`

### 4. Verifique o Banco de Dados

O banco de dados já deve estar configurado no Supabase com o schema completo. Verifique se as seguintes tabelas existem:

- `empresas`
- `notas_fiscais`
- `nf_itens`
- `nf_pagamentos`
- `nf_transporte`

O schema completo está em `database/schema_nfe_completo.sql`.

## 🏃 Executando a Aplicação

### Modo Desenvolvimento

```bash
# Com reload automático
python main.py

# Ou usando uvicorn diretamente
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Modo Produção

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Verificar se está Funcionando

Acesse no navegador:

- **API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Health Check**: [http://localhost:8000/health](http://localhost:8000/health)
- **Detailed Health**: [http://localhost:8000/health/detailed](http://localhost:8000/health/detailed)

## 📡 API Endpoints

### Chat Endpoints

#### POST /api/chat

Processa uma mensagem do usuário através do sistema multi-agente.

**Request:**

```json
{
  "session_id": "user-123-session",
  "message": "Quantas notas fiscais foram emitidas este mês?"
}
```

**Response:**

```json
{
  "session_id": "user-123-session",
  "message": "Foram emitidas 42 notas fiscais este mês, totalizando R$ 125.430,50.",
  "agent_used": "coordenador",
  "timestamp": "2025-10-27T10:30:00",
  "metadata": {
    "processing_time_ms": 1250,
    "history_messages": 4
  }
}
```

**Exemplo com cURL:**

```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test-session",
    "message": "Qual o valor total das notas fiscais?"
  }'
```

**Exemplo com Python:**

```python
import requests

response = requests.post(
    "http://localhost:8000/api/chat",
    json={
        "session_id": "user-123",
        "message": "Mostre as últimas 5 notas fiscais"
    }
)

print(response.json())
```

#### GET /api/chat/history/{session_id}

Recupera o histórico de conversação de uma sessão.

**Response:**

```json
{
  "session_id": "user-123-session",
  "messages": [
    {
      "role": "user",
      "content": "Olá",
      "timestamp": "2025-10-27T10:29:00"
    },
    {
      "role": "assistant",
      "content": "Olá! Como posso ajudar?",
      "timestamp": "2025-10-27T10:29:01"
    }
  ],
  "message_count": 2
}
```

#### DELETE /api/chat/history/{session_id}

Limpa o histórico de conversação de uma sessão.

**Response:**

```json
{
  "session_id": "user-123-session",
  "cleared": true,
  "message": "Chat history cleared successfully"
}
```

### Batch Processing Endpoints

#### POST /api/batch/upload

Inicia o processamento em lote de arquivos XML.

**Request:**

```json
{
  "xml_folder": "xml_nf",
  "max_concurrent": 5
}
```

**Response:**

```json
{
  "job_id": "batch-20251027-103000-abc123",
  "status": "running",
  "total_files": 10,
  "successful": 0,
  "failed": 0,
  "errors": [],
  "duration_seconds": null,
  "started_at": "2025-10-27T10:30:00",
  "completed_at": null
}
```

**Exemplo com cURL:**

```bash
curl -X POST "http://localhost:8000/api/batch/upload" \
  -H "Content-Type: application/json" \
  -d '{
    "xml_folder": "xml_nf",
    "max_concurrent": 5
  }'
```

#### GET /api/batch/status/{job_id}

Consulta o status de um job de processamento em lote.

**Response:**

```json
{
  "job_id": "batch-20251027-103000-abc123",
  "status": "running",
  "progress": 60,
  "total": 10,
  "processed": 6,
  "successful": 5,
  "failed": 1,
  "current_file": null,
  "errors": [
    {
      "file": "nota_003.xml",
      "error": "XML malformado"
    }
  ],
  "started_at": "2025-10-27T10:30:00",
  "estimated_completion": null
}
```

#### GET /api/batch/jobs

Lista todos os jobs de processamento em lote.

**Query Parameters:**
- `status_filter` (opcional): Filtrar por status (pending, running, completed, failed)
- `limit` (opcional): Número máximo de jobs a retornar (padrão: 50)

**Response:**

```json
{
  "jobs": [
    {
      "job_id": "batch-20251027-103000-abc123",
      "status": "completed",
      "total_files": 10,
      "successful": 8,
      "failed": 2,
      "started_at": "2025-10-27T10:30:00",
      "completed_at": "2025-10-27T10:31:00"
    }
  ],
  "total_count": 1
}
```

### Health Check Endpoints

#### GET /health

Verificação básica de saúde da API.

**Response:**

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "development"
}
```

#### GET /health/detailed

Verificação detalhada com informações de todos os componentes.

**Response:**

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "development",
  "services": {
    "crewai": {
      "initialized": true,
      "agents": ["coordenador", "sql_specialist", "conversation_specialist"],
      "model": "gpt-4o-mini",
      "process": "hierarchical",
      "memory_enabled": true
    },
    "memory": {
      "initialized": true,
      "active_sessions": 5,
      "total_cached_messages": 42
    },
    "batch_processor": {
      "initialized": true,
      "active_jobs": 1,
      "total_jobs": 10
    }
  }
}
```

## 🤖 Sistema de Agentes

### Coordenador (Manager Agent)

O agente coordenador é o ponto central do sistema. Ele:

- Analisa a intenção de cada mensagem do usuário
- Decide qual agente especializado deve processar a requisição
- Gerencia o fluxo de comunicação entre agentes
- Retorna a resposta final ao usuário

**Quando usar:**
- Todas as mensagens passam pelo coordenador primeiro
- Ele decide automaticamente se precisa consultar o banco ou apenas conversar

### SQL Specialist

Especialista em consultas ao banco de dados. Ele:

- Gera queries SQL otimizadas e seguras
- Executa consultas no Supabase PostgreSQL
- Retorna dados estruturados
- **Apenas executa SELECT** (nunca modifica dados)

**Quando é acionado:**
- Perguntas sobre dados específicos de notas fiscais
- Consultas que requerem agregações ou cálculos
- Buscas por informações no banco de dados

**Exemplos de perguntas:**
- "Quantas notas fiscais foram emitidas este mês?"
- "Qual o valor total das notas do fornecedor X?"
- "Mostre as últimas 10 notas fiscais"

### Conversation Specialist

Especialista em comunicação natural. Ele:

- Formata respostas em linguagem natural e amigável
- Transforma dados técnicos em explicações claras
- Responde perguntas gerais sobre o sistema
- Mantém tom profissional mas acessível

**Quando é acionado:**
- Perguntas gerais sobre o sistema
- Saudações e conversas informais
- Formatação de respostas com dados do SQL Specialist

**Exemplos de perguntas:**
- "Olá, como você funciona?"
- "O que você pode fazer?"
- "Como faço para importar notas fiscais?"

## 💾 Sistema de Memória

O sistema utiliza memória RAG (Retrieval-Augmented Generation) com duas camadas:

### 1. Memória de Curto Prazo (Cache)

- Mantém as **últimas 4 mensagens** (2 interações) em cache
- Acesso rápido para contexto imediato
- Configurável via `MAX_CHAT_HISTORY`

### 2. Memória de Longo Prazo (RAG)

- Armazena todas as mensagens em banco vetorial (ChromaDB)
- Busca semântica para recuperar contexto relevante
- Permite referências a conversas antigas

### Como Funciona

```python
# 1. Usuário envia mensagem
"Qual o valor total das notas?"

# 2. Sistema recupera contexto
# - Cache: últimas 2 interações
# - RAG: mensagens semanticamente similares

# 3. Agente processa com contexto completo
# - Histórico recente
# - Informações relevantes de conversas antigas

# 4. Resposta contextualizada
"Com base nas notas que consultamos anteriormente, 
o valor total é R$ 125.430,50."
```

### Gerenciamento de Sessões

Cada usuário tem uma `session_id` única que:
- Isola conversas entre diferentes usuários
- Permite múltiplas sessões simultâneas
- Mantém contexto independente por sessão

## 📦 Processamento em Lote

### Como Funciona

1. **Upload**: Coloque arquivos XML na pasta `xml_nf/`
2. **Iniciar**: Faça POST para `/api/batch/upload`
3. **Monitorar**: Consulte status via `/api/batch/status/{job_id}`
4. **Resultado**: Receba relatório com sucessos e falhas

### Características

- ✅ **Processamento Assíncrono**: Não bloqueia a API
- ✅ **Controle de Concorrência**: Configura quantos XMLs processar simultaneamente
- ✅ **Tolerância a Falhas**: Continua processando mesmo se alguns arquivos falharem
- ✅ **Relatório Detalhado**: Lista de sucessos e erros com detalhes
- ✅ **Rastreamento**: Acompanhe progresso em tempo real

### Exemplo Completo

```python
import requests
import time

# 1. Iniciar processamento
response = requests.post(
    "http://localhost:8000/api/batch/upload",
    json={"xml_folder": "xml_nf", "max_concurrent": 5}
)
job_id = response.json()["job_id"]
print(f"Job iniciado: {job_id}")

# 2. Monitorar progresso
while True:
    status = requests.get(
        f"http://localhost:8000/api/batch/status/{job_id}"
    ).json()
    
    print(f"Progresso: {status['progress']}% "
          f"({status['processed']}/{status['total']})")
    
    if status['status'] in ['completed', 'failed']:
        break
    
    time.sleep(2)

# 3. Resultado final
print(f"\nConcluído!")
print(f"Sucessos: {status['successful']}")
print(f"Falhas: {status['failed']}")
if status['errors']:
    print("\nErros:")
    for error in status['errors']:
        print(f"  - {error['file']}: {error['error']}")
```

## 🧪 Testes

### Executar Todos os Testes

```bash
pytest
```

### Executar Testes Específicos

```bash
# Testes unitários
pytest tests/unit/

# Testes de integração
pytest tests/integration/

# Teste específico
pytest tests/unit/test_agents.py

# Com verbose
pytest -v

# Com coverage
pytest --cov=. --cov-report=html
```

### Teste Manual do Sistema

Use o script de teste manual:

```bash
python test_system.py
```

Este script testa:
- ✅ Processamento em lote de XMLs
- ✅ Chat com perguntas sobre NF-e
- ✅ Memória de contexto
- ✅ Delegação entre agentes
- ✅ Uso correto das ferramentas (Tools)

Veja `TEST_SYSTEM_README.md` para mais detalhes.

## 🔧 Troubleshooting

### Erro: "Missing required environment variables"

**Problema**: Variáveis de ambiente não configuradas.

**Solução**:
```bash
# Verifique se o arquivo .env existe
ls -la .env

# Verifique se as variáveis estão definidas
cat .env | grep OPENAI_API_KEY
cat .env | grep SUPABASE_URL

# Recrie o .env se necessário
cp .env.example .env
# Edite e adicione suas credenciais
```

### Erro: "OpenAI API error"

**Problema**: Problemas com a API da OpenAI.

**Possíveis causas**:
1. API key inválida ou expirada
2. Sem créditos na conta OpenAI
3. Rate limit excedido

**Solução**:
```bash
# Verifique sua API key
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"

# Verifique créditos em:
# https://platform.openai.com/account/billing
```

### Erro: "Database connection failed"

**Problema**: Não consegue conectar ao Supabase.

**Solução**:
```bash
# Verifique as credenciais
echo $SUPABASE_URL
echo $SUPABASE_SERVICE_KEY

# Teste a conexão
curl $SUPABASE_URL/rest/v1/ \
  -H "apikey: $SUPABASE_SERVICE_KEY"

# Verifique se o projeto está ativo no Supabase Dashboard
```

### Erro: "CrewAI initialization failed"

**Problema**: Falha ao inicializar o CrewAI.

**Solução**:
```bash
# Reinstale o CrewAI
pip uninstall crewai crewai-tools
pip install crewai>=0.80.0 crewai-tools>=0.12.0

# Verifique a versão
python -c "import crewai; print(crewai.__version__)"

# Limpe o cache do Python
find . -type d -name "__pycache__" -exec rm -r {} +
```

### Performance Lenta

**Problema**: Respostas demoram muito.

**Soluções**:
1. **Reduza a temperatura**: `OPENAI_TEMPERATURE=0.3`
2. **Use modelo mais rápido**: `OPENAI_MODEL=gpt-3.5-turbo`
3. **Limite histórico**: `MAX_CHAT_HISTORY=2`
4. **Aumente workers**: `uvicorn main:app --workers 4`

### Memória Alta

**Problema**: Aplicação consumindo muita memória.

**Soluções**:
```bash
# Limpe sessões antigas
curl -X POST "http://localhost:8000/api/batch/cleanup"

# Reduza histórico de chat
# No .env:
MAX_CHAT_HISTORY=2

# Reinicie a aplicação periodicamente
```

## 📚 Documentação Adicional

- **[Guia de Teste do Sistema](TEST_SYSTEM_README.md)**: Como testar o sistema completo
- **[Guia de Performance](PERFORMANCE_FIX.md)**: Otimizações e melhorias de performance
- **[Configuração de Memória](SETUP_MEMORY.md)**: Detalhes do sistema de memória RAG
- **[Configuração SQL Tool](SETUP_SQL_TOOL.md)**: Como funcionam as ferramentas SQL
- **[Quick Start Testing](QUICK_START_TESTING.md)**: Testes rápidos para validação

## 🤝 Contribuindo

Para contribuir com o projeto:

1. Faça fork do repositório
2. Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença especificada no arquivo LICENSE na raiz do repositório.

## 📞 Suporte

Para questões e suporte:

- Abra uma issue no repositório
- Consulte a documentação em `/docs`
- Verifique os logs em modo DEBUG: `LOG_LEVEL=DEBUG`

---

**Desenvolvido com ❤️ usando CrewAI, FastAPI e OpenAI**
