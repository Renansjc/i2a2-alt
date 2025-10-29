# Quick Start - Teste do Sistema

## Execução Rápida

```bash
cd backend
python test_system.py
```

## O que será testado

1. ✅ **Inicialização** - NFeCrew, ChatMemory, BatchProcessor
2. ✅ **Batch Processing** - Importação de XMLs da pasta `xml_nf`
3. ✅ **Chat Conversacional** - Saudações e perguntas gerais
4. ✅ **Chat com Queries** - Consultas ao banco de dados
5. ✅ **Memória de Contexto** - Histórico e perguntas de acompanhamento
6. ✅ **Delegação de Agentes** - coordenador → SQL/Conversation Specialists
7. ✅ **Tools** - SchemaInfoTool, SchemaSearchTool, SQLQueryTool

## Pré-requisitos Mínimos

### 1. Arquivo .env configurado

```bash
OPENAI_API_KEY=sk-...
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_KEY=eyJ...
```

### 2. Pasta xml_nf com arquivos XML

```bash
mkdir xml_nf
# Adicione arquivos XML de NF-e
```

### 3. Dependências instaladas

```bash
pip install -r requirements.txt
```

## Resultado Esperado

```
🎉 SUCESSO! Todos os testes passaram!

O sistema está funcionando corretamente:
  ✓ Processamento em lote de XMLs
  ✓ Chat com consultas ao banco via CrewAI
  ✓ Memória de contexto com RAG
  ✓ Delegação automática entre agentes
  ✓ Uso correto das Tools

📊 ESTATÍSTICAS:
  Total de testes: 7
  Testes aprovados: 7 (100.0%)
  Testes falhados: 0 (0.0%)
```

## Tempo Estimado

- **Inicialização**: ~5 segundos
- **Batch Processing**: ~2-10 segundos por XML
- **Testes de Chat**: ~5-15 segundos por teste
- **Total**: ~2-5 minutos (depende do número de XMLs)

## Troubleshooting Rápido

### Erro de API Key
```bash
# Verifique se a chave está definida
echo $OPENAI_API_KEY
```

### Erro de Conexão Supabase
```bash
# Teste a conexão
curl $SUPABASE_URL/rest/v1/ -H "apikey: $SUPABASE_SERVICE_KEY"
```

### Pasta xml_nf não encontrada
```bash
mkdir xml_nf
# Copie arquivos XML para esta pasta
```

## Documentação Completa

Para mais detalhes, consulte: `TEST_SYSTEM_README.md`

## Próximos Passos

Após validar o sistema:
1. Execute o servidor: `python main.py`
2. Acesse a API: http://localhost:8000/docs
3. Teste via frontend ou Postman
