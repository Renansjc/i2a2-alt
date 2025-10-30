# 🤖 Sistema Multi-Agente para NF-e

Sistema inteligente de processamento e análise de Notas Fiscais Eletrônicas (NF-e) usando IA multi-agente com CrewAI, GPT-4o-mini e Supabase.

## 📋 Índice

- [Visão Geral](#-visão-geral)
- [Arquitetura](#-arquitetura)
- [Funcionalidades](#-funcionalidades)
- [Pré-requisitos](#-pré-requisitos)
- [Instalação Rápida](#-instalação-rápida)
- [Como Funciona](#-como-funciona)
- [Uso](#-uso)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Tecnologias](#-tecnologias)
- [Documentação Adicional](#-documentação-adicional)

## 🎯 Visão Geral

O Sistema Multi-Agente para NF-e é uma solução completa que combina **Inteligência Artificial** com **processamento de dados fiscais**. Ele permite que você:

- 💬 **Converse em linguagem natural** sobre suas notas fiscais
- 📦 **Importe XMLs em lote** de forma automatizada
- 📊 **Analise dados fiscais** com consultas inteligentes
- 🧠 **Mantenha contexto** das conversas anteriores
- 🔍 **Busque informações** de forma semântica

### Como Funciona em 3 Passos

1. **Importe seus XMLs**: Faça upload dos arquivos XML de NF-e
2. **Faça perguntas**: "Qual o valor total das notas deste mês?"
3. **Receba respostas**: O sistema consulta o banco e responde em linguagem natural

### Exemplo de Uso

```
Você: Quantas notas fiscais foram emitidas este mês?

Sistema: Foram emitidas 42 notas fiscais em outubro de 2025, 
totalizando R$ 125.430,50 em vendas.

Você: E qual foi o produto mais vendido?

Sistema: O produto mais vendido foi "Notebook Dell Inspiron" 
com 15 unidades vendidas, representando R$ 45.000,00 do faturamento.
```

## 🏗️ Arquitetura

O sistema é composto por três camadas principais:

```
┌─────────────────────────────────────────────────────────┐
│                    FRONTEND (Nuxt 4)                    │
│  Dashboard • Chat Interface • Upload • Relatórios       │
└────────────────────┬────────────────────────────────────┘
                     │ REST API
┌────────────────────▼────────────────────────────────────┐
│                 BACKEND (FastAPI + CrewAI)              │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │         Sistema Multi-Agente (CrewAI)          │    │
│  │                                                 │    │
│  │  ┌──────────────────────────────────────┐     │    │
│  │  │  Coordenador (Manager)               │     │    │
│  │  │  • Analisa intenção                  │     │    │
│  │  │  • Delega tarefas                    │     │    │
│  │  └────────┬──────────────┬──────────────┘     │    │
│  │           │              │                     │    │
│  │  ┌────────▼────────┐  ┌─▼──────────────┐     │    │
│  │  │ SQL Specialist  │  │ Conversation    │     │    │
│  │  │ • Gera SQL      │  │ Specialist      │     │    │
│  │  │ • Executa query │  │ • Formata resp. │     │    │
│  │  └─────────────────┘  └─────────────────┘     │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │  Memória RAG (ChromaDB)                        │    │
│  │  • Cache de curto prazo (últimas 4 msgs)      │    │
│  │  • Busca semântica de longo prazo             │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │  Processador de Lote                           │    │
│  │  • Importação assíncrona de XMLs              │    │
│  │  • Rastreamento de jobs                       │    │
│  └────────────────────────────────────────────────┘    │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│              BANCO DE DADOS (Supabase/PostgreSQL)       │
│  • 20+ tabelas (layout NF-e 4.00)                      │
│  • Empresas, Notas, Itens, Impostos, Pagamentos        │
└─────────────────────────────────────────────────────────┘
```

### Agentes Especializados

O sistema utiliza **3 agentes de IA** trabalhando em equipe:

1. **🎯 Coordenador (Manager)**
   - Analisa a intenção de cada mensagem
   - Decide qual especialista deve responder
   - Gerencia o fluxo de comunicação

2. **💾 SQL Specialist**
   - Gera consultas SQL otimizadas
   - Executa queries no banco de dados
   - Retorna dados estruturados

3. **💬 Conversation Specialist**
   - Formata respostas em linguagem natural
   - Mantém tom profissional e amigável
   - Explica dados técnicos de forma clara

## ✨ Funcionalidades

### 💬 Chat Inteligente
- Perguntas em linguagem natural sobre suas NF-e
- Respostas contextualizadas com memória de conversas
- Busca semântica em histórico de conversas
- Suporte a múltiplas sessões simultâneas

### 📦 Processamento em Lote
- Importação assíncrona de múltiplos XMLs
- Rastreamento de progresso em tempo real
- Relatório detalhado de sucessos e falhas
- Controle de concorrência configurável

### 📊 Análise de Dados
- Consultas SQL geradas automaticamente
- Agregações e cálculos complexos
- Filtros por período, empresa, produto
- Relatórios fiscais e gerenciais

### 🧠 Memória Contextual
- Sistema RAG (Retrieval-Augmented Generation)
- Cache de curto prazo (últimas interações)
- Busca semântica de longo prazo
- Contexto mantido entre sessões

## 📋 Pré-requisitos

Antes de começar, você precisa ter:

### Software
- **Python 3.12+** (recomendado)
- **Node.js 18+** e **npm** (para o frontend)
- **Git** (para clonar o repositório)

### Contas e Credenciais
- **Conta OpenAI** com API key ([criar aqui](https://platform.openai.com/api-keys))
- **Projeto Supabase** configurado ([criar aqui](https://supabase.com))

### Conhecimentos Básicos
- Linha de comando (terminal/cmd)
- Variáveis de ambiente
- Conceitos básicos de API REST

## 🚀 Instalação Rápida

### 1. Clone o Repositório

```bash
git clone <repository-url>
cd multi-agent-nfe-system
```

### 2. Configure o Banco de Dados (Supabase)

1. Acesse seu projeto no [Supabase Dashboard](https://supabase.com/dashboard)
2. Vá em **SQL Editor**
3. Execute o arquivo `database/schema_nfe_completo.sql`
4. Execute o arquivo `database/configurar_permissoes_supabase.sql`

Veja o [Guia Completo do Supabase](GUIA_SUPABASE.md) para mais detalhes.

### 3. Configure o Backend

```bash
cd backend

# Crie um ambiente virtual
python -m venv venv

# Ative o ambiente virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instale as dependências
pip install -r requirements.txt

# Configure as variáveis de ambiente
cp .env.example .env
# Edite o .env com suas credenciais
```

**Edite o arquivo `.env`:**

```bash
# OpenAI
OPENAI_API_KEY=sk-sua-chave-aqui
OPENAI_MODEL=gpt-4o-mini

# Supabase
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_SERVICE_KEY=sua-service-key-aqui

# Aplicação
APP_ENV=development
LOG_LEVEL=INFO
```

### 4. Configure o Frontend

```bash
cd ../frontend

# Instale as dependências
npm install

# Configure as variáveis de ambiente
cp .env.example .env
# Edite o .env com suas credenciais
```

**Edite o arquivo `.env`:**

```bash
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_ANON_KEY=sua-anon-key-aqui
NUXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

### 5. Execute a Aplicação

**Terminal 1 - Backend:**
```bash
cd backend
python main.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### 6. Acesse a Aplicação

- **Frontend**: [http://localhost:3000](http://localhost:3000)
- **API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Health Check**: [http://localhost:8000/health](http://localhost:8000/health)

## 💡 Uso

### 1. Importar XMLs de NF-e

**Via Interface Web:**
1. Acesse [http://localhost:3000/upload](http://localhost:3000/upload)
2. Selecione os arquivos XML
3. Clique em "Importar"
4. Acompanhe o progresso em tempo real

**Via API:**
```bash
# Coloque os XMLs na pasta backend/xml_nf/
# Depois faça:

curl -X POST "http://localhost:8000/api/batch/upload" \
  -H "Content-Type: application/json" \
  -d '{
    "xml_folder": "xml_nf",
    "max_concurrent": 5
  }'
```

**Via Python:**
```python
import requests

response = requests.post(
    "http://localhost:8000/api/batch/upload",
    json={
        "xml_folder": "xml_nf",
        "max_concurrent": 5
    }
)

job_id = response.json()["job_id"]
print(f"Job iniciado: {job_id}")
```

### 2. Fazer Perguntas via Chat

**Via Interface Web:**
1. Acesse [http://localhost:3000](http://localhost:3000)
2. Digite sua pergunta no chat
3. Receba a resposta em linguagem natural

**Via API:**
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "minha-sessao",
    "message": "Quantas notas fiscais foram emitidas este mês?"
  }'
```

**Via Python:**
```python
import requests

response = requests.post(
    "http://localhost:8000/api/chat",
    json={
        "session_id": "user-123",
        "message": "Qual o valor total das notas fiscais?"
    }
)

print(response.json()["message"])
```

### 3. Exemplos de Perguntas

**Consultas Simples:**
- "Quantas notas fiscais foram emitidas este mês?"
- "Qual o valor total das notas?"
- "Mostre as últimas 5 notas fiscais"

**Consultas com Filtros:**
- "Quais notas foram emitidas para o CNPJ 12.345.678/0001-90?"
- "Mostre as notas canceladas de outubro"
- "Qual o valor total de ICMS das notas deste ano?"

**Análises:**
- "Qual foi o produto mais vendido?"
- "Quem são os 5 maiores clientes?"
- "Qual a média de valor das notas?"

**Contextuais:**
- "E quantas foram canceladas?" (após perguntar sobre total)
- "Mostre mais detalhes" (após uma consulta)
- "E no mês passado?" (comparação temporal)

## 🗄️ Banco de Dados

O sistema utiliza um schema completo baseado no **layout 4.00 da NF-e** da Receita Federal.

### Principais Tabelas

- **empresas** - Cadastro de emitentes e destinatários
- **notas_fiscais** - Dados principais das NF-e
- **nf_itens** - Produtos/serviços das notas
- **nf_itens_icms/ipi/pis/cofins/issqn** - Detalhamento de impostos
- **nf_transporte** - Informações de transporte
- **nf_pagamentos** - Formas de pagamento
- **nf_cobranca** e **nf_duplicatas** - Fatura e parcelas
- **nf_referencias** - Referências a outras notas
- **nf_cce** - Cartas de Correção Eletrônica

### Diagrama Simplificado

```
empresas (1) ──────┬────── (N) notas_fiscais
                   │              │
                   └──────────────┤
                                  │
                    ┌─────────────┴─────────────┬──────────────┬─────────────┐
                    │                           │              │             │
              (N) nf_itens                (N) nf_transporte   (N) nf_pagamentos  (N) nf_referencias
                    │
        ┌───────────┼───────────┬──────────┬──────────┐
        │           │           │          │          │
  nf_itens_icms  nf_itens_ipi  nf_itens_pis  nf_itens_cofins  nf_itens_issqn
```

## 📁 Estrutura do Projeto

```
multi-agent-nfe-system/
├── backend/                    # Backend Python (FastAPI + CrewAI)
│   ├── agents/                # Sistema multi-agente
│   │   ├── config/           # Configuração dos agentes (YAML)
│   │   ├── crew.py           # Orquestrador principal
│   │   └── tools/            # Ferramentas customizadas
│   ├── api/                  # Rotas da API REST
│   │   └── routes/
│   │       ├── chat.py       # Endpoints de chat
│   │       └── batch.py      # Endpoints de lote
│   ├── batch/                # Processamento em lote
│   │   ├── processor.py      # Processador de XMLs
│   │   └── job_manager.py    # Gerenciador de jobs
│   ├── memory/               # Sistema de memória RAG
│   │   └── chat_memory.py    # Memória de conversação
│   ├── database/             # Utilitários de banco
│   ├── storage/              # Armazenamento persistente
│   │   └── memory/           # ChromaDB (vetores)
│   ├── utils/                # Utilitários gerais
│   ├── tests/                # Testes automatizados
│   ├── main.py               # Ponto de entrada da API
│   ├── config.py             # Configurações
│   ├── requirements.txt      # Dependências Python
│   └── .env                  # Variáveis de ambiente
│
├── frontend/                  # Frontend Nuxt 3
│   ├── app/                  # Aplicação Nuxt
│   │   ├── components/       # Componentes Vue
│   │   ├── pages/            # Páginas/rotas
│   │   ├── layouts/          # Layouts
│   │   └── composables/      # Composables Vue
│   ├── public/               # Arquivos estáticos
│   ├── nuxt.config.ts        # Configuração Nuxt
│   ├── package.json          # Dependências Node
│   └── .env                  # Variáveis de ambiente
│
├── database/                  # Scripts SQL
│   ├── schema_nfe_completo.sql              # Schema completo
│   └── configurar_permissoes_supabase.sql   # Permissões
│
├── README.md                  # Este arquivo
└── GUIA_SUPABASE.md          # Guia de configuração do Supabase
```

## 🛠️ Tecnologias

### Backend
- **Python 3.12** - Linguagem principal
- **FastAPI** - Framework web moderno e rápido
- **CrewAI 0.80+** - Framework multi-agente
- **OpenAI GPT-4o-mini** - Modelo de linguagem
- **ChromaDB** - Banco de dados vetorial para RAG
- **Supabase/PostgreSQL** - Banco de dados relacional
- **psycopg2** - Driver PostgreSQL
- **Pydantic** - Validação de dados

### Frontend
- **Nuxt 4** - Framework Vue.js com SSR
- **Vue 3** - Framework JavaScript reativo
- **TypeScript** - Tipagem estática
- **Tailwind CSS 4** - Framework CSS utilitário
- **DaisyUI 5** - Componentes UI
- **Chart.js** - Gráficos e visualizações

### Banco de Dados
- **20+ tabelas** baseadas no layout NF-e 4.00
- **Índices otimizados** para consultas rápidas
- **Relacionamentos complexos** entre entidades
- **Suporte completo** a impostos (ICMS, IPI, PIS, COFINS, ISSQN)

## 🔧 Comandos Úteis

### Backend

```bash
# Ativar ambiente virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Executar servidor de desenvolvimento
python main.py

# Executar servidor de produção
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

# Executar testes
pytest

# Executar testes com cobertura
pytest --cov=. --cov-report=html

# Teste manual do sistema
python test_system.py
```

### Frontend

```bash
# Instalar dependências
npm install

# Desenvolvimento
npm run dev

# Build para produção
npm run build

# Preview da build
npm run preview

# Gerar site estático
npm run generate
```

## 🐛 Troubleshooting

### Erro: "Missing required environment variables"

Verifique se o arquivo `.env` existe e contém todas as variáveis necessárias:

```bash
# Backend
cd backend
cat .env

# Deve conter:
# OPENAI_API_KEY=...
# SUPABASE_URL=...
# SUPABASE_SERVICE_KEY=...
```

### Erro: "OpenAI API error"

1. Verifique se sua API key está correta
2. Confirme que tem créditos na conta OpenAI
3. Verifique rate limits em [https://platform.openai.com/account/limits](https://platform.openai.com/account/limits)

### Erro: "Database connection failed"

1. Verifique se o Supabase está online
2. Confirme as credenciais no `.env`
3. Teste a conexão:

```bash
curl $SUPABASE_URL/rest/v1/ \
  -H "apikey: $SUPABASE_SERVICE_KEY"
```

### Performance Lenta

1. Reduza a temperatura: `OPENAI_TEMPERATURE=0.3`
2. Limite o histórico: `MAX_CHAT_HISTORY=2`
3. Use modelo mais rápido: `OPENAI_MODEL=gpt-3.5-turbo`
4. Aumente workers: `uvicorn main:app --workers 4`

### Memória Alta

1. Limpe sessões antigas periodicamente
2. Reduza `MAX_CHAT_HISTORY` no `.env`
3. Reinicie a aplicação regularmente

## 📚 Documentação Adicional

### Backend
- [README do Backend](backend/README.md) - Documentação completa do backend
- [API Documentation](backend/API_DOCUMENTATION.md) - Detalhes dos endpoints
- [Testing Guide](backend/TESTING_GUIDE.md) - Guia de testes

### Frontend
- [README do Frontend](frontend/README.md) - Documentação do frontend

### Banco de Dados
- [Guia Supabase](GUIA_SUPABASE.md) - Configuração completa do Supabase
- [Schema SQL](database/schema_nfe_completo.sql) - Schema completo do banco

### Referências Externas
- [Portal da NF-e](http://www.nfe.fazenda.gov.br/) - Documentação oficial
- [CrewAI Docs](https://docs.crewai.com/) - Documentação do CrewAI
- [FastAPI Docs](https://fastapi.tiangolo.com/) - Documentação do FastAPI
- [Nuxt Docs](https://nuxt.com/) - Documentação do Nuxt

## 🎯 Próximos Passos

Após a instalação, você pode:

1. ✅ **Importar XMLs de teste** - Use os arquivos de exemplo em `xml_nf/`
2. ✅ **Testar o chat** - Faça perguntas sobre as notas importadas
3. ✅ **Explorar a API** - Acesse [http://localhost:8000/docs](http://localhost:8000/docs)
4. ✅ **Personalizar agentes** - Edite `backend/agents/config/agents.yaml`
5. ✅ **Criar relatórios** - Use o frontend para visualizar dados

## 🤝 Contribuindo

Contribuições são bem-vindas! Para contribuir:

1. Fork o repositório
2. Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

### Áreas de Interesse

- Novos agentes especializados
- Melhorias de performance
- Novos tipos de relatórios
- Integração com outros sistemas fiscais
- Testes automatizados
- Documentação

## 📄 Licença

Este projeto está sob a licença especificada no arquivo LICENSE.

## 📧 Suporte

Para questões e suporte:

- Abra uma issue no repositório
- Consulte a documentação em `/docs`
- Verifique os logs: `LOG_LEVEL=DEBUG` no `.env`

## ⚠️ Avisos Importantes

- Este sistema **não substitui** um sistema de emissão de NF-e
- **Não envia** notas para a SEFAZ (apenas armazena e consulta)
- **Não valida** regras fiscais específicas
- Use em **ambiente de produção** por sua conta e risco
- Mantenha suas **credenciais seguras** (nunca commite o `.env`)

## 🌟 Características Técnicas

- ✅ **Assíncrono**: Processamento não-bloqueante
- ✅ **Escalável**: Suporta múltiplos workers
- ✅ **Resiliente**: Tratamento robusto de erros
- ✅ **Observável**: Logging estruturado
- ✅ **Testável**: Suite completa de testes
- ✅ **Documentado**: API docs automática (Swagger/ReDoc)

---

**Desenvolvido com ❤️ usando CrewAI, FastAPI, OpenAI e Supabase**

**Layout NF-e 4.00 - Receita Federal do Brasil**
