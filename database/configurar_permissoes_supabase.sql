-- ============================================================================
-- CONFIGURAÇÃO DE PERMISSÕES PARA SUPABASE
-- Execute este script APÓS criar as tabelas
-- ============================================================================

-- 1. GARANTIR ACESSO AO SCHEMA PUBLIC
GRANT USAGE ON SCHEMA public TO postgres, anon, authenticated, service_role;
GRANT ALL ON SCHEMA public TO postgres, service_role;

-- 2. GARANTIR ACESSO A TODAS AS TABELAS EXISTENTES
GRANT ALL ON ALL TABLES IN SCHEMA public TO postgres, service_role;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO anon, authenticated;

-- 3. GARANTIR ACESSO A TODAS AS SEQUENCES
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO postgres, service_role;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO anon, authenticated;

-- 4. GARANTIR ACESSO A TABELAS FUTURAS (AUTO)
ALTER DEFAULT PRIVILEGES IN SCHEMA public 
    GRANT ALL ON TABLES TO postgres, service_role;
    
ALTER DEFAULT PRIVILEGES IN SCHEMA public 
    GRANT SELECT ON TABLES TO anon, authenticated;

ALTER DEFAULT PRIVILEGES IN SCHEMA public 
    GRANT ALL ON SEQUENCES TO postgres, service_role;

-- 5. DESABILITAR RLS EM TODAS AS TABELAS
ALTER TABLE empresas DISABLE ROW LEVEL SECURITY;
ALTER TABLE notas_fiscais DISABLE ROW LEVEL SECURITY;
ALTER TABLE nf_referencias DISABLE ROW LEVEL SECURITY;
ALTER TABLE nf_itens DISABLE ROW LEVEL SECURITY;
ALTER TABLE nf_itens_icms DISABLE ROW LEVEL SECURITY;
ALTER TABLE nf_itens_ipi DISABLE ROW LEVEL SECURITY;
ALTER TABLE nf_itens_ii DISABLE ROW LEVEL SECURITY;
ALTER TABLE nf_itens_pis DISABLE ROW LEVEL SECURITY;
ALTER TABLE nf_itens_cofins DISABLE ROW LEVEL SECURITY;
ALTER TABLE nf_itens_issqn DISABLE ROW LEVEL SECURITY;
ALTER TABLE nf_itens_di DISABLE ROW LEVEL SECURITY;
ALTER TABLE nf_itens_di_adicoes DISABLE ROW LEVEL SECURITY;
ALTER TABLE nf_itens_rastreabilidade DISABLE ROW LEVEL SECURITY;
ALTER TABLE nf_transporte DISABLE ROW LEVEL SECURITY;
ALTER TABLE nf_transporte_reboque DISABLE ROW LEVEL SECURITY;
ALTER TABLE nf_transporte_volumes DISABLE ROW LEVEL SECURITY;
ALTER TABLE nf_transporte_volumes_lacres DISABLE ROW LEVEL SECURITY;
ALTER TABLE nf_cobranca DISABLE ROW LEVEL SECURITY;
ALTER TABLE nf_duplicatas DISABLE ROW LEVEL SECURITY;
ALTER TABLE nf_pagamentos DISABLE ROW LEVEL SECURITY;
ALTER TABLE nf_cce DISABLE ROW LEVEL SECURITY;
ALTER TABLE nf_processamento DISABLE ROW LEVEL SECURITY;
ALTER TABLE nf_itens_combustivel DISABLE ROW LEVEL SECURITY;

-- 6. VERIFICAR PERMISSÕES
SELECT 
    schemaname,
    tablename,
    tableowner,
    CASE 
        WHEN rowsecurity THEN 'RLS Ativado'
        ELSE 'RLS Desativado'
    END as rls_status
FROM pg_tables
WHERE schemaname = 'public'
    AND tablename LIKE 'nf_%' OR tablename = 'empresas'
ORDER BY tablename;

-- 7. VERIFICAR SE AS TABELAS FORAM CRIADAS
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
    AND table_type = 'BASE TABLE'
ORDER BY table_name;

-- ============================================================================
-- MENSAGEM DE SUCESSO
-- ============================================================================
DO $$
BEGIN
    RAISE NOTICE '✅ Permissões configuradas com sucesso!';
    RAISE NOTICE '✅ RLS desabilitado em todas as tabelas.';
    RAISE NOTICE '✅ Service role tem acesso total.';
    RAISE NOTICE '';
    RAISE NOTICE '🚀 Agora você pode executar o script Python de importação!';
END $$;
