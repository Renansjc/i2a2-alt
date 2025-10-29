# Guia de Testes - Multi-Agent NF-e System

Guia completo para testar o sistema multi-agente de NF-e.

## 📋 Índice

- [Visão Geral](#visão-geral)
- [Pré-requisitos](#pré-requisitos)
- [Testes Manuais](#testes-manuais)
- [Testes Automatizados](#testes-automatizados)
- [Testes de Integração](#testes-de-integração)
- [Testes de Performance](#testes-de-performance)
- [Validação de Componentes](#validação-de-componentes)
- [Troubleshooting](#troubleshooting)

## 🎯 Visão Geral

Este guia cobre todos os aspectos de teste do sistema:

- ✅ **Testes Manuais**: Validação rápida de funcionalidades
- ✅ **Testes Automatizados**: Suite completa de testes unitários e de integração
- ✅ **Testes de API**: Validação de endpoints REST
- ✅ **Testes de Agentes**: Verificação do sistema multi-agente
- ✅ **Testes de Memória**: Validação do sistema RAG
- ✅ **Testes de Batch**: Processamento em lote

## 📦 Pré-requisitos

### 1. Ambiente Configurado

```bash
# Verificar Python
python --version  # Deve ser 3.12.x

# Verificar dependências instaladas
pip list | grep crewai
pip list | grep fastapi

# Verificar variáveis de ambiente
cat .env | grep OPENAI_API_KEY
cat .env | grep SUPABASE_URL
```

### 2. Servidor em Execução

```bash
# Terminal 1: Iniciar servidor
python main.py

# Terminal 2: Verificar health
curl http://localhost:8000/health
```

### 3. Dados de Teste

```bash
# Verificar XMLs de teste
ls xml_nf/*.xml

# Deve ter pelo menos alguns arquivos XML
```

## 🧪 Testes Manuais

### Teste 1: Health Check

Verifica se a API está funcionando.

```bash
# Health básico
curl http://localhost:8000/health

# Esperado:
# {
#   "status": "healthy",
#   "version": "1.0.0",
#   "environment": "development"
# }

# Health detalhado
curl http://localhost:8000/health/detailed

# Esperado: JSON com informações de todos os serviços
```

**✅ Sucesso**: Status "healthy" e todos os serviços inicializados  
**❌ Falha**: Status "degraded" ou serviços não inicializados

---

### Teste 2: Chat Simples

Testa o sistema de chat com uma pergunta simples.

```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test-session-1",
    "message": "Olá, como você funciona?"
  }'
```

**Esperado:**
```json
{
  "session_id": "test-session-1",
  "message": "Olá! Sou um assistente especializado em notas fiscais eletrônicas...",
  "agent_used": "coordenador",
  "timestamp": "2025-10-27T10:30:00",
  "metadata": {
    "processing_time_ms": 1000
  }
}
```

**✅ Sucesso**: Resposta coerente do conversation_specialist  
**❌ Falha**: Erro ou resposta vazia

---

### Teste 3: Consulta ao Banco de Dados

Testa consulta SQL através do agente.

```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test-session-2",
    "message": "Quantas notas fiscais existem no banco de dados?"
  }'
```

**Esperado:**
```json
{
  "session_id": "test-session-2",
  "message": "Existem 42 notas fiscais no banco de dados.",
  "agent_used": "coordenador",
  "timestamp": "2025-10-27T10:31:00",
  "metadata": {
    "processing_time_ms": 2500
  }
}
```

**✅ Sucesso**: Resposta com número específico de notas  
**❌ Falha**: Erro de banco de dados ou resposta genérica

---

### Teste 4: Memória de Contexto

Testa se o sistema mantém contexto entre mensagens.

```bash
# Primeira pergunta
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test-session-3",
    "message": "Quantas notas fiscais temos?"
  }'

# Segunda pergunta (referência à primeira)
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test-session-3",
    "message": "E qual o valor total delas?"
  }'
```

**Esperado na segunda resposta:**
- Referência às notas fiscais mencionadas anteriormente
- Resposta contextualizada (ex: "O valor total das 42 notas fiscais é...")

**✅ Sucesso**: Resposta usa contexto da conversa anterior  
**❌ Falha**: Resposta não contextualizada ou pede esclarecimento

---

### Teste 5: Histórico de Chat

Verifica recuperação de histórico.

```bash
# Recuperar histórico
curl "http://localhost:8000/api/chat/history/test-session-3"
```

**Esperado:**
```json
{
  "session_id": "test-session-3",
  "messages": [
    {
      "role": "user",
      "content": "Quantas notas fiscais temos?",
      "timestamp": "2025-10-27T10:30:00"
    },
    {
      "role": "assistant",
      "content": "Temos 42 notas fiscais.",
      "timestamp": "2025-10-27T10:30:02"
    }
  ],
  "message_count": 2
}
```

**✅ Sucesso**: Histórico completo retornado  
**❌ Falha**: Histórico vazio ou incompleto

---

### Teste 6: Processamento em Lote

Testa importação de XMLs em lote.

```bash
# Iniciar processamento
curl -X POST "http://localhost:8000/api/batch/upload" \
  -H "Content-Type: application/json" \
  -d '{
    "xml_folder": "xml_nf",
    "max_concurrent": 3
  }'

# Salvar o job_id retornado
# Exemplo: batch-20251027-103000-abc123

# Consultar status
curl "http://localhost:8000/api/batch/status/batch-20251027-103000-abc123"
```

**Esperado:**
```json
{
  "job_id": "batch-20251027-103000-abc123",
  "status": "running",
  "progress": 60,
  "total": 5,
  "processed": 3,
  "successful": 3,
  "failed": 0,
  "errors": []
}
```

**✅ Sucesso**: Job criado e processando arquivos  
**❌ Falha**: Erro ao criar job ou processar arquivos

---

### Teste 7: Limpar Histórico

Testa limpeza de sessão.

```bash
# Limpar histórico
curl -X DELETE "http://localhost:8000/api/chat/history/test-session-3"

# Verificar se foi limpo
curl "http://localhost:8000/api/chat/history/test-session-3"
```

**Esperado:**
- DELETE retorna sucesso
- GET retorna 404 (sessão não encontrada)

**✅ Sucesso**: Histórico limpo com sucesso  
**❌ Falha**: Histórico ainda existe

---

## 🤖 Testes Automatizados

### Executar Todos os Testes

```bash
# Executar suite completa
pytest

# Com verbose
pytest -v

# Com coverage
pytest --cov=. --cov-report=html

# Apenas testes rápidos
pytest -m "not slow"
```

### Executar Testes Específicos

```bash
# Testes unitários
pytest tests/unit/

# Testes de integração
pytest tests/integration/

# Teste específico
pytest tests/unit/test_agents.py

# Teste específico de função
pytest tests/unit/test_agents.py::test_coordinator_agent
```

### Estrutura de Testes

```
tests/
├── unit/
│   ├── test_agents.py          # Testes dos agentes
│   ├── test_memory.py          # Testes de memória
│   ├── test_batch.py           # Testes de batch
│   └── test_tools.py           # Testes das tools
├── integration/
│   ├── test_api.py             # Testes de API
│   ├── test_database.py        # Testes de banco
│   └── test_end_to_end.py      # Testes E2E
└── conftest.py                 # Fixtures compartilhadas
```

---

## 🔗 Testes de Integração

### Script de Teste Completo

Use o script `test_system.py` para teste end-to-end:

```bash
python test_system.py
```

Este script testa:

1. ✅ **Inicialização**: Verifica se todos os componentes inicializam
2. ✅ **Batch Processing**: Processa XMLs da pasta xml_nf
3. ✅ **Chat Queries**: Faz perguntas sobre as notas importadas
4. ✅ **Memory**: Verifica contexto entre mensagens
5. ✅ **Agent Delegation**: Valida delegação entre agentes
6. ✅ **Tools**: Verifica uso correto das ferramentas

**Saída esperada:**

```
=== Multi-Agent NF-e System - Test Suite ===

[1/6] Testing system initialization...
✅ System initialized successfully

[2/6] Testing batch processing...
✅ Batch processing completed: 5 successful, 0 failed

[3/6] Testing chat queries...
✅ Query 1: "Quantas notas fiscais foram importadas?"
   Response: "Foram importadas 5 notas fiscais."

[4/6] Testing memory context...
✅ Context maintained across messages

[5/6] Testing agent delegation...
✅ Coordinator delegated to SQL Specialist
✅ Coordinator delegated to Conversation Specialist

[6/6] Testing tools usage...
✅ DatabaseQueryTool used correctly
✅ SchemaInfoTool used correctly

=== All tests passed! ===
```

---

## 📊 Testes de Performance

### Teste de Latência

Mede tempo de resposta do chat.

```python
import requests
import time

def test_latency(num_requests=10):
    times = []
    
    for i in range(num_requests):
        start = time.time()
        
        response = requests.post(
            "http://localhost:8000/api/chat",
            json={
                "session_id": f"perf-test-{i}",
                "message": "Quantas notas fiscais temos?"
            }
        )
        
        elapsed = time.time() - start
        times.append(elapsed)
        
        print(f"Request {i+1}: {elapsed:.2f}s")
    
    avg = sum(times) / len(times)
    print(f"\nAverage: {avg:.2f}s")
    print(f"Min: {min(times):.2f}s")
    print(f"Max: {max(times):.2f}s")

test_latency()
```

**Benchmarks esperados:**
- Primeira requisição: 2-5s (cold start)
- Requisições subsequentes: 1-3s
- Média: < 2.5s

---

### Teste de Concorrência

Testa múltiplas requisições simultâneas.

```python
import requests
import concurrent.futures
import time

def make_request(session_id):
    start = time.time()
    response = requests.post(
        "http://localhost:8000/api/chat",
        json={
            "session_id": session_id,
            "message": "Olá"
        }
    )
    elapsed = time.time() - start
    return elapsed, response.status_code

def test_concurrency(num_concurrent=10):
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_concurrent) as executor:
        futures = [
            executor.submit(make_request, f"concurrent-{i}")
            for i in range(num_concurrent)
        ]
        
        results = [f.result() for f in concurrent.futures.as_completed(futures)]
    
    times = [r[0] for r in results]
    statuses = [r[1] for r in results]
    
    print(f"Concurrent requests: {num_concurrent}")
    print(f"All successful: {all(s == 200 for s in statuses)}")
    print(f"Average time: {sum(times)/len(times):.2f}s")
    print(f"Max time: {max(times):.2f}s")

test_concurrency()
```

**Benchmarks esperados:**
- Todas as requisições devem retornar 200
- Tempo máximo: < 10s
- Sem erros de timeout

---

### Teste de Batch Performance

Mede performance do processamento em lote.

```python
import requests
import time

def test_batch_performance():
    # Iniciar
    start = time.time()
    
    response = requests.post(
        "http://localhost:8000/api/batch/upload",
        json={"xml_folder": "xml_nf"}
    )
    job_id = response.json()["job_id"]
    total_files = response.json()["total_files"]
    
    # Monitorar
    while True:
        status = requests.get(
            f"http://localhost:8000/api/batch/status/{job_id}"
        ).json()
        
        if status['status'] in ['completed', 'failed']:
            break
        
        time.sleep(1)
    
    elapsed = time.time() - start
    
    print(f"Total files: {total_files}")
    print(f"Total time: {elapsed:.2f}s")
    print(f"Time per file: {elapsed/total_files:.2f}s")
    print(f"Successful: {status['successful']}")
    print(f"Failed: {status['failed']}")

test_batch_performance()
```

**Benchmarks esperados:**
- Tempo por arquivo: < 5s
- Taxa de sucesso: > 90%

---

## ✅ Validação de Componentes

### 1. Validar CrewAI

```python
from agents.crew import NFeCrew

# Inicializar
crew = NFeCrew()

# Verificar agentes
print("Agentes disponíveis:")
print("- Coordenador:", crew.coordenador() is not None)
print("- SQL Specialist:", crew.sql_specialist() is not None)
print("- Conversation Specialist:", crew.conversation_specialist() is not None)

# Testar processamento
result = crew.process_message(
    message="Olá",
    chat_history=[],
    session_id="test"
)
print(f"\nResposta: {result}")
```

**✅ Sucesso**: Todos os agentes inicializados e resposta gerada  
**❌ Falha**: Erro ao inicializar ou processar

---

### 2. Validar Memória

```python
from memory.chat_memory import ChatMemory

# Inicializar
memory = ChatMemory()

# Testar cache
memory.add_message("test-session", "user", "Olá")
memory.add_message("test-session", "assistant", "Olá! Como posso ajudar?")

history = memory.get_history("test-session")
print(f"Histórico: {len(history)} mensagens")

# Testar RAG
memory.add_message("test-session", "user", "Quantas notas fiscais temos?")
similar = memory.search_similar_messages("test-session", "notas fiscais", limit=3)
print(f"Mensagens similares: {len(similar)}")

# Testar estatísticas
stats = memory.get_memory_stats()
print(f"Sessões ativas: {stats['total_sessions']}")
```

**✅ Sucesso**: Histórico salvo e busca semântica funcionando  
**❌ Falha**: Erro ao salvar ou buscar mensagens

---

### 3. Validar Database Tools

```python
from agents.tools.database_tool import DatabaseQueryTool
from agents.tools.schema_tool import SchemaInfoTool

# Testar SchemaInfoTool
schema_tool = SchemaInfoTool()
schema = schema_tool._run("all")
print("Schema info:")
print(schema[:200] + "...")

# Testar DatabaseQueryTool
db_tool = DatabaseQueryTool()
result = db_tool._run("SELECT COUNT(*) as total FROM notas_fiscais")
print(f"\nQuery result: {result}")
```

**✅ Sucesso**: Schema retornado e query executada  
**❌ Falha**: Erro ao acessar banco de dados

---

### 4. Validar Batch Processor

```python
from batch.processor import BatchProcessor
import asyncio

async def test_batch():
    processor = BatchProcessor(max_concurrent=3)
    
    result = await processor.process_folder(
        folder_path="xml_nf",
        job_id="test-job-123"
    )
    
    print(f"Total: {result['total']}")
    print(f"Successful: {result['successful']}")
    print(f"Failed: {result['failed']}")
    
    if result['errors']:
        print("\nErrors:")
        for error in result['errors']:
            print(f"  - {error['file']}: {error['error']}")

asyncio.run(test_batch())
```

**✅ Sucesso**: Arquivos processados com sucesso  
**❌ Falha**: Erro ao processar arquivos

---

## 🔍 Troubleshooting

### Problema: Testes Falhando

**Sintomas:**
- Testes retornam erro
- Timeouts frequentes
- Respostas vazias

**Soluções:**

1. **Verificar servidor:**
```bash
curl http://localhost:8000/health
```

2. **Verificar logs:**
```bash
# Aumentar log level
export LOG_LEVEL=DEBUG
python main.py
```

3. **Verificar credenciais:**
```bash
# OpenAI
python -c "import os; print('OpenAI Key:', os.getenv('OPENAI_API_KEY')[:10] + '...')"

# Supabase
python -c "import os; print('Supabase URL:', os.getenv('SUPABASE_URL'))"
```

---

### Problema: Testes Lentos

**Sintomas:**
- Testes demoram muito
- Timeouts

**Soluções:**

1. **Reduzir temperatura:**
```bash
export OPENAI_TEMPERATURE=0.3
```

2. **Usar modelo mais rápido:**
```bash
export OPENAI_MODEL=gpt-3.5-turbo
```

3. **Limitar histórico:**
```bash
export MAX_CHAT_HISTORY=2
```

---

### Problema: Memória Alta

**Sintomas:**
- Uso de memória crescente
- Sistema lento

**Soluções:**

1. **Limpar sessões:**
```bash
curl -X POST "http://localhost:8000/api/batch/cleanup"
```

2. **Reduzir cache:**
```bash
export MAX_CHAT_HISTORY=2
```

3. **Reiniciar servidor:**
```bash
# Ctrl+C para parar
python main.py
```

---

## 📝 Checklist de Testes

Antes de considerar o sistema pronto para produção:

### Funcionalidades Básicas
- [ ] Health check retorna "healthy"
- [ ] Chat responde perguntas simples
- [ ] Chat consulta banco de dados
- [ ] Memória mantém contexto
- [ ] Histórico é recuperado corretamente
- [ ] Batch processa XMLs com sucesso

### Agentes
- [ ] Coordenador delega corretamente
- [ ] SQL Specialist gera queries válidas
- [ ] Conversation Specialist formata respostas
- [ ] Tools são usadas corretamente

### Performance
- [ ] Latência média < 3s
- [ ] Suporta 10+ requisições concorrentes
- [ ] Batch processa < 5s por arquivo
- [ ] Sem memory leaks

### Robustez
- [ ] Trata erros gracefully
- [ ] Continua funcionando após falhas
- [ ] Logs estruturados funcionam
- [ ] Recupera de erros de API

### Segurança
- [ ] Credenciais não expostas
- [ ] Apenas SELECT queries permitidas
- [ ] Validação de entrada funciona
- [ ] CORS configurado corretamente

---

## 📚 Recursos Adicionais

- **Documentação da API**: `API_DOCUMENTATION.md`
- **README Principal**: `README.md`
- **Script de Teste**: `test_system.py`
- **Logs**: Verifique console ou arquivo de log

---

**Última atualização**: 2025-10-27
