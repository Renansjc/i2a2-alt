# Chat Memory System with CrewAI RAG

Sistema de memória de chat avançado que utiliza o sistema nativo de memória do CrewAI com RAG (Retrieval-Augmented Generation) para vetorização e busca semântica.

## Visão Geral

O sistema de memória integra três componentes do CrewAI:

1. **Short-Term Memory (RAG)**: Armazena mensagens recentes com vetorização usando ChromaDB para busca semântica
2. **Long-Term Memory**: Persiste interações importantes para aprendizado de longo prazo
3. **Entity Memory**: Rastreia e extrai entidades mencionadas (empresas, valores, datas, etc.)

## Arquitetura

```
ChatMemory
├── Short-Term Memory (ChromaDB + RAG)
│   ├── Vetorização automática de mensagens
│   ├── Busca semântica por similaridade
│   └── Cache de mensagens recentes (4 últimas)
│
├── Long-Term Memory (SQLite)
│   ├── Armazenamento persistente
│   ├── Histórico completo de sessões
│   └── Aprendizado entre sessões
│
└── Entity Memory (RAG)
    ├── Extração de entidades
    ├── Rastreamento de contexto
    └── Relacionamentos entre entidades
```

## Funcionalidades

### 1. Armazenamento com Vetorização

```python
from memory.chat_memory import ChatMemory

memory = ChatMemory()

# Adiciona mensagem - automaticamente vetorizada
memory.add_message(
    session_id="user-123",
    role="user",
    content="Quantas notas fiscais foram emitidas em janeiro?",
    metadata={"user_id": "123", "timestamp": "2024-01-15"}
)
```

### 2. Busca Semântica

```python
# Busca por contexto relevante usando similaridade vetorial
results = memory.search_relevant_context(
    session_id="user-123",
    query="valores monetários de janeiro",
    max_results=5
)

for result in results:
    print(f"Relevância: {result['relevance_score']}")
    print(f"Conteúdo: {result['content']}")
```

### 3. Rastreamento de Entidades

```python
# Entidades são extraídas automaticamente
memory.add_message(
    session_id="user-123",
    role="user",
    content="Mostre as notas da empresa ACME Corp CNPJ 12.345.678/0001-90"
)

# Recupera entidades mencionadas
entities = memory.get_session_entities("user-123")
# Retorna: ["ACME Corp", "12.345.678/0001-90", ...]
```

### 4. Histórico Contextual

```python
# Recupera histórico formatado para LLMs
history = memory.get_history("user-123")
# Retorna: [{"role": "user", "content": "..."}, ...]

# Resumo legível do contexto
summary = memory.get_context_summary("user-123")
print(summary)
```

## Configuração

### Variáveis de Ambiente

```bash
# .env
CREWAI_STORAGE_DIR=./storage/memory  # Diretório para ChromaDB
MAX_CHAT_HISTORY=4                    # Mensagens recentes em cache
ENABLE_SEMANTIC_SEARCH=true           # Habilitar busca semântica
MEMORY_SEARCH_LIMIT=5                 # Máx resultados de busca
```

### Configuração Programática

```python
from memory.chat_memory import ChatMemory

# Diretório customizado
memory = ChatMemory(storage_dir="./custom_storage")

# Estatísticas de memória
stats = memory.get_memory_stats()
print(f"Sessões ativas: {stats['total_sessions']}")
print(f"Mensagens em cache: {stats['total_cached_messages']}")
```

## Localização de Armazenamento

O CrewAI armazena dados de memória em locais específicos por plataforma:

### Windows
```
C:\Users\{username}\AppData\Local\CrewAI\multi-agent-nfe-system\
├── short_term_memory\    # ChromaDB para memória de curto prazo
├── long_term_memory\     # ChromaDB para memória de longo prazo
├── entities\             # ChromaDB para entidades
└── long_term_memory_storage.db  # SQLite
```

### Linux
```
~/.local/share/CrewAI/multi-agent-nfe-system/
```

### macOS
```
~/Library/Application Support/CrewAI/multi-agent-nfe-system/
```

### Customizar Localização

