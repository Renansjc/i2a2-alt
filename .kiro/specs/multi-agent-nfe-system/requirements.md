# Requirements Document

## Introduction

Este documento especifica os requisitos para um sistema multi-agente de IA que processa notas fiscais eletrônicas (NF-e) em lote e responde perguntas dos usuários através de um chat interativo. O sistema utiliza três agentes especializados que se comunicam entre si: um agente Master para coordenação, um agente SQL para consultas ao banco de dados, e um agente de Conversa para interação com o usuário. O sistema mantém contexto de conversação através de memória de chat.

## Glossary

- **Sistema**: O sistema multi-agente de IA para processamento de NF-e
- **Agente Master**: Agente coordenador que gerencia e delega tarefas aos outros agentes
- **Agente SQL**: Agente especializado em criar e executar consultas SQL no banco de dados Supabase
- **Agente Conversa**: Agente especializado em interagir com o usuário através de linguagem natural
- **Processador de Lote**: Componente que processa múltiplos arquivos XML de NF-e da pasta xml_nf
- **Memória de Chat**: Sistema de armazenamento de histórico de conversação com contexto de pelo menos 2 interações anteriores
- **Supabase**: Banco de dados PostgreSQL hospedado onde as NF-e são armazenadas
- **XML NF-e**: Arquivo XML contendo dados estruturados de nota fiscal eletrônica
- **GPT-4o-mini**: Modelo de linguagem da OpenAI utilizado pelos agentes

## Requirements

### Requirement 1

**User Story:** Como administrador do sistema, eu quero processar múltiplos arquivos XML de NF-e em lote da pasta xml_nf, para que todas as notas fiscais sejam importadas automaticamente para o banco de dados.

#### Acceptance Criteria

1. WHEN o processador de lote é executado, THE Sistema SHALL localizar todos os arquivos XML na pasta xml_nf
2. WHEN um arquivo XML é encontrado, THE Sistema SHALL processar o arquivo utilizando a lógica existente em db.py
3. WHEN um arquivo XML é processado com sucesso, THE Sistema SHALL registrar o sucesso da importação
4. IF um arquivo XML falha no processamento, THEN THE Sistema SHALL registrar o erro e continuar processando os demais arquivos
5. WHEN todos os arquivos são processados, THE Sistema SHALL gerar um relatório com total de sucessos e falhas

### Requirement 2

**User Story:** Como desenvolvedor, eu quero que o sistema tenha três agentes de IA distintos utilizando GPT-4o-mini, para que cada agente possa executar sua função especializada.

#### Acceptance Criteria

1. THE Sistema SHALL implementar um Agente Master utilizando o modelo GPT-4o-mini da OpenAI
2. THE Sistema SHALL implementar um Agente SQL utilizando o modelo GPT-4o-mini da OpenAI
3. THE Sistema SHALL implementar um Agente Conversa utilizando o modelo GPT-4o-mini da OpenAI
4. WHEN um agente é inicializado, THE Sistema SHALL configurar o agente com sua especialização específica através de system prompts
5. THE Sistema SHALL manter instâncias separadas de cada agente durante a execução

### Requirement 3

**User Story:** Como desenvolvedor, eu quero que o Agente Master coordene os outros agentes, para que as requisições do usuário sejam direcionadas ao agente apropriado.

#### Acceptance Criteria

1. WHEN uma mensagem do usuário é recebida, THE Agente Master SHALL analisar a intenção da mensagem
2. IF a mensagem requer consulta ao banco de dados, THEN THE Agente Master SHALL delegar a tarefa ao Agente SQL
3. IF a mensagem requer resposta conversacional, THEN THE Agente Master SHALL delegar a tarefa ao Agente Conversa
4. WHEN um agente especializado retorna uma resposta, THE Agente Master SHALL processar e encaminhar a resposta ao usuário
5. THE Agente Master SHALL manter o fluxo de comunicação entre os agentes

### Requirement 4

**User Story:** Como desenvolvedor, eu quero que o Agente SQL gere e execute consultas SQL, para que dados das notas fiscais possam ser recuperados do banco de dados.

#### Acceptance Criteria

1. WHEN o Agente SQL recebe uma solicitação de dados, THE Agente SQL SHALL gerar uma consulta SQL válida baseada na solicitação
2. THE Agente SQL SHALL ter acesso ao schema do banco de dados Supabase
3. WHEN uma consulta SQL é gerada, THE Agente SQL SHALL executar a consulta utilizando as credenciais do Supabase
4. WHEN a consulta retorna resultados, THE Agente SQL SHALL formatar os resultados de forma estruturada
5. IF a consulta falha, THEN THE Agente SQL SHALL retornar uma mensagem de erro descritiva

