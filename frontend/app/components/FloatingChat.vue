<template>
  <div class="fixed bottom-6 right-6 z-50">
    <!-- Chat Widget Expandido -->
    <Transition name="chat-expand">
      <div 
        v-if="isOpen" 
        class="bg-base-100 rounded-2xl shadow-2xl border border-base-300 mb-4 overflow-hidden"
        style="width: 400px; height: 600px;"
      >
        <!-- Header -->
        <div class="bg-primary text-primary-content p-4 flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="avatar placeholder">
              <div class="w-10 h-10 rounded-full bg-white/20 flex items-center justify-center">
                <span class="text-xl">🤖</span>
              </div>
            </div>
            <div>
              <h3 class="font-bold">Assistente NF-e</h3>
              <p class="text-xs opacity-80">Online</p>
            </div>
          </div>
          <div class="flex gap-2">
            <button 
              @click="clearHistory" 
              class="btn btn-ghost btn-sm btn-circle text-white hover:bg-white/20"
              title="Limpar histórico"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
            <button 
              @click="isOpen = false" 
              class="btn btn-ghost btn-sm btn-circle text-white hover:bg-white/20"
              title="Minimizar"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
              </svg>
            </button>
          </div>
        </div>

        <!-- Messages Container -->
        <div ref="messagesContainer" class="h-[calc(100%-140px)] overflow-y-auto p-4 space-y-3 bg-base-200/30">
          <!-- Welcome Message -->
          <div v-if="messages.length === 0" class="flex items-center justify-center h-full">
            <div class="text-center px-4">
              <div class="text-5xl mb-3">💬</div>
              <h3 class="font-bold mb-2">Olá! Como posso ajudar?</h3>
              <p class="text-sm text-base-content/60 mb-4">
                Faça perguntas sobre suas notas fiscais
              </p>
              <div class="space-y-2 text-xs text-left">
                <button 
                  @click="sendQuickMessage('Quantas notas fiscais tenho?')"
                  class="btn btn-sm btn-outline w-full justify-start text-left"
                >
                  💡 Quantas notas fiscais tenho?
                </button>
                <button 
                  @click="sendQuickMessage('Qual o valor total das notas?')"
                  class="btn btn-sm btn-outline w-full justify-start text-left"
                >
                  💰 Qual o valor total das notas?
                </button>
              </div>
            </div>
          </div>

          <!-- Messages -->
          <div v-for="(msg, index) in messages" :key="index">
            <!-- User Message -->
            <div v-if="msg.role === 'user'" class="flex justify-end">
              <div class="bg-primary text-primary-content rounded-2xl rounded-tr-sm px-4 py-2 max-w-[85%] shadow-md">
                <p class="text-sm whitespace-pre-wrap">{{ msg.content }}</p>
                <p class="text-xs opacity-70 mt-1">{{ formatTime(msg.timestamp) }}</p>
              </div>
            </div>

            <!-- Assistant Message -->
            <div v-else class="flex justify-start">
              <div class="flex gap-2 max-w-[85%]">
                <div class="avatar placeholder flex-shrink-0">
                  <div class="w-8 h-8 rounded-full bg-secondary text-secondary-content flex items-center justify-center">
                    <span class="text-sm">🤖</span>
                  </div>
                </div>
                <div class="bg-base-100 rounded-2xl rounded-tl-sm px-4 py-2 shadow-md border border-base-300">
                  <div class="prose prose-sm max-w-none text-sm" v-html="renderMarkdown(msg.content)"></div>
                  <p class="text-xs opacity-60 mt-1">{{ formatTime(msg.timestamp) }}</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Loading -->
          <div v-if="loading" class="flex justify-start">
            <div class="flex gap-2">
              <div class="avatar placeholder">
                <div class="w-8 h-8 rounded-full bg-secondary text-secondary-content flex items-center justify-center">
                  <span class="text-sm">🤖</span>
                </div>
              </div>
              <div class="bg-base-100 rounded-2xl rounded-tl-sm px-4 py-2 shadow-md border border-base-300">
                <span class="loading loading-dots loading-sm"></span>
              </div>
            </div>
          </div>
        </div>

        <!-- Input Area -->
        <div class="p-3 bg-base-100 border-t border-base-300">
          <div class="flex gap-2 items-end">
            <textarea 
              v-model="userMessage" 
              @keydown.enter.exact.prevent="sendMessage"
              @keydown.shift.enter="userMessage += '\n'"
              rows="1"
              placeholder="Digite sua mensagem..." 
              class="textarea textarea-bordered textarea-sm w-full resize-none text-sm"
              :disabled="loading"
              ref="inputRef"
              style="min-height: 36px; max-height: 80px;"
            ></textarea>
            <button 
              @click="sendMessage" 
              class="btn btn-primary btn-sm btn-circle"
              :disabled="loading || !userMessage.trim()"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Floating Button -->
    <button 
      @click="toggleChat"
      class="btn btn-circle btn-lg btn-primary border-none shadow-2xl hover:shadow-3xl hover:scale-110 transition-all duration-300"
      :class="{ 'rotate-0': !isOpen, 'rotate-180': isOpen }"
    >
      <Transition name="icon-fade" mode="out-in">
        <svg v-if="!isOpen" xmlns="http://www.w3.org/2000/svg" class="h-7 w-7" fill="none" viewBox="0 0 24 24" stroke="currentColor" key="chat">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
        </svg>
        <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-7 w-7" fill="none" viewBox="0 0 24 24" stroke="currentColor" key="close">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </Transition>
      
      <!-- Notification Badge -->
      <span v-if="unreadCount > 0 && !isOpen" class="absolute -top-1 -right-1 badge badge-error badge-sm">
        {{ unreadCount }}
      </span>
    </button>
  </div>
