<template>
  <div class="p-6 bg-base-100 min-h-screen">
    <!-- Header Executivo -->
    <div class="mb-8 pb-6 border-b-2 border-base-300">
      <h1 class="text-4xl font-bold mb-2 text-base-content">Dashboard Executivo</h1>
      <p class="text-base-content/70 text-lg">Visão estratégica do negócio em tempo real</p>
    </div>
    
    <div v-if="loading" class="flex justify-center items-center h-96">
      <span class="loading loading-spinner loading-lg"></span>
    </div>
    
    <div v-else>
      <!-- Insights Analíticos - Movido para o topo -->
      <div class="card bg-gradient-to-br from-slate-700 to-slate-900 text-white p-6 shadow-xl mb-8">
        <h2 class="text-2xl font-bold mb-4 flex items-center gap-2">
          <span>💡</span>
          <span>Insights Estratégicos</span>
        </h2>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div class="p-5 bg-white/10 rounded-xl backdrop-blur border border-white/20 hover:bg-white/15 transition-all hover:scale-105 cursor-pointer">
            <div class="flex items-center gap-3 mb-3">
              <div class="text-3xl">⚖️</div>
              <h3 class="font-bold text-lg">Distribuição de Operações</h3>
            </div>
            <p class="text-sm opacity-95 leading-relaxed">
              <span class="font-bold text-xl">{{ operationStats.entrada }}</span> entradas e 
              <span class="font-bold text-xl">{{ operationStats.saida }}</span> saídas
            </p>
            <p class="text-xs mt-2 opacity-80">
              {{ operationBalance > 0 ? '📤 Mais saídas que entradas' : operationBalance < 0 ? '📥 Mais entradas que saídas' : '⚖️ Equilíbrio perfeito' }}
            </p>
          </div>
          <div class="p-5 bg-white/10 rounded-xl backdrop-blur border border-white/20 hover:bg-white/15 transition-all hover:scale-105 cursor-pointer">
            <div class="flex items-center gap-3 mb-3">
              <div class="text-3xl">🏛️</div>
              <h3 class="font-bold text-lg">Carga Tributária</h3>
            </div>
            <p class="text-sm opacity-95 leading-relaxed">
              Impostos representam <span class="font-bold text-xl">{{ taxMetrics.percentage }}%</span> do valor total
            </p>
            <p class="text-xs mt-2 opacity-80">
              {{ taxMetrics.percentage > 30 ? '⚠️ Carga elevada - avaliar planejamento' : '✅ Dentro da média brasileira' }}
            </p>
          </div>
          <div class="p-5 bg-white/10 rounded-xl backdrop-blur border border-white/20 hover:bg-white/15 transition-all hover:scale-105 cursor-pointer">
            <div class="flex items-center gap-3 mb-3">
              <div class="text-3xl">📊</div>
              <h3 class="font-bold text-lg">Tendência de Volume</h3>
            </div>
            <p class="text-sm opacity-95 leading-relaxed">
              Variação de <span class="font-bold text-xl" :class="growthRate >= 0 ? 'text-green-300' : 'text-red-300'">{{ growthRate >= 0 ? '+' : '' }}{{ growthRate.toFixed(1) }}%</span> ao mês
            </p>
            <p class="text-xs mt-2 opacity-80">
              {{ growthRate > 5 ? '🚀 Volume crescente acelerado' : growthRate > 0 ? '📈 Crescimento estável' : '📉 Atenção à queda' }}
            </p>
          </div>
        </div>
      </div>

      <!-- KPIs Principais -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <div class="card bg-gradient-to-br from-blue-600 to-blue-800 text-white p-6 shadow-xl">
          <div class="flex items-center justify-between">
            <div>
              <h2 class="text-sm font-bold uppercase tracking-wide">Total de Notas</h2>
              <p class="text-4xl font-bold mt-2 drop-shadow-lg">{{ stats.totalNotas }}</p>
              <p class="text-xs mt-2 font-medium">Notas fiscais processadas</p>
            </div>
            <div class="text-6xl opacity-20">📄</div>
          </div>
        </div>
        
        <div class="card bg-gradient-to-br from-green-600 to-green-800 text-white p-6 shadow-xl">
          <div class="flex items-center justify-between">
            <div>
              <h2 class="text-sm font-bold uppercase tracking-wide">Valor Total</h2>
              <p class="text-4xl font-bold mt-2 drop-shadow-lg">R$ {{ formatCurrency(stats.valorTotal) }}</p>
              <p class="text-xs mt-2 font-medium">Movimentação total</p>
            </div>
            <div class="text-6xl opacity-20">💰</div>
          </div>
        </div>

        <div class="card bg-gradient-to-br from-amber-600 to-amber-800 text-white p-6 shadow-xl">
          <div class="flex items-center justify-between">
            <div>
              <h2 class="text-sm font-bold uppercase tracking-wide">Impostos Totais</h2>
              <p class="text-4xl font-bold mt-2 drop-shadow-lg">R$ {{ formatCurrency(taxMetrics.total) }}</p>
              <p class="text-xs mt-2 font-medium">{{ taxMetrics.percentage }}% do total</p>
            </div>
            <div class="text-6xl opacity-20">🏛️</div>
          </div>
        </div>

        <div class="card bg-gradient-to-br from-cyan-600 to-cyan-800 text-white p-6 shadow-xl">
          <div class="flex items-center justify-between">
            <div>
              <h2 class="text-sm font-bold uppercase tracking-wide">Ticket Médio</h2>
              <p class="text-4xl font-bold mt-2 drop-shadow-lg">R$ {{ formatCurrency(averageTicket) }}</p>
              <p class="text-xs mt-2 font-medium">Por nota fiscal</p>
            </div>
            <div class="text-6xl opacity-20">🎯</div>
          </div>
        </div>
      </div>

      <!-- Movimentação Fiscal Mensal -->
      <div class="card bg-base-200 p-6 shadow-xl mb-8">
        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
          <div>
            <div class="flex items-center gap-2 mb-1">
              <span class="text-2xl">📊</span>
              <h2 class="text-2xl font-bold">Movimentação Fiscal Mensal</h2>
            </div>
            <p class="text-sm text-base-content/60">Análise de entradas e saídas de notas fiscais</p>
          </div>
          <div class="flex gap-4">
            <div class="px-4 py-2 bg-info/10 rounded-lg border-2 border-info/30">
              <div class="text-xs font-semibold text-info uppercase">Entradas</div>
              <div class="text-2xl font-bold text-info">{{ operationStats.entrada }}</div>
            </div>
            <div class="px-4 py-2 bg-success/10 rounded-lg border-2 border-success/30">
              <div class="text-xs font-semibold text-success uppercase">Saídas</div>
              <div class="text-2xl font-bold text-success">{{ operationStats.saida }}</div>
            </div>
          </div>
        </div>
        <div class="h-64">
          <LineChart 
            v-if="cashFlowData.length > 0"
            :labels="cashFlowLabels"
            :datasets="movementDatasets"
            title=""
          />
          <div v-else class="text-center py-8 text-base-content/50">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto mb-2 opacity-30" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            Sem dados disponíveis
          </div>
        </div>
      </div>

      <!-- Análise de Movimentação e Tributação -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <!-- Evolução de Movimentação -->
        <div class="card bg-base-200 p-6 shadow-xl">
          <div class="flex items-center gap-2 mb-4">
            <span class="text-xl">📈</span>
            <h2 class="text-xl font-bold">Evolução de Movimentação</h2>
          </div>
          <div class="h-48">
            <LineChart 
              v-if="monthlyData.length > 0"
              :labels="monthlyLabels"
              :datasets="movementEvolutionDatasets"
              title=""
            />
            <div v-else class="text-center py-8 text-base-content/50">
              Sem dados disponíveis
            </div>
          </div>
          <div class="mt-4 p-4 bg-gradient-to-r from-base-300 to-base-200 rounded-lg border-l-4" :class="growthRate >= 0 ? 'border-success' : 'border-error'">
            <p class="text-xs font-semibold text-base-content/70 uppercase tracking-wide">Variação Média Mensal</p>
            <p class="text-3xl font-bold mt-1" :class="growthRate >= 0 ? 'text-success' : 'text-error'">
              {{ growthRate >= 0 ? '+' : '' }}{{ growthRate.toFixed(1) }}%
            </p>
          </div>
        </div>

        <!-- Composição Tributária -->
        <div class="card bg-base-200 p-6 shadow-xl">
          <div class="flex items-center gap-2 mb-4">
            <span class="text-xl">🏛️</span>
            <h2 class="text-xl font-bold">Composição Tributária</h2>
          </div>
          <div class="h-48 flex items-center justify-center">
            <DoughnutChart 
              v-if="taxData.length > 0"
              :labels="taxLabels"
              :data="taxValues"
              title=""
            />
            <div v-else class="text-center py-8 text-base-content/50">
              Sem dados disponíveis
            </div>
          </div>
          <div class="mt-4 grid grid-cols-2 gap-2">
            <div v-for="tax in taxData" :key="tax.tipo" class="p-3 bg-base-300 rounded-lg hover:bg-base-100 transition-colors">
              <p class="text-xs font-semibold text-base-content/70 uppercase">{{ tax.tipo }}</p>
              <p class="text-lg font-bold text-warning">R$ {{ formatCurrency(tax.valor) }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Top Empresas e Produtos -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <!-- Top 5 Empresas por Movimentação -->
        <div class="card bg-base-200 p-6 shadow-xl">
          <div class="flex items-center gap-2 mb-4">
            <span class="text-2xl">🏢</span>
            <h2 class="text-xl font-bold">Top 5 Empresas</h2>
          </div>
          <div v-if="topCustomers.length > 0" class="space-y-2">
            <div v-for="(customer, index) in topCustomers" :key="index" 
                 class="flex items-center justify-between p-4 bg-base-300 rounded-lg hover:bg-base-100 transition-all hover:shadow-md group">
              <div class="flex items-center gap-4 flex-1">
                <div class="flex items-center justify-center w-8 h-8 rounded-full bg-primary/20 text-primary font-bold text-sm group-hover:bg-primary group-hover:text-primary-content transition-colors">
                  {{ index + 1 }}
                </div>
                <div class="flex-1">
                  <p class="font-bold text-base group-hover:text-primary transition-colors">{{ customer.razao_social }}</p>
                  <p class="text-xs text-base-content/60 mt-1">
                    <span class="inline-flex items-center gap-1">
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                      {{ customer.quantidade_notas }} notas
                    </span>
                  </p>
                </div>
              </div>
              <div class="text-right">
                <p class="font-bold text-lg text-success">R$ {{ formatCurrency(customer.total_compras) }}</p>
              </div>
            </div>
          </div>
          <div v-else class="text-center py-8 text-base-content/50">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto mb-2 opacity-30" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
            </svg>
            Sem dados disponíveis
          </div>
        </div>

        <!-- Top 5 Produtos por Valor -->
        <div class="card bg-base-200 p-6 shadow-xl">
          <div class="flex items-center gap-2 mb-4">
            <span class="text-2xl">📦</span>
            <h2 class="text-xl font-bold">Top 5 Produtos</h2>
          </div>
          <div class="h-64">
            <BarChart 
              v-if="topProducts.length > 0"
              :labels="topProductLabels"
              :datasets="topProductDatasets"
              title=""
            />
            <div v-else class="text-center py-8 text-base-content/50">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto mb-2 opacity-30" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
              </svg>
              Sem dados disponíveis
            </div>
          </div>
        </div>
      </div>


    </div>
  </div>
</template>

<script setup>
const { 
  getDashboardStats, 
  getMonthlyData, 
  getTopProducts, 
  getOperationTypeData,
  getTaxData,
  getTopCustomers,
  getCashFlowData
} = useSupabase()

const loading = ref(true)
const stats = ref({ totalNotas: 0, valorTotal: 0 })
const monthlyData = ref([])
const topProducts = ref([])
const operationTypeData = ref([])
const taxData = ref([])
const topCustomers = ref([])
const cashFlowData = ref([])

// KPIs e Métricas
const operationStats = computed(() => {
  const entradaItem = operationTypeData.value.find(d => d.tipo === 'Entrada')
  const saidaItem = operationTypeData.value.find(d => d.tipo === 'Saída')
  const entrada = entradaItem ? entradaItem.quantidade : 0
  const saida = saidaItem ? saidaItem.quantidade : 0
  return { entrada, saida }
})

const operationBalance = computed(() => {
  return operationStats.value.saida - operationStats.value.entrada
})

const averageTicket = computed(() => {
  return stats.value.totalNotas > 0 
    ? stats.value.valorTotal / stats.value.totalNotas 
    : 0
})

const taxMetrics = computed(() => {
  const total = taxData.value.reduce((sum, t) => sum + t.valor, 0)
  const percentage = stats.value.valorTotal > 0 
    ? (total / stats.value.valorTotal) * 100 
    : 0
  
  return {
    total,
    percentage: percentage.toFixed(1)
  }
})

const growthRate = computed(() => {
  if (monthlyData.value.length < 2) return 0
  
  const recent = monthlyData.value.slice(-3).map(m => m.valor)
  const older = monthlyData.value.slice(-6, -3).map(m => m.valor)
  
  const recentAvg = recent.reduce((sum, v) => sum + v, 0) / recent.length
  const olderAvg = older.length > 0 
    ? older.reduce((sum, v) => sum + v, 0) / older.length 
    : recentAvg
  
  return olderAvg > 0 ? ((recentAvg - olderAvg) / olderAvg) * 100 : 0
})

// Labels e Datasets
const monthlyLabels = computed(() => {
  return monthlyData.value.map(d => {
    const [year, month] = d.mes.split('-')
    const monthNames = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
    return `${monthNames[parseInt(month) - 1]}/${year.slice(2)}`
  })
})

const movementEvolutionDatasets = computed(() => [{
  label: 'Valor Total (R$)',
  data: monthlyData.value.map(d => d.valor),
  borderColor: 'rgb(59, 130, 246)',
  backgroundColor: 'rgba(59, 130, 246, 0.1)',
  tension: 0.4,
  fill: true,
  borderWidth: 3
}])

const cashFlowLabels = computed(() => {
  return cashFlowData.value.map(d => {
    const [year, month] = d.mes.split('-')
    const monthNames = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
    return `${monthNames[parseInt(month) - 1]}/${year.slice(2)}`
  })
})

const movementDatasets = computed(() => [
  {
    label: 'Notas de Saída (R$)',
    data: cashFlowData.value.map(d => d.saidas),
    borderColor: 'rgb(34, 197, 94)',
    backgroundColor: 'rgba(34, 197, 94, 0.2)',
    tension: 0.3,
    fill: true
  },
  {
    label: 'Notas de Entrada (R$)',
    data: cashFlowData.value.map(d => d.entradas),
    borderColor: 'rgb(59, 130, 246)',
    backgroundColor: 'rgba(59, 130, 246, 0.2)',
    tension: 0.3,
    fill: true
  }
])

const topProductLabels = computed(() => {
  return topProducts.value.map(p => {
    const desc = p.descricao || 'Sem descrição'
    return desc.length > 25 ? desc.substring(0, 25) + '...' : desc
  })
})

const topProductDatasets = computed(() => [{
  label: 'Valor Total (R$)',
  data: topProducts.value.map(p => p.valor_total),
  backgroundColor: [
    'rgba(59, 130, 246, 0.8)',
    'rgba(34, 197, 94, 0.8)',
    'rgba(251, 191, 36, 0.8)',
    'rgba(168, 85, 247, 0.8)',
    'rgba(236, 72, 153, 0.8)'
  ],
  borderWidth: 0
}])

const taxLabels = computed(() => taxData.value.map(t => t.tipo))
const taxValues = computed(() => taxData.value.map(t => t.valor))

onMounted(async () => {
  try {
    const [statsData, monthly, products, operations, taxes, customers, cashFlow] = await Promise.all([
      getDashboardStats(),
      getMonthlyData(),
      getTopProducts(5),
      getOperationTypeData(),
      getTaxData(),
      getTopCustomers(5),
      getCashFlowData()
    ])
    
    stats.value = statsData
    monthlyData.value = monthly
    topProducts.value = products
    operationTypeData.value = operations
    taxData.value = taxes
    topCustomers.value = customers
    cashFlowData.value = cashFlow
  } catch (error) {
    console.error('Erro ao carregar dados:', error)
    alert('Erro ao carregar estatísticas do dashboard')
  } finally {
    loading.value = false
  }
})

const formatCurrency = (value) => {
  return new Intl.NumberFormat('pt-BR', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(value)
}
</script>
