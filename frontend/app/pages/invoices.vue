<template>
  <div class="p-6 min-h-screen bg-gradient-to-br from-base-100 to-base-200">
    <!-- Header -->
    <div class="mb-8">
      <h1 class="text-4xl font-bold mb-2 flex items-center gap-3">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        Notas Fiscais
      </h1>
      <p class="text-base-content/60 text-lg">Visualize e gerencie todas as notas fiscais importadas</p>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
      <div class="card bg-gradient-to-br from-primary to-primary-focus text-primary-content shadow-xl">
        <div class="card-body">
          <div class="flex items-center justify-between">
            <div>
              <h2 class="card-title text-sm opacity-80 uppercase tracking-wide">Total de Notas</h2>
              <p class="text-4xl font-bold mt-2">{{ totalCount.toLocaleString('pt-BR') }}</p>
              <p class="text-sm opacity-70 mt-1">Registros no sistema</p>
            </div>
            <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 opacity-20" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
        </div>
      </div>
      
      <div class="card bg-gradient-to-br from-success to-success-focus text-success-content shadow-xl">
        <div class="card-body">
          <div class="flex items-center justify-between">
            <div>
              <h2 class="card-title text-sm opacity-80 uppercase tracking-wide">Valor Total</h2>
              <p class="text-4xl font-bold mt-2">R$ {{ formatCurrency(totalValue) }}</p>
              <p class="text-sm opacity-70 mt-1">Soma desta página</p>
            </div>
            <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 opacity-20" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
        </div>
      </div>
      
      <div class="card bg-gradient-to-br from-info to-info-focus text-info-content shadow-xl">
        <div class="card-body">
          <div class="flex items-center justify-between">
            <div>
              <h2 class="card-title text-sm opacity-80 uppercase tracking-wide">Navegação</h2>
              <p class="text-4xl font-bold mt-2">{{ currentPage + 1 }} / {{ totalPages }}</p>
              <p class="text-sm opacity-70 mt-1">Páginas disponíveis</p>
            </div>
            <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 opacity-20" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
            </svg>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center items-center py-20">
      <div class="text-center">
        <span class="loading loading-spinner loading-lg text-primary"></span>
        <p class="mt-4 text-lg">Carregando notas fiscais...</p>
      </div>
    </div>
    
    <!-- Table -->
    <div v-else class="card bg-base-100 shadow-2xl border border-base-300">
      <div class="card-body p-0">
        <div class="overflow-x-auto">
          <table class="table">
            <thead class="bg-gradient-to-r from-base-200 to-base-300">
              <tr>
                <th class="w-20 cursor-pointer hover:bg-base-300" @click="sortBy('numero_nf')">
                  <div class="flex items-center gap-1">
                    Número
                    <span class="text-xs opacity-60">{{ getSortIcon('numero_nf') }}</span>
                  </div>
                </th>
                <th class="w-16 cursor-pointer hover:bg-base-300" @click="sortBy('serie')">
                  <div class="flex items-center gap-1">
                    Série
                    <span class="text-xs opacity-60">{{ getSortIcon('serie') }}</span>
                  </div>
                </th>
                <th>Emissor</th>
                <th>Destinatário</th>
                <th class="cursor-pointer hover:bg-base-300" @click="sortBy('natureza_operacao')">
                  <div class="flex items-center gap-1">
                    Natureza
                    <span class="text-xs opacity-60">{{ getSortIcon('natureza_operacao') }}</span>
                  </div>
                </th>
                <th class="w-32 cursor-pointer hover:bg-base-300" @click="sortBy('valor_total_nota')">
                  <div class="flex items-center gap-1">
                    Valor Total
                    <span class="text-xs opacity-60">{{ getSortIcon('valor_total_nota') }}</span>
                  </div>
                </th>
                <th class="w-32 cursor-pointer hover:bg-base-300" @click="sortBy('data_hora_emissao')">
                  <div class="flex items-center gap-1">
                    Data Emissão
                    <span class="text-xs opacity-60">{{ getSortIcon('data_hora_emissao') }}</span>
                  </div>
                </th>
                <th class="w-24 cursor-pointer hover:bg-base-300" @click="sortBy('status')">
                  <div class="flex items-center gap-1">
                    Status
                    <span class="text-xs opacity-60">{{ getSortIcon('status') }}</span>
                  </div>
                </th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="invoice in invoices" :key="invoice.chave_acesso" class="hover">
                <td class="font-semibold">{{ invoice.numero_nf }}</td>
                <td>{{ invoice.serie }}</td>
                <td>
                  <span class="font-medium">{{ truncate(getEmpresaName(invoice.emitente), 35) }}</span>
                </td>
                <td>
                  <span class="font-medium">{{ truncate(getEmpresaName(invoice.destinatario), 35) }}</span>
                </td>
                <td>
                  <span class="text-sm">{{ truncate(invoice.natureza_operacao, 25) }}</span>
                </td>
                <td>
                  <span class="font-bold text-success">R$ {{ formatCurrency(invoice.valor_total_nota) }}</span>
                </td>
                <td>
                  <div class="flex flex-col">
                    <span class="text-sm">{{ formatDate(invoice.data_hora_emissao) }}</span>
                    <span class="text-xs text-base-content/60">{{ formatTime(invoice.data_hora_emissao) }}</span>
                  </div>
                </td>
                <td>
                  <span :class="getStatusBadgeClass(invoice.status)" class="badge badge-sm">
                    {{ formatStatus(invoice.status) }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Pagination -->
        <div class="flex flex-col sm:flex-row justify-between items-center gap-4 p-6 bg-base-200 border-t border-base-300">
          <button 
            @click="previousPage" 
            class="btn btn-outline gap-2"
            :disabled="currentPage === 0"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
            </svg>
            Anterior
          </button>
          
          <div class="flex flex-col items-center gap-1">
            <span class="text-lg font-bold">Página {{ currentPage + 1 }} de {{ totalPages }}</span>
            <span class="text-sm text-base-content/60">{{ totalCount.toLocaleString('pt-BR') }} registros totais</span>
          </div>
          
          <button 
            @click="nextPage" 
            class="btn btn-outline gap-2"
            :disabled="currentPage >= totalPages - 1"
          >
            Próxima
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
const { getInvoices } = useSupabase()
const loading = ref(true)
const invoices = ref([])
const currentPage = ref(0)
const totalCount = ref(0)
const pageSize = 50
const sortColumn = ref('data_hora_emissao')
const sortDirection = ref('desc')

const totalPages = computed(() => Math.ceil(totalCount.value / pageSize))

const totalValue = computed(() => {
  return invoices.value.reduce((sum, invoice) => sum + (invoice.valor_total_nota || 0), 0)
})

const loadInvoices = async () => {
  loading.value = true
  try {
    const { data, count } = await getInvoices(currentPage.value, pageSize, sortColumn.value, sortDirection.value)
    invoices.value = data
    totalCount.value = count
  } catch (error) {
    alert('Erro ao carregar notas fiscais')
  } finally {
    loading.value = false
  }
}

const sortBy = (column) => {
  if (sortColumn.value === column) {
    sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortColumn.value = column
    sortDirection.value = 'asc'
  }
  currentPage.value = 0
  loadInvoices()
}

const getSortIcon = (column) => {
  if (sortColumn.value !== column) return '↕'
  return sortDirection.value === 'asc' ? '↑' : '↓'
}

const nextPage = () => {
  currentPage.value++
  loadInvoices()
}

const previousPage = () => {
  currentPage.value--
  loadInvoices()
}

const formatCurrency = (value) => {
  return new Intl.NumberFormat('pt-BR', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(value || 0)
}

const formatDate = (date) => {
  if (!date) return '-'
  return new Date(date).toLocaleDateString('pt-BR')
}

const formatTime = (date) => {
  if (!date) return '-'
  return new Date(date).toLocaleTimeString('pt-BR', { 
    hour: '2-digit', 
    minute: '2-digit' 
  })
}

const formatStatus = (status) => {
  const statusMap = {
    'emitida': 'Emitida',
    'autorizada': 'Autorizada',
    'cancelada': 'Cancelada',
    'denegada': 'Denegada',
    'rejeitada': 'Rejeitada',
    'inutilizada': 'Inutilizada'
  }
  return statusMap[status] || status
}

const getStatusBadgeClass = (status) => {
  const classMap = {
    'emitida': 'badge-info',
    'autorizada': 'badge-success',
    'cancelada': 'badge-error',
    'denegada': 'badge-warning',
    'rejeitada': 'badge-error',
    'inutilizada': 'badge-ghost'
  }
  return classMap[status] || 'badge-ghost'
}

const truncate = (text, maxLength) => {
  if (!text) return '-'
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}

const getEmpresaName = (empresa) => {
  if (!empresa) return null
  return empresa.nome_fantasia || empresa.razao_social || null
}

onMounted(() => {
  loadInvoices()
})
</script>
