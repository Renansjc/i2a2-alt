<template>
  <div class="min-h-screen bg-gradient-to-br from-base-100 to-base-200">
    <div v-if="loading" class="flex justify-center items-center h-96">
      <span class="loading loading-spinner loading-lg"></span>
    </div>

    <div v-else-if="invoice" class="max-w-7xl mx-auto p-4 md:p-6">
      <!-- Header com Breadcrumb e Ações -->
      <div class="mb-6">
        <div class="text-sm breadcrumbs mb-4">
          <ul>
            <li><NuxtLink to="/" class="hover:text-primary">Dashboard</NuxtLink></li>
            <li><NuxtLink to="/invoices" class="hover:text-primary">Notas Fiscais</NuxtLink></li>
            <li class="font-semibold">NF-e {{ invoice.numero_nf }}</li>
          </ul>
        </div>
        
        <div class="flex items-center gap-3 mb-2">
          <h1 class="text-3xl md:text-4xl font-bold">NF-e #{{ invoice.numero_nf }}</h1>
          <div class="badge badge-lg" :class="getStatusBadgeClass(invoice.status)">
            {{ formatStatus(invoice.status) }}
          </div>
        </div>
        <p class="text-base-content/60 text-sm md:text-base">
          Série {{ invoice.serie }} • {{ invoice.natureza_operacao }}
        </p>
      </div>

      <!-- Cards de Informações Principais -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div class="stats shadow-lg bg-gradient-to-br from-blue-600 to-blue-700">
          <div class="stat text-white">
            <div class="stat-figure text-white/30">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div class="stat-title text-white/80 text-xs">Valor Total</div>
            <div class="stat-value text-2xl">R$ {{ formatCurrency(invoice.valor_total_nota) }}</div>
            <div class="stat-desc text-white/70">{{ items.length }} itens</div>
          </div>
        </div>

        <div class="stats shadow-lg bg-gradient-to-br from-amber-600 to-amber-700">
          <div class="stat text-white">
            <div class="stat-figure text-white/30">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
              </svg>
            </div>
            <div class="stat-title text-white/80 text-xs">Impostos</div>
            <div class="stat-value text-2xl">R$ {{ formatCurrency(totalImpostos) }}</div>
            <div class="stat-desc text-white/70">{{ percentualImpostos }}% do total</div>
          </div>
        </div>

        <div class="stats shadow-lg bg-gradient-to-br from-green-600 to-green-700">
          <div class="stat text-white">
            <div class="stat-figure text-white/30">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </div>
            <div class="stat-title text-white/80 text-xs">Emissão</div>
            <div class="stat-value text-xl">{{ formatDate(invoice.data_hora_emissao) }}</div>
            <div class="stat-desc text-white/70">{{ formatTime(invoice.data_hora_emissao) }}</div>
          </div>
        </div>

        <div class="stats shadow-lg bg-gradient-to-br from-purple-600 to-purple-700">
          <div class="stat text-white">
            <div class="stat-figure text-white/30">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
              </svg>
            </div>
            <div class="stat-title text-white/80 text-xs">Produtos</div>
            <div class="stat-value text-2xl">R$ {{ formatCurrency(invoice.valor_total_produtos) }}</div>
            <div class="stat-desc text-white/70">Base de cálculo</div>
          </div>
        </div>
      </div>

      <!-- Tabs de Navegação -->
      <div class="card bg-base-100 shadow-xl mb-6">
        <div class="card-body p-0">
          <div role="tablist" class="tabs tabs-boxed tabs-lg bg-base-200 p-2 mb-0 gap-2">
            <button 
              @click="activeTab = 'geral'" 
              :class="['tab text-base font-semibold px-6', activeTab === 'geral' ? 'tab-active' : '']"
            >
              Geral
            </button>
            <button 
              @click="activeTab = 'itens'" 
              :class="['tab text-base font-semibold px-6', activeTab === 'itens' ? 'tab-active' : '']"
            >
              Itens
            </button>
            <button 
              @click="activeTab = 'complementares'" 
              :class="['tab text-base font-semibold px-6', activeTab === 'complementares' ? 'tab-active' : '']"
            >
              Complementares
            </button>
          </div>
          
          <div class="p-6">
            <!-- Tab Geral -->
            <div v-show="activeTab === 'geral'">
              <!-- Informações Gerais -->
              <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <!-- Emitente -->
                <div class="card bg-base-200/50 border border-base-300">
                  <div class="card-body">
                    <h3 class="flex items-center gap-2 font-bold text-lg mb-4">
                      <div class="badge badge-primary badge-sm">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                        </svg>
                      </div>
                      Emitente
                    </h3>
                    <div v-if="invoice.emitente" class="space-y-3">
                      <div>
                        <p class="font-bold text-lg">{{ invoice.emitente.razao_social || invoice.emitente.nome_fantasia }}</p>
                        <p class="text-sm text-base-content/60">{{ formatCnpjCpf(invoice.emitente.cpf_cnpj) }}</p>
                      </div>
                      
                      <div class="divider my-2"></div>
                      
                      <div class="grid grid-cols-2 gap-3 text-sm">
                        <div v-if="invoice.emitente.inscricao_estadual">
                          <p class="text-base-content/60">IE</p>
                          <p class="font-semibold">{{ invoice.emitente.inscricao_estadual }}</p>
                        </div>
                        <div v-if="invoice.emitente.uf">
                          <p class="text-base-content/60">UF</p>
                          <p class="font-semibold">{{ invoice.emitente.uf }}</p>
                        </div>
                      </div>
                      
                      <div v-if="invoice.emitente.logradouro" class="text-sm">
                        <p class="text-base-content/60 mb-1">Endereço</p>
                        <p>{{ invoice.emitente.logradouro }}, {{ invoice.emitente.numero }}</p>
                        <p>{{ invoice.emitente.bairro }}</p>
                        <p>{{ invoice.emitente.nome_municipio }}/{{ invoice.emitente.uf }} - CEP {{ formatCep(invoice.emitente.cep) }}</p>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Destinatário -->
                <div class="card bg-base-200/50 border border-base-300">
                  <div class="card-body">
                    <h3 class="flex items-center gap-2 font-bold text-lg mb-4">
                      <div class="badge badge-success badge-sm">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                        </svg>
                      </div>
                      Destinatário
                    </h3>
                    <div v-if="invoice.destinatario" class="space-y-3">
                      <div>
                        <p class="font-bold text-lg">{{ invoice.destinatario.razao_social || invoice.destinatario.nome_fantasia }}</p>
                        <p class="text-sm text-base-content/60">{{ formatCnpjCpf(invoice.destinatario.cpf_cnpj) }}</p>
                      </div>
                      
                      <div class="divider my-2"></div>
                      
                      <div class="grid grid-cols-2 gap-3 text-sm">
                        <div v-if="invoice.destinatario.inscricao_estadual">
                          <p class="text-base-content/60">IE</p>
                          <p class="font-semibold">{{ invoice.destinatario.inscricao_estadual }}</p>
                        </div>
                        <div v-if="invoice.destinatario.uf">
                          <p class="text-base-content/60">UF</p>
                          <p class="font-semibold">{{ invoice.destinatario.uf }}</p>
                        </div>
                      </div>
                      
                      <div v-if="invoice.destinatario.logradouro" class="text-sm">
                        <p class="text-base-content/60 mb-1">Endereço</p>
                        <p>{{ invoice.destinatario.logradouro }}, {{ invoice.destinatario.numero }}</p>
                        <p>{{ invoice.destinatario.bairro }}</p>
                        <p>{{ invoice.destinatario.nome_municipio }}/{{ invoice.destinatario.uf }} - CEP {{ formatCep(invoice.destinatario.cep) }}</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>



              <!-- Detalhes Fiscais e Totalizadores -->
              <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
                <!-- Informações Fiscais -->
                <div class="card bg-base-200/50 border border-base-300">
                  <div class="card-body">
                    <h3 class="flex items-center gap-2 font-bold text-lg mb-4">
                      <div class="badge badge-info badge-sm">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                      </div>
                      Informações Fiscais
                    </h3>
                    <div class="space-y-3 text-sm">
                      <div>
                        <p class="text-base-content/60 mb-1">Chave de Acesso</p>
                        <div class="flex items-center gap-2">
                          <p class="font-mono text-xs bg-base-300 p-2 rounded flex-1 break-all">{{ invoice.chave_acesso }}</p>
                          <button class="btn btn-square btn-sm btn-ghost" title="Copiar">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                            </svg>
                          </button>
                        </div>
                      </div>
                      <div class="grid grid-cols-2 gap-3">
                        <div>
                          <p class="text-base-content/60">Modelo</p>
                          <p class="font-semibold">{{ invoice.modelo === '55' ? 'NF-e' : 'NFC-e' }}</p>
                        </div>
                        <div>
                          <p class="text-base-content/60">Tipo</p>
                          <p class="font-semibold">{{ invoice.tipo_operacao === '0' ? 'Entrada' : 'Saída' }}</p>
                        </div>
                        <div>
                          <p class="text-base-content/60">Finalidade</p>
                          <p class="font-semibold">{{ getFinalidade(invoice.finalidade_emissao) }}</p>
                        </div>
                        <div>
                          <p class="text-base-content/60">Natureza</p>
                          <p class="font-semibold">{{ invoice.natureza_operacao }}</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Totalizadores -->
                <div class="card bg-base-200/50 border border-base-300">
                  <div class="card-body">
                    <h3 class="flex items-center gap-2 font-bold text-lg mb-4">
                      <div class="badge badge-warning badge-sm">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                      </div>
                      Valores e Impostos
                    </h3>
                    <div class="space-y-2 text-sm">
                      <div class="flex justify-between items-center p-2 bg-base-300/50 rounded">
                        <span class="text-base-content/70">Produtos</span>
                        <span class="font-bold">R$ {{ formatCurrency(invoice.valor_total_produtos) }}</span>
                      </div>
                      <div class="flex justify-between items-center p-2 rounded">
                        <span class="text-base-content/70">Frete</span>
                        <span class="font-semibold">R$ {{ formatCurrency(invoice.valor_frete) }}</span>
                      </div>
                      <div class="flex justify-between items-center p-2 rounded">
                        <span class="text-base-content/70">Desconto</span>
                        <span class="font-semibold text-success">- R$ {{ formatCurrency(invoice.valor_desconto) }}</span>
                      </div>
                      <div class="flex justify-between items-center p-2 rounded">
                        <span class="text-base-content/70">Outras Despesas</span>
                        <span class="font-semibold">R$ {{ formatCurrency(invoice.valor_outras_despesas) }}</span>
                      </div>
                      
                      <div class="divider my-1">Impostos</div>
                      
                      <div class="grid grid-cols-2 gap-2">
                        <div class="p-2 bg-warning/10 rounded border border-warning/20">
                          <p class="text-xs text-warning/80">ICMS</p>
                          <p class="font-bold text-warning">R$ {{ formatCurrency(invoice.valor_icms) }}</p>
                        </div>
                        <div class="p-2 bg-warning/10 rounded border border-warning/20">
                          <p class="text-xs text-warning/80">IPI</p>
                          <p class="font-bold text-warning">R$ {{ formatCurrency(invoice.valor_ipi) }}</p>
                        </div>
                        <div class="p-2 bg-warning/10 rounded border border-warning/20">
                          <p class="text-xs text-warning/80">PIS</p>
                          <p class="font-bold text-warning">R$ {{ formatCurrency(invoice.valor_pis) }}</p>
                        </div>
                        <div class="p-2 bg-warning/10 rounded border border-warning/20">
                          <p class="text-xs text-warning/80">COFINS</p>
                          <p class="font-bold text-warning">R$ {{ formatCurrency(invoice.valor_cofins) }}</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Tab Itens -->
            <div v-show="activeTab === 'itens'">
              <!-- Itens da Nota -->
              <div v-if="loadingItems" class="flex justify-center py-12">
                <span class="loading loading-spinner loading-lg"></span>
              </div>

              <div v-else-if="items.length > 0">
                <div class="flex items-center justify-between mb-4">
                  <h3 class="font-bold text-lg">{{ items.length }} {{ items.length === 1 ? 'Item' : 'Itens' }}</h3>
                  <div class="text-sm text-base-content/60">
                    Total: <span class="font-bold text-success text-lg">R$ {{ formatCurrency(totalItens) }}</span>
                  </div>
                </div>

                <!-- Mobile: Cards -->
                <div class="lg:hidden space-y-3">
                  <div v-for="item in items" :key="item.id" class="card bg-base-200/50 border border-base-300">
                    <div class="card-body p-4">
                      <div class="flex justify-between items-start mb-2">
                        <div class="badge badge-neutral badge-sm">Item {{ item.numero_item }}</div>
                        <div class="text-right">
                          <div class="font-bold text-success">R$ {{ formatCurrency(item.valor_total_bruto) }}</div>
                          <div class="text-xs text-base-content/60">{{ formatQuantity(item.quantidade_comercial) }} {{ item.unidade_comercial }}</div>
                        </div>
                      </div>
                      <h4 class="font-bold">{{ item.descricao }}</h4>
                      <div class="grid grid-cols-2 gap-2 text-xs mt-2">
                        <div>
                          <span class="text-base-content/60">Código:</span>
                          <span class="font-mono ml-1">{{ item.codigo_produto }}</span>
                        </div>
                        <div>
                          <span class="text-base-content/60">NCM:</span>
                          <span class="font-mono ml-1">{{ item.ncm }}</span>
                        </div>
                        <div>
                          <span class="text-base-content/60">CFOP:</span>
                          <span class="font-mono ml-1">{{ item.cfop }}</span>
                        </div>
                        <div>
                          <span class="text-base-content/60">Unit:</span>
                          <span class="ml-1">R$ {{ formatCurrency(item.valor_unitario_comercial) }}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Desktop: Table -->
                <div class="hidden lg:block overflow-x-auto">
                  <table class="table table-zebra">
                    <thead>
                      <tr class="bg-base-200">
                        <th class="w-12">#</th>
                        <th>Produto</th>
                        <th class="text-center">NCM</th>
                        <th class="text-center">CFOP</th>
                        <th class="text-right">Quantidade</th>
                        <th class="text-right">Valor Unit.</th>
                        <th class="text-right">Total</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="item in items" :key="item.id" class="hover">
                        <td class="font-bold text-base-content/60">{{ item.numero_item }}</td>
                        <td>
                          <div class="font-semibold">{{ item.descricao }}</div>
                          <div class="text-xs text-base-content/60 font-mono">{{ item.codigo_produto }}</div>
                        </td>
                        <td class="text-center font-mono text-sm">{{ item.ncm }}</td>
                        <td class="text-center font-mono text-sm">{{ item.cfop }}</td>
                        <td class="text-right">
                          <div>{{ formatQuantity(item.quantidade_comercial) }}</div>
                          <div class="text-xs text-base-content/60">{{ item.unidade_comercial }}</div>
                        </td>
                        <td class="text-right font-semibold">R$ {{ formatCurrency(item.valor_unitario_comercial) }}</td>
                        <td class="text-right font-bold text-success text-lg">R$ {{ formatCurrency(item.valor_total_bruto) }}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>

              <div v-else class="text-center py-12">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto mb-4 text-base-content/20" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
                </svg>
                <p class="text-base-content/50">Nenhum item encontrado</p>
              </div>
            </div>

            <!-- Tab Complementares -->
            <div v-show="activeTab === 'complementares'">
              <!-- Informações Complementares -->
              <div v-if="invoice.informacoes_complementares">
                <h3 class="font-bold text-lg mb-4">Informações Complementares</h3>
                <div class="card bg-base-200/50 border border-base-300">
                  <div class="card-body">
                    <p class="whitespace-pre-wrap text-sm leading-relaxed">{{ invoice.informacoes_complementares }}</p>
                  </div>
                </div>
              </div>
              <div v-else class="text-center py-12">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto mb-4 text-base-content/20" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <p class="text-base-content/50">Nenhuma informação complementar</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="text-center py-20">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto mb-4 text-error" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      <h2 class="text-2xl font-bold mb-2">Nota Fiscal não encontrada</h2>
      <NuxtLink to="/invoices" class="btn btn-primary mt-4">Voltar para Notas Fiscais</NuxtLink>
    </div>
  </div>
