"""
Database Schema Information Module

Provides comprehensive information about the NF-e database schema
for AI agents to construct accurate SQL queries.
"""

from typing import Dict, List, Any, Optional


def get_schema_info() -> Dict[str, Any]:
    """
    Retorna informações completas do schema de NF-e.
    
    Returns:
        Dicionário com estrutura completa do banco
    """
    return {
        "database": "postgresql",
        "description": "Sistema de Notas Fiscais Eletrônicas (NF-e)",
        "version": "4.00",
        "encoding": "UTF-8",
        "timezone": "America/Sao_Paulo",
        
        "main_tables": get_main_tables(),
        "relationships": get_relationships(),
        "common_queries": get_common_queries(),
        
        "important_notes": [
            "SEMPRE use LIMIT para evitar retornar muitos dados",
            "SEMPRE filtre por status='autorizada' para dados válidos",
            "Use LEFT JOIN para empresas (pode ser NULL)",
            "Use INNER JOIN para itens (sempre existem)",
            "Valores monetários são NUMERIC(15,2)",
            "Datas são TIMESTAMP WITH TIME ZONE"
        ]
    }


def get_main_tables() -> List[Dict[str, Any]]:
    """
    Retorna lista das tabelas principais do sistema.
    
    Returns:
        Lista de tabelas com descrições
    """
    return [
        {
            "name": "notas_fiscais",
            "description": "Tabela principal com dados gerais das NF-e",
            "primary_key": "id",
            "unique_keys": ["chave_acesso"],
            "row_estimate": "milhares a milhões",
            "main_columns": [
                "id (PK)",
                "chave_acesso (44 dígitos)",
                "numero_nf, serie",
                "data_hora_emissao",
                "emitente_id (FK → empresas)",
                "destinatario_id (FK → empresas)",
                "valor_total_nota",
                "valor_total_produtos",
                "valor_icms, valor_ipi, valor_pis, valor_cofins",
                "status (emitida|autorizada|cancelada)"
            ]
        },
        {
            "name": "empresas",
            "description": "Cadastro de empresas (emitentes e destinatários)",
            "primary_key": "id",
            "unique_keys": ["cpf_cnpj"],
            "row_estimate": "centenas a milhares",
            "main_columns": [
                "id (PK)",
                "cpf_cnpj",
                "tipo_pessoa (juridica|fisica)",
                "razao_social, nome_fantasia",
                "inscricao_estadual",
                "logradouro, numero, bairro",
                "nome_municipio (cidade), uf, cep"
            ]
        },
        {
            "name": "nf_itens",
            "description": "Produtos/serviços da nota fiscal",
            "primary_key": "id",
            "foreign_keys": ["nota_fiscal_id → notas_fiscais"],
            "row_estimate": "dezenas de milhares a milhões",
            "main_columns": [
                "id (PK)",
                "nota_fiscal_id (FK)",
                "numero_item",
                "codigo_produto, descricao",
                "ncm, cfop",
                "quantidade_comercial",
                "valor_unitario_comercial",
                "valor_total_bruto",
                "unidade_comercial"
            ]
        },
        {
            "name": "nf_itens_icms",
            "description": "Detalhamento de ICMS por item",
            "primary_key": "id",
            "foreign_keys": ["nf_item_id → nf_itens"],
            "main_columns": [
                "nf_item_id (FK)",
                "origem, cst, csosn",
                "valor_bc, aliquota, valor_icms"
            ]
        },
        {
            "name": "nf_itens_ipi",
            "description": "Detalhamento de IPI por item",
            "primary_key": "id",
            "foreign_keys": ["nf_item_id → nf_itens"],
            "main_columns": [
                "nf_item_id (FK)",
                "cst, valor_bc, aliquota, valor_ipi"
            ]
        },
        {
            "name": "nf_itens_pis",
            "description": "Detalhamento de PIS por item",
            "primary_key": "id",
            "foreign_keys": ["nf_item_id → nf_itens"],
            "main_columns": [
                "nf_item_id (FK)",
                "cst, valor_bc, aliquota, valor_pis"
            ]
        },
        {
            "name": "nf_itens_cofins",
            "description": "Detalhamento de COFINS por item",
            "primary_key": "id",
            "foreign_keys": ["nf_item_id → nf_itens"],
            "main_columns": [
                "nf_item_id (FK)",
                "cst, valor_bc, aliquota, valor_cofins"
            ]
        },
        {
            "name": "nf_pagamentos",
            "description": "Formas de pagamento da nota",
            "primary_key": "id",
            "foreign_keys": ["nota_fiscal_id → notas_fiscais"],
            "main_columns": [
                "nota_fiscal_id (FK)",
                "forma_pagamento",
                "valor_pagamento"
            ]
        },
        {
            "name": "nf_transporte",
            "description": "Dados de transporte da nota",
            "primary_key": "id",
            "foreign_keys": ["nota_fiscal_id → notas_fiscais"],
            "main_columns": [
                "nota_fiscal_id (FK)",
                "modalidade_frete"
            ]
        },
        {
            "name": "nf_transporte_volumes",
            "description": "Volumes transportados",
            "primary_key": "id",
            "foreign_keys": ["transporte_id → nf_transporte"],
            "main_columns": [
                "transporte_id (FK)",
                "quantidade, especie",
                "peso_liquido, peso_bruto"
            ]
        },
        {
            "name": "nf_referencias",
            "description": "Notas fiscais referenciadas",
            "primary_key": "id",
            "foreign_keys": ["nota_fiscal_id → notas_fiscais"],
            "main_columns": [
                "nota_fiscal_id (FK)",
                "tipo",
                "chave_acesso_referenciada"
            ]
        },
        {
            "name": "nf_duplicatas",
            "description": "Duplicatas/parcelas da cobrança",
            "primary_key": "id",
            "foreign_keys": ["cobranca_id → nf_cobranca"],
            "main_columns": [
                "cobranca_id (FK)",
                "numero_duplicata",
                "data_vencimento",
                "valor_duplicata"
            ]
        }
    ]


