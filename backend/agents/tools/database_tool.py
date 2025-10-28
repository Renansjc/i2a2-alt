"""
Database Query Tool for CrewAI

This tool allows AI agents to query the Supabase database using the REST API.
It supports PostgREST filters and only allows SELECT operations for safety.
"""

from typing import Type, Optional, Dict, Any, List
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
import requests
import json
from config import settings


class DatabaseQueryInput(BaseModel):
    """Input schema for DatabaseQueryTool"""
    table: str = Field(
        ...,
        description="Nome da tabela para consultar (ex: notas_fiscais, empresas, nf_itens)"
    )
    select: str = Field(
        default="*",
        description="Colunas para selecionar, separadas por vírgula (ex: 'id,numero_nf,valor_total_nota' ou '*' para todas)"
    )
    filters: Optional[Dict[str, str]] = Field(
        default=None,
        description=(
            "Filtros PostgREST no formato {coluna: 'operador.valor'}. "
            "Operadores: eq (igual), gt (maior), lt (menor), gte (maior ou igual), "
            "lte (menor ou igual), like (contém), ilike (contém case-insensitive), "
            "in (lista de valores). "
            "Exemplo: {'status': 'eq.autorizada', 'valor_total_nota': 'gt.1000'}"
        )
    )
    order: Optional[str] = Field(
        default=None,
        description="Ordenação no formato 'coluna.asc' ou 'coluna.desc' (ex: 'data_hora_emissao.desc')"
    )
    limit: int = Field(
        default=100,
        description="Número máximo de registros a retornar (padrão: 100, máximo: 1000)"
    )
    offset: int = Field(
        default=0,
        description="Número de registros para pular (para paginação)"
    )


