# Sistema de Banco de Dados para NF-e (Nota Fiscal Eletrônica)

Sistema completo de armazenamento e gestão de Notas Fiscais Eletrônicas (NF-e) em PostgreSQL, baseado no layout 4.00 da Receita Federal do Brasil.

## 📋 Índice

- [Características](#características)
- [Estrutura do Banco de Dados](#estrutura-do-banco-de-dados)
- [Instalação](#instalação)
- [Uso](#uso)
- [Queries Úteis](#queries-úteis)
- [Campos Principais](#campos-principais)
- [Referências](#referências)

## ✨ Características

- ✅ **Completo**: Suporta todos os campos do layout 4.00 da NF-e
- ✅ **Normalizado**: Estrutura relacional otimizada
- ✅ **Impostos**: ICMS, IPI, PIS, COFINS, II, ISSQN
- ✅ **Rastreabilidade**: Histórico completo de alterações
- ✅ **Performance**: Índices estratégicos para consultas rápidas
- ✅ **Views**: Views pré-configuradas para relatórios
- ✅ **Integração**: Script Python para importação de XML

## 🗄️ Estrutura do Banco de Dados

### Tabelas Principais

#### 1. **empresas**
Cadastro de emitentes e destinatários (pessoas físicas e jurídicas).

#### 2. **notas_fiscais**
Tabela principal com todos os dados da NF-e:
- Identificação (chave de acesso, número, série)
- Datas (emissão, saída/entrada)
- Totalizadores (produtos, impostos, frete, etc)
- Status e protocolo de autorização
- Informações adicionais

#### 3. **nf_itens**
Produtos/serviços da nota fiscal:
- Descrição, código, NCM, CFOP
- Quantidades e valores
- Medicamentos, veículos, combustíveis, armamentos

#### 4. **nf_itens_icms**
Detalhamento do ICMS por item:
- CST/CSOSN
- Base de cálculo, alíquota, valor
- ICMS ST, FCP
- ICMS monofásico
- Partilha DIFAL

#### 5. **nf_itens_ipi**
Detalhamento do IPI.

#### 6. **nf_itens_pis**
Detalhamento do PIS.

#### 7. **nf_itens_cofins**
Detalhamento do COFINS.

#### 8. **nf_itens_issqn**
Detalhamento do ISS (serviços).

#### 9. **nf_transporte**
Informações de transporte:
- Modalidade de frete
- Transportadora
- Veículo
- Volumes, lacres

#### 10. **nf_pagamentos**
Formas de pagamento:
- Dinheiro, cartão, PIX, boleto, etc
- Dados de credenciadora (cartão)

#### 11. **nf_cobranca** e **nf_duplicatas**
Fatura e parcelas.

#### 12. **nf_referencias**
Referências a outras notas fiscais.

#### 13. **nf_cce**
Cartas de Correção Eletrônica.

### Diagrama de Relacionamentos

```
empresas (1) ──────┬────── (N) notas_fiscais
                   │              │
                   └──────────────┤
                                  │
                    ┌─────────────┴─────────────┬──────────────┬─────────────┐
                    │                           │              │             │
              (N) nf_itens                (N) nf_transporte   (N) nf_pagamentos  (N) nf_referencias
                    │
        ┌───────────┼───────────┬──────────┬──────────┐
        │           │           │          │          │
  nf_itens_icms  nf_itens_ipi  nf_itens_pis  nf_itens_cofins  nf_itens_issqn
```

## 🚀 Instalação

### Pré-requisitos

- PostgreSQL 12+
- Python 3.8+ (para importação)
- pip (gerenciador de pacotes Python)

### Passo 1: Criar o Banco de Dados

```bash
# Conectar ao PostgreSQL
psql -U postgres

# Criar banco de dados
CREATE DATABASE nfe_db;

# Conectar ao banco criado
\c nfe_db
```

### Passo 2: Executar o Schema

```bash
psql -U postgres -d nfe_db -f schema_nfe_completo.sql
```

### Passo 3: Instalar Dependências Python

```bash
pip install psycopg2-binary
```

## 📖 Uso

### Importar XML de NF-e

```python
from importar_nfe import NFeImporter

# Configurar conexão com o banco
db_config = {
    'host': 'localhost',
    'database': 'nfe_db',
    'user': 'postgres',
    'password': 'sua_senha'
}

# Importar NF-e
importer = NFeImporter(db_config)
nf_id = importer.import_nfe('caminho/para/nfe.xml')

print(f"NF-e importada com ID: {nf_id}")
```

### Consultar Notas Fiscais

```python
import psycopg2

conn = psycopg2.connect(**db_config)
cursor = conn.cursor()

# Buscar nota por chave de acesso
cursor.execute("""
    SELECT * FROM notas_fiscais 
    WHERE chave_acesso = %s
""", ('42250383261420001201550990003348371042993209',))

nota = cursor.fetchone()
```

## 📊 Queries Úteis

O arquivo `queries_uteis.sql` contém 20+ queries prontas para:

1. **Relatórios de Vendas**
   - Vendas por período
   - Top produtos mais vendidos
   - Faturamento mensal

2. **Análises Tributárias**
   - Carga tributária por nota
   - Impostos por NCM
   - CFOP mais utilizados

3. **Gestão de Clientes**
   - Ranking de clientes
   - Ticket médio
   - Última compra

4. **Controle de Estoque**
   - Entradas vs Saídas
   - Saldo por produto

5. **Auditoria**
   - Notas com problemas
   - Divergências de valores
   - Histórico de alterações

### Exemplo: Vendas do Mês

```sql
SELECT 
    DATE(data_hora_emissao) AS data,
    COUNT(*) AS quantidade_notas,
    SUM(valor_total_nota) AS total
FROM notas_fiscais
WHERE data_hora_emissao >= DATE_TRUNC('month', CURRENT_DATE)
  AND tipo_operacao = '1' -- Saída
  AND status = 'autorizada'
GROUP BY DATE(data_hora_emissao)
ORDER BY data;
```

## 🔑 Campos Principais

### Identificação da NF-e (ide)

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `chave_acesso` | VARCHAR(44) | Chave de acesso de 44 dígitos |
| `numero_nf` | INTEGER | Número da nota fiscal |
| `serie` | VARCHAR(3) | Série da nota |
| `modelo` | VARCHAR(2) | 55-NFe, 65-NFCe |
| `tipo_operacao` | CHAR(1) | 0-Entrada, 1-Saída |
| `finalidade_emissao` | CHAR(1) | 1-Normal, 4-Devolução |

### Totalizadores

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `valor_total_produtos` | DECIMAL(15,2) | Valor total dos produtos |
| `valor_total_nota` | DECIMAL(15,2) | Valor total da nota |
| `valor_icms` | DECIMAL(15,2) | Valor total do ICMS |
| `valor_ipi` | DECIMAL(15,2) | Valor total do IPI |
| `valor_pis` | DECIMAL(15,2) | Valor total do PIS |
| `valor_cofins` | DECIMAL(15,2) | Valor total do COFINS |

### Status da NF-e

| Valor | Descrição |
|-------|-----------|
| `emitida` | NF-e emitida mas não enviada |
| `autorizada` | Autorizada pela SEFAZ |
| `cancelada` | Cancelada |
| `denegada` | Uso denegado |
| `rejeitada` | Rejeitada pela SEFAZ |
| `inutilizada` | Numeração inutilizada |

### Tipos de Operação (tipo_operacao)

| Valor | Descrição |
|-------|-----------|
| `0` | Entrada |
| `1` | Saída |

### Finalidade de Emissão (finalidade_emissao)

| Valor | Descrição |
|-------|-----------|
| `1` | NF-e normal |
| `2` | NF-e complementar |
| `3` | NF-e de ajuste |
| `4` | Devolução de mercadoria |

### Formas de Pagamento (forma_pagamento)

| Código | Descrição |
|--------|-----------|
| `01` | Dinheiro |
| `02` | Cheque |
| `03` | Cartão de Crédito |
| `04` | Cartão de Débito |
| `05` | Crédito Loja |
| `10` | Vale Alimentação |
| `11` | Vale Refeição |
| `12` | Vale Presente |
| `13` | Vale Combustível |
| `15` | Boleto Bancário |
| `16` | Depósito Bancário |
| `17` | PIX |
| `18` | Transferência bancária |
| `90` | Sem pagamento |

## 🎯 CFOP Comuns

| CFOP | Descrição |
|------|-----------|
| 5101 | Venda de produção do estabelecimento |
| 5102 | Venda de mercadoria adquirida |
| 5202 | Devolução de compra para comercialização |
| 6101 | Venda de produção (interestadual) |
| 6102 | Venda de mercadoria (interestadual) |
| 1102 | Compra para comercialização |
| 1202 | Devolução de venda de mercadoria |

## 📈 Performance

### Índices Criados

O schema inclui índices estratégicos em:
- Chave de acesso
- Datas de emissão
- CPF/CNPJ
- Códigos de produtos
- Status da nota
- NCM, CFOP

### Dicas de Otimização

1. **Particionamento**: Para bancos com milhões de registros, considere particionar `notas_fiscais` por data
2. **Arquivamento**: Mova notas antigas para tabelas de histórico
3. **VACUUM**: Execute periodicamente `VACUUM ANALYZE` nas tabelas
4. **Monitoramento**: Use `pg_stat_statements` para identificar queries lentas

```sql
-- Criar particionamento por ano (exemplo)
CREATE TABLE notas_fiscais_2025 
PARTITION OF notas_fiscais
FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');
```

## 🔒 Segurança

### Recomendações

1. **Usuários**: Crie usuários específicos com permissões limitadas
```sql
CREATE USER app_nfe WITH PASSWORD 'senha_forte';
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO app_nfe;
```

2. **Backup**: Configure backups automáticos diários
```bash
pg_dump -U postgres nfe_db > backup_$(date +%Y%m%d).sql
```

3. **SSL**: Configure conexões SSL no PostgreSQL
4. **Auditoria**: Ative log de transações importantes

## 📝 Notas Técnicas

### Compatibilidade

- **Layout**: 4.00 (versão atual da NF-e)
- **Modelos suportados**: 55 (NF-e), 65 (NFC-e)
- **Schemas XML**: http://www.portalfiscal.inf.br/nfe

### Limitações

- Não inclui integração direta com SEFAZ (foco em armazenamento)
- Não valida regras de negócio específicas (CST, alíquotas, etc)
- XML completo armazenado como TEXT (considerar uso de XML nativo do PostgreSQL para queries XPath)

### Campos Opcionais

Muitos campos são opcionais e podem ser NULL. Revise o schema e ajuste constraints conforme suas necessidades:
```sql
ALTER TABLE notas_fiscais 
ALTER COLUMN campo_exemplo SET NOT NULL;
```

## 🔄 Extensões Futuras

Possíveis melhorias:

1. **CT-e**: Conhecimento de Transporte Eletrônico
2. **MDF-e**: Manifesto Eletrônico de Documentos Fiscais
3. **NFS-e**: Nota Fiscal de Serviços Eletrônica
4. **EFD**: Escrituração Fiscal Digital
5. **Integração**: APIs REST para consulta e inserção
6. **Dashboard**: Interface web com gráficos e relatórios
7. **Jobs**: Rotinas automáticas de processamento

## 📚 Referências

- [Portal da NF-e](http://www.nfe.fazenda.gov.br/)
- [Manual de Orientação do Contribuinte](http://www.nfe.fazenda.gov.br/portal/listaConteudo.aspx?tipoConteudo=/fS87nGWBbQ=)
- [Schemas XML](http://www.portalfiscal.inf.br/nfe)
- [Tabelas de Códigos](http://www.nfe.fazenda.gov.br/portal/listaConteudo.aspx?tipoConteudo=Iy/5Qol1YbE=)

## 📄 Licença

Este projeto é fornecido como está, sem garantias. Use por sua conta e risco.

## 🤝 Contribuições

Melhorias são bem-vindas! Áreas de interesse:
- Otimizações de queries
- Novos relatórios
- Validações de dados
- Integração com outros sistemas

## 📧 Suporte

Para dúvidas sobre:
- **NF-e**: Consulte a documentação oficial da Receita Federal
- **PostgreSQL**: Documentação em https://www.postgresql.org/docs/
- **Python**: Documentação do psycopg2 em https://www.psycopg.org/

---

**Desenvolvido com base no layout 4.00 da NF-e da Receita Federal do Brasil**
