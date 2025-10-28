# Setup SQL Query Tool - Conexão Direta ao PostgreSQL

## Por que mudamos para SQL direto?

✅ **Vantagens:**
- Suporte completo a SQL (COUNT, SUM, AVG, JOINs complexos)
- Sem limitações da REST API do Supabase
- Mais rápido e direto
- O agente pode escrever SQL puro do PostgreSQL

## Instalação

### 1. Instalar psycopg2

```bash
pip install psycopg2-binary
```

Ou instalar todas as dependências:

```bash
pip install -r requirements.txt
```

### 2. Configurar senha do banco de dados

Adicione ao seu `.env`:

```bash
# Senha do banco PostgreSQL (encontre no Supabase)
SUPABASE_DB_PASSWORD=sua_senha_aqui
```

**Como encontrar a senha:**

1. Acesse seu projeto no Supabase
2. Vá em **Settings** → **Database**
3. Em **Connection string**, você verá:
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.xxx.supabase.co:5432/postgres
   ```
4. Copie `[YOUR-PASSWORD]` e cole no `.env` como `SUPABASE_DB_PASSWORD`

**Nota:** Se você não adicionar `SUPABASE_DB_PASSWORD`, o sistema tentará usar `SUPABASE_SERVICE_KEY` como fallback.

## Como funciona

### Nova Ferramenta: SQL Query Tool

A ferramenta `SQLQueryTool` permite que os agentes executem queries SQL diretamente:

```python
# Exemplo de uso pelo agente
query = "SELECT COUNT(*) as total FROM notas_fiscais WHERE status = 'autorizada'"
result = sql_tool.run(query)
```

### Exemplos de Queries Suportadas

1. **Contar registros:**
   ```sql
   SELECT COUNT(*) as total FROM notas_fiscais
   ```

2. **Contar com filtro:**
   ```sql
   SELECT COUNT(*) as total FROM notas_fiscais WHERE status = 'autorizada'
   ```

3. **Somar valores:**
   ```sql
   SELECT SUM(valor_total_nota) as total FROM notas_fiscais
   ```

4. **Média:**
   ```sql
   SELECT AVG(valor_total_nota) as media FROM notas_fiscais WHERE status = 'autorizada'
   ```

5. **JOIN complexo:**
   ```sql
   SELECT 
     e.razao_social,
     COUNT(nf.id) as total_notas,
     SUM(nf.valor_total_nota) as valor_total
   FROM empresas e
   LEFT JOIN notas_fiscais nf ON e.id = nf.emitente_id
   GROUP BY e.razao_social
   ORDER BY total_notas DESC
   LIMIT 10
   ```

6. **Subquery:**
   ```sql
   SELECT * FROM notas_fiscais 
   WHERE valor_total_nota > (SELECT AVG(valor_total_nota) FROM notas_fiscais)
   LIMIT 10
   ```

### Segurança

A ferramenta tem proteções embutidas:

- ✅ Apenas queries `SELECT` são permitidas
- ❌ Bloqueio de: INSERT, UPDATE, DELETE, DROP, CREATE, ALTER, TRUNCATE
- ❌ Bloqueio de múltiplas queries (SQL injection)
- ✅ Validação antes de executar

## Testando

### 1. Limpar memória antiga (opcional)

Se o agente ainda está usando dados antigos da memória, limpe:

```bash
# Deletar pasta de memória
rm -rf backend/storage/memory
```

Ou via API:

```bash
curl -X DELETE http://localhost:8000/api/chat/history/user-123456-session?clear_vectors=true
```

### 2. Testar query direta

Crie um teste rápido:

```python
# test_sql_tool.py
from agents.tools.sql_query_tool import SQLQueryTool

tool = SQLQueryTool()
result = tool._run("SELECT COUNT(*) as total FROM notas_fiscais")
print(result)
```

### 3. Testar via API

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id": "test-new", "message": "Quantas notas fiscais existem no banco?"}'
```

## Troubleshooting

### Erro: "password authentication failed"

- Verifique se `SUPABASE_DB_PASSWORD` está correto no `.env`
- Confirme a senha no Supabase Dashboard → Settings → Database

### Erro: "could not connect to server"

- Verifique se o host está correto (db.xxx.supabase.co)
- Confirme que a porta 5432 está acessível
- Verifique firewall/rede

### Erro: "psycopg2 not found"

```bash
pip install psycopg2-binary
```

### Agente ainda retorna valores errados

Limpe a memória do CrewAI:

```bash
rm -rf backend/storage/memory
```

E reinicie o servidor.

## Comparação: REST API vs SQL Direto

| Recurso | REST API | SQL Direto |
|---------|----------|------------|
| COUNT(*) | ❌ Limitado | ✅ Funciona |
| SUM, AVG | ❌ Limitado | ✅ Funciona |
| JOINs complexos | ⚠️ Difícil | ✅ Fácil |
| Subqueries | ❌ Não | ✅ Sim |
| GROUP BY | ⚠️ Limitado | ✅ Completo |
| Performance | ⚠️ Média | ✅ Rápida |
| Flexibilidade | ⚠️ Baixa | ✅ Alta |

## Próximos Passos

1. Instale psycopg2: `pip install psycopg2-binary`
2. Configure `SUPABASE_DB_PASSWORD` no `.env`
3. Reinicie o servidor: `python main.py`
4. Teste: "Quantas notas fiscais existem?"
5. Agora deve retornar o valor correto! 🎉
