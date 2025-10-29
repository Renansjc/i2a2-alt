# Sistema Multi-Agente de Análise de Notas Fiscais Eletrônicas

## Pitch Deck & Apresentação Técnica

---

## 🎯 Visão Geral

**Sistema inteligente que transforma a gestão de Notas Fiscais Eletrônicas (NF-e) através de Inteligência Artificial Multi-Agente, permitindo consultas em linguagem natural e análises automatizadas.**

### O Problema

- Empresas brasileiras lidam com milhares de NF-e mensalmente
- Consultar dados fiscais requer conhecimento técnico de SQL e sistemas complexos
- Análises demoram horas e dependem de especialistas
- Informações críticas ficam "presas" em bancos de dados inacessíveis

### A Solução

Um assistente de IA que conversa naturalmente sobre suas notas fiscais:

- **"Quanto vendemos este mês?"** → Resposta instantânea com análise
- **"Quais os 5 produtos mais vendidos?"** → Ranking automático
- **"Mostre as notas da empresa XYZ"** → Busca inteligente

---

## 🏗️ Arquitetura da Solução

### Stack Tecnológico Moderno

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (Nuxt 4)                        │
│  • Vue 3.5 + TypeScript                                     │
│  • Tailwind CSS 4.1 + DaisyUI 5.3                          │
│  • Dashboard Executivo + Chat Flutuante                     │
└─────────────────────────────────────────────────────────────┘
                            ↕ REST API
┌─────────────────────────────────────────────────────────────┐
│                   BACKEND (Python 3.12)                     │
│  • FastAPI (async/await)                                    │
│  • CrewAI 0.80+ (Multi-Agent System)                       │
│  • OpenAI GPT-4o-mini                                       │
│  • RAG Memory (ChromaDB)                                    │
└─────────────────────────────────────────────────────────────┘
                            ↕ SQL
┌─────────────────────────────────────────────────────────────┐
│              DATABASE (Supabase/PostgreSQL)                 │
│  • Schema completo NF-e Layout 4.00                        │
│  • 15+ tabelas relacionadas                                 │
│  • Dados fiscais estruturados                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 🤖 Sistema Multi-Agente (CrewAI)

### Arquitetura Hierárquica com 3 Agentes Especializados

#### 1. **Coordenador** (Manager)

- **Função**: Analisa intenção do usuário e orquestra o fluxo
- **Decisões**:
  - Pergunta requer dados? → Delega para SQL Specialist
  - Resposta conversacional? → Delega para Conversation Specialist
  - Follow-up? → Usa contexto da conversa
- **Modelo**: GPT-4o-mini (temperatura 0.4)

#### 2. **SQL Specialist** (Worker)

- **Função**: Gera e executa queries SQL otimizadas
- **Capacidades**:
  - Entende schema complexo de NF-e
  - Gera JOINs eficientes
  - Agregações (SUM, COUNT, AVG, GROUP BY)
  - Validação de segurança (apenas SELECT)
- **Modelo**: GPT-4o-mini (temperatura 0.1 - precisão máxima)

#### 3. **Conversation Specialist** (Worker)

- **Função**: Formata respostas em linguagem natural
- **Capacidades**:
  - Transforma JSON em narrativas fluidas
  - Formata valores monetários (R$ 1.234,56)
  - Adiciona insights e contexto
  - Responde follow-ups usando histórico
- **Modelo**: GPT-4o-mini (temperatura 0.4)

### Fluxo de Processamento

```
Usuário: "Quanto vendemos em outubro?"
    ↓
[Coordenador] Analisa → Identifica: precisa de dados
    ↓
[Coordenador] Delega → SQL Specialist
    ↓
[SQL Specialist] Gera query:
    SELECT COUNT(*), SUM(valor_total_nota)
    FROM notas_fiscais
    WHERE status='autorizada'
    AND EXTRACT(MONTH FROM data_hora_emissao) = 10
    ↓
[SQL Specialist] Executa → Retorna dados brutos
    ↓
[Coordenador] Delega → Conversation Specialist
    ↓
[Conversation Specialist] Formata:
    "Em outubro foram emitidas 45 notas fiscais
     totalizando R$ 125.430,50. Isso representa
     15% a mais que setembro."
    ↓
Usuário recebe resposta natural e contextualizada
```

