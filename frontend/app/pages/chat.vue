<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-base-100 to-base-200 p-6">
    <div class="text-center max-w-md">
      <div class="text-6xl mb-6">💬</div>
      <h1 class="text-3xl font-bold mb-4">Chat Movido!</h1>
      <p class="text-lg text-base-content/70 mb-6">
        O chat agora está disponível como um botão flutuante no canto inferior direito de todas as páginas.
      </p>
      <div class="flex flex-col gap-3">
        <NuxtLink to="/" class="btn btn-primary btn-lg gap-2">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
          </svg>
          Ir para Dashboard
        </NuxtLink>
        <p class="text-sm text-base-content/60">
          Procure pelo botão azul com ícone de chat 💬
        </p>
      </div>
    </div>
  </div>
  
  <!-- Old chat interface kept below for reference, hidden -->
  <div class="hidden h-screen flex-col bg-gradient-to-br from-base-100 to-base-200">
    <!-- Header -->
    <div class="navbar bg-base-100 shadow-lg border-b border-base-300">
      <div class="flex-1">
        <h1 class="text-2xl font-bold ml-4 flex items-center gap-2">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
          </svg>
          Chat com Assistente NF-e
        </h1>
      </div>
      <div class="flex-none mr-4">
        <button @click="clearHistory" class="btn btn-ghost btn-sm gap-2">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
          Limpar Histórico
        </button>
      </div>
    </div>

    <!-- Messages Container -->
    <div ref="messagesContainer" class="flex-1 overflow-y-auto p-6 space-y-4">
      <!-- Welcome Message -->
      <div v-if="messages.length === 0" class="flex items-center justify-center h-full">
        <div class="text-center max-w-md">
          <div class="text-6xl mb-4">💬</div>
          <h2 class="text-2xl font-bold mb-2">Bem-vindo ao Chat NF-e</h2>
          <p class="text-base-content/60">
            Faça perguntas sobre suas notas fiscais em linguagem natural. 
            O assistente irá ajudá-lo a consultar e analisar seus dados.
          </p>
          <div class="mt-6 space-y-2 text-sm text-left bg-base-200 p-4 rounded-lg">
            <p class="font-semibold mb-2">Exemplos de perguntas:</p>
            <p class="text-base-content/70">• Quantas notas fiscais autorizadas tenho?</p>
            <p class="text-base-content/70">• Qual o valor total das notas de janeiro?</p>
            <p class="text-base-content/70">• Mostre as notas do fornecedor X</p>
          </div>
        </div>
      </div>

      <!-- Messages -->
      <div v-for="(msg, index) in messages" :key="index" class="flex" :class="msg.role === 'user' ? 'justify-end' : 'justify-start'">
        <div class="flex gap-3 max-w-[80%]" :class="msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'">
          <!-- Avatar -->
          <div class="avatar placeholder">
            <div :class="[
              'w-10 h-10 rounded-full',
              msg.role === 'user' ? 'bg-primary text-primary-content' : 'bg-secondary text-secondary-content'
            ]">
              <span class="text-lg">{{ msg.role === 'user' ? '👤' : '🤖' }}</span>
            </div>
          </div>
          
          <!-- Message Bubble -->
          <div :class="[
            'chat-bubble p-4 rounded-2xl shadow-md',
            msg.role === 'user' 
              ? 'bg-primary text-primary-content rounded-tr-none' 
              : 'bg-base-100 text-base-content rounded-tl-none border border-base-300'
          ]">
            <div v-if="msg.role === 'user'" class="whitespace-pre-wrap">{{ msg.content }}</div>
            <div v-else class="prose prose-sm max-w-none" v-html="renderMarkdown(msg.content)"></div>
            <div class="text-xs opacity-60 mt-2">{{ formatTime(msg.timestamp) }}</div>
          </div>
        </div>
      </div>
      
      <!-- Loading Indicator -->
      <div v-if="loading" class="flex justify-start">
        <div class="flex gap-3 max-w-[80%]">
          <div class="avatar placeholder">
            <div class="w-10 h-10 rounded-full bg-secondary text-secondary-content">
              <span class="text-lg">🤖</span>
            </div>
          </div>
          <div class="chat-bubble bg-base-100 border border-base-300 p-4 rounded-2xl rounded-tl-none shadow-md">
            <div class="flex items-center gap-2">
              <span class="loading loading-dots loading-sm"></span>
              <span class="text-sm">Pensando...</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Input Area -->
    <div class="bg-base-100 border-t border-base-300 p-4 shadow-lg">
      <div class="max-w-4xl mx-auto">
        <div class="flex gap-3 items-end">
          <div class="flex-1">
            <textarea 
              v-model="userMessage" 
              @keydown.enter.exact.prevent="sendMessage"
              @keydown.enter.shift.exact="userMessage += '\n'"
              rows="1"
              placeholder="Digite sua mensagem... (Shift+Enter para nova linha)" 
              class="textarea textarea-bordered w-full resize-none focus:outline-none focus:ring-2 focus:ring-primary"
              :disabled="loading"
              ref="inputRef"
            ></textarea>
          </div>
          <button 
            @click="sendMessage" 
            class="btn btn-primary btn-circle btn-lg shadow-lg hover:shadow-xl transition-shadow"
            :disabled="loading || !userMessage.trim()"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { marked } from 'marked'

