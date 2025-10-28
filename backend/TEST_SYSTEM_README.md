# Sistema de Teste Manual Completo

## Visão Geral

O script `test_system.py` é um sistema de teste manual abrangente que valida o funcionamento completo do Multi-Agent NF-e System. Ele testa todos os componentes principais do sistema de forma integrada.

## O que é Testado

### 1. Inicialização dos Componentes
- ✅ NFeCrew (sistema multi-agente CrewAI)
- ✅ ChatMemory (memória com RAG)
- ✅ BatchProcessor (processamento em lote)
- ✅ JobManager (gerenciamento de jobs)

### 2. Processamento em Lote de XMLs
- ✅ Localização de arquivos XML na pasta `xml_nf`
- ✅ Processamento assíncrono com controle de concorrência
- ✅ Importação usando lógica existente em `db.py`
- ✅ Tratamento de erros e continuação do processamento
- ✅ Relatório de sucessos e falhas

**Requirement testado:** 1.1

### 3. Chat Conversacional
- ✅ Saudações e interações gerais
- ✅ Perguntas sobre o sistema
- ✅ Respostas em linguagem natural
- ✅ Delegação para Conversation Specialist

**Requirements testados:** 2.3, 5.1-5.5

### 4. Chat com Consultas ao Banco
- ✅ Contagem de notas fiscais
- ✅ Cálculo de valores totais
- ✅ Listagem de empresas
- ✅ Execução de queries SQL
- ✅ Formatação de respostas com valores monetários

**Requirements testados:** 2.2, 4.1-4.5

### 5. Memória de Contexto
- ✅ Armazenamento de histórico (mínimo 2 interações)
- ✅ Recuperação de contexto para agentes
- ✅ Perguntas de acompanhamento usando contexto
- ✅ Resumo de conversação
- ✅ Estatísticas de memória

**Requirements testados:** 6.1-6.5

### 6. Delegação Automática entre Agentes
- ✅ Coordinator → SQL Specialist (para queries)
- ✅ Coordinator → Conversation Specialist (para conversação)
- ✅ Processo hierárquico do CrewAI
- ✅ Verificação de configuração dos agentes

**Requirements testados:** 2.1, 3.1-3.5

### 7. Uso Correto das Tools
- ✅ SchemaInfoTool (informações do schema)
- ✅ SchemaSearchTool (busca semântica no schema)
- ✅ SQLQueryTool (execução de queries SQL)
- ✅ Distribuição correta de tools entre agentes

**Requirements testados:** 4.1-4.4, 10.1

## Pré-requisitos

### 1. Variáveis de Ambiente

Certifique-se de que o arquivo `.env` está configurado com:

```bash
# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_MODEL_NAME=gpt-4o-mini

# Supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_KEY=eyJ...

# Aplicação
APP_ENV=development
LOG_LEVEL=INFO
MAX_CHAT_HISTORY=4

# Batch Processing
XML_FOLDER=xml_nf
MAX_CONCURRENT_UPLOADS=3
```

### 2. Arquivos XML

Coloque arquivos XML de NF-e na pasta `xml_nf/` para testar o processamento em lote.

### 3. Banco de Dados

O banco de dados Supabase deve estar configurado e acessível com o schema completo de NF-e.

## Como Executar

### Execução Básica

```bash
cd backend
python test_system.py
```

### Execução com Ambiente Virtual

```bash
cd backend
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

python test_system.py
```

## Fluxo de Execução

1. **Inicialização**: O script inicializa todos os componentes do sistema
2. **Batch Processing**: Processa XMLs da pasta `xml_nf`
3. **Chat Conversacional**: Testa interações gerais
4. **Chat com Queries**: Testa consultas ao banco de dados
5. **Memória**: Valida contexto e histórico
6. **Delegação**: Verifica delegação entre agentes
7. **Tools**: Testa uso das ferramentas
8. **Resumo**: Apresenta estatísticas e resultados

## Saída Esperada

### Sucesso Total