---

## 💾 Banco de Dados (Supabase/PostgreSQL)

### Schema Completo NF-e Layout 4.00

**15 Tabelas Principais:**

1. **empresas** - Emitentes e destinatários

   - CPF/CNPJ, razão social, endereço completo
   - Regime tributário, inscrições estaduais

2. **notas_fiscais** - Dados principais da NF-e

   - Chave de acesso (44 dígitos)
   - Valores totais, impostos, datas
   - Tipo de operação (entrada/saída)
   - Status (autorizada, cancelada, etc)

3. **nf_itens** - Produtos/serviços da nota

   - Descrição, quantidade, valores
   - NCM, CFOP, unidade comercial

4. **nf_itens_icms/ipi/pis/cofins/issqn** - Impostos detalhados

   - Base de cálculo, alíquotas, valores
   - CST, modalidade de cálculo

5. **nf_pagamentos** - Formas de pagamento

   - Tipo (dinheiro, cartão, boleto)
   - Valores, parcelas

6. **nf_transporte** - Dados de transporte

   - Transportadora, volumes, frete

7. **nf_cobranca, nf_duplicatas** - Cobrança e parcelas

8. **nf_referencias** - Notas referenciadas

9. **nf_cce** - Cartas de correção eletrônica

### Relacionamentos Principais

```sql
notas_fiscais
├── emitente_id → empresas.id
├── destinatario_id → empresas.id
└── nf_itens (1:N)
    ├── nf_itens_icms (1:1)
    ├── nf_itens_ipi (1:1)
    ├── nf_itens_pis (1:1)
    └── nf_itens_cofins (1:1)
```

---

## 🎨 Frontend (Nuxt 3 + Vue 3)

### 4 Páginas Principais

#### 1. **Dashboard Executivo** (`/`)

**Visão estratégica do negócio em tempo real**

**Componentes:**

- **4 KPIs Principais**:

  - Movimentação Fiscal Total
  - Carga Tributária
  - Operações do Período
  - Ticket Médio

- **Insights Estratégicos** (topo da página):

  - Distribuição de Operações (entradas vs saídas)
  - Principais Parceiros Comerciais
  - Análise de Carga Tributária

- **6 Gráficos Interativos**:
  - Evolução Mensal (linha)
  - Distribuição por Tipo de Operação (rosca)
  - Top 5 Produtos (barras)
  - Composição Tributária (rosca)
  - Top 5 Empresas (barras)
  - Fluxo de Caixa (barras empilhadas)

**Tecnologias:**

- Chart.js + vue-chartjs
- Tailwind CSS para layout responsivo
- Gradientes e animações suaves

#### 2. **Upload de NF-e** (`/upload`)

**Importação em lote de arquivos XML**

**Funcionalidades:**

- Drag & drop de múltiplos arquivos
- Upload assíncrono com progress bar
- Validação de formato XML
- Tracking de jobs em tempo real
- Histórico de importações

**Processo:**

1. Usuário seleciona XMLs
2. Backend processa em paralelo (máx 5 simultâneos)
3. Parser extrai dados do XML
4. Validação contra schema NF-e
5. Inserção no PostgreSQL
6. Feedback em tempo real

#### 3. **Notas Fiscais** (`/invoices`)

**Listagem e busca de notas**

**Funcionalidades:**

- Tabela paginada com todas as notas
- Filtros por status, período, empresa
- Busca por chave de acesso
- Cards com estatísticas (total, valor, navegação)
- Visualização responsiva (cards em mobile)

**Detalhes da Nota** (`/invoices/[id]`)

- **Sistema de Tabs** (Geral, Itens, Complementares)
- **Tab Geral**:
  - 4 stats cards (Valor Total, Impostos, Emissão, Produtos)
  - Cards de Emitente e Destinatário
  - Informações Fiscais (chave, modelo, tipo)
  - Totalizadores (produtos, frete, impostos)