```python
import os

# Definir antes de inicializar ChatMemory
os.environ["CREWAI_STORAGE_DIR"] = "./my_custom_storage"

memory = ChatMemory()
```

## Vantagens do RAG

### 1. Busca Semântica
- Encontra mensagens relevantes mesmo sem palavras-chave exatas
- Usa similaridade vetorial para contexto
- Exemplo: "valores" encontra "R$ 1.250.000,00"

### 2. Escalabilidade
- ChromaDB otimizado para grandes volumes
- Busca eficiente em milhares de mensagens
- Índices vetoriais para performance

### 3. Contexto Inteligente
- Mantém contexto além das últimas mensagens
- Recupera informações relevantes de toda a sessão
- Aprendizado entre sessões

### 4. Extração de Entidades
- Identifica automaticamente entidades importantes
- Rastreia menções ao longo da conversa
- Relacionamentos entre entidades

## Integração com CrewAI Agents

```python
from crewai import Agent, Crew, Task
from memory.chat_memory import ChatMemory

# Inicializar memória
memory = ChatMemory()

# Criar crew com memória habilitada
crew = Crew(
    agents=[...],
    tasks=[...],
    memory=True,  # Habilita sistema de memória do CrewAI
    verbose=True
)

# Processar mensagem com contexto
session_id = "user-123"
user_message = "Qual foi o valor total de janeiro?"

# Recuperar contexto relevante
context = memory.search_relevant_context(session_id, user_message)
history = memory.get_history(session_id)

# Executar crew com contexto
result = crew.kickoff(inputs={
    "message": user_message,
    "history": history,
    "relevant_context": context
})

# Salvar resposta
memory.add_message(session_id, "assistant", result)
```

## Manutenção

### Limpar Sessão

```python
# Limpar apenas cache (rápido)
memory.clear_session("user-123")

# Limpar incluindo vetores (lento, não recomendado)
memory.clear_session("user-123", clear_vectors=True)
```

### Reset Completo

```python
# CUIDADO: Remove todas as sessões
memory.reset_all_memory()
```

### Monitoramento

```python
# Estatísticas detalhadas
stats = memory.get_memory_stats()

print(f"Sessões: {stats['total_sessions']}")
print(f"Mensagens: {stats['total_cached_messages']}")
print(f"Storage: {stats['storage_directory']}")

# Por sessão
for session_id, details in stats['sessions'].items():
    print(f"{session_id}: {details['message_count']} mensagens")
    print(f"Última atividade: {details['last_activity']}")
```

## Performance

### Otimizações

1. **Cache Local**: Últimas 4 mensagens em memória para acesso rápido
2. **Vetorização Assíncrona**: Não bloqueia operações principais
3. **Índices ChromaDB**: Busca vetorial otimizada
4. **Batch Processing**: Múltiplas mensagens processadas eficientemente

### Benchmarks Típicos

- Adicionar mensagem: ~50-100ms (com vetorização)
- Recuperar histórico: ~5-10ms (do cache)
- Busca semântica: ~50-200ms (dependendo do volume)
- Extração de entidades: ~100-300ms

## Troubleshooting

### Problema: Busca semântica não retorna resultados

**Solução**: 
- Aguarde alguns segundos após adicionar mensagens para vetorização
- Verifique se ChromaDB está instalado: `pip install chromadb`
- Verifique permissões do diretório de storage

### Problema: Erro ao inicializar memória

**Solução**:
- Verifique se o diretório de storage existe e tem permissões
- Limpe o storage antigo se houver corrupção
- Reinstale dependências: `pip install -r requirements.txt`

### Problema: Performance lenta

**Solução**:
- Reduza `MEMORY_SEARCH_LIMIT` para menos resultados
- Use cache local (`get_history`) ao invés de busca semântica quando possível
- Considere limpar sessões antigas periodicamente

## Requisitos

```txt
crewai>=0.80.0
crewai-tools>=0.12.0
chromadb>=0.4.0
sentence-transformers>=2.2.0
openai>=1.0.0
```

## Referências

- [CrewAI Memory Documentation](https://docs.crewai.com/concepts/memory)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [RAG Pattern](https://python.langchain.com/docs/use_cases/question_answering/)