</template>

<script setup>
const route = useRoute()
const { getInvoiceDetails, getInvoiceItems } = useSupabase()

const loading = ref(true)
const loadingItems = ref(true)
const invoice = ref(null)
const items = ref([])
const activeTab = ref('geral')

const totalImpostos = computed(() => {
  if (!invoice.value) return 0
  return (invoice.value.valor_icms || 0) + 
         (invoice.value.valor_ipi || 0) + 
         (invoice.value.valor_pis || 0) + 
         (invoice.value.valor_cofins || 0)
})

const percentualImpostos = computed(() => {
  if (!invoice.value || invoice.value.valor_total_nota === 0) return '0.0'
  return ((totalImpostos.value / invoice.value.valor_total_nota) * 100).toFixed(1)
})

const totalItens = computed(() => {
  return items.value.reduce((sum, item) => sum + (item.valor_total_bruto || 0), 0)
})

onMounted(async () => {
  try {
    const id = route.params.id
    invoice.value = await getInvoiceDetails(id)
    
    if (invoice.value) {
      loadingItems.value = true
      items.value = await getInvoiceItems(id)
    }
  } catch (error) {
    console.error('Erro ao carregar nota fiscal:', error)
  } finally {
    loading.value = false
    loadingItems.value = false
  }
})

const formatCurrency = (value) => {
  return new Intl.NumberFormat('pt-BR', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(value || 0)
}

const formatQuantity = (value) => {
  return new Intl.NumberFormat('pt-BR', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 4
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

const formatCnpjCpf = (value) => {
  if (!value) return '-'
  if (value.length === 14) {
    return value.replace(/(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/, '$1.$2.$3/$4-$5')
  } else if (value.length === 11) {
    return value.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4')
  }
  return value
}

const formatCep = (value) => {
  if (!value) return '-'
  return value.replace(/(\d{5})(\d{3})/, '$1-$2')
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

const getFinalidade = (finalidade) => {
  const map = {
    '1': 'Normal',
    '2': 'Complementar',
    '3': 'Ajuste',
    '4': 'Devolução'
  }
  return map[finalidade] || '-'
}
</script>