```
🎉 SUCESSO! Todos os testes passaram!

O sistema está funcionando corretamente:
  ✓ Processamento em lote de XMLs
  ✓ Chat com consultas ao banco via CrewAI
  ✓ Memória de contexto com RAG
  ✓ Delegação automática entre agentes
  ✓ Uso correto das Tools
```

### Falhas Parciais

```
⚠️  ATENÇÃO: 2 teste(s) falharam

Revise os erros acima para identificar problemas.
```

## Interpretação dos Resultados

### ✓ PASSOU
- O teste executou com sucesso
- Todos os critérios foram atendidos
- Componente está funcionando corretamente

### ✗ FALHOU
- O teste encontrou problemas
- Verifique os detalhes do erro
- Pode indicar:
  - Configuração incorreta
  - Serviço indisponível
  - Bug no código

## Troubleshooting

### Erro: "Pasta xml_nf não encontrada"

**Solução**: Crie a pasta e adicione arquivos XML:
```bash
mkdir xml_nf
# Copie arquivos XML para xml_nf/
```

### Erro: "OpenAI API error"

**Solução**: Verifique a chave API:
```bash
# Verifique se OPENAI_API_KEY está definida
echo $OPENAI_API_KEY

# Teste a chave
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

### Erro: "Supabase connection failed"

**Solução**: Verifique as credenciais do Supabase:
```bash
# Teste a conexão
curl $SUPABASE_URL/rest/v1/ \
  -H "apikey: $SUPABASE_SERVICE_KEY"
```

### Erro: "Memory initialization failed"

**Solução**: Verifique permissões de escrita:
```bash
# Criar diretório de storage
mkdir -p storage/memory
chmod 755 storage/memory
```

## Testes Individuais

Você pode executar testes individuais modificando o script:

```python
# No final do script, comente os testes que não quer executar
async def run_all_tests(self):
    await self.test_1_initialize_components()
    # await self.test_2_batch_processing()  # Comentado
    await self.test_3_chat_conversational()
    # ... etc
```

## Logs e Debugging

### Habilitar Logs Detalhados

```bash
# No .env
LOG_LEVEL=DEBUG
```

### Verificar Logs do CrewAI

O CrewAI gera logs detalhados durante a execução. Procure por:
- `[Coordinator]` - Ações do coordenador
- `[SQL Specialist]` - Queries executadas
- `[Conversation Specialist]` - Formatação de respostas

### Verificar Memória

```python
# Adicione ao script para debug
stats = self.memory.get_memory_stats()
print(json.dumps(stats, indent=2))
```

## Métricas de Performance

O script mede:
- **Tempo de processamento** de cada teste
- **Tempo de resposta** dos agentes
- **Número de mensagens** na memória
- **Taxa de sucesso** do batch processing

### Tempos Esperados

- Inicialização: < 5s
- Batch processing: 2-10s por XML
- Chat conversacional: 2-5s por mensagem
- Chat com query: 5-15s por mensagem

## Integração Contínua

Para usar em CI/CD:

```bash
# Executar sem interação
python test_system.py --no-prompt

# Ou modificar o script para remover input()
```

## Próximos Passos

Após validar o sistema com este script:

1. **Testes Unitários**: Adicione testes unitários para componentes individuais
2. **Testes de Carga**: Teste com grande volume de XMLs
3. **Testes de Stress**: Teste com muitas requisições simultâneas
4. **Testes de Integração**: Teste integração com frontend

## Suporte

Para problemas ou dúvidas:
1. Verifique os logs detalhados
2. Revise a configuração do `.env`
3. Consulte a documentação do CrewAI
4. Verifique a conectividade com Supabase e OpenAI

## Referências

- **Requirements**: `.kiro/specs/multi-agent-nfe-system/requirements.md`
- **Design**: `.kiro/specs/multi-agent-nfe-system/design.md`
- **Tasks**: `.kiro/specs/multi-agent-nfe-system/tasks.md`
- **CrewAI Docs**: https://docs.crewai.com/