### Requirement 5

**User Story:** Como desenvolvedor, eu quero que o Agente Conversa interaja naturalmente com o usuário, para que as respostas sejam compreensíveis e contextualizadas.

#### Acceptance Criteria

1. WHEN o Agente Conversa recebe dados ou informações, THE Agente Conversa SHALL formatar a resposta em linguagem natural
2. THE Agente Conversa SHALL manter tom profissional e amigável nas respostas
3. WHEN dados numéricos são apresentados, THE Agente Conversa SHALL formatar valores monetários e quantidades de forma legível
4. THE Agente Conversa SHALL responder perguntas gerais sobre o sistema e suas funcionalidades
5. WHEN informações estão incompletas, THE Agente Conversa SHALL solicitar esclarecimentos ao usuário

### Requirement 6

**User Story:** Como usuário, eu quero que o sistema mantenha contexto das minhas conversas anteriores, para que eu possa fazer perguntas de acompanhamento sem repetir informações.

#### Acceptance Criteria

1. THE Sistema SHALL implementar um sistema de Memória de Chat para cada sessão de usuário
2. THE Sistema SHALL armazenar no mínimo as últimas 2 interações de chat (mensagens e respostas)
3. WHEN um agente processa uma mensagem, THE Sistema SHALL fornecer o histórico de chat ao agente
4. WHEN uma nova interação é concluída, THE Sistema SHALL adicionar a interação ao histórico de chat
5. THE Sistema SHALL manter o contexto de conversação durante toda a sessão do usuário

### Requirement 7

**User Story:** Como desenvolvedor, eu quero que o sistema tenha uma API REST para comunicação com o frontend, para que o frontend possa enviar mensagens e receber respostas dos agentes.

#### Acceptance Criteria

1. THE Sistema SHALL implementar uma API REST utilizando FastAPI
2. THE Sistema SHALL expor um endpoint para envio de mensagens do usuário
3. WHEN uma mensagem é recebida via API, THE Sistema SHALL processar a mensagem através do Agente Master
4. WHEN o processamento é concluído, THE Sistema SHALL retornar a resposta via API
5. THE Sistema SHALL expor um endpoint para iniciar o processamento em lote de XMLs

### Requirement 8

**User Story:** Como desenvolvedor, eu quero que o sistema utilize variáveis de ambiente para configurações sensíveis, para que credenciais e chaves API não sejam expostas no código.

#### Acceptance Criteria

1. THE Sistema SHALL carregar a chave API da OpenAI de variável de ambiente
2. THE Sistema SHALL carregar as credenciais do Supabase de variáveis de ambiente
3. WHEN uma variável de ambiente obrigatória está ausente, THE Sistema SHALL retornar erro descritivo na inicialização
4. THE Sistema SHALL fornecer um arquivo de exemplo (.env.example) com todas as variáveis necessárias
5. THE Sistema SHALL documentar todas as variáveis de ambiente requeridas

### Requirement 9

**User Story:** Como desenvolvedor, eu quero que o sistema tenha tratamento de erros robusto, para que falhas sejam registradas e não interrompam o funcionamento geral do sistema.

#### Acceptance Criteria

1. WHEN um erro ocorre durante processamento de XML, THE Sistema SHALL registrar o erro em log e continuar processando
2. WHEN um agente falha ao processar uma requisição, THE Sistema SHALL retornar mensagem de erro amigável ao usuário
3. WHEN a conexão com OpenAI falha, THE Sistema SHALL registrar o erro e retornar mensagem apropriada
4. WHEN a conexão com Supabase falha, THE Sistema SHALL registrar o erro e retornar mensagem apropriada
5. THE Sistema SHALL implementar logging estruturado para todas as operações críticas

### Requirement 10

**User Story:** Como desenvolvedor, eu quero que o sistema seja modular e extensível, para que novos agentes possam ser adicionados no futuro sem refatoração significativa.

#### Acceptance Criteria

1. THE Sistema SHALL implementar uma classe base abstrata para agentes
2. THE Sistema SHALL utilizar injeção de dependências para componentes principais
3. WHEN um novo agente é criado, THE Sistema SHALL permitir registro do agente através de interface comum
4. THE Sistema SHALL separar lógica de negócio de lógica de apresentação
5. THE Sistema SHALL organizar código em módulos distintos por responsabilidade