</template>

<script setup>
import { marked } from 'marked'

const { chatMessage, clearChatHistory } = useApi()

const isOpen = ref(false)
const messages = ref([])
const userMessage = ref('')
const loading = ref(false)
const unreadCount = ref(0)
const messagesContainer = ref(null)
const inputRef = ref(null)

// Configure marked
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

const toggleChat = () => {
  isOpen.value = !isOpen.value
  if (isOpen.value) {
    unreadCount.value = 0
    nextTick(() => {
      if (inputRef.value) {
        inputRef.value.focus()
      }
      scrollToBottom()
    })
  }
}

const sendMessage = async () => {
  if (!userMessage.value || !userMessage.value.trim()) return
  
  const msg = userMessage.value
  messages.value.push({ 
    role: 'user', 
    content: msg,
    timestamp: new Date()
  })
  userMessage.value = ''
  loading.value = true
  scrollToBottom()
  
  try {
    const response = await chatMessage(msg)
    messages.value.push({ 
      role: 'assistant', 
      content: response.message,
      timestamp: new Date()
    })
    
    if (!isOpen.value) {
      unreadCount.value++
    }
    
    scrollToBottom()
  } catch (error) {
    console.error('Error sending message:', error)
    messages.value.pop()
    alert('Erro ao enviar mensagem. Verifique se o backend está rodando.')
  } finally {
    loading.value = false
  }
}

const sendQuickMessage = (message) => {
  userMessage.value = message
  sendMessage()
}

const clearHistory = async () => {
  if (messages.value.length === 0) return
  
  if (!confirm('Limpar todo o histórico de conversas?')) return
  
  try {
    await clearChatHistory()
    messages.value = []
  } catch (error) {
    console.error('Error clearing history:', error)
    alert('Erro ao limpar histórico')
  }
}

// Auto-resize textarea
watch(userMessage, () => {
  nextTick(() => {
    if (inputRef.value) {
      inputRef.value.style.height = 'auto'
      inputRef.value.style.height = Math.min(inputRef.value.scrollHeight, 80) + 'px'
    }
  })
})
</script>

<style scoped>
/* Chat expand animation */
.chat-expand-enter-active,
.chat-expand-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  transform-origin: bottom right;
}

.chat-expand-enter-from,
.chat-expand-leave-to {
  opacity: 0;
  transform: scale(0.8) translateY(20px);
}

/* Icon fade animation */
.icon-fade-enter-active,
.icon-fade-leave-active {
  transition: all 0.2s ease;
}

.icon-fade-enter-from,
.icon-fade-leave-to {
  opacity: 0;
  transform: scale(0.8);
}

/* Custom scrollbar */
.overflow-y-auto::-webkit-scrollbar {
  width: 6px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: transparent;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 3px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 0, 0, 0.3);
}

/* Markdown styling */
.prose {
  color: inherit;
}

.prose :deep(p) {
  margin: 0.25em 0;
}

.prose :deep(code) {
  background: rgba(0, 0, 0, 0.1);
  padding: 0.1em 0.3em;
  border-radius: 3px;
  font-size: 0.85em;
}

.prose :deep(ul), .prose :deep(ol) {
  margin: 0.25em 0;
  padding-left: 1.2em;
}

.prose :deep(li) {
  margin: 0.1em 0;
}

/* Message animations */
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

.space-y-3 > div {
  animation: slideIn 0.3s ease-out;
}

/* Button pulse effect */
@keyframes pulse-ring {
  0% {
    box-shadow: 0 0 0 0 rgba(59, 130, 246, 0.7);
  }
  70% {
    box-shadow: 0 0 0 10px rgba(59, 130, 246, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(59, 130, 246, 0);
  }
}

.btn-circle:hover {
  animation: pulse-ring 1.5s infinite;
}
</style>