- **Tab Itens**:
  - Tabela completa de produtos (desktop)
  - Cards individuais (mobile)
  - Totalizador de itens
- **Tab Complementares**:
  - Informações adicionais da nota

#### 4. **Chat** (`/chat`)

**Redirecionamento para widget flutuante**

---

## 💬 Chat Flutuante (Floating Widget)

### Design Moderno Estilo Chatbot

**Características:**

- **Botão flutuante** no canto inferior direito
- **Sempre disponível** em todas as páginas
- **Expansível/minimizável** com animações suaves
- **Badge de notificação** para mensagens não lidas

**Interface do Chat:**

```
┌─────────────────────────────────┐
│ 🤖 Assistente NF-e    🗑️  ⌄    │ ← Header azul
├─────────────────────────────────┤
│                                 │
│  💬 Olá! Como posso ajudar?    │
│                                 │
│  💡 Quantas notas fiscais       │
│     tenho?                      │
│                                 │
│  💰 Qual o valor total das      │
│     notas?                      │
│                                 │
├─────────────────────────────────┤
│ Digite sua mensagem...      ➤  │ ← Input
└─────────────────────────────────┘
```

**Funcionalidades:**

- Sugestões de perguntas rápidas
- Suporte a Markdown nas respostas
- Scroll automático
- Timestamps
- Indicador de "digitando..."
- Histórico de conversas
- Botão de limpar histórico

**Dimensões:**

- Minimizado: Botão circular 64px
- Expandido: 400px × 600px
- Z-index: 50 (sempre no topo)

---

## 🧠 Sistema de Memória (RAG)

### ChromaDB + Embeddings

**Arquitetura:**

```
Mensagem do usuário
    ↓
[Embedding] sentence-transformers
    ↓
[ChromaDB] Busca semântica
    ↓
[Contexto] Últimas 4 mensagens relevantes
    ↓
[CrewAI] Processa com contexto
```

**Benefícios:**

- Conversas contextualizadas
- Follow-ups inteligentes
- Memória de longo prazo
- Busca semântica (não apenas keywords)

**Exemplo:**

```
User: "Gere uma empresa aleatória"
AI: "A empresa XYZ (CNPJ 12.345.678/0001-90)..."

User: "Qual foi o nome?" ← Follow-up
AI: "A empresa era XYZ" ← Usa contexto, não consulta banco
```

---

## 📊 Funcionalidades Principais

### 1. Consultas em Linguagem Natural

**Exemplos de Perguntas:**

- "Quanto vendemos este mês?"
- "Quais os 5 produtos mais vendidos?"
- "Mostre as notas da empresa XYZ"
- "Qual o total de ICMS pago em outubro?"
- "Compare vendas de janeiro vs fevereiro"
- "Gere uma empresa aleatória do banco"

**Tipos de Análise:**

- ✅ Totalizações (SUM, COUNT, AVG)
- ✅ Rankings (TOP N)
- ✅ Filtros (por período, empresa, produto)
- ✅ Comparações (períodos, empresas)
- ✅ Agregações complexas (GROUP BY)
- ✅ Estatísticas (média, máximo, mínimo)

### 2. Dashboard Executivo

**Métricas em Tempo Real:**

- Movimentação fiscal total
- Carga tributária (%)
- Número de operações
- Ticket médio

**Análises Visuais:**

- Evolução temporal
- Distribuição por tipo
- Top produtos/empresas
- Composição de impostos
- Fluxo de caixa

### 3. Importação em Lote

**Capacidades:**

- Upload de múltiplos XMLs
- Processamento paralelo (até 5 simultâneos)
- Validação automática
- Tracking de progresso
- Histórico de jobs

**Performance:**

- ~2-3 segundos por XML
- Processamento assíncrono
- Feedback em tempo real

### 4. Gestão de Notas

**Visualização:**

- Lista completa paginada
- Filtros avançados
- Busca por chave
- Detalhes completos

**Informações Disponíveis:**

