"""
Schema Information Helper for NF-e Database

This module provides comprehensive information about the existing database schema
for Notas Fiscais Eletrônicas (NF-e). The database is already created and configured
in Supabase - this module only documents the structure for AI agents and tools.

DO NOT use this to create tables - the database already exists!
"""

from typing import Dict, List


def get_schema_info() -> str:
    """
    Returns comprehensive information about the NF-e database schema.
    
    This function provides a detailed description of all tables, columns,
    relationships, and indexes in the existing Supabase database.
    
    Returns:
        str: Formatted schema information for use by AI agents
    """
    return """
# Schema do Banco de Dados de Notas Fiscais Eletrônicas (NF-e)

## Visão Geral
Banco de dados PostgreSQL hospedado no Supabase contendo estrutura completa
para armazenamento de Notas Fiscais Eletrônicas baseado no Layout 4.00 da Receita Federal.

## Tabelas Principais

### 1. empresas
Cadastro de empresas (emitentes e destinatários das notas fiscais)

**Colunas principais:**
- id (SERIAL PRIMARY KEY)
- tipo_pessoa (VARCHAR): 'fisica' ou 'juridica'
- cpf_cnpj (VARCHAR): CPF ou CNPJ da empresa (UNIQUE)
- razao_social (VARCHAR): Nome empresarial
- nome_fantasia (VARCHAR): Nome fantasia
- inscricao_estadual (VARCHAR): IE
- regime_tributario (CHAR): 1-Simples Nacional, 2-Simples Excesso, 3-Regime Normal

**Endereço:**
- logradouro, numero, complemento, bairro
- codigo_municipio, nome_municipio, uf, cep
- telefone, email

**Índices:**
- idx_empresas_cpf_cnpj ON cpf_cnpj
- idx_empresas_tipo ON tipo_pessoa

---

### 2. notas_fiscais
Tabela principal contendo dados das Notas Fiscais Eletrônicas

**Identificação (Grupo ide):**
- id (SERIAL PRIMARY KEY)
- chave_acesso (VARCHAR UNIQUE): Chave de 44 dígitos
- numero_nf (INTEGER): Número da nota
- serie (VARCHAR): Série da nota
- modelo (VARCHAR): 55-NFe, 65-NFCe
- data_hora_emissao (TIMESTAMP): Data/hora de emissão
- data_hora_saida_entrada (TIMESTAMP): Data/hora de saída/entrada
- natureza_operacao (VARCHAR): Descrição da operação
- tipo_operacao (CHAR): 0-Entrada, 1-Saída
- destino_operacao (CHAR): 1-Interna, 2-Interestadual, 3-Exterior
- finalidade_emissao (CHAR): 1-Normal, 2-Complementar, 3-Ajuste, 4-Devolução
- status (VARCHAR): emitida, autorizada, cancelada, denegada, rejeitada, inutilizada

**Relacionamentos:**
- emitente_id (FK → empresas.id): Empresa emitente
- destinatario_id (FK → empresas.id): Empresa destinatária

**Valores Totais:**
- valor_total_produtos (DECIMAL): Valor total dos produtos/serviços
- valor_frete (DECIMAL): Valor do frete
- valor_seguro (DECIMAL): Valor do seguro
- valor_desconto (DECIMAL): Valor do desconto
- valor_total_nota (DECIMAL): Valor total da nota

**Impostos:**
- base_calculo_icms, valor_icms (DECIMAL): ICMS
- valor_ipi (DECIMAL): IPI
- valor_pis (DECIMAL): PIS
- valor_cofins (DECIMAL): COFINS
- valor_total_tributos (DECIMAL): Total de tributos (Lei da Transparência)

**Transporte:**
- modalidade_frete (CHAR): 0-Emitente, 1-Destinatário, 2-Terceiros, 9-Sem Frete

**Informações Adicionais:**
- informacoes_complementares (TEXT): Informações complementares
- informacoes_fisco (TEXT): Informações ao fisco

**Protocolo:**
- numero_protocolo (VARCHAR): Número do protocolo de autorização
- data_hora_recebimento (TIMESTAMP): Data/hora do recebimento
- codigo_status (VARCHAR): Código do status
- motivo_status (VARCHAR): Motivo do status

**Índices:**
- idx_nf_chave_acesso ON chave_acesso
- idx_nf_numero ON (numero_nf, serie, modelo)
- idx_nf_emitente ON emitente_id
- idx_nf_destinatario ON destinatario_id
- idx_nf_data_emissao ON data_hora_emissao
- idx_nf_status ON status
- idx_nf_tipo_operacao ON tipo_operacao
- idx_nf_valor ON valor_total_nota

---

### 3. nf_itens
Itens/produtos das notas fiscais

**Colunas principais:**
- id (SERIAL PRIMARY KEY)
- nota_fiscal_id (FK → notas_fiscais.id): Nota fiscal relacionada
- numero_item (INTEGER): Número sequencial do item
- codigo_produto (VARCHAR): Código do produto
- codigo_ean (VARCHAR): Código de barras EAN
- descricao (VARCHAR): Descrição do produto
- ncm (VARCHAR): Nomenclatura Comum do Mercosul
- cfop (VARCHAR): Código Fiscal de Operações e Prestações
- unidade_comercial (VARCHAR): Unidade (UN, KG, etc)
- quantidade_comercial (DECIMAL): Quantidade
- valor_unitario_comercial (DECIMAL): Valor unitário
- valor_total_bruto (DECIMAL): Valor total do item
- valor_desconto (DECIMAL): Desconto no item
- valor_frete (DECIMAL): Frete do item
- valor_seguro (DECIMAL): Seguro do item

**Campos Específicos:**
- numero_pedido_compra (VARCHAR): Número do pedido
- item_pedido_compra (INTEGER): Item do pedido

**Índices:**
- idx_nf_itens_nota ON nota_fiscal_id
- idx_nf_itens_produto ON codigo_produto
- idx_nf_itens_ncm ON ncm
- idx_nf_itens_cfop ON cfop

---

### 4. nf_itens_icms
Dados de ICMS dos itens

**Colunas principais:**
- id (SERIAL PRIMARY KEY)
- nf_item_id (FK → nf_itens.id): Item relacionado
- origem (VARCHAR): 0-Nacional, 1-Estrangeira, etc
- cst (VARCHAR): Código Situação Tributária
- csosn (VARCHAR): Código Situação Operação Simples Nacional
- modalidade_bc (VARCHAR): Modalidade de determinação da BC
- valor_bc (DECIMAL): Base de cálculo
- aliquota (DECIMAL): Alíquota do ICMS
- valor_icms (DECIMAL): Valor do ICMS
- valor_icms_desonerado (DECIMAL): Valor do ICMS desonerado

**ICMS Substituição Tributária:**
- modalidade_bc_st (VARCHAR): Modalidade BC ST
- valor_bc_st (DECIMAL): Base de cálculo ST
- aliquota_st (DECIMAL): Alíquota ST
- valor_icms_st (DECIMAL): Valor ICMS ST

**Índice:**
- idx_nf_itens_icms_item ON nf_item_id

---

### 5. nf_itens_ipi
Dados de IPI dos itens

**Colunas principais:**
- id (SERIAL PRIMARY KEY)
- nf_item_id (FK → nf_itens.id): Item relacionado
- cst (VARCHAR): Código Situação Tributária
- valor_bc (DECIMAL): Base de cálculo
- aliquota (DECIMAL): Alíquota do IPI
- valor_ipi (DECIMAL): Valor do IPI

**Índice:**
- idx_nf_itens_ipi_item ON nf_item_id

---

### 6. nf_itens_pis
Dados de PIS dos itens

**Colunas principais:**
- id (SERIAL PRIMARY KEY)
- nf_item_id (FK → nf_itens.id): Item relacionado
- cst (VARCHAR): Código Situação Tributária
- valor_bc (DECIMAL): Base de cálculo
- aliquota (DECIMAL): Alíquota do PIS
- valor_pis (DECIMAL): Valor do PIS

**PIS ST:**
- valor_bc_st (DECIMAL): Base de cálculo ST
- aliquota_st (DECIMAL): Alíquota ST
- valor_pis_st (DECIMAL): Valor PIS ST

**Índice:**
- idx_nf_itens_pis_item ON nf_item_id

---

### 7. nf_itens_cofins
Dados de COFINS dos itens

**Colunas principais:**
- id (SERIAL PRIMARY KEY)
- nf_item_id (FK → nf_itens.id): Item relacionado
- cst (VARCHAR): Código Situação Tributária
- valor_bc (DECIMAL): Base de cálculo
- aliquota (DECIMAL): Alíquota do COFINS
- valor_cofins (DECIMAL): Valor do COFINS

**COFINS ST:**
- valor_bc_st (DECIMAL): Base de cálculo ST
- aliquota_st (DECIMAL): Alíquota ST
- valor_cofins_st (DECIMAL): Valor COFINS ST

**Índice:**
- idx_nf_itens_cofins_item ON nf_item_id

---

### 8. nf_pagamentos
Formas de pagamento das notas fiscais

**Colunas principais:**
- id (SERIAL PRIMARY KEY)
- nota_fiscal_id (FK → notas_fiscais.id): Nota fiscal relacionada
- indicador_pagamento (VARCHAR): 0-À Vista, 1-A Prazo
- forma_pagamento (VARCHAR): 01-Dinheiro, 02-Cheque, 03-Cartão Crédito, etc
- valor_pagamento (DECIMAL): Valor do pagamento

**Dados do Cartão:**
- tipo_integracao (VARCHAR): 1-Integrado, 2-Não integrado
- cnpj_credenciadora (VARCHAR): CNPJ da credenciadora
- bandeira_cartao (VARCHAR): 01-Visa, 02-Mastercard, etc
- numero_autorizacao (VARCHAR): Número de autorização

**PIX:**
- cnpj_psp (VARCHAR): CNPJ do PSP
- end_to_end_id (VARCHAR): Identificador E2E

**Índices:**
- idx_nf_pagamentos_nota ON nota_fiscal_id
- idx_nf_pagamentos_forma ON forma_pagamento

---

### 9. nf_transporte
Informações de transporte das notas fiscais

**Colunas principais:**
- id (SERIAL PRIMARY KEY)
- nota_fiscal_id (FK → notas_fiscais.id): Nota fiscal relacionada
- modalidade_frete (CHAR): 0-Emitente, 1-Destinatário, 2-Terceiros, 9-Sem Frete

**Transportadora:**
- transportadora_cpf_cnpj (VARCHAR): CPF/CNPJ da transportadora
- transportadora_nome (VARCHAR): Nome da transportadora
- transportadora_inscricao_estadual (VARCHAR): IE da transportadora
- transportadora_endereco (VARCHAR): Endereço
- transportadora_municipio (VARCHAR): Município
- transportadora_uf (CHAR): UF

**Veículo:**
- placa_veiculo (VARCHAR): Placa do veículo
- uf_veiculo (CHAR): UF do veículo
- rntc (VARCHAR): Registro Nacional Transportador de Carga

**Retenção ICMS:**
- valor_servico (DECIMAL): Valor do serviço
- valor_bc_retencao_icms (DECIMAL): BC da retenção
- aliquota_retencao (DECIMAL): Alíquota de retenção
- valor_icms_retido (DECIMAL): Valor do ICMS retido

**Índice:**
- idx_nf_transporte_nota ON nota_fiscal_id

---

### 10. nf_transporte_volumes
Volumes transportados

**Colunas principais:**
- id (SERIAL PRIMARY KEY)
- transporte_id (FK → nf_transporte.id): Transporte relacionado
- quantidade (INTEGER): Quantidade de volumes
- especie (VARCHAR): Espécie dos volumes
- marca (VARCHAR): Marca dos volumes
- numeracao (VARCHAR): Numeração
- peso_liquido (DECIMAL): Peso líquido
- peso_bruto (DECIMAL): Peso bruto

---

### 11. nf_cobranca
Dados de cobrança/fatura

**Colunas principais:**
- id (SERIAL PRIMARY KEY)
- nota_fiscal_id (FK → notas_fiscais.id): Nota fiscal relacionada
- numero_fatura (VARCHAR): Número da fatura
- valor_original (DECIMAL): Valor original
- valor_desconto (DECIMAL): Desconto
- valor_liquido (DECIMAL): Valor líquido

---

### 12. nf_duplicatas
Duplicatas das notas fiscais

**Colunas principais:**
- id (SERIAL PRIMARY KEY)
- cobranca_id (FK → nf_cobranca.id): Cobrança relacionada
- numero_duplicata (VARCHAR): Número da duplicata
- data_vencimento (DATE): Data de vencimento
- valor (DECIMAL): Valor da duplicata

---

### 13. nf_referencias
Referências a outras notas fiscais

**Colunas principais:**
- id (SERIAL PRIMARY KEY)
- nota_fiscal_id (FK → notas_fiscais.id): Nota fiscal relacionada
- tipo (VARCHAR): nfe, nfce, modelo1, cte, nfp, ecf
- chave_acesso_referenciada (VARCHAR): Chave da nota referenciada

---

### 14. nf_cce
Cartas de Correção Eletrônica

**Colunas principais:**
- id (SERIAL PRIMARY KEY)
- nota_fiscal_id (FK → notas_fiscais.id): Nota fiscal relacionada
- sequencia_evento (INTEGER): Sequência do evento
- data_hora_evento (TIMESTAMP): Data/hora do evento
- correcao (TEXT): Texto da correção
- numero_protocolo (VARCHAR): Protocolo do evento

---

## Relacionamentos Principais

```
empresas (1) ----< (N) notas_fiscais [emitente_id]
empresas (1) ----< (N) notas_fiscais [destinatario_id]
notas_fiscais (1) ----< (N) nf_itens
notas_fiscais (1) ----< (N) nf_pagamentos
notas_fiscais (1) ----< (N) nf_transporte
notas_fiscais (1) ----< (N) nf_referencias
notas_fiscais (1) ----< (N) nf_cobranca
notas_fiscais (1) ----< (N) nf_cce
nf_itens (1) ----< (1) nf_itens_icms
nf_itens (1) ----< (1) nf_itens_ipi
nf_itens (1) ----< (1) nf_itens_pis
nf_itens (1) ----< (1) nf_itens_cofins
nf_transporte (1) ----< (N) nf_transporte_volumes
nf_cobranca (1) ----< (N) nf_duplicatas
```

---

## Views Disponíveis

### vw_notas_fiscais_resumo
View com resumo das notas fiscais incluindo dados do emitente e destinatário

**Colunas:**
- id, chave_acesso, numero_nf, serie
- data_hora_emissao, natureza_operacao, tipo_operacao, status
- emitente, emitente_cpf_cnpj
- destinatario, destinatario_cpf_cnpj
- valor_total_produtos, valor_total_nota
- valor_icms, valor_ipi, valor_pis, valor_cofins
- quantidade_itens

### vw_nf_itens_completo
View com itens detalhados incluindo impostos

**Colunas:**
- chave_acesso, numero_nf, serie, numero_item
- codigo_produto, descricao, ncm, cfop
- quantidade_comercial, valor_unitario_comercial, valor_total_bruto
- icms_bc, valor_icms, valor_ipi, valor_pis, valor_cofins

---

## Consultas Comuns

### Buscar notas fiscais por período
```sql
SELECT * FROM notas_fiscais 
WHERE data_hora_emissao BETWEEN '2025-01-01' AND '2025-01-31'
ORDER BY data_hora_emissao DESC;
```

### Buscar notas por emitente
```sql
SELECT nf.*, e.razao_social 
FROM notas_fiscais nf
JOIN empresas e ON nf.emitente_id = e.id
WHERE e.cpf_cnpj = '12345678901234';
```

### Buscar itens de uma nota
```sql
SELECT i.*, icms.valor_icms, ipi.valor_ipi
FROM nf_itens i
LEFT JOIN nf_itens_icms icms ON i.id = icms.nf_item_id
LEFT JOIN nf_itens_ipi ipi ON i.id = ipi.nf_item_id
WHERE i.nota_fiscal_id = 123;
```

### Total de vendas por período
```sql
SELECT 
    DATE_TRUNC('month', data_hora_emissao) AS mes,
    COUNT(*) AS quantidade_notas,
    SUM(valor_total_nota) AS total_vendas
FROM notas_fiscais
WHERE tipo_operacao = '1' AND status = 'autorizada'
GROUP BY mes
ORDER BY mes DESC;
```

### Produtos mais vendidos
```sql
SELECT 
    i.codigo_produto,
    i.descricao,
    SUM(i.quantidade_comercial) AS quantidade_total,
    SUM(i.valor_total_bruto) AS valor_total
FROM nf_itens i
JOIN notas_fiscais nf ON i.nota_fiscal_id = nf.id
WHERE nf.status = 'autorizada'
GROUP BY i.codigo_produto, i.descricao
ORDER BY quantidade_total DESC
LIMIT 10;
```

---

## Notas Importantes

1. **Banco já existe**: Todas as tabelas já estão criadas no Supabase
2. **Não criar tabelas**: Este schema é apenas para consulta
3. **Usar REST API**: Acessar via Supabase REST API, não psycopg2 direto
4. **Importação funciona**: A lógica de importação está em backend/db.py
5. **Índices otimizados**: Índices já criados para queries comuns
6. **Triggers ativos**: Triggers de updated_at já configurados
"""


