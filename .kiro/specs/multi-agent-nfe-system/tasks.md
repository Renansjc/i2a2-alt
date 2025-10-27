# Implementation Plan

## ⚠️ IMPORTANTE - Requisitos do Projeto

### Banco de Dados Existente

**O banco de dados já existe e está totalmente configurado no Supabase.**

- ✅ Schema completo em `database/schema_nfe_completo.sql`
- ✅ Tabelas criadas: empresas, notas_fiscais, nf_itens, nf_pagamentos, nf_transporte, etc.
- ✅ Lógica de importação funcionando em `backend/db.py` (SupabaseNFeImporter)
- ✅ Conexão via Supabase REST API (não usar psycopg2 direto)

**NADA deve ser criado no banco de dados. Apenas consultar dados existentes via REST API.**

### Versão do Python

**Usar Python 3.12 para melhor suporte e compatibilidade.**

- ✅ Python 3.12.x
- ✅ Compatível com CrewAI (requer Python >=3.10 <3.14)
- ✅ Melhor performance e recursos modernos

---

## Tasks de Implementação

- [x] 1. Configurar estrutura base do projeto e dependências

  - Criar estrutura de diretórios conforme design (api/, agents/, memory/, batch/, database/, utils/)
  - Criar arquivo config.py com Settings usando pydantic-settings
  - Criar arquivo .env.example com todas as variáveis de ambiente necessárias
  - Atualizar requirements.txt com CrewAI e dependências necessárias
  - IMPORTANTE: Banco de dados já existe no Supabase, não criar novas tabelas
  - _Requirements: 8.4, 8.5_

- [x] 2. Implementar sistema de exceções e logging






  - Criar utils/exceptions.py com AppException e ErrorCode
  - Criar utils/logger.py com StructuredLogger
  - Implementar exception handlers para FastAPI
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_

- [x] 3. Implementar sistema de memória de chat









  - Criar memory/chat_memory.py com classe ChatMemory
  - Implementar métodos add_message, get_history, get_context_summary
  - Implementar lógica de manutenção de histórico limitado (últimas 2 interações)
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [ ] 4. Criar helper de informações do schema

  - Criar database/schema.py com função get_schema_info() que retorna descrição do schema
  - Ler e documentar estrutura do banco existente (database/schema_nfe_completo.sql)
  - Listar tabelas principais: notas_fiscais, empresas, nf_itens, nf_pagamentos, nf_transporte
  - Incluir informações sobre colunas e relacionamentos principais
  - IMPORTANTE: Não criar tabelas, apenas documentar o que já existe
  - _Requirements: 4.2_

- [ ] 5. Implementar CrewAI Tools para consulta ao banco existente

  - Criar agents/tools/database_tool.py com DatabaseQueryTool usando crewai_tools.BaseTool
  - Usar Supabase REST API (mesmo padrão de backend/db.py) para consultas
  - Implementar consultas usando requests (não psycopg2)
  - Suportar filtros PostgREST (eq, gt, lt, like, etc.)
  - Criar agents/tools/schema_tool.py com SchemaInfoTool
  - SchemaInfoTool deve retornar informações do schema existente
  - IMPORTANTE: Apenas consultas SELECT via REST API, nenhuma modificação no banco
  - _Requirements: 2.4, 4.1, 4.3, 4.4, 10.1_

- [ ] 6. Criar configuração YAML dos agentes

  - Criar agents/config/agents.yaml com definições dos três agentes
  - Definir sql_specialist com role, goal e backstory
  - Definir conversation_specialist com role, goal e backstory
  - Definir coordinator com role, goal e backstory
  - _Requirements: 2.1, 2.2, 2.3, 10.2_

