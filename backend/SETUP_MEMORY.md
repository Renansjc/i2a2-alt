# Setup do Sistema de Memória com CrewAI RAG

## Instalação de Dependências

### 1. Instalar Dependências Python

```bash
cd backend
pip install -r requirements.txt
```

Isso instalará:
- `crewai>=0.80.0` - Framework multi-agente
- `crewai-tools>=0.12.0` - Ferramentas para agentes
- `chromadb>=0.4.0` - Banco de dados vetorial
- `sentence-transformers>=2.2.0` - Modelos de embedding
- `openai>=1.0.0` - Cliente OpenAI

### 2. Configurar Variáveis de Ambiente

Crie ou atualize o arquivo `.env`:

```bash
# OpenAI API
OPENAI_API_KEY=sk-your-key-here

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-key

# Memory Configuration
CREWAI_STORAGE_DIR=./storage/memory
MAX_CHAT_HISTORY=4
ENABLE_SEMANTIC_SEARCH=true
MEMORY_SEARCH_LIMIT=5
```

### 3. Verificar Instalação

```bash
python -c "import crewai; print(f'CrewAI version: {crewai.__version__}')"
python -c "import chromadb; print('ChromaDB installed successfully')"
```

## Estrutura de Armazenamento

Após a primeira execução, a seguinte estrutura será criada:

```
backend/
├── storage/
│   └── memory/
│       ├── short_term_memory/     # ChromaDB - Memória de curto prazo
│       ├── long_term_memory/      # ChromaDB - Memória de longo prazo
│       ├── entities/              # ChromaDB - Entidades extraídas
│       └── long_term_memory_storage.db  # SQLite
```

## Testando o Sistema

### Teste Básico (sem dependências)

```bash
python test_chat_memory.py
```

Este teste usa apenas a funcionalidade básica sem RAG.

### Teste Completo com RAG (requer instalação)

```bash
python test_chat_memory_rag.py
```

Este teste demonstra:
- Vetorização automática de mensagens
- Busca semântica
- Extração de entidades
- Estatísticas de memória

## Uso no Código

### Exemplo Básico

```python
from memory.chat_memory import ChatMemory

# Inicializar
memory = ChatMemory()

# Adicionar mensagens (automaticamente vetorizadas)
memory.add_message(
    session_id="user-123",
    role="user",
    content="Quantas notas fiscais foram emitidas?"
)

memory.add_message(
    session_id="user-123",
    role="assistant",
    content="Foram emitidas 150 notas fiscais."
)

# Recuperar histórico
history = memory.get_history("user-123")
```

### Exemplo com Busca Semântica

```python
# Buscar contexto relevante
results = memory.search_relevant_context(
    session_id="user-123",
    query="valores monetários",
    max_results=5
)

for result in results:
    print(f"Relevância: {result['relevance_score']}")
    print(f"Mensagem: {result['content']}")
```

### Exemplo com Entidades

```python
# Adicionar mensagem com entidades
memory.add_message(
    session_id="user-123",
    role="user",
    content="Mostre as notas da ACME Corp CNPJ 12.345.678/0001-90"
)

# Recuperar entidades extraídas
entities = memory.get_session_entities("user-123")
print(f"Entidades: {entities}")
```

## Integração com CrewAI Agents

```python
from crewai import Crew, Agent, Task
from memory.chat_memory import ChatMemory

# Inicializar memória
memory = ChatMemory()

# Criar agentes
sql_agent = Agent(
    role="SQL Specialist",
    goal="Execute SQL queries",
    backstory="Expert in database queries",
    verbose=True
)

# Criar crew com memória habilitada
crew = Crew(
    agents=[sql_agent],
    tasks=[],
    memory=True,  # Habilita memória do CrewAI
    verbose=True
)

# Processar com contexto
session_id = "user-123"
user_message = "Qual o total de janeiro?"

# Recuperar contexto
history = memory.get_history(session_id)
context = memory.search_relevant_context(session_id, user_message)

# Executar crew
result = crew.kickoff(inputs={
    "message": user_message,
    "history": history,
    "context": context
})

# Salvar resposta
memory.add_message(session_id, "assistant", str(result))
```

## Troubleshooting

### Erro: ModuleNotFoundError: No module named 'crewai'

**Solução**: Instale as dependências
```bash
pip install crewai crewai-tools chromadb sentence-transformers
```

### Erro: Permission denied ao criar storage

**Solução**: Verifique permissões ou use diretório customizado
```python
memory = ChatMemory(storage_dir="./custom_storage")
```

### Erro: ChromaDB initialization failed

**Solução**: Limpe o diretório de storage e reinicie
```bash
rm -rf storage/memory
python test_chat_memory_rag.py
```

### Performance lenta na primeira execução

**Normal**: O primeiro uso baixa modelos de embedding (~500MB)
- Modelos são cacheados para uso futuro
- Execuções subsequentes são muito mais rápidas

## Próximos Passos

1. ✅ Sistema de memória implementado com RAG
2. ⏭️ Integrar com agentes CrewAI (Task 4)
3. ⏭️ Implementar API endpoints (Task 7)
4. ⏭️ Testar fluxo completo end-to-end

## Recursos Adicionais

- [CrewAI Memory Docs](https://docs.crewai.com/concepts/memory)
- [ChromaDB Getting Started](https://docs.trychroma.com/getting-started)
- [Sentence Transformers](https://www.sbert.net/)
- [RAG Pattern Explained](https://python.langchain.com/docs/use_cases/question_answering/)
