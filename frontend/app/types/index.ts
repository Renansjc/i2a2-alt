// TypeScript interfaces for the NF-e frontend application

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}

export interface BatchJob {
  job_id: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  total_files: number
  successful: number
  failed: number
  errors: Array<{ file: string; error: string }>
}

export interface Invoice {
  numero_nf: string
  serie_nf: string
  chave_acesso: string
  valor_total_nota: number
  data_emissao: string
}

export interface DashboardStats {
  totalNotas: number
  valorTotal: number
}

export interface MonthlyData {
  mes: string
  quantidade: number
  valor: number
}

export interface TopProduct {
  descricao: string
  quantidade: number
  valor_total: number
}

export interface OperationTypeData {
  tipo: string
  quantidade: number
}

export interface TaxData {
  tipo: string
  valor: number
}

export interface TopCustomer {
  razao_social: string
  total_compras: number
  quantidade_notas: number
}

export interface CashFlowData {
  mes: string
  entradas: number
  saidas: number
  saldo: number
}
