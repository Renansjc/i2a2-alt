/**
 * API Client Composable
 * Provides methods to interact with the backend API
 */

const API_BASE = 'http://localhost:8000'

interface ChatResponse {
  message: string
  session_id: string
}

interface BatchUploadResponse {
  job_id: string
  status: string
  message: string
}

interface BatchStatusResponse {
  job_id: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  total_files: number
  successful: number
  failed: number
  errors?: Array<{ file: string; error: string }>
}

interface ClearHistoryResponse {
  message: string
  session_id: string
}

export const useApi = () => {
  /**
   * Send a chat message to the backend
   * @param message - User message
   * @returns Chat response from the agent
   */
  const chatMessage = async (message: string): Promise<ChatResponse> => {
    const response = await fetch(`${API_BASE}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: 'user-session',
        message
      })
    })
    
    if (!response.ok) {
      throw new Error('Erro na API')
    }
    
    return response.json()
  }

  /**
   * Start batch upload of XML files
   * @param files - Array of XML files to upload
   * @returns Job information with job_id
   */
  const startBatchUpload = async (files: File[]): Promise<BatchUploadResponse> => {
    const formData = new FormData()
    files.forEach(file => {
      formData.append('files', file)
    })

    const response = await fetch(`${API_BASE}/api/batch/upload`, {
      method: 'POST',
      body: formData
    })
    
    if (!response.ok) {
      throw new Error('Erro ao iniciar upload')
    }
    
    return response.json()
  }

  /**
   * Get batch job status
   * @param jobId - Job ID to check status
   * @returns Current job status and progress
   */
  const getBatchStatus = async (jobId: string): Promise<BatchStatusResponse> => {
    const response = await fetch(`${API_BASE}/api/batch/status/${jobId}`)
    
    if (!response.ok) {
      throw new Error('Erro ao buscar status')
    }
    
    return response.json()
  }

  /**
   * Clear chat history for the current session
   * @returns Confirmation message
   */
  const clearChatHistory = async (): Promise<ClearHistoryResponse> => {
    const response = await fetch(`${API_BASE}/api/chat/history/user-session`, {
      method: 'DELETE'
    })
    
    if (!response.ok) {
      throw new Error('Erro ao limpar histórico')
    }
    
    return response.json()
  }

  return {
    chatMessage,
    startBatchUpload,
    getBatchStatus,
    clearChatHistory
  }
}
