# Dashboard Analítico de NF-e - Documentação

## Visão Geral

Dashboard analítico desenvolvido para análise de notas fiscais eletrônicas de múltiplas empresas, com foco em movimentações fiscais, tributação e insights operacionais.

**Importante**: Este dashboard analisa notas fiscais de diversos emissores e destinatários, portanto as métricas representam movimentações fiscais (entradas e saídas), não receitas e custos de uma única empresa.

## Métricas Principais (KPIs)

### 1. Total de Notas 📄
- **Métrica**: Quantidade total de notas fiscais processadas
- **Insight**: Volume de movimentação fiscal no sistema
- **Cálculo**: COUNT(*) de todas as notas fiscais

### 2. Valor Total 💰
- **Métrica**: Soma de todos os valores das notas fiscais
- **Insight**: Volume financeiro total movimentado
- **Cálculo**: SUM(valor_total_nota) de todas as notas
- **Observação**: Inclui entradas e saídas

### 3. Impostos Totais 🏛️
- **Métrica**: Soma de todos os impostos (ICMS, IPI, PIS, COFINS)
- **Insight**: Carga tributária total nas operações
- **Cálculo**: SUM(valor_icms + valor_ipi + valor_pis + valor_cofins)
- **Percentual**: Impostos / Valor Total × 100

### 4. Ticket Médio 🎯
- **Métrica**: Valor médio por nota fiscal
- **Insight**: Tamanho médio das operações
- **Cálculo**: Valor Total / Quantidade de Notas

## Gráficos Analíticos

### 1. Movimentação Fiscal Mensal
**Objetivo**: Visualizar fluxo de notas de entrada e saída

**Linhas**:
- Notas de Saída (verde): Operações de saída (tipo_operacao = '1')
- Notas de Entrada (azul): Operações de entrada (tipo_operacao = '0')

**Insights**:
- Proporção entre entradas e saídas
- Sazonalidade nas operações
- Padrões de movimentação fiscal

**Estatísticas**:
- Quantidade de entradas vs saídas
- Equilíbrio operacional

### 2. Evolução de Movimentação
**Objetivo**: Acompanhar tendências de volume

**Métricas derivadas**:
- Taxa de variação mensal
- Comparação de períodos
- Identificação de sazonalidade

**Alertas**:
- 📈 Variação > 5%/mês: Volume crescente
- ➡️ Variação 0-5%/mês: Volume estável
- 📉 Variação negativa: Volume decrescente

### 3. Composição Tributária (Priority: CFO)
**Objetivo**: Visualizar distribuição de impostos

**Impostos monitorados**:
- ICMS (maior impacto)
- IPI (produtos industrializados)
- PIS/COFINS (federais)

**Ações**:
- Identificar oportunidades de crédito tributário
- Avaliar regime tributário (Simples, Lucro Real, Presumido)
- Planejamento tributário estratégico

### 4. Top 5 Empresas por Movimentação
**Objetivo**: Identificar principais participantes

**Métricas por empresa**:
- Valor total movimentado
- Quantidade de notas
- Ticket médio

**Insights**:
- Empresas com maior volume de operações
- Padrões de movimentação
- Análise de concentração

**Observação**: Baseado em notas de saída (destinatários)

### 5. Top 5 Produtos por Valor
**Objetivo**: Análise de produtos mais movimentados

**Análise**:
- Produtos com maior valor total
- Volume de transações
- Relevância no conjunto de dados

## Insights Analíticos Automatizados

### 1. Distribuição de Operações
**Cálculo**: Quantidade de entradas vs saídas

**Interpretação**:
- 📤 Mais saídas: Predominância de operações de saída
- 📥 Mais entradas: Predominância de operações de entrada
- ⚖️ Equilíbrio: Distribuição balanceada

**Análise**:
- Identificar padrões operacionais
- Entender fluxo de mercadorias
- Detectar anomalias

### 2. Carga Tributária
**Cálculo**: Impostos totais / Valor total × 100

**Interpretação**:
- < 25%: ✅ Carga baixa
- 25-35%: ⚠️ Dentro da média brasileira
- > 35%: 🚨 Carga elevada

**Observações**:
- Varia por setor e regime tributário
- Inclui ICMS, IPI, PIS e COFINS
- Base para análise de eficiência fiscal

### 3. Tendência de Volume
**Cálculo**: Média móvel 3 meses vs. 3 meses anteriores

**Interpretação**:
- > 5%: 📈 Volume crescente
- 0-5%: ➡️ Volume estável
- < 0%: 📉 Volume decrescente

**Análise**:
- Identificar tendências de mercado
- Sazonalidade nas operações
- Padrões de crescimento ou retração

## Tecnologias Utilizadas

- **Chart.js**: Biblioteca de gráficos responsivos
- **Vue 3**: Framework reativo
- **Tailwind CSS + DaisyUI**: Design system
- **Supabase**: Backend e queries otimizadas

## Queries Otimizadas

Todas as queries foram otimizadas para:
- Minimizar chamadas ao banco
- Agregar dados no cliente quando possível
- Usar índices existentes (data_emissao, tipo_operacao)
- Carregar dados em paralelo (Promise.all)

## Próximas Melhorias

1. **Filtros de período**: Permitir análise por trimestre/ano
2. **Comparativo YoY**: Comparar com ano anterior
3. **Previsões**: Machine learning para projeções
4. **Alertas automáticos**: Notificações de anomalias
5. **Export para PDF**: Relatórios executivos
6. **Drill-down**: Detalhamento de métricas
7. **Benchmarking**: Comparação com mercado

## Uso Recomendado

### CEO
- Foco: Receita Total, Crescimento, Top Clientes
- Frequência: Diária/Semanal
- Decisões: Estratégia, investimentos, expansão

### CFO
- Foco: Fluxo de Caixa, Margem, Carga Tributária
- Frequência: Diária
- Decisões: Financeiro, tributário, custos

### COO
- Foco: Eficiência operacional, produtos, clientes
- Frequência: Semanal
- Decisões: Processos, qualidade, produtividade

### Comercial
- Foco: Top Clientes, Top Produtos, Ticket Médio
- Frequência: Diária/Semanal
- Decisões: Vendas, precificação, relacionamento
