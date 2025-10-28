"""
NFeCrew - Multi-Agent System for NF-e Processing

This module implements the CrewAI-based multi-agent system for processing
electronic invoices (NF-e) and answering user queries through natural language.

The system consists of three specialized agents:
1. Coordinator: Analyzes user intent and delegates tasks
2. SQL Specialist: Generates and executes database queries
3. Conversation Specialist: Formats responses in natural language

Architecture:
- Uses CrewAI's hierarchical process with coordinator as manager
- Integrates with Supabase database via REST API tools
- Maintains conversation context through CrewAI's built-in memory
- Supports both database queries and conversational interactions
"""

from crewai import Agent, Crew, Task, Process
from crewai.project import CrewBase, agent, crew, task
from typing import Dict, Any, List, Optional
import yaml
from pathlib import Path

from agents.tools.database_tool import DatabaseQueryTool, DatabaseJoinQueryTool
from agents.tools.schema_tool import SchemaInfoTool, SchemaSearchTool
from agents.tools.sql_query_tool import SQLQueryTool
from config import settings


@CrewBase
class NFeCrew:
    """
    Crew for processing NF-e queries and conversations.
    
    This class implements a multi-agent system using CrewAI that can:
    - Analyze user messages and determine intent
    - Execute SQL queries on the NF-e database
    - Format responses in natural, friendly language
    - Maintain conversation context across interactions
    
    The crew uses a hierarchical process where the coordinator agent
    acts as a manager, delegating tasks to specialized agents.
    
    Usage:
        crew = NFeCrew()
        response = crew.process_message(
            message="Quantas notas fiscais foram emitidas hoje?",
            chat_history=[...]
        )
    """
    
    agents_config_path = "agents/config/agents.yaml"
    tasks_config_path = "agents/config/tasks.yaml"
    
    def __init__(self):
        """Initialize the NFeCrew with configuration and tools"""
        # Load agent configurations
        config_path = Path(__file__).parent / "config"
        
        with open(config_path / "agents.yaml", encoding="utf-8") as f:
            self.agents_config = yaml.safe_load(f)
        
        with open(config_path / "tasks.yaml", encoding="utf-8") as f:
            self.tasks_config = yaml.safe_load(f)
        
        # Initialize tools
        self.sql_tool = SQLQueryTool()  # Direct SQL - most powerful
        self.db_tool = DatabaseQueryTool()  # REST API fallback
        self.db_join_tool = DatabaseJoinQueryTool()  # REST API with joins
        self.schema_tool = SchemaInfoTool()
        self.schema_search_tool = SchemaSearchTool()
    
    @agent
    def sql_specialist(self) -> Agent:
        """
        SQL Specialist Agent
        
        Responsible for:
        - Understanding user queries that require database access
        - Generating optimized SQL queries
        - Executing queries via DatabaseQueryTool
        - Returning structured results
        
        Tools:
        - DatabaseQueryTool: Execute SELECT queries via Supabase REST API
        - DatabaseJoinQueryTool: Execute complex queries with JOINs
        - SchemaInfoTool: Get database schema information
        - SchemaSearchTool: Search for relevant tables/columns
        """
        return Agent(
            role=self.agents_config['sql_specialist']['role'],
            goal=self.agents_config['sql_specialist']['goal'],
            backstory=self.agents_config['sql_specialist']['backstory'],
            tools=[
                self.sql_tool,  # Primary: Direct SQL queries
                self.schema_tool,
                self.schema_search_tool
            ],
            verbose=True,
            allow_delegation=False,  # SQL specialist doesn't delegate
            max_iter=7,  # REDUZIDO: Evita loops (era 15)
            memory=False  # DESABILITADO: Memory muito lenta
        )
    
    @agent
    def conversation_specialist(self) -> Agent:
        """
        Conversation Specialist Agent
        
        Responsible for:
        - Formatting database results into natural language
        - Handling conversational interactions (greetings, explanations)
        - Maintaining friendly and professional tone
        - Formatting monetary values and numbers appropriately
        
        This agent does not have database tools - it only formats
        information provided by other agents or responds to general queries.
        """
        return Agent(
            role=self.agents_config['conversation_specialist']['role'],
            goal=self.agents_config['conversation_specialist']['goal'],
            backstory=self.agents_config['conversation_specialist']['backstory'],
            tools=[],  # No tools - only formats responses
            verbose=True,
            allow_delegation=False,  # Conversation specialist doesn't delegate
            max_iter=3,  # REDUZIDO: Evita loops (era 10)
            memory=False  # DESABILITADO: Memory muito lenta
        )
    
    @agent
    def coordinator(self) -> Agent:
        """
        Coordinator Agent
        
        Responsible for:
        - Analyzing user message intent
        - Deciding which agent should handle the request
        - Delegating tasks to specialized agents
        - Coordinating the overall response flow
        
        Has access to all tools to handle requests directly or delegate.
        """
        return Agent(
            role=self.agents_config['coordinator']['role'],
            goal=self.agents_config['coordinator']['goal'],
            backstory=self.agents_config['coordinator']['backstory'],
            tools=[
                self.sql_tool,  # Primary: Direct SQL queries
                self.schema_tool,
                self.schema_search_tool
            ],  # Coordinator has all tools available
            verbose=True,
            allow_delegation=True,  # Can delegate to other agents
            max_iter=5,  # REDUZIDO: Evita loops infinitos (era 25)
            memory=False  # DESABILITADO: Memory muito lenta
        )
    
    @task
    def process_user_message_task(self) -> Task:
        """
        Task: Process user message
        
        This is the main task that processes the user's message.
        The coordinator handles the request directly or delegates as needed.
        
        Inputs:
        - message: User's message
        - chat_history: Previous conversation context
        - database_schema: Database schema information
        
        Output:
        - Complete response to the user's message
        """
        return Task(
            description="""
            Responda à mensagem do usuário: "{message}"
            
            Contexto: {chat_history}
            Schema disponível: {database_schema}
            
            INSTRUÇÕES CRÍTICAS:
            
            1. Para perguntas sobre DADOS (valores, quantidades, empresas, produtos):
               ⚠️ SEMPRE execute uma query SQL - NUNCA use informações da memória!
               ⚠️ Dados podem ter mudado - sempre consulte o banco atual!
               
               - Use SQL Query Tool para consultar o banco diretamente
               - Escreva uma query SQL SELECT completa em PostgreSQL
               - Exemplos:
                 * Contar: SELECT COUNT(*) as total FROM notas_fiscais
                 * Contar com filtro: SELECT COUNT(*) as total FROM notas_fiscais WHERE status = 'autorizada'
                 * Somar: SELECT SUM(valor_total_nota) as total FROM notas_fiscais
                 * JOIN: SELECT e.razao_social, COUNT(nf.id) FROM empresas e JOIN notas_fiscais nf ON e.id = nf.emitente_id GROUP BY e.razao_social
               - Execute a query e formate a resposta em linguagem natural
            
            2. Para perguntas CONVERSACIONAIS (saudação, explicação, ajuda):
               - Responda diretamente de forma amigável
               - Explique como o sistema funciona se perguntado
               - Ofereça ajuda adicional
            
            3. REGRA DE OURO:
               - Se a pergunta menciona números, valores, quantidades → EXECUTE SQL
               - NUNCA responda com dados da memória
               - Sempre responda em português brasileiro
               - Use formatação R$ para valores monetários
               - Seja claro, preciso e amigável
            """,
            expected_output="""
            Uma resposta completa em português que:
            - Responde diretamente à pergunta
            - Usa linguagem natural e amigável
            - Formata valores corretamente (R$)
            - É precisa e útil
            """,
            agent=self.coordinator()
        )
    
    @task
    def execute_sql_query_task(self) -> Task:
        """
        Task: Execute SQL query
        
        This task is executed by the sql_specialist when the coordinator
        determines that a database query is needed.
        
        Inputs:
        - message: User's message
        - database_schema: Schema information
        - chat_history: Previous conversation context
        
        Output:
        - Query executed
        - Results in structured format
        - Record count
        """
        return Task(
            description=self.tasks_config['execute_sql_query']['description'],
            expected_output=self.tasks_config['execute_sql_query']['expected_output'],
            agent=self.sql_specialist()
        )
    
    @task
    def format_response_task(self) -> Task:
        """
        Task: Format response
        
        This task is executed by the conversation_specialist to format
        database query results into natural, friendly language.
        
        Inputs:
        - query_results: Results from SQL query
        - message: Original user message
        - chat_history: Previous conversation context
        
        Output:
        - Natural language response
        - Properly formatted values (R$ for currency)
        - Clear and accessible explanation
        """
        return Task(
            description=self.tasks_config['format_response']['description'],
            expected_output=self.tasks_config['format_response']['expected_output'],
            agent=self.conversation_specialist()
        )
    
    @task
    def direct_conversation_task(self) -> Task:
        """
        Task: Direct conversation
        
        This task is executed by the conversation_specialist for
        conversational interactions that don't require database access
        (greetings, explanations, general questions).
        
        Inputs:
        - message: User's message
        - chat_history: Previous conversation context
        
        Output:
        - Friendly conversational response
        - Helpful information about the system if requested
        """
        return Task(
            description=self.tasks_config['direct_conversation']['description'],
            expected_output=self.tasks_config['direct_conversation']['expected_output'],
            agent=self.conversation_specialist()
        )
    
    @crew
    def crew(self) -> Crew:
        """
        Create the NFeCrew with sequential process.
        
        The crew uses a sequential process where tasks are executed in order.
        The coordinator can delegate to specialized agents as needed.
        
        Process Flow:
        1. User message arrives
        2. Main task processes the message
        3. Agent determines if database query or conversation is needed
        4. Appropriate specialist handles the request
        5. Final response is returned
        
        Features:
        - Sequential process with delegation capabilities
        - Built-in memory for conversation context
        - Verbose logging for debugging
        - Agents can delegate to each other
        """
        # Prepare crew configuration
        crew_config = {
            "agents": [
                self.coordinator(),
                self.sql_specialist(),
                self.conversation_specialist()
            ],
            "tasks": [
                # Single main task that handles the entire flow
                self.process_user_message_task()
            ],
            "process": Process.sequential,  # Sequential execution
            "verbose": True,  # Enable detailed logging
            "memory": False,  # DESABILITADO: Entity Memory muito lenta (10s+ por save)
        }
        
        # DESABILITADO: Embedder não necessário com memory=False
        # Add embedder configuration for semantic memory
        # if settings.enable_semantic_search and settings.openai_api_key:
        #     import os
        #     os.environ["CHROMA_OPENAI_API_KEY"] = settings.openai_api_key
        #     
        #     crew_config["embedder"] = {
        #         "provider": "openai",
        #         "config": {
        #             "model": "text-embedding-3-small"
        #         }
        #     }
        
        return Crew(**crew_config)
    
    def process_message(
        self,
        message: str,
        chat_history: Optional[List[Dict[str, str]]] = None,
        session_id: Optional[str] = None
    ) -> str:
        """
        Process a user message through the multi-agent system.
        
        This is the main entry point for processing user messages.
        It prepares the inputs, kicks off the crew, and returns the response.
        
        Args:
            message: User's message to process
            chat_history: Previous conversation history (list of dicts with 'role' and 'content')
            session_id: Optional session ID for memory persistence
        
        Returns:
            str: The agent's response to the user's message
        
        Example:
            crew = NFeCrew()
            response = crew.process_message(
                message="Quantas notas fiscais foram emitidas hoje?",
                chat_history=[
                    {"role": "user", "content": "Olá"},
                    {"role": "assistant", "content": "Olá! Como posso ajudar?"}
                ],
                session_id="user-123"
            )
        """
        # Prepare chat history string
        if chat_history:
            history_str = "\n".join([
                f"{msg['role']}: {msg['content']}"
                for msg in chat_history[-settings.max_chat_history:]
            ])
        else:
            history_str = "Nenhum histórico disponível"
        
        # Get database schema information
        database_schema = self._get_schema_summary()
        
        # Prepare inputs for the crew
        inputs = {
            "message": message,
            "chat_history": history_str,
            "database_schema": database_schema,
            "query_results": "",  # Will be filled by sql_specialist if needed
        }
        
        # Kickoff the crew
        # The hierarchical process will automatically:
        # 1. Have coordinator analyze intent
        # 2. Delegate to appropriate agent
        # 3. Return formatted response
        result = self.crew().kickoff(inputs=inputs)
        
        # Extract the final output
        # CrewAI returns a CrewOutput object, we need the raw output
        if hasattr(result, 'raw'):
            return result.raw
        else:
            return str(result)
    
    def _get_schema_summary(self) -> str:
        """
        Get a summary of the database schema for agents.
        
        This provides agents with essential information about the database
        structure without overwhelming them with details.
        
        Returns:
            str: Formatted schema summary
        """
        return """
Schema NF-e (PostgreSQL):

Tabelas: empresas, notas_fiscais, nf_itens, nf_pagamentos, nf_transporte

Colunas principais:
- empresas: id, cpf_cnpj, razao_social, nome_fantasia
- notas_fiscais: id, chave_acesso, numero_nf, emitente_id, destinatario_id, 
  valor_total_nota, data_hora_emissao, status
- nf_itens: id, nota_fiscal_id, descricao_produto, quantidade_comercial, valor_total_bruto

Relacionamentos:
- notas_fiscais.emitente_id → empresas.id
- notas_fiscais.destinatario_id → empresas.id
- nf_itens.nota_fiscal_id → notas_fiscais.id

Regras SQL:
1. LIMIT obrigatório (máx 100)
2. Filtre status='autorizada'
3. LEFT JOIN para empresas, INNER JOIN para itens
"""


# Convenience function for easy import
def create_nfe_crew() -> NFeCrew:
    """
    Factory function to create an NFeCrew instance.
    
    Returns:
        NFeCrew: Initialized crew ready to process messages
    """
    return NFeCrew()