- [ ] 7. Criar configuração YAML das tarefas

  - Criar agents/config/tasks.yaml com definições das tarefas
  - Definir analyze_intent task para o coordinator
  - Definir execute_sql_query task para o sql_specialist
  - Definir format_response task para o conversation_specialist
  - Definir direct_conversation task para o conversation_specialist
  - _Requirements: 3.1, 3.2, 3.3, 4.5, 5.1, 5.2, 5.3, 5.4, 5.5_

- [ ] 8. Implementar NFeCrew com CrewAI

  - Criar agents/crew.py com classe NFeCrew usando @CrewBase decorator
  - Implementar métodos @agent para sql_specialist, conversation_specialist e coordinator
  - Implementar métodos @task para as tarefas definidas no YAML
  - Implementar método @crew para criar Crew com processo hierárquico
  - Implementar método process_message para processar mensagens do usuário
  - Configurar coordinator como manager_agent
  - Habilitar memória integrada do CrewAI
  - _Requirements: 2.1, 2.2, 2.3, 3.4, 3.5, 10.3_

- [ ] 9. Implementar processador de lote usando código existente

  - Criar batch/processor.py com classe BatchProcessor
  - Reutilizar SupabaseNFeImporter de backend/db.py para importação de XMLs
  - Implementar método process_folder para processar XMLs em lote da pasta xml_nf
  - Criar batch/job_manager.py para gerenciar status de jobs
  - Implementar processamento assíncrono com controle de concorrência
  - Implementar tratamento de erros que permite continuar processamento
  - IMPORTANTE: Usar a lógica de importação que já existe e funciona em db.py
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [ ] 10. Implementar modelos Pydantic para API

  - Criar api/models/requests.py com ChatRequest e BatchUploadRequest
  - Criar api/models/responses.py com ChatResponse, BatchUploadResponse, BatchStatusResponse
  - Adicionar validações apropriadas nos modelos
  - _Requirements: 7.1, 7.2_

- [ ] 11. Implementar endpoints de chat com CrewAI

  - Criar api/routes/chat.py com router FastAPI
  - Implementar POST /api/chat que processa mensagens através da NFeCrew
  - Recuperar histórico da ChatMemory e passar para a Crew
  - Salvar interações (user e assistant) na memória após processamento
  - Implementar tratamento de erros e logging
  - _Requirements: 7.1, 7.2, 7.3, 7.4_

- [ ] 12. Implementar endpoints de processamento em lote

  - Criar api/routes/batch.py com router FastAPI
  - Implementar POST /api/batch/upload para iniciar processamento
  - Implementar GET /api/batch/status/{job_id} para consultar status
  - Integrar com BatchProcessor
  - _Requirements: 7.5, 1.1_

- [ ] 13. Implementar aplicação FastAPI principal com CrewAI

  - Criar main.py com aplicação FastAPI
  - Configurar variáveis de ambiente para CrewAI (OPENAI_API_KEY, OPENAI_MODEL_NAME)
  - Implementar startup event para inicializar NFeCrew e ChatMemory
  - Configurar CORS middleware
  - Incluir routers de chat e batch
  - Implementar endpoints de health check com informações do CrewAI
  - _Requirements: 7.1, 8.1, 8.2, 8.3_

- [ ] 14. Criar script de teste manual do sistema com CrewAI

  - Criar script test_system.py para testar fluxo completo
  - Testar processamento de lote com XMLs da pasta xml_nf
  - Testar chat com perguntas sobre notas fiscais através da NFeCrew
  - Testar memória de contexto com múltiplas interações
  - Validar delegação automática entre agentes (coordinator → sql_specialist/conversation_specialist)
  - Verificar uso correto das Tools (DatabaseQueryTool, SchemaInfoTool)
  - _Requirements: 1.1, 2.1, 2.2, 2.3, 6.1_

- [ ] 15. Criar documentação de uso
  - Criar README.md do backend com instruções de instalação
  - Documentar variáveis de ambiente necessárias
  - Documentar endpoints da API com exemplos
  - Criar guia de teste do sistema
  - _Requirements: 8.5_