def get_table_info(table_name: str) -> str:
    """
    Returns detailed information about a specific table.
    
    Args:
        table_name: Name of the table to get information about
        
    Returns:
        str: Detailed information about the specified table
    """
    tables = {
        "empresas": """
Tabela: empresas
Descrição: Cadastro de empresas (emitentes e destinatários)

Colunas principais:
- id: Identificador único
- cpf_cnpj: CPF ou CNPJ (UNIQUE)
- razao_social: Nome empresarial
- nome_fantasia: Nome fantasia
- inscricao_estadual: Inscrição estadual
- logradouro, numero, bairro, municipio, uf, cep: Endereço completo
- telefone, email: Contatos

Relacionamentos:
- Referenciada por notas_fiscais.emitente_id
- Referenciada por notas_fiscais.destinatario_id
""",
        "notas_fiscais": """
Tabela: notas_fiscais
Descrição: Tabela principal de Notas Fiscais Eletrônicas

Colunas principais:
- id: Identificador único
- chave_acesso: Chave de 44 dígitos (UNIQUE)
- numero_nf, serie, modelo: Identificação da nota
- data_hora_emissao: Data/hora de emissão
- emitente_id: FK para empresas (emitente)
- destinatario_id: FK para empresas (destinatário)
- valor_total_produtos: Valor dos produtos
- valor_total_nota: Valor total da nota
- valor_icms, valor_ipi, valor_pis, valor_cofins: Impostos
- status: emitida, autorizada, cancelada, etc
- natureza_operacao: Descrição da operação
- tipo_operacao: 0-Entrada, 1-Saída

Relacionamentos:
- Referencia empresas (emitente_id, destinatario_id)
- Referenciada por nf_itens, nf_pagamentos, nf_transporte
""",
        "nf_itens": """
Tabela: nf_itens
Descrição: Itens/produtos das notas fiscais

Colunas principais:
- id: Identificador único
- nota_fiscal_id: FK para notas_fiscais
- numero_item: Número sequencial do item
- codigo_produto: Código do produto
- descricao: Descrição do produto
- ncm: Nomenclatura Comum do Mercosul
- cfop: Código Fiscal de Operações
- quantidade_comercial: Quantidade
- valor_unitario_comercial: Valor unitário
- valor_total_bruto: Valor total do item

Relacionamentos:
- Referencia notas_fiscais (nota_fiscal_id)
- Referenciada por nf_itens_icms, nf_itens_ipi, nf_itens_pis, nf_itens_cofins
""",
        "nf_pagamentos": """
Tabela: nf_pagamentos
Descrição: Formas de pagamento das notas fiscais

Colunas principais:
- id: Identificador único
- nota_fiscal_id: FK para notas_fiscais
- forma_pagamento: 01-Dinheiro, 02-Cheque, 03-Cartão, etc
- valor_pagamento: Valor do pagamento
- bandeira_cartao: Visa, Mastercard, etc (se cartão)
- numero_autorizacao: Número de autorização (se cartão)

Relacionamentos:
- Referencia notas_fiscais (nota_fiscal_id)
""",
        "nf_transporte": """
Tabela: nf_transporte
Descrição: Informações de transporte das notas fiscais

Colunas principais:
- id: Identificador único
- nota_fiscal_id: FK para notas_fiscais
- modalidade_frete: 0-Emitente, 1-Destinatário, 2-Terceiros, 9-Sem
- transportadora_cpf_cnpj: CPF/CNPJ da transportadora
- transportadora_nome: Nome da transportadora
- placa_veiculo: Placa do veículo
- uf_veiculo: UF do veículo

Relacionamentos:
- Referencia notas_fiscais (nota_fiscal_id)
- Referenciada por nf_transporte_volumes
"""
    }
    
    return tables.get(table_name, f"Tabela '{table_name}' não encontrada no schema.")