- Dados do emitente/destinatário
- Itens e produtos
- Impostos detalhados
- Pagamentos e transporte
- Informações complementares

---

## 🔒 Segurança e Validação

### Backend

- ✅ Apenas queries SELECT (sem INSERT/UPDATE/DELETE)
- ✅ Validação de SQL injection
- ✅ LIMIT obrigatório (máx 100 registros)
- ✅ Timeout de queries
- ✅ Validação de ambiente (variáveis obrigatórias)
- ✅ Logs estruturados

### Frontend

- ✅ Validação de tipos (TypeScript)
- ✅ Sanitização de inputs
- ✅ CORS configurado
- ✅ Tratamento de erros

### Database

- ✅ Constraints e foreign keys
- ✅ Índices otimizados
- ✅ Backup automático (Supabase)

---

## ⚡ Performance

### Tempos de Resposta

**Chat/Consultas:**

- Pergunta simples: ~3-5 segundos
- Pergunta complexa: ~8-12 segundos
- Follow-up (usa contexto): ~2-3 segundos

**Dashboard:**

- Carregamento inicial: ~1-2 segundos
- Atualização de gráficos: instantâneo

**Upload:**

- 1 XML: ~2-3 segundos
- 10 XMLs (paralelo): ~15-20 segundos

### Otimizações Implementadas

**Backend:**

- Async/await em todas operações I/O
- Connection pooling (PostgreSQL)
- Cache de schema
- Processamento paralelo de XMLs

**Frontend:**

- Code splitting (Nuxt 3)
- Lazy loading de componentes
- Otimização de imagens
- Debounce em inputs

**Database:**

- Índices em chaves de busca
- Queries otimizadas com EXPLAIN
- Particionamento futuro (se necessário)

---

## 🎯 Diferenciais Competitivos

### 1. **Inteligência Artificial Multi-Agente**

- Não é um chatbot simples
- Sistema especializado com 3 agentes
- Cada agente tem expertise específica
- Coordenação inteligente de tarefas

### 2. **Linguagem Natural Real**

- Não requer conhecimento de SQL
- Entende português brasileiro
- Contexto de conversação
- Follow-ups inteligentes

### 3. **Memória Semântica (RAG)**

- Não esquece o contexto
- Busca por similaridade
- Conversas naturais
- Aprendizado contínuo

### 4. **Interface Moderna**

- Dashboard executivo profissional
- Chat flutuante sempre disponível
- Design responsivo
- Animações suaves

### 5. **Compliance Fiscal**

- Schema completo NF-e Layout 4.00
- Todos os campos da Receita Federal
- Validação de dados
- Auditoria completa

---

## 📈 Casos de Uso

### 1. **CFO/Controller**

"Preciso do valor total de vendas do trimestre para o board"
→ Resposta em 5 segundos, sem depender de analista

### 2. **Gerente Comercial**

"Quais produtos estão vendendo mais este mês?"
→ Ranking instantâneo com valores

### 3. **Contador**

"Qual o total de ICMS a recolher?"
→ Cálculo automático por período

### 4. **Analista Fiscal**

"Mostre todas as notas da empresa XYZ"
→ Lista completa com detalhes

### 5. **Auditor**

"Compare vendas de janeiro vs fevereiro"
→ Análise comparativa automática

---

## 🚀 Roadmap Futuro

### Curto Prazo (1-3 meses)

- [ ] Exportação de relatórios (PDF, Excel)
- [ ] Alertas automáticos (impostos, prazos)
- [ ] Integração com e-mail
- [ ] Dashboard personalizável

### Médio Prazo (3-6 meses)

- [ ] Análise preditiva (ML)
- [ ] Detecção de anomalias
- [ ] Recomendações fiscais
- [ ] API pública

### Longo Prazo (6-12 meses)

- [ ] Mobile app (React Native)
- [ ] Integração com ERPs
- [ ] Multi-tenancy
- [ ] Marketplace de análises

---

## 💰 Modelo de Negócio

### Planos Sugeridos

**Starter** - R$ 297/mês

- Até 1.000 notas/mês
- 1 usuário
- Chat básico
- Dashboard padrão

