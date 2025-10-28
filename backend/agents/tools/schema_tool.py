"""
Schema Information Tool for CrewAI

This tool provides AI agents with information about the database schema,
including table structures, relationships, and common query patterns.
"""

from typing import Type, Optional, List
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
import json
from database.schema import (
    get_schema_info,
    get_table_info,
    get_main_tables,
    get_relationships,
    get_common_queries
)


class SchemaInfoInput(BaseModel):
    """Input schema for SchemaInfoTool"""
    query_type: str = Field(
        default="full",
        description=(
            "Tipo de informação do schema a retornar: "
            "'full' (schema completo), "
            "'table' (informações de uma tabela específica), "
            "'tables' (lista de tabelas principais), "
            "'relationships' (relacionamentos entre tabelas), "
            "'queries' (exemplos de queries comuns)"
        )
    )
    table_name: Optional[str] = Field(
        default=None,
        description="Nome da tabela (obrigatório quando query_type='table')"
    )


class SchemaInfoTool(BaseTool):
    """
    Tool para obter informações sobre o schema do banco de dados de NF-e.
    
    Esta tool fornece aos agentes de IA informações detalhadas sobre:
    - Estrutura das tabelas (colunas, tipos, constraints)
    - Relacionamentos entre tabelas (foreign keys)
    - Índices e otimizações
    - Exemplos de queries comuns
    
    Use esta tool ANTES de executar consultas para entender a estrutura
    do banco de dados e construir queries corretas.
    
    Exemplos de uso:
    
    1. Obter schema completo:
       query_type="full"
    
    2. Obter informações de uma tabela específica:
       query_type="table"
       table_name="notas_fiscais"
    
    3. Listar todas as tabelas principais:
       query_type="tables"
    
    4. Ver relacionamentos entre tabelas:
       query_type="relationships"
    
    5. Ver exemplos de queries comuns:
       query_type="queries"
    """
    
    name: str = "Schema Info Tool"
    description: str = (
        "Retorna informações sobre o schema do banco de dados de notas fiscais eletrônicas. "
        "Use esta tool para entender a estrutura das tabelas, relacionamentos, e ver exemplos "
        "de queries antes de executar consultas. Suporta consultas sobre schema completo, "
        "tabelas específicas, relacionamentos e queries comuns."
    )
    args_schema: Type[BaseModel] = SchemaInfoInput
    
    def _run(
        self,
        query_type: str = "full",
        table_name: Optional[str] = None
    ) -> str:
        """
        Retorna informações do schema conforme o tipo de consulta.
        
        Args:
            query_type: Tipo de informação a retornar
            table_name: Nome da tabela (para query_type='table')
        
        Returns:
            str: Informações do schema formatadas
        """
        try:
            if query_type == "full":
                # Retorna schema completo
                schema_info = get_schema_info()
                return json.dumps({
                    "success": True,
                    "query_type": "full",
                    "schema": schema_info
                }, ensure_ascii=False, indent=2)
            
            elif query_type == "table":
                # Retorna informações de uma tabela específica
                if not table_name:
                    return json.dumps({
                        "success": False,
                        "error": "table_name é obrigatório quando query_type='table'",
                        "available_tables": get_main_tables()
                    }, ensure_ascii=False, indent=2)
                
                table_info = get_table_info(table_name)
                return json.dumps({
                    "success": True,
                    "query_type": "table",
                    "table_name": table_name,
                    "info": table_info
                }, ensure_ascii=False, indent=2)
            
            elif query_type == "tables":
                # Retorna lista de tabelas principais
                tables = get_main_tables()
                return json.dumps({
                    "success": True,
                    "query_type": "tables",
                    "tables": tables,
                    "count": len(tables)
                }, ensure_ascii=False, indent=2)
            
            elif query_type == "relationships":
                # Retorna relacionamentos entre tabelas
                relationships = get_relationships()
                return json.dumps({
                    "success": True,
                    "query_type": "relationships",
                    "relationships": relationships
                }, ensure_ascii=False, indent=2)
            
            elif query_type == "queries":
                # Retorna exemplos de queries comuns
                queries = get_common_queries()
                return json.dumps({
                    "success": True,
                    "query_type": "queries",
                    "common_queries": queries,
                    "note": "Use {placeholders} para substituir valores dinâmicos"
                }, ensure_ascii=False, indent=2)
            
            else:
                # Tipo de query inválido
                return json.dumps({
                    "success": False,
                    "error": f"query_type inválido: '{query_type}'",
                    "valid_types": ["full", "table", "tables", "relationships", "queries"]
                }, ensure_ascii=False, indent=2)
        
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": "Erro ao obter informações do schema",
                "details": str(e),
                "query_type": query_type
            }, ensure_ascii=False, indent=2)


