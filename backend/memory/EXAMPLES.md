# Exemplos Práticos: Sistema de Memória com RAG

## Exemplos de Uso Real

### Exemplo 1: Chat Básico com Contexto

```python
from memory.chat_memory import ChatMemory

# Inicializar memória
memory = ChatMemory()
session_id = "user-123"

# Primeira interação
memory.add_message(session_id, "user", "Quantas notas fiscais foram emitidas em janeiro?")
memory.add_message(session_id, "assistant", "Foram emitidas 150 notas fiscais em janeiro de 2024.")

# Segunda interação (com contexto)
memory.add_message(session_id, "user", "E qual foi o valor total?")

# Recuperar histórico para o agente
history = memory.get_history(session_id)
# Retorna:
# [
#   {"role": "user", "content": "Quantas notas fiscais..."},
#   {"role": "assistant", "content": "Foram emitidas 150..."},
#   {"role": "user", "content": "E qual foi o valor total?"}
# ]

# Agente pode usar o contexto para entender que "valor total" 
# se refere às notas fiscais de janeiro
```

### Exemplo 2: Busca Semântica para Contexto Relevante

```python
# Usuário teve uma conversa longa sobre vários tópicos
memory.add_message(session_id, "user", "Mostre as notas de janeiro")
memory.add_message(session_id, "assistant", "150 notas, R$ 1.250.000,00")

memory.add_message(session_id, "user", "E de fevereiro?")
memory.add_message(session_id, "assistant", "120 notas, R$ 980.000,00")

memory.add_message(session_id, "user", "Quais empresas emitiram mais?")
memory.add_message(session_id, "assistant", "ACME Corp (45) e XYZ Ltda (38)")

# Mais tarde, usuário pergunta sobre valores
memory.add_message(session_id, "user", "Qual foi o maior valor mensal?")

# Buscar contexto relevante sobre valores
relevant = memory.search_relevant_context(
    session_id=session_id,
    query="valores monetários mensais",
    max_results=3
)

# Retorna as mensagens mais relevantes:
# 1. "150 notas, R$ 1.250.000,00" (relevância: 0.85)
# 2. "120 notas, R$ 980.000,00" (relevância: 0.82)
# 3. "Qual foi o maior valor mensal?" (relevância: 0.75)

# Agente pode usar esse contexto para responder corretamente:
# "O maior valor mensal foi R$ 1.250.000,00 em janeiro"
```

### Exemplo 3: Extração de Entidades

```python
# Usuário menciona empresa e CNPJ
memory.add_message(
    session_id,
    "user",
    "Mostre as notas da ACME Corp CNPJ 12.345.678/0001-90 de janeiro"
)

memory.add_message(
    session_id,
    "assistant",
    "Encontrei 23 notas da ACME Corp no valor de R$ 450.000,00"
)

# Extrair entidades mencionadas
entities = memory.get_session_entities(session_id)
# Retorna: ["12.345.678/0001-90", "R$ 450.000,00", "ACME Corp"]

# Útil para:
# - Preencher formulários automaticamente
# - Sugerir filtros
# - Manter contexto de empresas mencionadas
```

### Exemplo 4: Resumo de Contexto

```python
# Obter resumo legível da conversa
summary = memory.get_context_summary(session_id)

print(summary)
# Saída:
# === Histórico Recente ===
# [20:36:01] user: Quantas notas fiscais foram emitidas em janeiro?
# [20:36:03] assistant: Foram emitidas 150 notas fiscais em janeiro de 2024.
# [20:36:04] user: E qual foi o valor total?
# [20:36:05] assistant: O valor total foi R$ 1.250.000,00.
#
# === Entidades Mencionadas ===
# - R$ 1.250.000,00
```

### Exemplo 5: Integração com CrewAI Agent

```python
from crewai import Agent, Task, Crew
from memory.chat_memory import ChatMemory

# Inicializar memória
memory = ChatMemory()

# Criar agente SQL
sql_agent = Agent(
    role="SQL Specialist",
    goal="Execute SQL queries on NF-e database",
    backstory="Expert in database queries",
    verbose=True
)

# Processar mensagem do usuário
session_id = "user-123"
user_message = "Quantas notas fiscais foram emitidas este mês?"

# Recuperar contexto
history = memory.get_history(session_id)
relevant_context = memory.search_relevant_context(session_id, user_message)

# Criar task com contexto
task = Task(
    description=f"""
    User message: {user_message}
    
    Recent history:
    {history}
    
    Relevant context from past conversations:
    {relevant_context}
    
    Execute appropriate SQL query and format response.
    """,
    agent=sql_agent,
    expected_output="Natural language response with query results"
)

# Executar crew
crew = Crew(
    agents=[sql_agent],
    tasks=[task],
    memory=True,  # Habilita memória do CrewAI
    verbose=True
)

result = crew.kickoff()

# Salvar resposta na memória
memory.add_message(session_id, "assistant", str(result))
```