**Professional** - R$ 797/mês

- Até 10.000 notas/mês
- 5 usuários
- Chat avançado
- Dashboards personalizados
- Exportação de relatórios

**Enterprise** - Sob consulta

- Notas ilimitadas
- Usuários ilimitados
- API dedicada
- Suporte prioritário
- Customizações

---

## 🛠️ Setup e Deployment

### Requisitos

**Backend:**

- Python 3.12+
- PostgreSQL 14+
- OpenAI API key
- Supabase account

**Frontend:**

- Node.js 18+
- NPM/Yarn

### Instalação Rápida

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Configurar .env
python main.py

# Frontend
cd frontend
npm install
cp .env.example .env
# Configurar .env
npm run dev
```

### Deploy

**Backend:**

- Railway, Render, ou AWS EC2
- Variáveis de ambiente configuradas
- PostgreSQL gerenciado (Supabase)

**Frontend:**

- Vercel (recomendado para Nuxt)
- Netlify
- AWS Amplify

---

## 📞 Contato e Suporte

### Documentação

- `/backend/README.md` - Setup backend
- `/backend/API_DOCUMENTATION.md` - Endpoints
- `/frontend/README.md` - Setup frontend
- `/database/schema_nfe_completo.sql` - Schema completo

### Endpoints Úteis

- API Docs: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/health`
- Frontend: `http://localhost:3000`

---

## 🎬 Roteiro para Vídeo de Apresentação

### Abertura (30s)

- Problema: Empresas com milhares de NF-e, dados inacessíveis
- Solução: IA que conversa sobre suas notas fiscais

### Demo Dashboard (1min)

- Mostrar KPIs em tempo real
- Navegar pelos gráficos
- Destacar insights automáticos

### Demo Chat (2min)

- Abrir widget flutuante
- Fazer pergunta: "Quanto vendemos este mês?"
- Mostrar resposta formatada
- Follow-up: "E qual foi o produto mais vendido?"
- Destacar contexto da conversa

### Demo Upload (1min)

- Arrastar XMLs
- Mostrar processamento paralelo
- Verificar notas importadas

### Arquitetura (1min)

- Mostrar diagrama multi-agente
- Explicar fluxo: Coordenador → SQL → Conversation
- Destacar tecnologias (CrewAI, Supabase, Nuxt)

### Diferenciais (30s)

- Multi-agente (não é chatbot simples)
- Memória semântica (RAG)
- Compliance fiscal completo
- Interface moderna

### Fechamento (30s)

- Call to action
- Contato
- Próximos passos

**Duração Total: ~6 minutos**

---

## 📊 Métricas de Sucesso

### Técnicas

- ✅ 3 agentes especializados funcionando
- ✅ 15+ tabelas de NF-e implementadas
- ✅ 4 páginas frontend completas
- ✅ Chat flutuante em todas as páginas
- ✅ Dashboard com 6 gráficos interativos
- ✅ Upload em lote funcional
- ✅ Memória RAG implementada

### Performance

- ✅ Respostas em 3-5 segundos
- ✅ Upload de 10 XMLs em ~20 segundos
- ✅ Dashboard carrega em 1-2 segundos
- ✅ 100% responsivo (mobile/desktop)

### Qualidade

- ✅ TypeScript no frontend
- ✅ Validação de dados
- ✅ Tratamento de erros
- ✅ Logs estruturados
- ✅ Documentação completa

---

## 🏆 Conclusão

**Sistema Multi-Agente de NF-e** é uma solução completa e inovadora que:

✅ **Democratiza** o acesso a dados fiscais através de linguagem natural  
✅ **Automatiza** análises que levariam horas  
✅ **Moderniza** a gestão fiscal com IA de ponta  
✅ **Escala** para empresas de qualquer porte  
✅ **Garante** compliance com legislação brasileira

**Tecnologias de ponta + UX excepcional + IA multi-agente = Transformação digital fiscal**

---

_Documento preparado para pitch deck e apresentação em vídeo_  
_Versão 1.0 - Outubro 2025_