class SchemaSearchInput(BaseModel):
    """Input schema for SchemaSearchTool"""
    search_term: str = Field(
        ...,
        description="Termo de busca para encontrar tabelas ou colunas relevantes"
    )


class SchemaSearchTool(BaseTool):
    """
    Tool para buscar tabelas e colunas no schema por termo de busca.
    
    Esta tool ajuda a encontrar rapidamente onde determinadas informações
    estão armazenadas no banco de dados.
    
    Exemplos:
    
    1. Buscar onde estão armazenados dados de ICMS:
       search_term="icms"
    
    2. Buscar informações sobre pagamento:
       search_term="pagamento"
    
    3. Buscar dados de transporte:
       search_term="transporte"
    """
    
    name: str = "Schema Search Tool"
    description: str = (
        "Busca tabelas e colunas no schema do banco de dados por termo de busca. "
        "Use esta tool para encontrar rapidamente onde determinadas informações "
        "estão armazenadas (ex: buscar 'icms' para encontrar tabelas de impostos)."
    )
    args_schema: Type[BaseModel] = SchemaSearchInput
    
    def _run(self, search_term: str) -> str:
        """
        Busca tabelas e colunas que correspondem ao termo de busca.
        
        Args:
            search_term: Termo para buscar
        
        Returns:
            str: JSON com resultados da busca
        """
        try:
            search_lower = search_term.lower()
            
            # Mapeamento de tabelas e suas descrições/colunas principais
            table_keywords = {
                "empresas": ["empresa", "emitente", "destinatario", "cnpj", "cpf", "razao social", "endereco"],
                "notas_fiscais": ["nota", "nfe", "nf-e", "fiscal", "chave", "numero", "valor", "total", "emissao"],
                "nf_itens": ["item", "produto", "mercadoria", "quantidade", "preco", "unitario", "ncm", "cfop"],
                "nf_itens_icms": ["icms", "imposto", "tributacao", "aliquota", "base calculo"],
                "nf_itens_ipi": ["ipi", "imposto", "produto industrializado"],
                "nf_itens_pis": ["pis", "contribuicao", "social"],
                "nf_itens_cofins": ["cofins", "contribuicao", "financiamento"],
                "nf_pagamentos": ["pagamento", "forma", "dinheiro", "cartao", "pix", "boleto"],
                "nf_transporte": ["transporte", "frete", "transportadora", "veiculo", "placa"],
                "nf_transporte_volumes": ["volume", "peso", "quantidade", "embalagem"],
                "nf_cobranca": ["cobranca", "fatura", "duplicata"],
                "nf_duplicatas": ["duplicata", "vencimento", "parcela"],
                "nf_referencias": ["referencia", "nota referenciada", "devolucao"],
                "nf_cce": ["carta", "correcao", "cce", "evento"]
            }
            
            # Buscar tabelas relevantes
            matching_tables = []
            for table, keywords in table_keywords.items():
                if search_lower in table.lower():
                    matching_tables.append({
                        "table": table,
                        "match_type": "table_name",
                        "relevance": "high"
                    })
                elif any(search_lower in keyword for keyword in keywords):
                    matching_tables.append({
                        "table": table,
                        "match_type": "keyword",
                        "relevance": "medium"
                    })
            
            if matching_tables:
                # Obter informações detalhadas das tabelas encontradas
                detailed_info = []
                for match in matching_tables:
                    table_info = get_table_info(match["table"])
                    detailed_info.append({
                        "table": match["table"],
                        "match_type": match["match_type"],
                        "relevance": match["relevance"],
                        "info": table_info
                    })
                
                return json.dumps({
                    "success": True,
                    "search_term": search_term,
                    "matches_found": len(matching_tables),
                    "results": detailed_info
                }, ensure_ascii=False, indent=2)
            
            else:
                return json.dumps({
                    "success": True,
                    "search_term": search_term,
                    "matches_found": 0,
                    "message": f"Nenhuma tabela encontrada para '{search_term}'",
                    "suggestion": "Tente termos como: nota, empresa, item, pagamento, transporte, icms, ipi"
                }, ensure_ascii=False, indent=2)
        
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": "Erro ao buscar no schema",
                "details": str(e),
                "search_term": search_term
            }, ensure_ascii=False, indent=2)
