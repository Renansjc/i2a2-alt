# Guia de Configuração do Ambiente

Guia passo a passo para configurar o ambiente de desenvolvimento do Multi-Agent NF-e System.

## 📋 Índice

- [Requisitos do Sistema](#requisitos-do-sistema)
- [Instalação do Python](#instalação-do-python)
- [Configuração do Ambiente Virtual](#configuração-do-ambiente-virtual)
- [Instalação de Dependências](#instalação-de-dependências)
- [Configuração de Credenciais](#configuração-de-credenciais)
- [Verificação da Instalação](#verificação-da-instalação)
- [Problemas Comuns](#problemas-comuns)

## 💻 Requisitos do Sistema

### Hardware Mínimo

- **CPU**: 2 cores
- **RAM**: 4 GB
- **Disco**: 2 GB livres

### Hardware Recomendado

- **CPU**: 4+ cores
- **RAM**: 8+ GB
- **Disco**: 5+ GB livres

### Sistema Operacional

- ✅ Windows 10/11
- ✅ macOS 10.15+
- ✅ Linux (Ubuntu 20.04+, Debian 10+, etc.)

## 🐍 Instalação do Python

### Python 3.12 (Recomendado)

#### Windows

**Opção 1: Instalador Oficial**

1. Acesse [python.org/downloads](https://www.python.org/downloads/)
2. Baixe Python 3.12.x para Windows
3. Execute o instalador
4. ⚠️ **IMPORTANTE**: Marque "Add Python to PATH"
5. Clique em "Install Now"

**Opção 2: Microsoft Store**

```powershell
# Abra o Microsoft Store e busque por "Python 3.12"
# Ou use winget:
winget install Python.Python.3.12
```

**Verificar instalação:**

```powershell
python --version
# Deve mostrar: Python 3.12.x

pip --version
# Deve mostrar: pip 23.x.x
```

#### macOS

**Opção 1: Homebrew (Recomendado)**

```bash
# Instalar Homebrew (se não tiver)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Instalar Python 3.12
brew install python@3.12

# Adicionar ao PATH
echo 'export PATH="/usr/local/opt/python@3.12/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

**Opção 2: Instalador Oficial**

1. Acesse [python.org/downloads](https://www.python.org/downloads/)
2. Baixe Python 3.12.x para macOS
3. Execute o instalador .pkg
4. Siga as instruções

**Verificar instalação:**

```bash
python3 --version
# Deve mostrar: Python 3.12.x

pip3 --version
# Deve mostrar: pip 23.x.x
```

#### Linux (Ubuntu/Debian)

```bash
# Atualizar repositórios
sudo apt update

# Instalar dependências
sudo apt install -y software-properties-common

# Adicionar repositório deadsnakes (para Python 3.12)
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update

# Instalar Python 3.12
sudo apt install -y python3.12 python3.12-venv python3.12-dev

# Instalar pip
curl -sS https://bootstrap.pypa.io/get-pip.py | python3.12

# Verificar instalação
python3.12 --version
pip3.12 --version
```

#### Linux (Fedora/RHEL)

```bash
# Instalar Python 3.12
sudo dnf install python3.12 python3.12-pip

# Verificar instalação
python3.12 --version
pip3.12 --version
```

## 📦 Configuração do Ambiente Virtual

### Por que usar ambiente virtual?

- ✅ Isola dependências do projeto
- ✅ Evita conflitos entre projetos
- ✅ Facilita reprodução do ambiente
- ✅ Mantém sistema limpo

### Criar Ambiente Virtual

#### Windows

```powershell
# Navegar até a pasta do projeto
cd caminho\para\backend

# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
venv\Scripts\activate

# Você verá (venv) no início do prompt
```

#### macOS/Linux

```bash
# Navegar até a pasta do projeto
cd caminho/para/backend

# Criar ambiente virtual
python3.12 -m venv venv

# Ativar ambiente virtual
source venv/bin/activate

# Você verá (venv) no início do prompt
```

### Desativar Ambiente Virtual

```bash
# Quando terminar de trabalhar
deactivate
```

### Reativar Ambiente Virtual

```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

## 📚 Instalação de Dependências

### 1. Atualizar pip

```bash
# Sempre atualize o pip primeiro
python -m pip install --upgrade pip
```

### 2. Instalar Dependências do Projeto

```bash
# Instalar todas as dependências
pip install -r requirements.txt

# Isso instalará:
# - CrewAI e ferramentas
# - FastAPI e Uvicorn
# - OpenAI client
# - ChromaDB (para RAG)
# - PostgreSQL driver
# - E outras dependências
```

### 3. Verificar Instalação

```bash
# Listar pacotes instalados
pip list

# Verificar pacotes principais
pip show crewai
pip show fastapi
pip show openai
```

### 4. Instalar Dependências de Desenvolvimento (Opcional)

```bash
# Para desenvolvimento e testes
pip install pytest pytest-asyncio httpx black flake8 mypy
```

## 🔑 Configuração de Credenciais

### 1. Criar Arquivo .env

```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Windows (PowerShell)
copy .env.example .env
```

### 2. Obter OpenAI API Key

1. **Criar conta OpenAI**
   - Acesse [platform.openai.com](https://platform.openai.com)
   - Crie uma conta ou faça login

2. **Gerar API Key**
   - Vá em [API Keys](https://platform.openai.com/api-keys)
   - Clique em "Create new secret key"
   - Dê um nome (ex: "nfe-system")
   - Copie a chave (começa com `sk-`)
   - ⚠️ **IMPORTANTE**: Salve a chave, não será mostrada novamente

3. **Adicionar créditos**
   - Vá em [Billing](https://platform.openai.com/account/billing)
   - Adicione método de pagamento
   - Adicione créditos (mínimo $5)

4. **Configurar no .env**
   ```bash
   OPENAI_API_KEY=sk-sua-chave-aqui
   OPENAI_MODEL=gpt-4o-mini
   ```

### 3. Obter Supabase Credentials

1. **Criar projeto Supabase**
   - Acesse [supabase.com](https://supabase.com)
   - Crie uma conta ou faça login
   - Clique em "New Project"
   - Escolha nome, senha e região
   - Aguarde criação do projeto (~2 minutos)

2. **Obter credenciais**
   - No dashboard do projeto, vá em **Settings** → **API**
   - Copie:
     - **URL**: `https://seu-projeto.supabase.co`
     - **anon public key**: Para uso público (não usar)
     - **service_role key**: Para uso no backend ⚠️ **Use esta!**

3. **Configurar no .env**
   ```bash
   SUPABASE_URL=https://seu-projeto.supabase.co
   SUPABASE_SERVICE_KEY=sua-service-role-key-aqui
   ```

4. **Configurar banco de dados**
   - No Supabase, vá em **SQL Editor**
   - Abra o arquivo `database/schema_nfe_completo.sql`
   - Copie todo o conteúdo
   - Cole no SQL Editor do Supabase
   - Execute (Run)
   - Verifique se as tabelas foram criadas em **Table Editor**

### 4. Configurar Variáveis Opcionais

Edite o arquivo `.env` com suas preferências:

```bash
# Application Configuration
APP_ENV=development          # development ou production
LOG_LEVEL=INFO              # DEBUG, INFO, WARNING, ERROR

# Chat Memory Configuration
MAX_CHAT_HISTORY=4          # Número de mensagens em cache (2 interações)

# Batch Processing Configuration
XML_FOLDER=xml_nf           # Pasta com XMLs
MAX_CONCURRENT_UPLOADS=5    # Uploads simultâneos

# API Configuration
API_HOST=0.0.0.0           # Host da API
API_PORT=8000              # Porta da API
API_RELOAD=true            # Auto-reload em desenvolvimento
```

### 5. Verificar Configuração

```bash
# Verificar se variáveis estão definidas
python -c "from config import settings; print('OpenAI:', settings.openai_api_key[:10] + '...'); print('Supabase:', settings.supabase_url)"
```

## ✅ Verificação da Instalação

### 1. Verificar Python e Dependências

```bash
# Python
python --version
# Esperado: Python 3.12.x

# Pip
pip --version
# Esperado: pip 23.x.x

# CrewAI
python -c "import crewai; print(f'CrewAI: {crewai.__version__}')"
# Esperado: CrewAI: 0.80.x ou superior

# FastAPI
python -c "import fastapi; print(f'FastAPI: {fastapi.__version__}')"
# Esperado: FastAPI: 0.104.x ou superior

# OpenAI
python -c "import openai; print(f'OpenAI: {openai.__version__}')"
# Esperado: OpenAI: 1.x.x
```

### 2. Verificar Credenciais

```bash
# Testar OpenAI
python -c "
from openai import OpenAI
import os
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
models = client.models.list()
print('✅ OpenAI conectado com sucesso')
"

# Testar Supabase
python -c "
import requests
import os
url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_KEY')
response = requests.get(
    f'{url}/rest/v1/',
    headers={'apikey': key}
)
print('✅ Supabase conectado com sucesso' if response.status_code == 200 else '❌ Erro ao conectar')
"
```

### 3. Iniciar Servidor

```bash
# Iniciar servidor de desenvolvimento
python main.py

# Ou com uvicorn
uvicorn main:app --reload
```

**Saída esperada:**

```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### 4. Testar API

Em outro terminal:

```bash
# Health check
curl http://localhost:8000/health

# Esperado:
# {
#   "status": "healthy",
#   "version": "1.0.0",
#   "environment": "development"
# }

# Teste de chat
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test",
    "message": "Olá"
  }'

# Esperado: Resposta JSON com mensagem do agente
```

### 5. Acessar Documentação

Abra no navegador:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔧 Problemas Comuns

### Problema: "python: command not found"

**Solução:**

```bash
# Windows: Reinstale Python e marque "Add to PATH"
# macOS/Linux: Use python3 ao invés de python
python3 --version
```

### Problema: "pip: command not found"

**Solução:**

```bash
# Instalar pip
python -m ensurepip --upgrade

# Ou baixar get-pip.py
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python get-pip.py
```

### Problema: "Permission denied" ao instalar pacotes

**Solução:**

```bash
# NÃO use sudo! Use ambiente virtual:
python -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate no Windows
pip install -r requirements.txt
```

### Problema: "ModuleNotFoundError: No module named 'crewai'"

**Solução:**

```bash
# Verificar se ambiente virtual está ativado
# Deve ter (venv) no prompt

# Reinstalar dependências
pip install -r requirements.txt

# Verificar instalação
pip show crewai
```

### Problema: "OpenAI API error: Invalid API key"

**Solução:**

```bash
# Verificar se a chave está correta no .env
cat .env | grep OPENAI_API_KEY

# Verificar se começa com sk-
# Verificar se não tem espaços extras

# Gerar nova chave em platform.openai.com/api-keys
```

### Problema: "Supabase connection failed"

**Solução:**

```bash
# Verificar URL e key no .env
cat .env | grep SUPABASE

# Testar conexão manualmente
curl https://seu-projeto.supabase.co/rest/v1/ \
  -H "apikey: sua-service-role-key"

# Verificar se projeto está ativo no Supabase Dashboard
```

### Problema: "Port 8000 already in use"

**Solução:**

```bash
# Windows: Encontrar e matar processo
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS/Linux: Encontrar e matar processo
lsof -ti:8000 | xargs kill -9

# Ou usar porta diferente
uvicorn main:app --port 8001
```

### Problema: Servidor lento ou travando

**Solução:**

```bash
# Reduzir temperatura
export OPENAI_TEMPERATURE=0.3

# Usar modelo mais rápido
export OPENAI_MODEL=gpt-3.5-turbo

# Limitar histórico
export MAX_CHAT_HISTORY=2

# Aumentar timeout
export BATCH_TIMEOUT_SECONDS=600
```

## 📝 Checklist de Configuração

Antes de começar a desenvolver, verifique:

- [ ] Python 3.12.x instalado
- [ ] Ambiente virtual criado e ativado
- [ ] Dependências instaladas (`pip list` mostra crewai, fastapi, etc.)
- [ ] Arquivo .env criado e configurado
- [ ] OpenAI API key válida e com créditos
- [ ] Supabase projeto criado e credenciais configuradas
- [ ] Banco de dados Supabase com schema criado
- [ ] Servidor inicia sem erros
- [ ] Health check retorna "healthy"
- [ ] Documentação acessível em /docs

## 🎓 Próximos Passos

Após configurar o ambiente:

1. **Leia o README**: `README.md` para visão geral do sistema
2. **Explore a API**: Acesse http://localhost:8000/docs
3. **Execute testes**: `python test_system.py`
4. **Leia documentação**: `API_DOCUMENTATION.md` e `TESTING_GUIDE.md`
5. **Comece a desenvolver**: Faça suas primeiras modificações

## 📚 Recursos Adicionais

- **Python**: [python.org/doc](https://www.python.org/doc/)
- **pip**: [pip.pypa.io](https://pip.pypa.io/)
- **venv**: [docs.python.org/3/library/venv.html](https://docs.python.org/3/library/venv.html)
- **OpenAI**: [platform.openai.com/docs](https://platform.openai.com/docs)
- **Supabase**: [supabase.com/docs](https://supabase.com/docs)
- **CrewAI**: [docs.crewai.com](https://docs.crewai.com)
- **FastAPI**: [fastapi.tiangolo.com](https://fastapi.tiangolo.com)

---

**Última atualização**: 2025-10-27
