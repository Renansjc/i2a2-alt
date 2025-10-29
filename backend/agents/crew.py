"""
NFeCrew - Multi-Agent System for NF-e Processing

This module implements the CrewAI-based multi-agent system for processing
electronic invoices (NF-e) and answering user queries through natural language.

The system consists of three specialized agents:
1. coordenador: Analyzes user intent and delegates tasks
2. SQL Specialist: Generates and executes database queries
3. Conversation Specialist: Formats responses in natural language

Architecture:
- Uses CrewAI's sequential process with coordenador managing flow
- Integrates with PostgreSQL database via direct SQL queries
- Maintains conversation context through task inputs
- Supports both database queries and conversational interactions
"""

from crewai import Agent, Crew, Task, Process, LLM
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
    
    The crew uses a sequential process where the coordenador agent
    manages the flow and can delegate to specialized agents.
    
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
        self.db_tool = DatabaseQueryTool()  # REST API fallback (not used)
        self.db_join_tool = DatabaseJoinQueryTool()  # REST API with joins (not used)
        self.schema_tool = SchemaInfoTool()
        self.schema_search_tool = SchemaSearchTool()
    
    def _create_llm(self, agent_name: str) -> LLM:
        """
        Cria LLM com configurações do YAML.
        
        Centraliza a criação de LLM para todos os agentes,
        usando model e temperature definidos em agents.yaml.
        
        Args:
            agent_name: Nome do agente no YAML (sql_specialist, coordenador, etc.)
        
        Returns:
            LLM: Instância configurada do LLM
        """
        config = self.agents_config[agent_name]
        
        return LLM(
            model=config.get('model', 'gpt-4o-mini'),
            temperature=config.get('temperature', 0.1)
        )
    
    @agent
    def sql_specialist(self) -> Agent:
        """
        SQL Specialist Agent
        
        Responsible for:
        - Understanding user queries that require database access
        - Generating optimized SQL queries
        - Executing queries via SQLQueryTool (direct PostgreSQL)
        - Returning structured results
        
        Tools:
        - SQLQueryTool: Execute SELECT queries directly on PostgreSQL
        - SchemaInfoTool: Get database schema information
        - SchemaSearchTool: Search for relevant tables/columns
        
        Configuration:
        - Model and temperature loaded from agents.yaml
        - allow_delegation=False: Does not delegate
        - max_iter=2: Limited iterations to prevent loops
        """
        config = self.agents_config['sql_specialist']
        
        return Agent(
            role=config['role'],
            goal=config['goal'],
            backstory=config['backstory'],
            tools=[
                self.schema_search_tool,
                self.schema_tool,
                self.sql_tool  # Primary: Direct SQL queries
            ],
            verbose=config.get('verbose', True),
            allow_delegation=config.get('allow_delegation', False),
            max_iter=4,
            memory=False,
            llm=self._create_llm('sql_specialist')  # ✅ LLM from YAML
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
        
        Tools:
        - None: Only formats responses, does not execute queries
        
        Configuration:
        - Model and temperature loaded from agents.yaml
        - allow_delegation=False: Does not delegate
        - max_iter=2: Limited iterations to prevent loops
        """
        config = self.agents_config['conversation_specialist']
        
        return Agent(
            role=config['role'],
            goal=config['goal'],
            backstory=config['backstory'],
            tools=[],  # No tools - only formats responses
            verbose=config.get('verbose', True),
            allow_delegation=config.get('allow_delegation', False),
            max_iter=4,
            memory=False,
            llm=self._create_llm('conversation_specialist')  # ✅ LLM from YAML
        )

    @agent
    def fiscal_specialist(self) -> Agent:
        """
        Fiscal Specialist Agent
        
        Responsible for:
        - Analyzing tax-related questions
        - Calculating tax burdens and effective rates
        - Identifying fiscal inconsistencies
        - Providing guidance on tax compliance
        - Analyzing CST, CSOSN, CFOP codes
        - Tax credit analysis
        - Comparing tax periods
        
        Tools:
        - SchemaInfoTool: Understand database structure for tax queries
        - SchemaSearchTool: Search for tax-related tables/columns
        - Does NOT execute SQL directly (delegates to sql_specialist)
        
        Configuration:
        - Model and temperature loaded from agents.yaml
        - allow_delegation=False: Does not delegate (works with coordinator)
        - temperature=0.2: Precise for tax calculations
        """
        config = self.agents_config['fiscal_specialist']
        
        return Agent(
            role=config['role'],
            goal=config['goal'],
            backstory=config['backstory'],
            tools=[
                self.schema_tool,  # To understand tax-related schema
                self.schema_search_tool  # To search for tax columns
            ],
            verbose=config.get('verbose', True),
            allow_delegation=config.get('allow_delegation', False),
            max_iter=4,
            memory=False,
            llm=self._create_llm('fiscal_specialist')  # ✅ LLM from YAML
        )


    @agent
    def coordenador(self) -> Agent:
        """
        coordenador Agent
        
        Responsible for:
        - Analyzing user message intent
        - Deciding which agent should handle the request
        - Delegating tasks to specialized agents (if allow_delegation=True)
        - Coordinating the overall response flow
        
        Tools:
        - SchemaInfoTool: Understand database structure
        - SchemaSearchTool: Search for tables/columns
        - NO SQLQueryTool: Does not execute SQL (delegates to specialist)
        
        Configuration:
        - Model and temperature loaded from agents.yaml
        - allow_delegation: Configurable (False for all-in-one, True for hybrid)
        - max_iter=2: Limited iterations to prevent loops
        
        Architecture Options:
        1. All-in-One (allow_delegation=False): coordenador does everything
           - Fastest: ~3-5s
           - Less modular
        
        2. Hybrid (allow_delegation=True): coordenador delegates SQL to specialist
           - Moderate: ~10-15s
           - More modular
           - coordenador uses schema tools, SQL specialist executes queries
        """
        config = self.agents_config['coordenador']
        
        return Agent(
            role=config['role'],
            goal=config['goal'],
            backstory=config['backstory'],
            verbose=config.get('verbose', True),
            allow_delegation=False,
            max_iter=4,
            memory=False,
            llm=self._create_llm('coordenador')  # ✅ LLM from YAML
        )
    
    @task
    def process_user_message_task(self) -> Task:
        """
        Task: Process user message - HIERARCHICAL VERSION
        
        Manager (coordenador) analyzes and delegates to workers.
        Workers execute and return results.
        Manager coordinates final response.
        """
        return Task(
            description="""
            Responda à mensagem do usuário: "{message}"
            
            Contexto: {chat_history}
            Schema disponível: {database_schema}
            
            ════════════════════════════════════════════════════════════
            ⚠️ VOCÊ É O MANAGER - DELEGUE, NÃO EXECUTE!
            ════════════════════════════════════════════════════════════
            
            Para perguntas sobre DADOS:
            → DELEGUE para "sql_specialist"
            → Use "Delegate work to coworker"
            → Forneça contexto COMPLETO: tabelas, colunas, filtros, agregações
            
            Para FORMATAÇÃO:
            → DELEGUE para "comunication_specialist"
            → Use "Delegate work to coworker"
            → Forneça dados brutos a formatar
            
            Para CONVERSAÇÃO:
            → DELEGUE para "comunication_specialist"
            → Use "Delegate work to coworker"
            
            ⚠️ NUNCA:
            - Execute SQL você mesmo
            - Use "Ask question to coworker"
            - Delegue para "Coordenador"
            
            ✅ SEMPRE:
            - Use "Delegate work to coworker"
            - Forneça contexto completo
            - Use nomes EXATOS dos workers acima
            
            FORMATO CORRETO:
            Action: Delegate work to coworker
            Action Input: {
            "task": "[tarefa específica]",
            "context": "[TODO contexto necessário]",
            "coworker": "[nome EXATO do worker]"
            }
            """,
            expected_output="""
            Resposta completa em português brasileiro que:
            - Responde à pergunta
            - Foi construída delegando aos workers
            - Usa linguagem natural
            - Formata valores corretamente (R$)
            """,
            agent=self.coordenador()
        )
    
    @task
    def execute_sql_query_task(self) -> Task:
        """
        Task: Execute SQL query
        
        This task is executed by the sql_specialist when the coordenador
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

    @task
    def fiscal_analysis_task(self) -> Task:
        """
        Task: Fiscal Analysis
        
        This task is executed by the fiscal_specialist to analyze
        tax-related questions, calculate tax burdens, identify
        fiscal inconsistencies, and provide tax guidance.
        
        Inputs:
        - message: User's fiscal question
        - chat_history: Previous conversation context
        - query_results: Tax data from database (if consulted)
        
        Output:
        - Comprehensive fiscal analysis
        - Tax calculations with proper formatting
        - Legal context when applicable
        - Recommendations and alerts
        """
        return Task(
            description=self.tasks_config['fiscal_analysis']['description'],
            expected_output=self.tasks_config['fiscal_analysis']['expected_output'],
            agent=self.fiscal_specialist()
        )        
    
    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=[
                self.coordenador(),
                self.sql_specialist(),
                self.fiscal_specialist(),
                self.conversation_specialist()
            ],
            tasks=[
                # ✅ PASSAR TODAS AS TASKS
                self.process_user_message_task(),
                self.execute_sql_query_task(),
                self.fiscal_analysis_task(),      # Para SQL Specialist
                self.format_response_task(),         # Para Conversation
                self.direct_conversation_task()     # Para Conversation
            ],
            process=Process.sequential,  # Sequential execution
            #manager_agent=self.coordenador(),
            verbose=True,  # Enable detailed logging
            memory=False,  # Disabled for performance (was causing 10s+ delays)
        )
    
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
            # default para evitar erro de template quando tasks esperam essa variável
            "detected_entities": {
                "time_period": "",
                "companies": [],
                "products": [],
                "metrics": []
            }
        }
        
        # Kickoff the crew
        # The sequential process will:
        # 1. Have coordenador analyze intent
        # 2. Execute query or respond directly
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