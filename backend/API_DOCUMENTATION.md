# API Documentation - Multi-Agent NF-e System

Documentação completa dos endpoints da API REST do sistema multi-agente de NF-e.

## 📋 Índice

- [Visão Geral](#visão-geral)
- [Autenticação](#autenticação)
- [Base URL](#base-url)
- [Formato de Resposta](#formato-de-resposta)
- [Códigos de Status HTTP](#códigos-de-status-http)
- [Endpoints de Chat](#endpoints-de-chat)
- [Endpoints de Batch](#endpoints-de-batch)
- [Endpoints de Health](#endpoints-de-health)
- [Tratamento de Erros](#tratamento-de-erros)
- [Exemplos de Uso](#exemplos-de-uso)

## 🌐 Visão Geral

A API do Multi-Agent NF-e System fornece endpoints RESTful para:

- **Chat interativo** com sistema multi-agente
- **Processamento em lote** de arquivos XML de NF-e
- **Gerenciamento de sessões** e histórico de conversação
- **Monitoramento** de jobs e status do sistema

### Tecnologias

- **Framework**: FastAPI
- **Formato**: JSON
- **Protocolo**: HTTP/HTTPS
- **Documentação Interativa**: Swagger UI e ReDoc

## 🔐 Autenticação

Atualmente, a API não requer autenticação. Em produção, recomenda-se implementar:

- API Keys
- OAuth 2.0
- JWT Tokens

## 🌍 Base URL

### Desenvolvimento
```
http://localhost:8000
```

### Produção
```
https://your-domain.com
```

## 📦 Formato de Resposta

Todas as respostas são em formato JSON.

### Resposta de Sucesso

```json
{
  "campo1": "valor1",
  "campo2": "valor2"
}
```

### Resposta de Erro

```json
{
  "error": {
    "code": "error_code",
    "message": "Mensagem descritiva do erro",
    "details": {
      "campo": "informação adicional"
    }
  }
}
```

## 📊 Códigos de Status HTTP

| Código | Significado | Descrição |
|--------|-------------|-----------|
| 200 | OK | Requisição bem-sucedida |
| 202 | Accepted | Requisição aceita para processamento assíncrono |
| 400 | Bad Request | Dados de entrada inválidos |
| 404 | Not Found | Recurso não encontrado |
| 422 | Unprocessable Entity | Erro de validação |
| 500 | Internal Server Error | Erro interno do servidor |
| 502 | Bad Gateway | Erro ao comunicar com serviço externo (OpenAI) |

---

## 💬 Endpoints de Chat

### POST /api/chat

Processa uma mensagem do usuário através do sistema multi-agente.

#### Request

**Headers:**
```
Content-Type: application/json
```

**Body:**
```json
{
  "session_id": "string (1-100 caracteres, obrigatório)",
  "message": "string (1-5000 caracteres, obrigatório)"
}
```

**Campos:**

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| session_id | string | Sim | ID único da sessão do usuário |
| message | string | Sim | Mensagem do usuário |

#### Response

**Status:** 200 OK

```json
{
  "session_id": "user-123-session",
  "message": "Foram emitidas 42 notas fiscais este mês, totalizando R$ 125.430,50.",
  "agent_used": "coordenador",
  "timestamp": "2025-10-27T10:30:00",
  "metadata": {
    "processing_time_ms": 1250,
    "history_messages": 4,
    "message_length": 67
  }
}
```

**Campos de Resposta:**

| Campo | Tipo | Descrição |
|-------|------|-----------|
| session_id | string | ID da sessão |
| message | string | Resposta do sistema |
| agent_used | string | Agente que processou (coordenador, sql_specialist, conversation_specialist) |
| timestamp | datetime | Timestamp da resposta |
| metadata | object | Metadados do processamento |

#### Exemplos

**cURL:**
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "user-123",
    "message": "Quantas notas fiscais foram emitidas este mês?"
  }'
```

**Python:**
```python
import requests

response = requests.post(
    "http://localhost:8000/api/chat",
    json={
        "session_id": "user-123",
        "message": "Quantas notas fiscais foram emitidas este mês?"
    }
)

data = response.json()
print(f"Resposta: {data['message']}")
print(f"Tempo: {data['metadata']['processing_time_ms']}ms")
```

**JavaScript:**
```javascript
fetch('http://localhost:8000/api/chat', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    session_id: 'user-123',
    message: 'Quantas notas fiscais foram emitidas este mês?'
  })
})
.then(response => response.json())
.then(data => {
  console.log('Resposta:', data.message);
  console.log('Agente:', data.agent_used);
});
```

#### Erros Possíveis

| Status | Código | Descrição |
|--------|--------|-----------|
| 400 | validation_error | Dados de entrada inválidos |
| 500 | agent_error | Erro ao processar mensagem |
| 502 | openai_api_error | Erro ao comunicar com OpenAI |

---

### GET /api/chat/history/{session_id}

Recupera o histórico de conversação de uma sessão.

#### Request

**Path Parameters:**

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| session_id | string | ID da sessão |

#### Response

**Status:** 200 OK

```json
{
  "session_id": "user-123-session",
  "messages": [
    {
      "role": "user",
      "content": "Olá",
      "timestamp": "2025-10-27T10:29:00",
      "metadata": {}
    },
    {
      "role": "assistant",
      "content": "Olá! Como posso ajudar?",
      "timestamp": "2025-10-27T10:29:01",
      "metadata": {
        "agent_used": "conversation_specialist"
      }
    }
  ],
  "message_count": 2
}
```

#### Exemplos

**cURL:**
```bash
curl "http://localhost:8000/api/chat/history/user-123"
```

**Python:**
```python
import requests

response = requests.get(
    "http://localhost:8000/api/chat/history/user-123"
)

history = response.json()
for msg in history['messages']:
    print(f"{msg['role']}: {msg['content']}")
```

#### Erros Possíveis

| Status | Código | Descrição |
|--------|--------|-----------|
| 404 | not_found | Sessão não encontrada |
| 500 | internal_error | Erro interno |

---

### DELETE /api/chat/history/{session_id}

Limpa o histórico de conversação de uma sessão.

#### Request

**Path Parameters:**

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| session_id | string | ID da sessão |

**Query Parameters:**

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| clear_vectors | boolean | false | Limpar também dados vetorizados (RAG) |

#### Response

**Status:** 200 OK

```json
{
  "session_id": "user-123-session",
  "cleared": true,
  "message": "Chat history cleared successfully"
}
```

#### Exemplos

**cURL:**
```bash
# Limpar apenas cache
curl -X DELETE "http://localhost:8000/api/chat/history/user-123"

# Limpar cache e vetores
curl -X DELETE "http://localhost:8000/api/chat/history/user-123?clear_vectors=true"
```

**Python:**
```python
import requests

# Limpar histórico completo
response = requests.delete(
    "http://localhost:8000/api/chat/history/user-123",
    params={"clear_vectors": True}
)

print(response.json()['message'])
```

---

### GET /api/chat/stats

Obtém estatísticas sobre o uso de memória.

#### Response

**Status:** 200 OK

```json
{
  "total_sessions": 10,
  "total_cached_messages": 40,
  "storage_directory": "memory_storage",
  "memory_systems": {
    "cache": "active",
    "rag": "active"
  }
}
```

#### Exemplos

**cURL:**
```bash
curl "http://localhost:8000/api/chat/stats"
```

---

## 📦 Endpoints de Batch

### POST /api/batch/upload

Inicia o processamento em lote de arquivos XML de NF-e.

#### Request

**Headers:**
```
Content-Type: application/json
```

**Body:**
```json
{
  "xml_folder": "string (padrão: xml_nf)",
  "max_concurrent": "integer (1-20, opcional)"
}
```

**Campos:**

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| xml_folder | string | Não | Pasta contendo XMLs (padrão: xml_nf) |
| max_concurrent | integer | Não | Máximo de uploads simultâneos (padrão: 5) |

#### Response

**Status:** 202 Accepted

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

**Campos de Resposta:**

| Campo | Tipo | Descrição |
|-------|------|-----------|
| job_id | string | ID único do job |
| status | string | Status atual (pending, running, completed, failed) |
| total_files | integer | Total de arquivos encontrados |
| successful | integer | Arquivos processados com sucesso |
| failed | integer | Arquivos que falharam |
| errors | array | Lista de erros |
| duration_seconds | float | Duração total (quando completo) |
| started_at | datetime | Timestamp de início |
| completed_at | datetime | Timestamp de conclusão |

#### Exemplos

**cURL:**
```bash
curl -X POST "http://localhost:8000/api/batch/upload" \
  -H "Content-Type: application/json" \
  -d '{
    "xml_folder": "xml_nf",
    "max_concurrent": 5
  }'
```

**Python:**
```python
import requests

response = requests.post(
    "http://localhost:8000/api/batch/upload",
    json={
        "xml_folder": "xml_nf",
        "max_concurrent": 5
    }
)

job = response.json()
print(f"Job iniciado: {job['job_id']}")
print(f"Total de arquivos: {job['total_files']}")
```

**JavaScript:**
```javascript
fetch('http://localhost:8000/api/batch/upload', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    xml_folder: 'xml_nf',
    max_concurrent: 5
  })
})
.then(response => response.json())
.then(job => {
  console.log('Job ID:', job.job_id);
  console.log('Total files:', job.total_files);
});
```

#### Erros Possíveis

| Status | Código | Descrição |
|--------|--------|-----------|
| 400 | validation_error | Pasta não encontrada ou sem XMLs |
| 500 | batch_processing_error | Erro ao iniciar processamento |

---

### GET /api/batch/status/{job_id}

Consulta o status de um job de processamento em lote.

#### Request

**Path Parameters:**

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| job_id | string | ID do job |

#### Response

**Status:** 200 OK

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
      "error": "XML malformado: tag de fechamento ausente"
    }
  ],
  "started_at": "2025-10-27T10:30:00",
  "estimated_completion": null
}
```

**Campos de Resposta:**

| Campo | Tipo | Descrição |
|-------|------|-----------|
| job_id | string | ID do job |
| status | string | Status atual |
| progress | integer | Progresso em % (0-100) |
| total | integer | Total de arquivos |
| processed | integer | Arquivos processados |
| successful | integer | Sucessos |
| failed | integer | Falhas |
| current_file | string | Arquivo sendo processado |
| errors | array | Lista de erros |
| started_at | datetime | Início |
| estimated_completion | datetime | Estimativa de conclusão |

#### Exemplos

**cURL:**
```bash
curl "http://localhost:8000/api/batch/status/batch-20251027-103000-abc123"
```

**Python (Monitoramento):**
```python
import requests
import time

job_id = "batch-20251027-103000-abc123"

while True:
    response = requests.get(
        f"http://localhost:8000/api/batch/status/{job_id}"
    )
    status = response.json()
    
    print(f"\rProgresso: {status['progress']}% "
          f"({status['processed']}/{status['total']})", end='')
    
    if status['status'] in ['completed', 'failed']:
        print(f"\n\nStatus final: {status['status']}")
        print(f"Sucessos: {status['successful']}")
        print(f"Falhas: {status['failed']}")
        break
    
    time.sleep(2)
```

#### Erros Possíveis

| Status | Código | Descrição |
|--------|--------|-----------|
| 404 | not_found | Job não encontrado |
| 500 | internal_error | Erro interno |

---

### GET /api/batch/jobs

Lista todos os jobs de processamento em lote.

#### Request

**Query Parameters:**

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| status_filter | string | null | Filtrar por status |
| limit | integer | 50 | Máximo de jobs a retornar |

#### Response

**Status:** 200 OK

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

#### Exemplos

**cURL:**
```bash
# Todos os jobs
curl "http://localhost:8000/api/batch/jobs"

# Apenas jobs completados
curl "http://localhost:8000/api/batch/jobs?status_filter=completed"

# Limitar a 10 jobs
curl "http://localhost:8000/api/batch/jobs?limit=10"
```

---

### DELETE /api/batch/jobs/{job_id}

Remove um job do sistema.

#### Request

**Path Parameters:**

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| job_id | string | ID do job |

#### Response

**Status:** 200 OK

```json
{
  "job_id": "batch-20251027-103000-abc123",
  "deleted": true,
  "message": "Job deleted successfully"
}
```

#### Exemplos

**cURL:**
```bash
curl -X DELETE "http://localhost:8000/api/batch/jobs/batch-20251027-103000-abc123"
```

---

### POST /api/batch/cleanup

Limpa jobs antigos completados.

#### Request

**Query Parameters:**

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| max_age_seconds | integer | 3600 | Idade máxima em segundos |
| keep_failed | boolean | true | Manter jobs com falha |

#### Response

**Status:** 200 OK

```json
{
  "cleaned_up": 5,
  "message": "5 old jobs cleaned up successfully"
}
```

#### Exemplos

**cURL:**
```bash
# Limpar jobs com mais de 1 hora
curl -X POST "http://localhost:8000/api/batch/cleanup"

# Limpar jobs com mais de 30 minutos, incluindo falhas
curl -X POST "http://localhost:8000/api/batch/cleanup?max_age_seconds=1800&keep_failed=false"
```

---

## 🏥 Endpoints de Health

### GET /health

Verificação básica de saúde da API.

#### Response

**Status:** 200 OK

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "development"
}
```

#### Exemplos

**cURL:**
```bash
curl "http://localhost:8000/health"
```

---

### GET /health/detailed

Verificação detalhada com informações de todos os componentes.

#### Response

**Status:** 200 OK

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
      "memory_enabled": true,
      "tools": ["DatabaseQueryTool", "SchemaInfoTool"]
    },
    "memory": {
      "initialized": true,
      "active_sessions": 5,
      "total_cached_messages": 42,
      "storage_directory": "memory_storage",
      "max_history": 4,
      "memory_systems": {
        "cache": "active",
        "rag": "active"
      }
    },
    "batch_processor": {
      "initialized": true,
      "active_jobs": 1,
      "total_jobs": 10,
      "total_files_processed": 100,
      "total_successful": 95,
      "total_failed": 5,
      "max_concurrent": 5
    }
  },
  "configuration": {
    "openai_model": "gpt-4o-mini",
    "max_chat_history": 4,
    "max_concurrent_uploads": 5,
    "xml_folder": "xml_nf",
    "log_level": "INFO"
  }
}
```

#### Exemplos

**cURL:**
```bash
curl "http://localhost:8000/health/detailed"
```

**Python (Monitoramento):**
```python
import requests

response = requests.get("http://localhost:8000/health/detailed")
health = response.json()

print(f"Status: {health['status']}")
print(f"Versão: {health['version']}")

# Verificar serviços
for service, info in health['services'].items():
    status = "✅" if info.get('initialized') else "❌"
    print(f"{status} {service}")
```

---

## ⚠️ Tratamento de Erros

### Estrutura de Erro Padrão

```json
{
  "error": {
    "code": "error_code",
    "message": "Mensagem descritiva",
    "details": {
      "campo": "informação adicional"
    }
  }
}
```

### Códigos de Erro Comuns

| Código | Descrição | Solução |
|--------|-----------|---------|
| validation_error | Dados de entrada inválidos | Verifique os campos obrigatórios |
| openai_api_error | Erro ao comunicar com OpenAI | Verifique API key e créditos |
| database_error | Erro ao acessar banco de dados | Verifique credenciais Supabase |
| agent_error | Erro ao processar mensagem | Tente novamente ou simplifique a pergunta |
| batch_processing_error | Erro no processamento em lote | Verifique os arquivos XML |
| not_found | Recurso não encontrado | Verifique o ID fornecido |

### Exemplo de Tratamento de Erros

**Python:**
```python
import requests

try:
    response = requests.post(
        "http://localhost:8000/api/chat",
        json={"session_id": "user-123", "message": "Olá"}
    )
    response.raise_for_status()
    data = response.json()
    print(data['message'])
    
except requests.exceptions.HTTPError as e:
    error = e.response.json()
    print(f"Erro {error['error']['code']}: {error['error']['message']}")
    
except requests.exceptions.ConnectionError:
    print("Erro: Não foi possível conectar à API")
    
except Exception as e:
    print(f"Erro inesperado: {str(e)}")
```

---

## 📚 Exemplos de Uso

### Exemplo 1: Chat Simples

```python
import requests

def chat(session_id, message):
    response = requests.post(
        "http://localhost:8000/api/chat",
        json={"session_id": session_id, "message": message}
    )
    return response.json()['message']

# Usar
resposta = chat("user-123", "Quantas notas fiscais temos?")
print(resposta)
```

### Exemplo 2: Processamento em Lote Completo

```python
import requests
import time

def processar_lote(pasta="xml_nf"):
    # Iniciar
    response = requests.post(
        "http://localhost:8000/api/batch/upload",
        json={"xml_folder": pasta}
    )
    job_id = response.json()["job_id"]
    
    # Monitorar
    while True:
        status = requests.get(
            f"http://localhost:8000/api/batch/status/{job_id}"
        ).json()
        
        print(f"Progresso: {status['progress']}%")
        
        if status['status'] in ['completed', 'failed']:
            return status
        
        time.sleep(2)

# Usar
resultado = processar_lote()
print(f"Sucessos: {resultado['successful']}")
print(f"Falhas: {resultado['failed']}")
```

### Exemplo 3: Conversa com Contexto

```python
import requests

session_id = "user-123"

def perguntar(mensagem):
    response = requests.post(
        "http://localhost:8000/api/chat",
        json={"session_id": session_id, "message": mensagem}
    )
    return response.json()['message']

# Conversa com contexto
print(perguntar("Quantas notas fiscais temos?"))
# Resposta: "Temos 42 notas fiscais."

print(perguntar("E qual o valor total?"))
# Resposta: "O valor total das 42 notas fiscais é R$ 125.430,50."
# (O agente lembra da pergunta anterior!)
```

---

## 🔗 Links Úteis

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

---

**Última atualização**: 2025-10-27