def get_table_info(table_name: str) -> Dict[str, Any]:
    """
    Retorna informações detalhadas de uma tabela específica.
    
    Args:
        table_name: Nome da tabela
    
    Returns:
        Dicionário com informações da tabela
    """
    tables_info = {
        "notas_fiscais": {
            "description": "Tabela principal contendo dados gerais das NF-e",
            "columns": {
                "id": {"type": "SERIAL", "nullable": False, "description": "Chave primária"},
                "chave_acesso": {"type": "VARCHAR(44)", "nullable": False, "unique": True, "description": "Chave única de 44 dígitos"},
                "numero_nf": {"type": "INTEGER", "nullable": False, "description": "Número da nota fiscal"},
                "serie": {"type": "VARCHAR(3)", "nullable": True, "description": "Série da nota"},
                "data_hora_emissao": {"type": "TIMESTAMP", "nullable": False, "description": "Data e hora de emissão"},
                "emitente_id": {"type": "INTEGER", "nullable": False, "fk": "empresas(id)"},
                "destinatario_id": {"type": "INTEGER", "nullable": False, "fk": "empresas(id)"},
                "valor_total_nota": {"type": "NUMERIC(15,2)", "nullable": False, "description": "Valor total da NF-e"},
                "valor_total_produtos": {"type": "NUMERIC(15,2)", "nullable": True},
                "valor_icms": {"type": "NUMERIC(15,2)", "nullable": True},
                "valor_ipi": {"type": "NUMERIC(15,2)", "nullable": True},
                "valor_pis": {"type": "NUMERIC(15,2)", "nullable": True},
                "valor_cofins": {"type": "NUMERIC(15,2)", "nullable": True},
                "status": {"type": "VARCHAR(20)", "nullable": False, "description": "emitida, autorizada, cancelada"},
                "natureza_operacao": {"type": "VARCHAR(60)", "nullable": True},
                "tipo_operacao": {"type": "VARCHAR(1)", "nullable": True, "description": "0=Entrada, 1=Saída"},
            },
            "indexes": ["chave_acesso", "data_hora_emissao", "emitente_id", "destinatario_id", "status"],
            "relationships": [
                "notas_fiscais.emitente_id → empresas.id",
                "notas_fiscais.destinatario_id → empresas.id"
            ]
        },
        
        "empresas": {
            "description": "Cadastro de empresas (emitentes e destinatários)",
            "columns": {
                "id": {"type": "SERIAL", "nullable": False},
                "cpf_cnpj": {"type": "VARCHAR(14)", "nullable": False, "unique": True},
                "tipo_pessoa": {"type": "VARCHAR(20)", "nullable": False, "description": "juridica ou fisica"},
                "razao_social": {"type": "VARCHAR(100)", "nullable": False},
                "nome_fantasia": {"type": "VARCHAR(100)", "nullable": True},
                "inscricao_estadual": {"type": "VARCHAR(14)", "nullable": True},
                "logradouro": {"type": "VARCHAR(100)", "nullable": True},
                "numero": {"type": "VARCHAR(10)", "nullable": True},
                "bairro": {"type": "VARCHAR(60)", "nullable": True},
                "nome_municipio": {"type": "VARCHAR(60)", "nullable": True, "description": "Nome da cidade"},
                "uf": {"type": "VARCHAR(2)", "nullable": True},
                "cep": {"type": "VARCHAR(8)", "nullable": True}
            },
            "indexes": ["cpf_cnpj", "razao_social"],
            "relationships": []
        },
        
        "nf_itens": {
            "description": "Produtos/serviços da nota fiscal",
            "columns": {
                "id": {"type": "SERIAL", "nullable": False},
                "nota_fiscal_id": {"type": "INTEGER", "nullable": False, "fk": "notas_fiscais(id)"},
                "numero_item": {"type": "INTEGER", "nullable": False},
                "codigo_produto": {"type": "VARCHAR(60)", "nullable": True},
                "descricao": {"type": "VARCHAR(120)", "nullable": False},
                "ncm": {"type": "VARCHAR(8)", "nullable": True},
                "cfop": {"type": "VARCHAR(4)", "nullable": True},
                "unidade_comercial": {"type": "VARCHAR(6)", "nullable": True},
                "quantidade_comercial": {"type": "NUMERIC(15,4)", "nullable": False},
                "valor_unitario_comercial": {"type": "NUMERIC(15,10)", "nullable": False},
                "valor_total_bruto": {"type": "NUMERIC(15,2)", "nullable": False}
            },
            "indexes": ["nota_fiscal_id", "descricao"],
            "relationships": [
                "nf_itens.nota_fiscal_id → notas_fiscais.id"
            ]
        },
        
        "nf_itens_icms": {
            "description": "Informações de ICMS dos itens",
            "columns": {
                "id": {"type": "SERIAL", "nullable": False},
                "nf_item_id": {"type": "INTEGER", "nullable": False, "fk": "nf_itens(id)"},
                "origem": {"type": "VARCHAR(1)", "nullable": False},
                "cst": {"type": "VARCHAR(2)", "nullable": True},
                "csosn": {"type": "VARCHAR(3)", "nullable": True},
                "valor_bc": {"type": "NUMERIC(15,2)", "nullable": True},
                "aliquota": {"type": "NUMERIC(5,2)", "nullable": True},
                "valor_icms": {"type": "NUMERIC(15,2)", "nullable": True}
            },
            "indexes": ["nf_item_id"],
            "relationships": ["nf_itens_icms.nf_item_id → nf_itens.id"]
        },
        
        "nf_pagamentos": {
            "description": "Formas de pagamento da nota",
            "columns": {
                "id": {"type": "SERIAL", "nullable": False},
                "nota_fiscal_id": {"type": "INTEGER", "nullable": False, "fk": "notas_fiscais(id)"},
                "forma_pagamento": {"type": "VARCHAR(2)", "nullable": False},
                "valor_pagamento": {"type": "NUMERIC(15,2)", "nullable": False}
            },
            "indexes": ["nota_fiscal_id"],
            "relationships": ["nf_pagamentos.nota_fiscal_id → notas_fiscais.id"]
        }
    }
    
    # Retornar info da tabela ou erro
    if table_name in tables_info:
        return tables_info[table_name]
    else:
        return {
            "error": f"Tabela '{table_name}' não encontrada",
            "available_tables": list(tables_info.keys())
        }