def get_main_tables() -> List[str]:
    """
    Returns a list of the main tables in the database.
    
    Returns:
        List[str]: List of main table names
    """
    return [
        "empresas",
        "notas_fiscais",
        "nf_itens",
        "nf_itens_icms",
        "nf_itens_ipi",
        "nf_itens_pis",
        "nf_itens_cofins",
        "nf_pagamentos",
        "nf_transporte",
        "nf_cobranca",
        "nf_duplicatas",
        "nf_referencias",
        "nf_cce"
    ]


def get_relationships() -> Dict[str, List[str]]:
    """
    Returns a dictionary of table relationships.
    
    Returns:
        Dict[str, List[str]]: Dictionary mapping tables to their related tables
    """
    return {
        "empresas": [
            "notas_fiscais (emitente_id)",
            "notas_fiscais (destinatario_id)"
        ],
        "notas_fiscais": [
            "empresas (emitente_id → empresas.id)",
            "empresas (destinatario_id → empresas.id)",
            "nf_itens (nota_fiscal_id)",
            "nf_pagamentos (nota_fiscal_id)",
            "nf_transporte (nota_fiscal_id)",
            "nf_referencias (nota_fiscal_id)",
            "nf_cobranca (nota_fiscal_id)",
            "nf_cce (nota_fiscal_id)"
        ],
        "nf_itens": [
            "notas_fiscais (nota_fiscal_id → notas_fiscais.id)",
            "nf_itens_icms (nf_item_id)",
            "nf_itens_ipi (nf_item_id)",
            "nf_itens_pis (nf_item_id)",
            "nf_itens_cofins (nf_item_id)"
        ],
        "nf_transporte": [
            "notas_fiscais (nota_fiscal_id → notas_fiscais.id)",
            "nf_transporte_volumes (transporte_id)"
        ],
        "nf_cobranca": [
            "notas_fiscais (nota_fiscal_id → notas_fiscais.id)",
            "nf_duplicatas (cobranca_id)"
        ]
    }


