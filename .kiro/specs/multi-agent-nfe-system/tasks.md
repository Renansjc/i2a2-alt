# Implementation Plan

- [ ] 1. Configurar estrutura base do projeto e dependências
  - Criar estrutura de diretórios conforme design (api/, agents/, memory/, batch/, database/, utils/)
  - Criar arquivo config.py com Settings usando pydantic-settings
  - Criar arquivo .env.example com todas as variáveis de ambiente necessárias
  - Atualizar requirements.txt com dependências do OpenAI e outras bibliotecas necessárias
  - _Requirements: 8.4, 8.5_

- [ ] 2. Implementar sistema de exceções e logging
  - Criar utils/exceptions.py com AppException e ErrorCode
  - Criar utils/logger.py com StructuredLogger
  - Implementar exception handlers para FastAPI
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_

- [ ] 3. Implementar sistema de memória de chat
  - Criar memory/chat_memory.py com classe ChatMemory
  - Implementar métodos add_message, get_history, get_context_summary
  - Implementar lógica de manutenção de histórico limitado (últimas 2 interações)
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [ ] 4. Implementar cliente Supabase e schema
  - Criar database/client.py com classe SupabaseClient
  - Criar database/schema.py com função get_schema_info() que retorna descrição do schema
  - Implementar método query_table para consultas via REST API
  - Integrar com db.py existente
  - _Requirements: 4.2, 4.3_

- [ ] 5. Implementar classe base de agentes
  - Criar agents/base.py com classe abstrata BaseAgent
  - Implementar método _call_llm para chamadas à OpenAI
  - Definir interface abstrata com _get_system_prompt e process
  - _Requirements: 2.4, 10.1, 10.2_

- [ ] 6. Implementar Agente Conversa
  - Criar agents/conversation.py com classe ConversationAgent
  - Criar agents/prompts/conversation.py com system prompt
  - Implementar método process para responder mensagens
  - Implementar método format_response para formatar dados estruturados
  - _Requirements: 2.3, 5.1, 5.2, 5.3, 5.4, 5.5_

- [ ] 7. Implementar Agente SQL
  - Criar agents/sql_agent.py com classe SQLAgent
  - Criar agents/prompts/sql.py com system prompt incluindo schema
  - Implementar método _generate_sql para gerar queries
  - Implementar método process para executar queries e retornar resultados
  - Implementar validação de queries (apenas SELECT)
  - _Requirements: 2.2, 4.1, 4.2, 4.3, 4.4, 4.5_

- [ ] 8. Implementar Agente Master
  - Criar agents/master.py com classe MasterAgent
  - Criar agents/prompts/master.py com system prompt
  - Implementar método _analyze_intent para analisar intenção da mensagem
  - Implementar lógica de delegação para SQL Agent ou Conversation Agent
  - Implementar consolidação de respostas dos agentes especializados
  - _Requirements: 2.1, 3.1, 3.2, 3.3, 3.4, 3.5_

- [ ] 9. Implementar processador de lote
  - Criar batch/processor.py com classe BatchProcessor
  - Implementar método process_folder para processar XMLs em lote
  - Criar batch/job_manager.py para gerenciar status de jobs
  - Implementar processamento assíncrono com controle de concorrência
  - Implementar tratamento de erros que permite continuar processamento
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [ ] 10. Implementar modelos Pydantic para API
  - Criar api/models/requests.py com ChatRequest e BatchUploadRequest
  - Criar api/models/responses.py com ChatResponse, BatchUploadResponse, BatchStatusResponse
  - Adicionar validações apropriadas nos modelos
  - _Requirements: 7.1, 7.2_

- [ ] 11. Implementar endpoints de chat
  - Criar api/routes/chat.py com router FastAPI
  - Implementar POST /api/chat que processa mensagens através do Master Agent
  - Integrar com sistema de memória para manter contexto
  - Implementar tratamento de erros e logging
  - _Requirements: 7.1, 7.2, 7.3, 7.4_

- [ ] 12. Implementar endpoints de processamento em lote
  - Criar api/routes/batch.py com router FastAPI
  - Implementar POST /api/batch/upload para iniciar processamento
  - Implementar GET /api/batch/status/{job_id} para consultar status
  - Integrar com BatchProcessor
  - _Requirements: 7.5, 1.1_

- [ ] 13. Implementar aplicação FastAPI principal
  - Criar main.py com aplicação FastAPI
  - Implementar startup event para inicializar componentes (OpenAI client, agentes, memória)
  - Configurar CORS middleware
  - Incluir routers de chat e batch
  - Implementar endpoints de health check
  - _Requirements: 7.1, 8.1, 8.2, 8.3_

- [ ] 14. Criar script de teste manual do sistema
  - Criar script test_system.py para testar fluxo completo
  - Testar processamento de lote com XMLs da pasta xml_nf
  - Testar chat com perguntas sobre notas fiscais
  - Testar memória de contexto com múltiplas interações
  - Validar respostas dos agentes
  - _Requirements: 1.1, 2.1, 2.2, 2.3, 6.1_

- [ ] 15. Criar documentação de uso
  - Criar README.md do backend com instruções de instalação
  - Documentar variáveis de ambiente necessárias
  - Documentar endpoints da API com exemplos
  - Criar guia de teste do sistema
  - _Requirements: 8.5_