class DatabaseQueryTool(BaseTool):
    """
    Tool para executar consultas no banco de dados Supabase via REST API.
    
    Esta tool permite que agentes de IA consultem dados de notas fiscais
    usando a API REST do Supabase com filtros PostgREST.
    
    IMPORTANTE: Apenas operações SELECT são permitidas. Nenhuma modificação
    no banco de dados é possível através desta tool.
    
    Exemplos de uso:
    
    1. Buscar todas as notas fiscais autorizadas:
       table="notas_fiscais"
       filters={"status": "eq.autorizada"}
       limit=10
    
    2. Buscar notas com valor acima de R$ 1000:
       table="notas_fiscais"
       select="numero_nf,serie,valor_total_nota,data_hora_emissao"
       filters={"valor_total_nota": "gt.1000", "status": "eq.autorizada"}
       order="valor_total_nota.desc"
    
    3. Buscar empresa por CNPJ:
       table="empresas"
       filters={"cpf_cnpj": "eq.12345678901234"}
    
    4. Buscar itens de uma nota específica:
       table="nf_itens"
       filters={"nota_fiscal_id": "eq.123"}
       order="numero_item.asc"
    """
    
    name: str = "Database Query Tool"
    description: str = (
        "Executa consultas SELECT no banco de dados PostgreSQL de notas fiscais eletrônicas "
        "usando a API REST do Supabase. Suporta filtros PostgREST (eq, gt, lt, gte, lte, like, ilike, in), "
        "ordenação e paginação. Use esta tool para buscar dados de NF-e, empresas, itens, pagamentos, etc. "
        "IMPORTANTE: Apenas consultas SELECT são permitidas - nenhuma modificação no banco."
    )
    args_schema: Type[BaseModel] = DatabaseQueryInput
    
    def _get_base_url(self) -> str:
        """Get Supabase base URL"""
        return f"{settings.supabase_url}/rest/v1"
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers"""
        return {
            "apikey": settings.supabase_service_key,
            "Authorization": f"Bearer {settings.supabase_service_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
    
    def _run(
        self,
        table: str,
        select: str = "*",
        filters: Optional[Dict[str, str]] = None,
        order: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> str:
        """
        Executa uma consulta no banco de dados via Supabase REST API.
        
        Args:
            table: Nome da tabela para consultar
            select: Colunas para selecionar (padrão: "*")
            filters: Dicionário de filtros PostgREST
            order: Ordenação (ex: "data_hora_emissao.desc")
            limit: Número máximo de registros (padrão: 100, máximo: 1000)
            offset: Número de registros para pular (padrão: 0)
        
        Returns:
            str: JSON string com os resultados da consulta ou mensagem de erro
        """
        try:
            # Validar limite
            if limit > 1000:
                limit = 1000
            
            # Construir URL
            base_url = self._get_base_url()
            url = f"{base_url}/{table}"
            
            # Construir parâmetros da query
            params = {
                "select": select,
                "limit": str(limit),
                "offset": str(offset)
            }
            
            # Adicionar filtros PostgREST
            if filters:
                for column, filter_expr in filters.items():
                    params[column] = filter_expr
            
            # Adicionar ordenação
            if order:
                params["order"] = order
            
            # Executar requisição
            headers = self._get_headers()
            response = requests.get(url, headers=headers, params=params, timeout=30)
            
            # Verificar status
            if response.status_code == 200:
                results = response.json()
                
                # Formatar resposta
                return json.dumps({
                    "success": True,
                    "table": table,
                    "count": len(results),
                    "results": results,
                    "query_params": {
                        "select": select,
                        "filters": filters,
                        "order": order,
                        "limit": limit,
                        "offset": offset
                    }
                }, ensure_ascii=False, indent=2)
            
            else:
                # Erro na requisição
                error_detail = response.text
                try:
                    error_json = response.json()
                    error_detail = error_json.get("message", error_detail)
                except:
                    pass
                
                return json.dumps({
                    "success": False,
                    "error": f"Erro na consulta ao banco de dados (HTTP {response.status_code})",
                    "details": error_detail,
                    "table": table,
                    "query_params": {
                        "select": select,
                        "filters": filters,
                        "order": order,
                        "limit": limit,
                        "offset": offset
                    }
                }, ensure_ascii=False, indent=2)
        
        except requests.exceptions.Timeout:
            return json.dumps({
                "success": False,
                "error": "Timeout na consulta ao banco de dados",
                "details": "A consulta demorou mais de 30 segundos",
                "table": table
            }, ensure_ascii=False, indent=2)
        
        except requests.exceptions.RequestException as e:
            return json.dumps({
                "success": False,
                "error": "Erro de conexão com o banco de dados",
                "details": str(e),
                "table": table
            }, ensure_ascii=False, indent=2)
        
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": "Erro inesperado ao executar consulta",
                "details": str(e),
                "table": table
            }, ensure_ascii=False, indent=2)


class DatabaseJoinQueryInput(BaseModel):
    """Input schema for advanced queries with JOINs"""
    base_table: str = Field(
        ...,
        description="Tabela principal da consulta"
    )
    select: str = Field(
        ...,
        description=(
            "Colunas para selecionar com relacionamentos. "
            "Use notação de relacionamento do PostgREST: "
            "'*,empresas!emitente_id(razao_social,cpf_cnpj)' para incluir dados relacionados"
        )
    )
    filters: Optional[Dict[str, str]] = Field(
        default=None,
        description="Filtros PostgREST"
    )
    order: Optional[str] = Field(
        default=None,
        description="Ordenação"
    )
    limit: int = Field(
        default=100,
        description="Número máximo de registros"
    )


class DatabaseJoinQueryTool(BaseTool):
    """
    Tool avançada para consultas com JOINs usando a sintaxe de relacionamento do PostgREST.
    
    Esta tool permite consultas mais complexas que incluem dados de tabelas relacionadas.
    
    Exemplos:
    
    1. Buscar notas com dados do emitente e destinatário:
       base_table="notas_fiscais"
       select="*,empresas!emitente_id(razao_social,cpf_cnpj),empresas!destinatario_id(razao_social,cpf_cnpj)"
       filters={"status": "eq.autorizada"}
    
    2. Buscar itens com dados da nota fiscal:
       base_table="nf_itens"
       select="*,notas_fiscais(numero_nf,serie,data_hora_emissao)"
       filters={"valor_total_bruto": "gt.1000"}
    """
    
    name: str = "Database Join Query Tool"
    description: str = (
        "Executa consultas avançadas com JOINs no banco de dados usando a sintaxe "
        "de relacionamento do PostgREST. Permite incluir dados de tabelas relacionadas "
        "em uma única consulta."
    )
    args_schema: Type[BaseModel] = DatabaseJoinQueryInput
    
    def _get_base_url(self) -> str:
        """Get Supabase base URL"""
        return f"{settings.supabase_url}/rest/v1"
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers"""
        return {
            "apikey": settings.supabase_service_key,
            "Authorization": f"Bearer {settings.supabase_service_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
    
    def _run(
        self,
        base_table: str,
        select: str,
        filters: Optional[Dict[str, str]] = None,
        order: Optional[str] = None,
        limit: int = 100
    ) -> str:
        """
        Executa uma consulta com JOINs usando a sintaxe do PostgREST.
        
        Args:
            base_table: Tabela principal
            select: Colunas e relacionamentos para selecionar
            filters: Filtros PostgREST
            order: Ordenação
            limit: Número máximo de registros
        
        Returns:
            str: JSON string com os resultados
        """
        try:
            # Validar limite
            if limit > 1000:
                limit = 1000
            
            # Construir URL
            base_url = self._get_base_url()
            url = f"{base_url}/{base_table}"
            
            # Construir parâmetros
            params = {
                "select": select,
                "limit": str(limit)
            }
            
            # Adicionar filtros
            if filters:
                for column, filter_expr in filters.items():
                    params[column] = filter_expr
            
            # Adicionar ordenação
            if order:
                params["order"] = order
            
            # Executar requisição
            headers = self._get_headers()
            response = requests.get(url, headers=headers, params=params, timeout=30)
            
            if response.status_code == 200:
                results = response.json()
                
                return json.dumps({
                    "success": True,
                    "base_table": base_table,
                    "count": len(results),
                    "results": results,
                    "query_params": {
                        "select": select,
                        "filters": filters,
                        "order": order,
                        "limit": limit
                    }
                }, ensure_ascii=False, indent=2)
            
            else:
                error_detail = response.text
                try:
                    error_json = response.json()
                    error_detail = error_json.get("message", error_detail)
                except:
                    pass
                
                return json.dumps({
                    "success": False,
                    "error": f"Erro na consulta (HTTP {response.status_code})",
                    "details": error_detail,
                    "base_table": base_table
                }, ensure_ascii=False, indent=2)
        
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": "Erro ao executar consulta com JOIN",
                "details": str(e),
                "base_table": base_table
            }, ensure_ascii=False, indent=2)
