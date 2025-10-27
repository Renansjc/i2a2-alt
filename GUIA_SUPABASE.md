# 🚀 Guia de Instalação - NF-e no Supabase

## 📋 Pré-requisitos

- Conta no Supabase (https://supabase.com)
- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

## 🔧 Configuração do Supabase

### Passo 1: Criar as Tabelas

1. Acesse seu projeto no Supabase: https://uyxlfiongsucsuiwwgny.supabase.co
2. Vá em **SQL Editor** (ícone de código no menu lateral)
3. Copie todo o conteúdo do arquivo `schema_nfe_completo.sql`
4. Cole no editor SQL
5. Clique em **Run** (ou pressione Ctrl+Enter)

⚠️ **Importante**: Aguarde até que todas as tabelas sejam criadas. Isso pode levar alguns segundos.

### Passo 2: Verificar a Criação das Tabelas

Execute a seguinte query para verificar:

```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;
```

Você deve ver todas as tabelas criadas, incluindo:
- empresas
- notas_fiscais
- nf_itens
- nf_itens_icms
- nf_itens_ipi
- nf_itens_pis
- nf_itens_cofins
- nf_transporte
- nf_pagamentos
- E outras...

### Passo 3: Desabilitar RLS (Row Level Security)

Como você mencionou que não está preocupado com RLS e vai usar a service key, desabilite o RLS nas tabelas principais:

```sql
-- Desabilitar RLS em todas as tabelas
ALTER TABLE empresas DISABLE ROW LEVEL SECURITY;
ALTER TABLE notas_fiscais DISABLE ROW LEVEL SECURITY;
ALTER TABLE nf_itens DISABLE ROW LEVEL SECURITY;
ALTER TABLE nf_itens_icms DISABLE ROW LEVEL SECURITY;
ALTER TABLE nf_itens_ipi DISABLE ROW LEVEL SECURITY;
ALTER TABLE nf_itens_pis DISABLE ROW LEVEL SECURITY;
ALTER TABLE nf_itens_cofins DISABLE ROW LEVEL SECURITY;
ALTER TABLE nf_itens_issqn DISABLE ROW LEVEL SECURITY;
ALTER TABLE nf_itens_ii DISABLE ROW LEVEL SECURITY;
ALTER TABLE nf_itens_di DISABLE ROW LEVEL SECURITY;
ALTER TABLE nf_itens_di_adicoes DISABLE ROW LEVEL SECURITY;
ALTER TABLE nf_itens_rastreabilidade DISABLE ROW LEVEL SECURITY;
ALTER TABLE nf_itens_combustivel DISABLE ROW LEVEL SECURITY;
ALTER TABLE nf_referencias DISABLE ROW LEVEL SECURITY;
ALTER TABLE nf_transporte DISABLE ROW LEVEL SECURITY;
ALTER TABLE nf_transporte_reboque DISABLE ROW LEVEL SECURITY;
ALTER TABLE nf_transporte_volumes DISABLE ROW LEVEL SECURITY;
ALTER TABLE nf_transporte_volumes_lacres DISABLE ROW LEVEL SECURITY;
ALTER TABLE nf_cobranca DISABLE ROW LEVEL SECURITY;
ALTER TABLE nf_duplicatas DISABLE ROW LEVEL SECURITY;
ALTER TABLE nf_pagamentos DISABLE ROW LEVEL SECURITY;
ALTER TABLE nf_cce DISABLE ROW LEVEL SECURITY;
ALTER TABLE nf_processamento DISABLE ROW LEVEL SECURITY;
```

## 🐍 Configuração do Python

### Opção 1: Usando requests (mais simples)

```bash
pip install requests
```

Use o arquivo: `importar_nfe_supabase.py`

### Opção 2: Usando supabase-py (recomendado)

```bash
pip install supabase
```

Use o arquivo: `importar_nfe_supabase_v2.py`

## 📝 Configurando o Script

Ambos os scripts já vêm com suas credenciais configuradas:

```python
SUPABASE_URL = "https://uyxlfiongsucsuiwwgny.supabase.co"
SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

⚠️ **IMPORTANTE**: A service key tem acesso total ao banco. Mantenha-a segura e NUNCA exponha em código público!

## 🎯 Como Usar

### Importar uma NF-e

```python
from importar_nfe_supabase import SupabaseNFeImporter

# Criar instância do importador
importer = SupabaseNFeImporter()

# Importar NF-e
nf_id = importer.import_nfe('caminho/para/nfe.xml')

print(f"NF-e importada com ID: {nf_id}")
```

### Importar múltiplas NF-e

```python
import os
from importar_nfe_supabase import SupabaseNFeImporter

# Diretório com XMLs
xml_dir = 'pasta/com/xmls'

# Criar importador
importer = SupabaseNFeImporter()

# Processar todos os XMLs
for filename in os.listdir(xml_dir):
    if filename.endswith('.xml'):
        xml_path = os.path.join(xml_dir, filename)
        try:
            nf_id = importer.import_nfe(xml_path)
            print(f"✅ {filename} importada com sucesso! ID: {nf_id}")
        except Exception as e:
            print(f"❌ Erro ao importar {filename}: {str(e)}")
```

### Script completo de exemplo

```python
#!/usr/bin/env python3
"""
Script para importar todas as NF-e de um diretório
"""
import os
import sys
from importar_nfe_supabase import SupabaseNFeImporter

def main():
    if len(sys.argv) < 2:
        print("Uso: python importar_lote.py <diretorio_com_xmls>")
        sys.exit(1)
    
    xml_dir = sys.argv[1]
    
    if not os.path.isdir(xml_dir):
        print(f"Erro: {xml_dir} não é um diretório válido")
        sys.exit(1)
    
    importer = SupabaseNFeImporter()
    
    sucesso = 0
    erros = 0
    
    print(f"Processando XMLs em: {xml_dir}\n")
    
    for filename in sorted(os.listdir(xml_dir)):
        if not filename.endswith('.xml'):
            continue
        
        xml_path = os.path.join(xml_dir, filename)
        
        try:
            nf_id = importer.import_nfe(xml_path)
            sucesso += 1
            print(f"✅ {filename} → ID: {nf_id}")
        except Exception as e:
            erros += 1
            print(f"❌ {filename} → Erro: {str(e)}")
    
    print(f"\n{'='*60}")
    print(f"Processamento concluído!")
    print(f"Sucessos: {sucesso}")
    print(f"Erros: {erros}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
```

Salve como `importar_lote.py` e execute:

```bash
python importar_lote.py /caminho/para/pasta/com/xmls
```

## 🔍 Consultando os Dados

### Pelo Supabase Dashboard

1. Acesse: https://uyxlfiongsucsuiwwgny.supabase.co
2. Vá em **Table Editor**
3. Selecione a tabela desejada
4. Use filtros e buscas

### Via Python

```python
from supabase import create_client

SUPABASE_URL = "https://uyxlfiongsucsuiwwgny.supabase.co"
SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

supabase = create_client(SUPABASE_URL, SERVICE_KEY)

# Buscar todas as notas
notas = supabase.table('notas_fiscais').select('*').execute()

# Buscar nota por chave de acesso
nota = supabase.table('notas_fiscais')\
    .select('*')\
    .eq('chave_acesso', '42250383261420001201550990003348371042993209')\
    .execute()

# Buscar notas autorizadas
notas_autorizadas = supabase.table('notas_fiscais')\
    .select('*')\
    .eq('status', 'autorizada')\
    .order('data_hora_emissao', desc=True)\
    .limit(10)\
    .execute()

# Join com empresas
notas_com_emitente = supabase.table('notas_fiscais')\
    .select('*, empresas!emitente_id(razao_social)')\
    .execute()
```

### Via SQL

No SQL Editor do Supabase:

```sql
-- Listar últimas 10 notas
SELECT 
    chave_acesso,
    numero_nf,
    serie,
    data_hora_emissao,
    valor_total_nota,
    status
FROM notas_fiscais
ORDER BY data_hora_emissao DESC
LIMIT 10;

-- Buscar nota específica com emitente e destinatário
SELECT 
    nf.*,
    e_emit.razao_social AS emitente,
    e_dest.razao_social AS destinatario
FROM notas_fiscais nf
LEFT JOIN empresas e_emit ON nf.emitente_id = e_emit.id
LEFT JOIN empresas e_dest ON nf.destinatario_id = e_dest.id
WHERE nf.chave_acesso = '42250383261420001201550990003348371042993209';
```

## 📊 Queries Úteis

Confira o arquivo `queries_uteis.sql` para mais de 20 queries prontas para:
- Relatórios de vendas
- Análises tributárias
- Ranking de clientes
- Controle de estoque
- Dashboard e KPIs

## ⚡ Dicas de Performance

### 1. Habilitar Índices Adicionais

Se você vai fazer muitas buscas por produto:

```sql
CREATE INDEX idx_nf_itens_descricao ON nf_itens USING gin(to_tsvector('portuguese', descricao));
```

### 2. Vacuuming (Limpeza)

Execute periodicamente para otimizar:

```sql
VACUUM ANALYZE notas_fiscais;
VACUUM ANALYZE nf_itens;
```

### 3. Particionamento (para grandes volumes)

Se você vai ter milhões de notas, considere particionar por ano:

```sql
-- Criar partições
CREATE TABLE notas_fiscais_2025 
PARTITION OF notas_fiscais
FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');

CREATE TABLE notas_fiscais_2024 
PARTITION OF notas_fiscais
FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');
```

## 🔒 Segurança

### Opção 1: Continuar sem RLS (mais simples)
- Use apenas a service key
- Controle o acesso no nível da aplicação

### Opção 2: Habilitar RLS (mais seguro)

Se no futuro quiser habilitar RLS:

```sql
-- Habilitar RLS
ALTER TABLE notas_fiscais ENABLE ROW LEVEL SECURITY;

-- Criar política para service role (acesso total)
CREATE POLICY "Service role tem acesso total" ON notas_fiscais
    FOR ALL 
    USING (true)
    WITH CHECK (true);

-- Criar política para leitura pública (se necessário)
CREATE POLICY "Leitura pública" ON notas_fiscais
    FOR SELECT 
    USING (true);
```

## 🐛 Troubleshooting

### Erro: "relation 'notas_fiscais' does not exist"
**Solução**: Execute o schema SQL novamente.

### Erro: "duplicate key value violates unique constraint"
**Solução**: A NF-e já existe no banco. Verifique pela chave de acesso.

### Erro: "permission denied"
**Solução**: Verifique se a service key está correta e se o RLS está desabilitado.

### Erro ao importar: "Invalid date format"
**Solução**: Verifique o formato das datas no XML. O script espera ISO 8601.

### Performance lenta
**Solução**: 
1. Execute VACUUM ANALYZE
2. Verifique os índices
3. Considere particionamento

## 📞 Suporte

- **Documentação Supabase**: https://supabase.com/docs
- **Documentação NF-e**: http://www.nfe.fazenda.gov.br/
- **Python supabase-py**: https://github.com/supabase-community/supabase-py

## 🎉 Próximos Passos

1. ✅ Criar as tabelas no Supabase
2. ✅ Desabilitar RLS
3. ✅ Instalar dependências Python
4. ✅ Testar importação com 1 XML
5. ✅ Importar lote de XMLs
6. 📊 Criar dashboards e relatórios
7. 🔄 Automatizar importação (cron, webhook, etc)

---

**🚀 Pronto para começar!** Execute o schema SQL e importe sua primeira NF-e!