### Exemplo 6: API Endpoint com Memória

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from memory.chat_memory import ChatMemory

app = FastAPI()
memory = ChatMemory()

class ChatRequest(BaseModel):
    session_id: str
    message: str

class ChatResponse(BaseModel):
    session_id: str
    message: str
    relevant_context: list
    entities: list

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        # Adicionar mensagem do usuário
        memory.add_message(request.session_id, "user", request.message)
        
        # Buscar contexto relevante
        relevant_context = memory.search_relevant_context(
            request.session_id,
            request.message,
            max_results=3
        )
        
        # Extrair entidades
        entities = memory.get_session_entities(request.session_id)
        
        # Recuperar histórico
        history = memory.get_history(request.session_id)
        
        # Processar com agentes (simplificado)
        # result = crew.kickoff(inputs={...})
        result = "Resposta do agente aqui"
        
        # Salvar resposta
        memory.add_message(request.session_id, "assistant", result)
        
        return ChatResponse(
            session_id=request.session_id,
            message=result,
            relevant_context=[c['content'] for c in relevant_context],
            entities=entities
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/chat/{session_id}/summary")
async def get_summary(session_id: str):
    """Obter resumo da conversa"""
    summary = memory.get_context_summary(session_id)
    stats = memory.get_memory_stats()
    
    return {
        "session_id": session_id,
        "summary": summary,
        "message_count": memory.get_message_count(session_id),
        "entities": memory.get_session_entities(session_id)
    }

@app.delete("/api/chat/{session_id}")
async def clear_session(session_id: str):
    """Limpar histórico de uma sessão"""
    success = memory.clear_session(session_id)
    return {"success": success}
```

### Exemplo 7: Monitoramento e Estatísticas

```python
# Obter estatísticas completas
stats = memory.get_memory_stats()

print(f"Total de sessões ativas: {stats['total_sessions']}")
print(f"Total de mensagens em cache: {stats['total_cached_messages']}")
print(f"Diretório de storage: {stats['storage_directory']}")

# Detalhes por sessão
for session_id, details in stats['sessions'].items():
    print(f"\nSessão: {session_id}")
    print(f"  Mensagens: {details['message_count']}")
    print(f"  Última atividade: {details['last_activity']}")
    
    # Entidades da sessão
    entities = memory.get_session_entities(session_id)
    if entities:
        print(f"  Entidades: {', '.join(entities[:3])}")
```

### Exemplo 8: Busca Semântica Avançada

```python
# Cenário: Usuário quer informações sobre valores, mas não lembra exatamente

# Histórico da conversa
memory.add_message(session_id, "user", "Mostre as notas de janeiro")
memory.add_message(session_id, "assistant", "150 notas, total R$ 1.250.000,00")

memory.add_message(session_id, "user", "E os produtos mais vendidos?")
memory.add_message(session_id, "assistant", "Produto A: 1200 unidades, Produto B: 980 unidades")

memory.add_message(session_id, "user", "Quais empresas emitiram?")
memory.add_message(session_id, "assistant", "ACME Corp: 45 notas, XYZ Ltda: 38 notas")

# Usuário pergunta algo vago
memory.add_message(session_id, "user", "Quanto foi o faturamento?")

# Buscar contexto sobre valores/faturamento
results = memory.search_relevant_context(
    session_id=session_id,
    query="faturamento valores monetários total",
    max_results=5
)

# Resultados ordenados por relevância:
# 1. "150 notas, total R$ 1.250.000,00" (0.88) ← Mais relevante!
# 2. "Quanto foi o faturamento?" (0.85)
# 3. "Mostre as notas de janeiro" (0.72)
# 4. "Produto A: 1200 unidades..." (0.65)
# 5. "ACME Corp: 45 notas..." (0.58)

# Agente pode usar o contexto mais relevante para responder:
# "O faturamento total de janeiro foi R$ 1.250.000,00"
```

### Exemplo 9: Múltiplas Sessões Simultâneas

```python
# Gerenciar múltiplos usuários
users = ["user-123", "user-456", "user-789"]

for user_id in users:
    memory.add_message(user_id, "user", f"Olá, sou {user_id}")
    memory.add_message(user_id, "assistant", f"Olá {user_id}! Como posso ajudar?")

# Cada sessão é independente
print(f"Sessões ativas: {memory.get_session_count()}")  # 3

# Histórico separado por usuário
for user_id in users:
    history = memory.get_history(user_id)
    print(f"{user_id}: {len(history)} mensagens")
```

### Exemplo 10: Limpeza e Manutenção

```python
# Limpar sessão específica
memory.clear_session("user-123")

# Verificar se sessão existe
if memory.session_exists("user-123"):
    print("Sessão ainda existe")
else:
    print("Sessão foi limpa")

# Obter contagem de mensagens
count = memory.get_message_count("user-456")
print(f"Sessão user-456 tem {count} mensagens")

# Reset completo (cuidado!)
# memory.reset_all_memory()  # Remove TODAS as sessões
```

## Casos de Uso Reais

### Caso 1: Assistente de Consultas NF-e

```python
# Usuário faz várias perguntas sobre notas fiscais
session_id = "user-nfe-001"

# Pergunta 1
memory.add_message(session_id, "user", "Quantas notas foram emitidas em janeiro?")
# Agente consulta DB e responde
memory.add_message(session_id, "assistant", "150 notas em janeiro")

# Pergunta 2 (usa contexto)
memory.add_message(session_id, "user", "E em fevereiro?")
# Agente entende que é sobre notas fiscais
memory.add_message(session_id, "assistant", "120 notas em fevereiro")

# Pergunta 3 (referência a conversa anterior)
memory.add_message(session_id, "user", "Qual mês teve mais?")
# Busca semântica encontra contexto sobre janeiro e fevereiro
context = memory.search_relevant_context(session_id, "quantidade notas meses")
# Agente compara e responde
memory.add_message(session_id, "assistant", "Janeiro teve mais, com 150 notas")
```

### Caso 2: Análise de Empresas

```python
session_id = "user-analysis-001"

# Usuário menciona empresa
memory.add_message(
    session_id,
    "user",
    "Mostre dados da ACME Corp CNPJ 12.345.678/0001-90"
)

# Sistema extrai entidades
entities = memory.get_session_entities(session_id)
# ["12.345.678/0001-90", "ACME Corp"]

# Mais tarde, usuário faz pergunta sem mencionar empresa
memory.add_message(session_id, "user", "Quantas notas essa empresa emitiu?")

# Sistema usa entidades extraídas para saber que "essa empresa" = ACME Corp
# Busca contexto relevante
context = memory.search_relevant_context(session_id, "ACME Corp notas")
```

### Caso 3: Relatórios Personalizados

```python
session_id = "user-report-001"

# Usuário pede relatório
memory.add_message(session_id, "user", "Preciso de um relatório de janeiro")

# Agente pergunta detalhes
memory.add_message(session_id, "assistant", "Que tipo de relatório? Vendas, impostos ou geral?")

memory.add_message(session_id, "user", "Vendas por empresa")

# Sistema mantém contexto: relatório + janeiro + vendas + por empresa
history = memory.get_history(session_id)
# Agente gera relatório com todos os parâmetros corretos
```

## Dicas de Performance

### 1. Use Cache para Acesso Frequente

```python
# Rápido: usa cache local
history = memory.get_history(session_id)  # ~5ms

# Mais lento: busca vetorial
context = memory.search_relevant_context(session_id, query)  # ~100ms
```

### 2. Limite Resultados de Busca

```python
# Mais rápido
results = memory.search_relevant_context(session_id, query, max_results=3)

# Mais lento
results = memory.search_relevant_context(session_id, query, max_results=10)
```

### 3. Limpe Sessões Antigas

```python
# Periodicamente limpar sessões inativas
inactive_sessions = [...]  # Identificar sessões antigas
for session_id in inactive_sessions:
    memory.clear_session(session_id)
```

## Troubleshooting

### Problema: Busca semântica não encontra resultados

```python
# Aguarde vetorização completar
import time
memory.add_message(session_id, "user", "mensagem")
time.sleep(2)  # Aguardar vetorização
results = memory.search_relevant_context(session_id, "query")
```

### Problema: Entidades não sendo extraídas

```python
# Verifique formato das entidades
# CNPJ deve estar no formato: XX.XXX.XXX/XXXX-XX
# Valores devem ter: R$ X.XXX,XX

# Exemplo correto:
memory.add_message(session_id, "user", "CNPJ 12.345.678/0001-90 valor R$ 1.000,00")

# Exemplo incorreto:
memory.add_message(session_id, "user", "CNPJ 12345678000190 valor 1000")
```

### Problema: Performance lenta

```python
# Use cache quando possível
history = memory.get_history(session_id)  # Rápido

# Evite buscas desnecessárias
if len(history) < 2:
    # Não precisa de busca semântica com pouco histórico
    context = []
else:
    context = memory.search_relevant_context(session_id, query)
```