def get_relationships() -> List[Dict[str, str]]:
    """
    Retorna relacionamentos (Foreign Keys) entre tabelas.
    
    Returns:
        Lista de relacionamentos
    """
    return [
        {
            "from_table": "notas_fiscais",
            "from_column": "emitente_id",
            "to_table": "empresas",
            "to_column": "id",
            "relationship_type": "many-to-one",
            "description": "Cada nota tem um emitente (LEFT JOIN pois pode ser NULL)"
        },
        {
            "from_table": "notas_fiscais",
            "from_column": "destinatario_id",
            "to_table": "empresas",
            "to_column": "id",
            "relationship_type": "many-to-one",
            "description": "Cada nota tem um destinatário (LEFT JOIN pois pode ser NULL)"
        },
        {
            "from_table": "nf_itens",
            "from_column": "nota_fiscal_id",
            "to_table": "notas_fiscais",
            "to_column": "id",
            "relationship_type": "many-to-one",
            "description": "Cada item pertence a uma nota (INNER JOIN pois sempre existe)"
        },
        {
            "from_table": "nf_itens_icms",
            "from_column": "nf_item_id",
            "to_table": "nf_itens",
            "to_column": "id",
            "relationship_type": "one-to-one",
            "description": "Cada item pode ter dados de ICMS (LEFT JOIN)"
        },
        {
            "from_table": "nf_itens_ipi",
            "from_column": "nf_item_id",
            "to_table": "nf_itens",
            "to_column": "id",
            "relationship_type": "one-to-one",
            "description": "Cada item pode ter dados de IPI (LEFT JOIN)"
        },
        {
            "from_table": "nf_itens_pis",
            "from_column": "nf_item_id",
            "to_table": "nf_itens",
            "to_column": "id",
            "relationship_type": "one-to-one",
            "description": "Cada item pode ter dados de PIS (LEFT JOIN)"
        },
        {
            "from_table": "nf_itens_cofins",
            "from_column": "nf_item_id",
            "to_table": "nf_itens",
            "to_column": "id",
            "relationship_type": "one-to-one",
            "description": "Cada item pode ter dados de COFINS (LEFT JOIN)"
        },
        {
            "from_table": "nf_pagamentos",
            "from_column": "nota_fiscal_id",
            "to_table": "notas_fiscais",
            "to_column": "id",
            "relationship_type": "many-to-one",
            "description": "Uma nota pode ter múltiplos pagamentos (INNER JOIN)"
        },
        {
            "from_table": "nf_transporte",
            "from_column": "nota_fiscal_id",
            "to_table": "notas_fiscais",
            "to_column": "id",
            "relationship_type": "one-to-one",
            "description": "Uma nota pode ter dados de transporte (LEFT JOIN)"
        }
    ]


