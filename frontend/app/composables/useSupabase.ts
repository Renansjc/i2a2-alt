import { createClient } from '@supabase/supabase-js'

export const useSupabase = () => {
  const config = useRuntimeConfig()
  
  const supabase = createClient(
    config.public.supabaseUrl,
    config.public.supabaseAnonKey
  )

  const getInvoices = async (page: number = 0, pageSize: number = 50, sortColumn: string = 'data_hora_emissao', sortDirection: string = 'desc') => {
    const offset = page * pageSize

    const query = supabase
      .from('notas_fiscais')
      .select(`
        numero_nf, 
        serie, 
        chave_acesso, 
        valor_total_nota, 
        data_hora_emissao,
        natureza_operacao,
        status,
        emitente_id,
        destinatario_id
      `, { count: 'exact' })
      .order(sortColumn, { ascending: sortDirection === 'asc' })

    // Apply pagination using range instead of limit/offset
    const from = offset
    const to = offset + pageSize - 1
    
    const { data: notasData, error, count } = await query.range(from, to)

    if (error) throw error
    
    // Fetch empresa names separately
    let enrichedData = notasData || []
    
    if (notasData && notasData.length > 0) {
      const empresaIds = [...new Set([
        ...notasData.map((nf: any) => nf.emitente_id).filter(Boolean),
        ...notasData.map((nf: any) => nf.destinatario_id).filter(Boolean)
      ])]
      
      const { data: empresas } = await supabase
        .from('empresas')
        .select('id, razao_social, nome_fantasia')
        .in('id', empresaIds)
      
      const empresaMap = new Map(empresas?.map((e: any) => [e.id, e]) || [])
      
      // Enrich data with empresa names
      enrichedData = notasData.map((nf: any) => ({
        ...nf,
        emitente: empresaMap.get(nf.emitente_id) || null,
        destinatario: empresaMap.get(nf.destinatario_id) || null
      }))
    }
    
    return { data: enrichedData, count }
  }

  const getDashboardStats = async () => {
    // Total de notas
    const { count: totalNotas } = await supabase
      .from('notas_fiscais')
      .select('*', { count: 'exact', head: true })

    // Valor total
    const { data: valorData } = await supabase
      .from('notas_fiscais')
      .select('valor_total_nota')

    const valorTotal = valorData?.reduce((sum, nf) => sum + (nf.valor_total_nota || 0), 0) || 0

    return {
      totalNotas: totalNotas || 0,
      valorTotal
    }
  }

  const getMonthlyData = async () => {
    const { data, error } = await supabase
      .from('notas_fiscais')
      .select('data_hora_emissao, valor_total_nota')
      .order('data_hora_emissao', { ascending: true })
    
    if (error) throw error
    
    // Agregar por mês
    const monthlyMap = new Map()
    data?.forEach((nf: any) => {
      const date = new Date(nf.data_hora_emissao)
      const monthKey = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`
      
      if (!monthlyMap.has(monthKey)) {
        monthlyMap.set(monthKey, { mes: monthKey, quantidade: 0, valor: 0 })
      }
      
      const entry = monthlyMap.get(monthKey)
      entry.quantidade += 1
      entry.valor += nf.valor_total_nota || 0
    })
    
    return Array.from(monthlyMap.values())
  }

  const getTopProducts = async (limit = 5) => {
    const { data, error } = await supabase
      .from('nf_itens')
      .select('descricao, quantidade_comercial, valor_total_bruto')
    
    if (error) throw error
    
    // Agregar produtos com mesmo nome
    const aggregated = data?.reduce((acc: any[], item: any) => {
      const existing = acc.find(p => p.descricao === item.descricao)
      if (existing) {
        existing.quantidade += item.quantidade_comercial
        existing.valor_total += item.valor_total_bruto
      } else {
        acc.push({
          descricao: item.descricao,
          quantidade: item.quantidade_comercial,
          valor_total: item.valor_total_bruto
        })
      }
      return acc
    }, [])
    
    return aggregated?.sort((a: any, b: any) => b.valor_total - a.valor_total).slice(0, limit) || []
  }

  const getOperationTypeData = async () => {
    const { data, error } = await supabase
      .from('notas_fiscais')
      .select('tipo_operacao')
    
    if (error) throw error
    
    const entrada = data?.filter((nf: any) => nf.tipo_operacao === '0').length || 0
    const saida = data?.filter((nf: any) => nf.tipo_operacao === '1').length || 0
    
    return [
      { tipo: 'Entrada', quantidade: entrada },
      { tipo: 'Saída', quantidade: saida }
    ]
  }

  const getTaxData = async () => {
    const { data, error } = await supabase
      .from('notas_fiscais')
      .select('valor_icms, valor_ipi, valor_pis, valor_cofins')
    
    if (error) throw error
    
    const totals = data?.reduce((acc: any, nf: any) => {
      acc.icms += nf.valor_icms || 0
      acc.ipi += nf.valor_ipi || 0
      acc.pis += nf.valor_pis || 0
      acc.cofins += nf.valor_cofins || 0
      return acc
    }, { icms: 0, ipi: 0, pis: 0, cofins: 0 })
    
    return [
      { tipo: 'ICMS', valor: totals.icms },
      { tipo: 'IPI', valor: totals.ipi },
      { tipo: 'PIS', valor: totals.pis },
      { tipo: 'COFINS', valor: totals.cofins }
    ]
  }

  const getTopCustomers = async (limit = 5) => {
    const { data: notas, error } = await supabase
      .from('notas_fiscais')
      .select('destinatario_id, valor_total_nota, tipo_operacao')
      .eq('tipo_operacao', '1') // Apenas saídas (vendas)
    
    if (error) throw error
    
    // Agregar por destinatário
    const customerMap = new Map()
    notas?.forEach((nf: any) => {
      if (!nf.destinatario_id) return
      
      if (!customerMap.has(nf.destinatario_id)) {
        customerMap.set(nf.destinatario_id, {
          id: nf.destinatario_id,
          total_compras: 0,
          quantidade_notas: 0
        })
      }
      
      const customer = customerMap.get(nf.destinatario_id)
      customer.total_compras += nf.valor_total_nota || 0
      customer.quantidade_notas += 1
    })
    
    const topCustomerIds = Array.from(customerMap.values())
      .sort((a: any, b: any) => b.total_compras - a.total_compras)
      .slice(0, limit)
      .map((c: any) => c.id)
    
    if (topCustomerIds.length === 0) return []
    
    // Buscar nomes dos clientes
    const { data: empresas } = await supabase
      .from('empresas')
      .select('id, razao_social, nome_fantasia')
      .in('id', topCustomerIds)
    
    const empresaMap = new Map(empresas?.map((e: any) => [e.id, e]) || [])
    
    return topCustomerIds.map((id: number) => {
      const customer = customerMap.get(id)
      const empresa = empresaMap.get(id)
      return {
        razao_social: empresa?.razao_social || empresa?.nome_fantasia || 'Cliente não identificado',
        total_compras: customer.total_compras,
        quantidade_notas: customer.quantidade_notas
      }
    })
  }

  const getCashFlowData = async () => {
    const { data, error } = await supabase
      .from('notas_fiscais')
      .select('data_hora_emissao, valor_total_nota, tipo_operacao')
      .order('data_hora_emissao', { ascending: true })
    
    if (error) throw error
    
    // Agregar por mês
    const monthlyMap = new Map()
    data?.forEach((nf: any) => {
      const date = new Date(nf.data_hora_emissao)
      const monthKey = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`
      
      if (!monthlyMap.has(monthKey)) {
        monthlyMap.set(monthKey, { mes: monthKey, entradas: 0, saidas: 0, saldo: 0 })
      }
      
      const entry = monthlyMap.get(monthKey)
      const valor = nf.valor_total_nota || 0
      
      if (nf.tipo_operacao === '0') {
        entry.entradas += valor
      } else {
        entry.saidas += valor
      }
      entry.saldo = entry.saidas - entry.entradas
    })
    
    return Array.from(monthlyMap.values())
  }

  return {
    getInvoices,
    getDashboardStats,
    getMonthlyData,
    getTopProducts,
    getOperationTypeData,
    getTaxData,
    getTopCustomers,
    getCashFlowData
  }
}
