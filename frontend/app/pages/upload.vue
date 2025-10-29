<template>
  <div class="p-6 min-h-screen bg-gradient-to-br from-base-100 to-base-200">
    <!-- Header -->
    <div class="mb-8">
      <h1 class="text-4xl font-bold mb-2 flex items-center gap-3">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
        </svg>
        Importação de NF-e
      </h1>
      <p class="text-base-content/60 text-lg">Faça upload de arquivos XML para processar notas fiscais eletrônicas</p>
    </div>
    
    <!-- Upload Card -->
    <div class="card bg-base-100 shadow-2xl mb-8 border border-base-300">
      <div class="card-body">
        <h2 class="card-title text-2xl mb-4">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          Selecionar Arquivos
        </h2>
        
        <div class="form-control">
          <label class="label">
            <span class="label-text font-semibold">Arquivos XML de NF-e</span>
            <span class="label-text-alt text-base-content/60">Múltiplos arquivos permitidos</span>
          </label>
          
          <!-- Drop Zone -->
          <div 
            @drop.prevent="handleDrop"
            @dragover.prevent="isDragging = true"
            @dragleave.prevent="isDragging = false"
            :class="[
              'border-2 border-dashed rounded-lg p-8 text-center transition-all cursor-pointer',
              isDragging ? 'border-primary bg-primary/10' : 'border-base-300 hover:border-primary/50 hover:bg-base-200'
            ]"
            @click="$refs.fileInput.click()"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto mb-4 text-base-content/40" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
            <p class="text-lg font-semibold mb-2">Arraste arquivos XML aqui</p>
            <p class="text-sm text-base-content/60 mb-4">ou clique para selecionar</p>
            <input 
              ref="fileInput"
              type="file" 
              multiple 
              accept=".xml"
              @change="handleFileSelect"
              class="hidden"
            />
          </div>
          
          <!-- Selected Files List -->
          <div v-if="selectedFiles.length > 0" class="mt-4">
            <div class="flex items-center justify-between mb-2">
              <span class="label-text font-semibold">Arquivos Selecionados</span>
              <span class="badge badge-primary badge-lg">{{ selectedFiles.length }}</span>
            </div>
            <div class="max-h-48 overflow-y-auto space-y-2">
              <div v-for="(file, index) in selectedFiles" :key="index" 
                   class="flex items-center justify-between p-3 bg-base-200 rounded-lg">
                <div class="flex items-center gap-3">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-success" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span class="text-sm font-medium">{{ file.name }}</span>
                </div>
                <span class="text-xs text-base-content/60">{{ formatFileSize(file.size) }}</span>
              </div>
            </div>
          </div>
        </div>
        
        <div class="card-actions justify-end mt-6">
          <button 
            v-if="selectedFiles.length > 0"
            @click="selectedFiles = []"
            class="btn btn-ghost gap-2"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
            Limpar
          </button>
          <button 
            @click="startUpload" 
            class="btn btn-primary btn-lg gap-2"
            :disabled="uploading || selectedFiles.length === 0"
          >
            <svg v-if="!uploading" xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
            </svg>
            <span v-if="uploading" class="loading loading-spinner"></span>
            {{ uploading ? 'Processando...' : 'Iniciar Processamento' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Job Status Card -->
    <div v-if="jobId" class="card bg-base-100 shadow-2xl border border-base-300">
      <div class="card-body">
        <h2 class="card-title text-2xl mb-4">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-info" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
          </svg>
          Status do Processamento
        </h2>
        
        <div v-if="jobStatus" class="space-y-6">
          <!-- Status Badge -->
          <div class="flex items-center gap-4">
            <span class="text-sm font-semibold text-base-content/70">Job ID:</span>
            <code class="px-3 py-1 bg-base-200 rounded text-sm font-mono">{{ jobId }}</code>
            <div class="badge badge-lg" :class="{
              'badge-success': jobStatus.status === 'completed',
              'badge-error': jobStatus.status === 'failed',
              'badge-warning': jobStatus.status === 'running',
              'badge-info': jobStatus.status === 'pending'
            }">
              {{ formatStatus(jobStatus.status) }}
            </div>
          </div>
          
          <!-- Progress Stats -->
          <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div class="stat bg-base-200 rounded-lg shadow">
              <div class="stat-title">Total de Arquivos</div>
              <div class="stat-value text-primary">{{ jobStatus.total_files }}</div>
            </div>
            <div class="stat bg-base-200 rounded-lg shadow">
              <div class="stat-title">Processados</div>
              <div class="stat-value text-info">{{ jobStatus.successful + jobStatus.failed }}</div>
            </div>
            <div class="stat bg-base-200 rounded-lg shadow">
              <div class="stat-title">Sucessos</div>
              <div class="stat-value text-success">{{ jobStatus.successful }}</div>
            </div>
            <div class="stat bg-base-200 rounded-lg shadow">
              <div class="stat-title">Falhas</div>
              <div class="stat-value text-error">{{ jobStatus.failed }}</div>
            </div>
          </div>
          
          <!-- Progress Bar -->
          <div v-if="jobStatus.status === 'running'" class="space-y-2">
            <div class="flex justify-between text-sm">
              <span class="font-semibold">Progresso</span>
              <span>{{ progressPercentage }}%</span>
            </div>
            <progress class="progress progress-primary w-full" :value="progressPercentage" max="100"></progress>
          </div>
          
          <!-- Errors -->
          <div v-if="jobStatus.errors && jobStatus.errors.length > 0" class="alert alert-error shadow-lg">
            <div class="w-full">
              <div class="flex items-center gap-2 mb-3">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <h3 class="font-bold">Erros Encontrados ({{ jobStatus.errors.length }})</h3>
              </div>
              <div class="max-h-48 overflow-y-auto space-y-2">
                <div v-for="(error, index) in jobStatus.errors" :key="index" 
                     class="p-3 bg-base-100 rounded text-sm">
                  <p class="font-semibold">{{ error.file }}</p>
                  <p class="text-error-content/80">{{ error.error }}</p>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Success Message -->
          <div v-if="jobStatus.status === 'completed' && jobStatus.failed === 0" class="alert alert-success shadow-lg">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>Todos os arquivos foram processados com sucesso!</span>
          </div>
          
          <!-- Actions -->
          <div class="card-actions justify-end">
            <button 
              v-if="jobStatus.status === 'completed' || jobStatus.status === 'failed'"
              @click="resetUpload"
              class="btn btn-primary gap-2"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              Novo Upload
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
const { startBatchUpload, getBatchStatus } = useApi()
const uploading = ref(false)
const jobId = ref(null)
const jobStatus = ref(null)
const selectedFiles = ref([])
const isDragging = ref(false)
let pollInterval = null

const progressPercentage = computed(() => {
  if (!jobStatus.value) return 0
  const total = jobStatus.value.total_files
  const processed = jobStatus.value.successful + jobStatus.value.failed
  return total > 0 ? Math.round((processed / total) * 100) : 0
})

const handleFileSelect = (event) => {
  const files = Array.from(event.target.files)
  selectedFiles.value = files
}

const handleDrop = (event) => {
  isDragging.value = false
  const files = Array.from(event.dataTransfer.files).filter(f => f.name.endsWith('.xml'))
  selectedFiles.value = files
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

const formatStatus = (status) => {
  const statusMap = {
    'pending': 'Pendente',
    'running': 'Processando',
    'completed': 'Concluído',
    'failed': 'Falhou'
  }
  return statusMap[status] || status
}

const startUpload = async () => {
  if (selectedFiles.value.length === 0) {
    alert('Selecione pelo menos um arquivo XML')
    return
  }
  
  uploading.value = true
  try {
    const result = await startBatchUpload(selectedFiles.value)
    jobId.value = result.job_id
    jobStatus.value = result
    startPolling()
  } catch (error) {
    alert('Erro ao iniciar upload')
  } finally {
    uploading.value = false
  }
}

const startPolling = () => {
  pollInterval = setInterval(async () => {
    try {
      const status = await getBatchStatus(jobId.value)
      jobStatus.value = status
      
      if (status.status === 'completed' || status.status === 'failed') {
        clearInterval(pollInterval)
      }
    } catch (error) {
      clearInterval(pollInterval)
      console.error('Erro ao buscar status:', error)
      
      // Update status to show error
      if (jobStatus.value) {
        jobStatus.value.status = 'failed'
      }
      
      alert('Erro ao buscar status do job. O job pode ter expirado ou o servidor foi reiniciado.')
    }
  }, 3000)
}

const resetUpload = () => {
  jobId.value = null
  jobStatus.value = null
  selectedFiles.value = []
  if (pollInterval) {
    clearInterval(pollInterval)
    pollInterval = null
  }
}

onUnmounted(() => {
  if (pollInterval) clearInterval(pollInterval)
})
</script>