def get_common_queries() -> Dict[str, str]:
    """
    Returns a dictionary of common SQL query patterns.
    
    Returns:
        Dict[str, str]: Dictionary mapping query descriptions to SQL patterns
    """
    return {
        "buscar_notas_por_periodo": """
SELECT * FROM notas_fiscais 
WHERE data_hora_emissao BETWEEN '{data_inicio}' AND '{data_fim}'
ORDER BY data_hora_emissao DESC;
""",
        "buscar_notas_por_emitente": """
SELECT nf.*, e.razao_social 
FROM notas_fiscais nf
JOIN empresas e ON nf.emitente_id = e.id
WHERE e.cpf_cnpj = '{cpf_cnpj}';
""",
        "buscar_itens_nota": """
SELECT i.*, icms.valor_icms, ipi.valor_ipi, pis.valor_pis, cofins.valor_cofins
FROM nf_itens i
LEFT JOIN nf_itens_icms icms ON i.id = icms.nf_item_id
LEFT JOIN nf_itens_ipi ipi ON i.id = ipi.nf_item_id
LEFT JOIN nf_itens_pis pis ON i.id = pis.nf_item_id
LEFT JOIN nf_itens_cofins cofins ON i.id = cofins.nf_item_id
WHERE i.nota_fiscal_id = {nota_fiscal_id};
""",
        "total_vendas_periodo": """
SELECT 
    DATE_TRUNC('month', data_hora_emissao) AS mes,
    COUNT(*) AS quantidade_notas,
    SUM(valor_total_nota) AS total_vendas
FROM notas_fiscais
WHERE tipo_operacao = '1' AND status = 'autorizada'
  AND data_hora_emissao BETWEEN '{data_inicio}' AND '{data_fim}'
GROUP BY mes
ORDER BY mes DESC;
""",
        "produtos_mais_vendidos": """
SELECT 
    i.codigo_produto,
    i.descricao,
    SUM(i.quantidade_comercial) AS quantidade_total,
    SUM(i.valor_total_bruto) AS valor_total
FROM nf_itens i
JOIN notas_fiscais nf ON i.nota_fiscal_id = nf.id
WHERE nf.status = 'autorizada'
GROUP BY i.codigo_produto, i.descricao
ORDER BY quantidade_total DESC
LIMIT 10;
"""
    }
