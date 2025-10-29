# Multi-Agent NF-e System - Backend

Sistema multi-agente com CrewAI para processamento e consulta de Notas Fiscais Eletrônicas (NF-e).

## 🐍 Requisitos

- **Python 3.12** (requerido)
- Conta Supabase com banco de dados configurado
- Chave API da OpenAI

## 🚀 Instalação

### 1. Verificar versão do Python

```bash
python --version
# Deve retornar: Python 3.12.x
```

### 2. Criar ambiente virtual

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

## ⚙️ Configuração

### 1. Criar arquivo `.env`

Copie o arquivo `.env.example` e preencha com suas credenciais:

```bash
cp .env.example .env
```

### 2. Configurar variáveis de ambiente

Edite o arquivo `.env` com suas credenciais:

```env
# OpenAI
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_MODEL=gpt-4o-mini

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-supabase-service-role-key-here

# Aplicação
APP_ENV=development
LOG_LEVEL=INFO
MAX_CHAT_HISTORY=4

# Batch Processing
XML_FOLDER=xml_nf
MAX_CONCURRENT_UPLOADS=5
```

## 🏗️ Estrutura do Projeto

```
backend/
├── agents/              # CrewAI agents e tools
│   ├── crew.py         # NFeCrew principal
│   ├── tools/          # Database e Schema tools
│   └── config/         # agents.yaml e tasks.yaml
├── api/                # FastAPI routes e models
│   ├── routes/         # Endpoints (chat, batch)
│   └── models/         # Pydantic models
├── batch/              # Processamento em lote
├── database/           # Schema e helpers
├── memory/             # Sistema de memória de chat
├── utils/              # Exceções e logging
├── config.py           # Configurações da aplicação
├── main.py             # Entry point FastAPI
└── db.py               # Importador de NF-e (existente)
```

## 🤖 Agentes CrewAI

O sistema utiliza 3 agentes especializados:

1. **coordenador** (Manager)
   - Analisa intenções das mensagens
   - Delega tarefas aos agentes especializados
   - Coordena o fluxo de trabalho

2. **SQL Specialist**
   - Consulta dados no Supabase via REST API
   - Gera queries otimizadas
   - Retorna dados estruturados

3. **Conversation Specialist**
   - Formata respostas em linguagem natural
   - Mantém tom amigável e profissional
   - Explica dados técnicos de forma clara

## 🗄️ Banco de Dados

**IMPORTANTE**: O banco de dados já existe e está configurado no Supabase.

- Schema completo: `database/schema_nfe_completo.sql`
- Conexão via Supabase REST API
- Lógica de importação: `db.py` (SupabaseNFeImporter)

**Não criar novas tabelas. Apenas consultar dados existentes.**

## 🚀 Executar a Aplicação

### Modo Desenvolvimento

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Modo Produção

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 📡 Endpoints da API

### Chat

```bash
POST /api/chat
{
  "session_id": "user-123",
  "message": "Quantas notas fiscais foram emitidas este mês?"
}
```

### Batch Upload

```bash
POST /api/batch/upload
{
  "xml_folder": "xml_nf"
}
```

### Health Check

```bash
GET /health
```

## 🧪 Testes

```bash
# Executar todos os testes
pytest

# Executar com cobertura
pytest --cov=. --cov-report=html

# Executar testes específicos
pytest tests/unit/test_agents.py
```

## 📝 Desenvolvimento

### Adicionar novo agente

1. Editar `agents/config/agents.yaml`
2. Adicionar tarefas em `agents/config/tasks.yaml`
3. Atualizar `agents/crew.py` com novos métodos `@agent` e `@task`

### Criar nova tool

1. Criar arquivo em `agents/tools/`
2. Herdar de `crewai_tools.BaseTool`
3. Implementar método `_run()`
4. Adicionar tool aos agentes em `crew.py`

## 🐛 Troubleshooting

### Erro: "Module not found: crewai"

```bash
pip install --upgrade crewai crewai-tools
```

### Erro: "Python version not supported"

Certifique-se de estar usando Python 3.12:

```bash
python --version
```

### Erro de conexão com Supabase

Verifique suas credenciais no arquivo `.env`:
- `SUPABASE_URL` deve começar com `https://`
- `SUPABASE_SERVICE_KEY` deve ser a service role key (não anon key)

## 📚 Documentação

- [CrewAI Documentation](https://docs.crewai.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Supabase Documentation](https://supabase.com/docs)

## 📄 Licença

MIT License
