# CrewAI Tools for NF-e System

This directory contains custom CrewAI tools for querying the Supabase database and retrieving schema information.

## Available Tools

### 1. DatabaseQueryTool

Executes SELECT queries on the Supabase database using the REST API with PostgREST filters.

**Features:**
- Simple table queries with filters
- PostgREST filter operators: `eq`, `gt`, `lt`, `gte`, `lte`, `like`, `ilike`, `in`
- Ordering and pagination support
- Read-only (SELECT only) for safety

**Example Usage:**

```python
from agents.tools import DatabaseQueryTool

tool = DatabaseQueryTool()

# Query empresas table
result = tool._run(
    table="empresas",
    select="id,cpf_cnpj,razao_social",
    limit=10
)

# Query with filters
result = tool._run(
    table="notas_fiscais",
    select="numero_nf,serie,valor_total_nota",
    filters={"status": "eq.autorizada", "valor_total_nota": "gt.1000"},
    order="data_hora_emissao.desc",
    limit=20
)
```

**PostgREST Filter Operators:**

| Operator | Description | Example |
|----------|-------------|---------|
| `eq` | Equal | `{"status": "eq.autorizada"}` |
| `gt` | Greater than | `{"valor_total_nota": "gt.1000"}` |
| `lt` | Less than | `{"valor_total_nota": "lt.5000"}` |
| `gte` | Greater than or equal | `{"quantidade": "gte.10"}` |
| `lte` | Less than or equal | `{"quantidade": "lte.100"}` |
| `like` | Pattern match (case-sensitive) | `{"descricao": "like.*produto*"}` |
| `ilike` | Pattern match (case-insensitive) | `{"razao_social": "ilike.*ltda*"}` |
| `in` | In list | `{"status": "in.(autorizada,emitida)"}` |

### 2. DatabaseJoinQueryTool

Executes advanced queries with JOINs using PostgREST relationship syntax.

**Features:**
- Include related table data in a single query
- Nested relationships
- Efficient data retrieval

**Example Usage:**

```python
from agents.tools import DatabaseJoinQueryTool

tool = DatabaseJoinQueryTool()

# Query notas_fiscais with emitente and destinatario data
result = tool._run(
    base_table="notas_fiscais",
    select="*,empresas!emitente_id(razao_social,cpf_cnpj),empresas!destinatario_id(razao_social,cpf_cnpj)",
    filters={"status": "eq.autorizada"},
    limit=10
)

# Query nf_itens with nota fiscal data
result = tool._run(
    base_table="nf_itens",
    select="*,notas_fiscais(numero_nf,serie,data_hora_emissao)",
    filters={"valor_total_bruto": "gt.1000"},
    limit=10
)
```

### 3. SchemaInfoTool

Provides information about the database schema structure.

**Features:**
- Full schema documentation
- Table-specific information
- Relationship mapping
- Common query examples

**Example Usage:**

```python
from agents.tools import SchemaInfoTool

tool = SchemaInfoTool()

# Get full schema
result = tool._run(query_type="full")

# Get info about specific table
result = tool._run(query_type="table", table_name="notas_fiscais")

# Get list of all tables
result = tool._run(query_type="tables")

# Get table relationships
result = tool._run(query_type="relationships")

# Get common query examples
result = tool._run(query_type="queries")
```

### 4. SchemaSearchTool

Searches for tables and columns by keyword.

**Features:**
- Keyword-based search
- Finds relevant tables quickly
- Returns detailed table information

**Example Usage:**

```python
from agents.tools import SchemaSearchTool

tool = SchemaSearchTool()

# Search for ICMS-related tables
result = tool._run(search_term="icms")

# Search for payment-related tables
result = tool._run(search_term="pagamento")

# Search for transport-related tables
result = tool._run(search_term="transporte")
```

## Integration with CrewAI Agents

These tools are designed to be used with CrewAI agents. Here's how to integrate them:

```python
from crewai import Agent
from agents.tools import DatabaseQueryTool, SchemaInfoTool

# Create tools
db_tool = DatabaseQueryTool()
schema_tool = SchemaInfoTool()

# Create agent with tools
sql_agent = Agent(
    role="SQL Specialist",
    goal="Query the database to retrieve NF-e data",
    backstory="Expert in SQL and database queries",
    tools=[db_tool, schema_tool],
    verbose=True
)
```

## Testing

Run the test suite to verify all tools are working correctly:

```bash
cd backend
python agents/tools/test_tools.py
```

The test suite will:
1. Test SchemaInfoTool with various query types
2. Test SchemaSearchTool with different search terms
3. Test DatabaseQueryTool with various filters and queries
4. Test DatabaseJoinQueryTool with relationship queries

## Important Notes

### Security

- **Read-Only**: All database tools only support SELECT operations
- **No Modifications**: INSERT, UPDATE, DELETE operations are not allowed
- **Service Key**: Uses Supabase service key for bypassing RLS

### Performance

- **Query Limits**: Default limit is 100 records, maximum is 1000
- **Timeouts**: Queries timeout after 30 seconds
- **Pagination**: Use `offset` parameter for pagination

### Error Handling

All tools return JSON responses with:
- `success`: Boolean indicating success/failure
- `error`: Error message (if failed)
- `details`: Additional error details (if available)
- `results`: Query results (if successful)

Example error response:
```json
{
  "success": false,
  "error": "Erro na consulta ao banco de dados (HTTP 400)",
  "details": "Invalid filter syntax",
  "table": "notas_fiscais"
}
```

## Database Schema Reference

### Main Tables

- **empresas**: Companies (emitters and recipients)
- **notas_fiscais**: Electronic invoices (NF-e)
- **nf_itens**: Invoice items/products
- **nf_itens_icms**: ICMS tax details
- **nf_itens_ipi**: IPI tax details
- **nf_itens_pis**: PIS tax details
- **nf_itens_cofins**: COFINS tax details
- **nf_pagamentos**: Payment methods
- **nf_transporte**: Transport information
- **nf_transporte_volumes**: Transport volumes
- **nf_cobranca**: Billing information
- **nf_duplicatas**: Invoice installments
- **nf_referencias**: Referenced invoices
- **nf_cce**: Electronic correction letters

### Key Relationships

```
empresas (1) ----< (N) notas_fiscais [emitente_id, destinatario_id]
notas_fiscais (1) ----< (N) nf_itens
notas_fiscais (1) ----< (N) nf_pagamentos
notas_fiscais (1) ----< (N) nf_transporte
nf_itens (1) ----< (1) nf_itens_icms
nf_itens (1) ----< (1) nf_itens_ipi
nf_itens (1) ----< (1) nf_itens_pis
nf_itens (1) ----< (1) nf_itens_cofins
```

## Troubleshooting

### Connection Errors

If you get connection errors, verify:
1. `.env` file has correct `SUPABASE_URL` and `SUPABASE_SERVICE_KEY`
2. Supabase project is active and accessible
3. Network connectivity is working

### Query Errors

If queries fail:
1. Check table name spelling
2. Verify column names exist in the table
3. Check filter syntax (use PostgREST format)
4. Ensure the table has data

### Schema Errors

If schema information is incorrect:
1. Verify `database/schema.py` is up to date
2. Check if database schema has changed
3. Update schema documentation if needed

## Contributing

When adding new tools:
1. Inherit from `crewai_tools.BaseTool`
2. Define input schema with Pydantic `BaseModel`
3. Implement `_run()` method
4. Return JSON string responses
5. Add comprehensive docstrings
6. Update this README
7. Add tests to `test_tools.py`