def get_common_queries() -> List[Dict[str, Any]]:
    """
    Retorna exemplos de queries SQL comuns.
    
    Returns:
        Lista de queries com descrições
    """
    return [
        {
            "name": "Total de vendas por período",
            "description": "Soma o valor total das notas em um período",
            "sql": """
SELECT 
  COUNT(*) as total_notas,
  ROUND(SUM(valor_total_nota)::numeric, 2) as valor_total,
  ROUND(AVG(valor_total_nota)::numeric, 2) as valor_medio
FROM notas_fiscais
WHERE status = 'autorizada'
  AND data_hora_emissao >= '{data_inicio}'
  AND data_hora_emissao < '{data_fim}'
LIMIT 1;
            """,
            "placeholders": {
                "data_inicio": "2025-01-01",
                "data_fim": "2025-02-01"
            }
        },
        {
            "name": "Top produtos mais vendidos",
            "description": "Ranking de produtos por quantidade vendida",
            "sql": """
SELECT 
  i.descricao as produto,
  SUM(i.quantidade_comercial) as quantidade_total,
  ROUND(SUM(i.valor_total_bruto)::numeric, 2) as valor_total,
  COUNT(DISTINCT i.nota_fiscal_id) as num_notas
FROM nf_itens i
INNER JOIN notas_fiscais nf ON i.nota_fiscal_id = nf.id
WHERE nf.status = 'autorizada'
GROUP BY i.descricao
ORDER BY quantidade_total DESC
LIMIT {limit};
            """,
            "placeholders": {
                "limit": "10"
            }
        },
        {
            "name": "Notas por empresa",
            "description": "Lista notas fiscais de uma empresa específica",
            "sql": """
SELECT 
  nf.numero_nf,
  nf.serie,
  TO_CHAR(nf.data_hora_emissao, 'DD/MM/YYYY') as data_emissao,
  ROUND(nf.valor_total_nota::numeric, 2) as valor_total,
  e.razao_social as emitente,
  d.razao_social as destinatario
FROM notas_fiscais nf
LEFT JOIN empresas e ON nf.emitente_id = e.id
LEFT JOIN empresas d ON nf.destinatario_id = d.id
WHERE nf.status = 'autorizada'
  AND (e.razao_social ILIKE '%{empresa}%' OR d.razao_social ILIKE '%{empresa}%')
ORDER BY nf.data_hora_emissao DESC
LIMIT {limit};
            """,
            "placeholders": {
                "empresa": "nome da empresa",
                "limit": "20"
            }
        },
        {
            "name": "Faturamento mensal",
            "description": "Agrupa vendas por mês",
            "sql": """
SELECT 
  DATE_TRUNC('month', data_hora_emissao) as mes,
  COUNT(*) as total_notas,
  ROUND(SUM(valor_total_nota)::numeric, 2) as valor_total,
  ROUND(AVG(valor_total_nota)::numeric, 2) as valor_medio
FROM notas_fiscais
WHERE status = 'autorizada'
  AND data_hora_emissao >= '{data_inicio}'
GROUP BY mes
ORDER BY mes DESC
LIMIT {limit};
            """,
            "placeholders": {
                "data_inicio": "2024-01-01",
                "limit": "12"
            }
        },
        {
            "name": "Total de impostos",
            "description": "Soma todos os impostos de um período",
            "sql": """
SELECT 
  ROUND(SUM(valor_icms)::numeric, 2) as total_icms,
  ROUND(SUM(valor_ipi)::numeric, 2) as total_ipi,
  ROUND(SUM(valor_pis)::numeric, 2) as total_pis,
  ROUND(SUM(valor_cofins)::numeric, 2) as total_cofins,
  ROUND((SUM(valor_icms) + SUM(valor_ipi) + SUM(valor_pis) + SUM(valor_cofins))::numeric, 2) as total_geral
FROM notas_fiscais
WHERE status = 'autorizada'
  AND data_hora_emissao >= '{data_inicio}'
  AND data_hora_emissao < '{data_fim}'
LIMIT 1;
            """,
            "placeholders": {
                "data_inicio": "2025-01-01",
                "data_fim": "2025-02-01"
            }
        },
        {
            "name": "Buscar nota por chave",
            "description": "Busca nota fiscal pela chave de acesso",
            "sql": """
SELECT 
  nf.numero_nf,
  nf.serie,
  nf.chave_acesso,
  TO_CHAR(nf.data_hora_emissao, 'DD/MM/YYYY HH24:MI') as data_hora,
  ROUND(nf.valor_total_nota::numeric, 2) as valor_total,
  nf.status,
  e.razao_social as emitente,
  d.razao_social as destinatario
FROM notas_fiscais nf
LEFT JOIN empresas e ON nf.emitente_id = e.id
LEFT JOIN empresas d ON nf.destinatario_id = d.id
WHERE nf.chave_acesso = '{chave_acesso}'
LIMIT 1;
            """,
            "placeholders": {
                "chave_acesso": "44 dígitos da chave de acesso"
            }
        },
        {
            "name": "Itens de uma nota",
            "description": "Lista todos os itens de uma nota fiscal",
            "sql": """
SELECT 
  i.numero_item,
  i.codigo_produto,
  i.descricao,
  i.quantidade_comercial,
  ROUND(i.valor_unitario_comercial::numeric, 2) as valor_unitario,
  ROUND(i.valor_total_bruto::numeric, 2) as valor_total,
  i.unidade_comercial,
  i.ncm,
  i.cfop
FROM nf_itens i
WHERE i.nota_fiscal_id = {nota_fiscal_id}
ORDER BY i.numero_item
LIMIT 100;
            """,
            "placeholders": {
                "nota_fiscal_id": "ID da nota fiscal"
            }
        },
        {
            "name": "Notas de hoje",
            "description": "Lista notas emitidas hoje",
            "sql": """
SELECT 
  nf.numero_nf,
  nf.serie,
  TO_CHAR(nf.data_hora_emissao, 'HH24:MI') as hora,
  ROUND(nf.valor_total_nota::numeric, 2) as valor,
  e.razao_social as emitente
FROM notas_fiscais nf
LEFT JOIN empresas e ON nf.emitente_id = e.id
WHERE DATE(nf.data_hora_emissao) = CURRENT_DATE
  AND nf.status = 'autorizada'
ORDER BY nf.data_hora_emissao DESC
LIMIT 50;
            """
        }
    ]


# Função auxiliar para obter todas as tabelas
def get_all_tables() -> List[str]:
    """Retorna lista de nomes de todas as tabelas"""
    return [table["name"] for table in get_main_tables()]


# Função auxiliar para validar se tabela existe
def table_exists(table_name: str) -> bool:
    """Verifica se uma tabela existe no schema"""
    return table_name in get_all_tables()