const { chatMessage, clearChatHistory } = useApi()
const messages = ref([])
const userMessage = ref('')
const loading = ref(false)
const messagesContainer = ref(null)
const inputRef = ref(null)

// Configure marked for better rendering
marked.setOptions({
  breaks: true,
  gfm: true
})

const renderMarkdown = (content) => {
  return marked(content)
}

const formatTime = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  return date.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })
}

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

const sendMessage = async () => {
  console.log('sendMessage called, userMessage:', userMessage.value)
  
  if (!userMessage.value || !userMessage.value.trim()) {
    console.log('Message is empty, returning')
    return
  }
  
  const msg = userMessage.value
  console.log('Sending message:', msg)
  
  messages.value.push({ 
    role: 'user', 
    content: msg,
    timestamp: new Date()
  })
  userMessage.value = ''
  loading.value = true
  scrollToBottom()
  
  try {
    console.log('Calling chatMessage API...')
    const response = await chatMessage(msg)
    console.log('Response received:', response)
    messages.value.push({ 
      role: 'assistant', 
      content: response.message,
      timestamp: new Date()
    })
    scrollToBottom()
  } catch (error) {
    console.error('Error sending message:', error)
    // Remove user message if request failed
    messages.value.pop()
    alert('Erro ao enviar mensagem: ' + error.message + '\n\nVerifique se o backend está rodando em http://localhost:8000')
  } finally {
    loading.value = false
  }
}

const clearHistory = async () => {
  if (messages.value.length === 0) return
  
  if (!confirm('Tem certeza que deseja limpar todo o histórico de conversas?')) {
    return
  }
  
  try {
    await clearChatHistory()
    messages.value = []
  } catch (error) {
    console.error('Error clearing history:', error)
    alert('Erro ao limpar histórico: ' + error.message)
  }
}

// Auto-resize textarea
watch(userMessage, () => {
  nextTick(() => {
    if (inputRef.value) {
      inputRef.value.style.height = 'auto'
      inputRef.value.style.height = Math.min(inputRef.value.scrollHeight, 150) + 'px'
    }
  })
})

// Focus input on mount
onMounted(() => {
  if (inputRef.value) {
    inputRef.value.focus()
  }
})
</script>


<style scoped>
/* Custom scrollbar */
.overflow-y-auto::-webkit-scrollbar {
  width: 8px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: transparent;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 4px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 0, 0, 0.3);
}

/* Markdown styling */
.prose {
  color: inherit;
}

.prose :deep(p) {
  margin: 0.5em 0;
}

.prose :deep(p:first-child) {
  margin-top: 0;
}

.prose :deep(p:last-child) {
  margin-bottom: 0;
}

.prose :deep(strong) {
  font-weight: 700;
  color: inherit;
}

.prose :deep(em) {
  font-style: italic;
}

.prose :deep(code) {
  background: rgba(0, 0, 0, 0.1);
  padding: 0.2em 0.4em;
  border-radius: 3px;
  font-size: 0.9em;
  font-family: 'Courier New', monospace;
}

.prose :deep(pre) {
  background: rgba(0, 0, 0, 0.1);
  padding: 1em;
  border-radius: 6px;
  overflow-x: auto;
  margin: 0.5em 0;
}

.prose :deep(pre code) {
  background: transparent;
  padding: 0;
}

.prose :deep(ul), .prose :deep(ol) {
  margin: 0.5em 0;
  padding-left: 1.5em;
}

.prose :deep(li) {
  margin: 0.25em 0;
}

.prose :deep(blockquote) {
  border-left: 3px solid rgba(0, 0, 0, 0.2);
  padding-left: 1em;
  margin: 0.5em 0;
  font-style: italic;
}

.prose :deep(a) {
  color: #3b82f6;
  text-decoration: underline;
}

.prose :deep(h1), .prose :deep(h2), .prose :deep(h3), 
.prose :deep(h4), .prose :deep(h5), .prose :deep(h6) {
  font-weight: 700;
  margin: 0.75em 0 0.5em 0;
}

.prose :deep(h1) { font-size: 1.5em; }
.prose :deep(h2) { font-size: 1.3em; }
.prose :deep(h3) { font-size: 1.1em; }

.prose :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 0.5em 0;
}

.prose :deep(th), .prose :deep(td) {
  border: 1px solid rgba(0, 0, 0, 0.2);
  padding: 0.5em;
  text-align: left;
}

.prose :deep(th) {
  background: rgba(0, 0, 0, 0.1);
  font-weight: 700;
}

/* Textarea auto-resize */
textarea {
  min-height: 48px;
  max-height: 150px;
  overflow-y: auto;
}

/* Animation for new messages */
@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.flex > div {
  animation: slideIn 0.3s ease-out;
}
</style>
