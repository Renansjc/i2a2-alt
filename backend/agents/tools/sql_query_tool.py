"""
Direct SQL Query Tool for CrewAI

This tool allows AI agents to execute SQL queries directly on PostgreSQL database.
Much more powerful and flexible than REST API approach.
"""

from typing import Type, Optional, List, Dict, Any, ClassVar
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
import psycopg2
import psycopg2.extras
import json
from config import settings


class SQLQueryInput(BaseModel):
    """Input schema for SQLQueryTool"""
    query: str = Field(
        ...,
        description=(
            "SQL SELECT query to execute. "
            "IMPORTANT: Only SELECT queries are allowed. "
            "Use proper PostgreSQL syntax. "
            "Examples: "
            "'SELECT COUNT(*) FROM notas_fiscais WHERE status = 'autorizada'', "
            "'SELECT SUM(valor_total_nota) FROM notas_fiscais', "
            "'SELECT e.razao_social, COUNT(nf.id) FROM empresas e JOIN notas_fiscais nf ON e.id = nf.emitente_id GROUP BY e.razao_social'"
        )
    )


class SQLQueryTool(BaseTool):
    """
    Tool para executar consultas SQL diretamente no PostgreSQL.
    
    Esta tool permite que agentes de IA executem queries SQL completas
    no banco de dados PostgreSQL, com suporte total a:
    - Agregações (COUNT, SUM, AVG, MIN, MAX)
    - JOINs complexos
    - Subqueries
    - GROUP BY, HAVING
    - ORDER BY, LIMIT
    - Funções do PostgreSQL
    
    IMPORTANTE: Apenas queries SELECT são permitidas por segurança.
    Tentativas de INSERT, UPDATE, DELETE, DROP, etc. serão bloqueadas.
    
    Exemplos de uso:
    
    1. Contar notas fiscais:
       query="SELECT COUNT(*) as total FROM notas_fiscais"
    
    2. Contar notas autorizadas:
       query="SELECT COUNT(*) as total FROM notas_fiscais WHERE status = 'autorizada'"
    
    3. Somar valores:
       query="SELECT SUM(valor_total_nota) as total FROM notas_fiscais WHERE status = 'autorizada'"
    
    4. Consulta com JOIN:
       query="SELECT e.razao_social, COUNT(nf.id) as total_notas FROM empresas e LEFT JOIN notas_fiscais nf ON e.id = nf.emitente_id GROUP BY e.razao_social ORDER BY total_notas DESC LIMIT 10"
    
    5. Média de valores:
       query="SELECT AVG(valor_total_nota) as media FROM notas_fiscais WHERE status = 'autorizada'"
    """
    
    name: str = "SQL Query Tool"
    description: str = (
        "Executa consultas SQL SELECT diretamente no banco de dados PostgreSQL. "
        "Suporta todas as funcionalidades SQL: COUNT, SUM, AVG, JOINs, GROUP BY, subqueries, etc. "
        "Use esta tool para consultas complexas que requerem agregações ou múltiplas tabelas. "
        "IMPORTANTE: Apenas SELECT queries são permitidas - nenhuma modificação no banco."
    )
    args_schema: Type[BaseModel] = SQLQueryInput
    
    # Palavras-chave SQL perigosas que devem ser bloqueadas
    FORBIDDEN_KEYWORDS: ClassVar[List[str]] = [
        'INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 'ALTER',
        'TRUNCATE', 'GRANT', 'REVOKE', 'EXEC', 'EXECUTE'
    ]
    
    def _validate_query(self, query: str) -> tuple[bool, str]:
        """
        Valida se a query é segura (apenas SELECT).
        
        Args:
            query: SQL query to validate
            
        Returns:
            tuple: (is_valid, error_message)
        """
        query_upper = query.upper().strip()
        
        # Verificar se começa com SELECT
        if not query_upper.startswith('SELECT'):
            return False, "Apenas queries SELECT são permitidas"
        
        # Verificar palavras-chave perigosas
        for keyword in self.FORBIDDEN_KEYWORDS:
            if keyword in query_upper:
                return False, f"Palavra-chave '{keyword}' não é permitida por segurança"
        
        # Verificar ponto-e-vírgula múltiplo (possível SQL injection)
        if query.count(';') > 1:
            return False, "Múltiplas queries não são permitidas"
        
        return True, ""
    
    def _get_connection_string(self) -> str:
        """Get PostgreSQL connection string from Supabase URL"""
        # Parse Supabase URL to get project reference
        supabase_url = settings.supabase_url
        # Extract host from https://xxx.supabase.co
        host = supabase_url.replace('https://', '').replace('http://', '')
        project_ref = host.split('.')[0]
        
        # Get database password from settings
        # First try SUPABASE_DB_PASSWORD, fallback to service key
        import os
        from dotenv import load_dotenv
        load_dotenv()  # Reload to get latest values
        
        db_password = os.getenv('SUPABASE_DB_PASSWORD')
        if not db_password:
            db_password = settings.supabase_service_key
        
        # Construct PostgreSQL connection string
        return f"postgresql://postgres:{db_password}@db.{project_ref}.supabase.co:5432/postgres"
    
    def _run(self, query: str) -> str:
        """
        Executa uma query SQL no PostgreSQL.
        
        Args:
            query: SQL SELECT query to execute
            
        Returns:
            str: JSON string com os resultados ou mensagem de erro
        """
        try:
            # Validar query
            is_valid, error_msg = self._validate_query(query)
            if not is_valid:
                return json.dumps({
                    "success": False,
                    "error": "Query inválida",
                    "details": error_msg,
                    "query": query
                }, ensure_ascii=False, indent=2)
            
            # Conectar ao banco
            conn_string = self._get_connection_string()
            conn = psycopg2.connect(conn_string)
            
            # Executar query
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                cursor.execute(query)
                
                # Buscar resultados
                results = cursor.fetchall()
                
                # Converter para lista de dicionários
                results_list = [dict(row) for row in results]
                
                # Fechar conexão
                conn.close()
                
                # Formatar resposta
                return json.dumps({
                    "success": True,
                    "query": query,
                    "row_count": len(results_list),
                    "results": results_list
                }, ensure_ascii=False, indent=2, default=str)
        
        except psycopg2.Error as e:
            return json.dumps({
                "success": False,
                "error": "Erro ao executar query no PostgreSQL",
                "details": str(e),
                "query": query
            }, ensure_ascii=False, indent=2)
        
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": "Erro inesperado ao executar query",
                "details": str(e),
                "query": query
            }, ensure_ascii=False, indent=2)
