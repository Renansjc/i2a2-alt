-- ============================================================================
-- SCHEMA COMPLETO PARA NF-e - BASEADO NO LAYOUT 4.00 DA RECEITA FEDERAL
-- ============================================================================

-- Tabela de Empresas (Emitentes e Destinatários)
CREATE TABLE empresas (
    id SERIAL PRIMARY KEY,
    tipo_pessoa VARCHAR(10) CHECK (tipo_pessoa IN ('fisica', 'juridica')),
    cpf_cnpj VARCHAR(14) NOT NULL,
    razao_social VARCHAR(60),
    nome_fantasia VARCHAR(60),
    inscricao_estadual VARCHAR(14),
    inscricao_municipal VARCHAR(15),
    inscricao_suframa VARCHAR(9),
    regime_tributario CHAR(1), -- CRT: 1-Simples Nacional, 2-Simples Excesso, 3-Regime Normal
    
    -- Endereço
    logradouro VARCHAR(60),
    numero VARCHAR(60),
    complemento VARCHAR(60),
    bairro VARCHAR(60),
    codigo_municipio VARCHAR(7),
    nome_municipio VARCHAR(60),
    uf CHAR(2),
    cep VARCHAR(8),
    codigo_pais VARCHAR(4),
    nome_pais VARCHAR(60),
    telefone VARCHAR(14),
    email VARCHAR(60),
    
    -- Indicadores
    indicador_ie_destinatario CHAR(1), -- 1-Contribuinte ICMS, 2-Isento, 9-Não Contribuinte
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (cpf_cnpj)
);

-- Tabela principal de Notas Fiscais Eletrônicas
CREATE TABLE notas_fiscais (
    id SERIAL PRIMARY KEY,
    
    -- ===== GRUPO ide - Identificação da NF-e =====
    chave_acesso VARCHAR(44) UNIQUE NOT NULL,
    codigo_uf CHAR(2) NOT NULL,
    codigo_numerico_aleatorio VARCHAR(8),
    natureza_operacao VARCHAR(60) NOT NULL,
    modelo VARCHAR(2) NOT NULL, -- 55-NFe, 65-NFCe
    serie VARCHAR(3) NOT NULL,
    numero_nf INTEGER NOT NULL,
    data_hora_emissao TIMESTAMP NOT NULL,
    data_hora_saida_entrada TIMESTAMP,
    tipo_operacao CHAR(1) NOT NULL, -- 0-Entrada, 1-Saída
    destino_operacao CHAR(1) NOT NULL, -- 1-Interna, 2-Interestadual, 3-Exterior
    codigo_municipio_fato_gerador VARCHAR(7),
    tipo_impressao CHAR(1), -- 0-Sem impressão, 1-Normal Retrato, etc
    tipo_emissao CHAR(1), -- 1-Normal, 2-Contingência FS-IA, etc
    digito_verificador CHAR(1),
    tipo_ambiente CHAR(1), -- 1-Produção, 2-Homologação
    finalidade_emissao CHAR(1), -- 1-Normal, 2-Complementar, 3-Ajuste, 4-Devolução
    consumidor_final CHAR(1), -- 0-Normal, 1-Consumidor final
    presenca_comprador CHAR(1), -- 0-Não se aplica, 1-Presencial, etc
    indicador_intermediador CHAR(1), -- 0-Sem intermediador, 1-Com intermediador
    processo_emissao CHAR(1), -- 0-Aplicativo do contribuinte
    versao_processo VARCHAR(20),
    
    -- Referências a outras notas
    -- (armazenadas em tabela separada nf_referencias)
    
    -- ===== GRUPO emit - Emitente =====
    emitente_id INTEGER REFERENCES empresas(id),
    
    -- ===== GRUPO dest - Destinatário =====
    destinatario_id INTEGER REFERENCES empresas(id),
    
    -- ===== GRUPO retirada - Local de Retirada =====
    retirada_cpf_cnpj VARCHAR(14),
    retirada_logradouro VARCHAR(60),
    retirada_numero VARCHAR(60),
    retirada_complemento VARCHAR(60),
    retirada_bairro VARCHAR(60),
    retirada_codigo_municipio VARCHAR(7),
    retirada_nome_municipio VARCHAR(60),
    retirada_uf CHAR(2),
    retirada_cep VARCHAR(8),
    retirada_codigo_pais VARCHAR(4),
    retirada_nome_pais VARCHAR(60),
    retirada_telefone VARCHAR(14),
    retirada_email VARCHAR(60),
    retirada_inscricao_estadual VARCHAR(14),
    
    -- ===== GRUPO entrega - Local de Entrega =====
    entrega_cpf_cnpj VARCHAR(14),
    entrega_logradouro VARCHAR(60),
    entrega_numero VARCHAR(60),
    entrega_complemento VARCHAR(60),
    entrega_bairro VARCHAR(60),
    entrega_codigo_municipio VARCHAR(7),
    entrega_nome_municipio VARCHAR(60),
    entrega_uf CHAR(2),
    entrega_cep VARCHAR(8),
    entrega_codigo_pais VARCHAR(4),
    entrega_nome_pais VARCHAR(60),
    entrega_telefone VARCHAR(14),
    entrega_email VARCHAR(60),
    entrega_inscricao_estadual VARCHAR(14),
    
    -- ===== GRUPO total - Totalizadores =====
    -- Valores de ICMS
    base_calculo_icms DECIMAL(15,2) DEFAULT 0,
    valor_icms DECIMAL(15,2) DEFAULT 0,
    valor_icms_desonerado DECIMAL(15,2) DEFAULT 0,
    valor_fcp DECIMAL(15,2) DEFAULT 0, -- Fundo de Combate à Pobreza
    base_calculo_icms_st DECIMAL(15,2) DEFAULT 0,
    valor_icms_st DECIMAL(15,2) DEFAULT 0,
    valor_fcp_st DECIMAL(15,2) DEFAULT 0,
    valor_fcp_st_retido DECIMAL(15,2) DEFAULT 0,
    
    -- Valores dos produtos e serviços
    valor_total_produtos DECIMAL(15,2) NOT NULL DEFAULT 0,
    valor_frete DECIMAL(15,2) DEFAULT 0,
    valor_seguro DECIMAL(15,2) DEFAULT 0,
    valor_desconto DECIMAL(15,2) DEFAULT 0,
    valor_imposto_importacao DECIMAL(15,2) DEFAULT 0,
    valor_ipi DECIMAL(15,2) DEFAULT 0,
    valor_ipi_devolvido DECIMAL(15,2) DEFAULT 0,
    valor_pis DECIMAL(15,2) DEFAULT 0,
    valor_cofins DECIMAL(15,2) DEFAULT 0,
    valor_outras_despesas DECIMAL(15,2) DEFAULT 0,
    valor_total_nota DECIMAL(15,2) NOT NULL,
    
    -- Totais de tributos (Lei da Transparência)
    valor_total_tributos DECIMAL(15,2) DEFAULT 0,
    
    -- ===== GRUPO transp - Transporte =====
    modalidade_frete CHAR(1), -- 0-Emitente, 1-Destinatário, 2-Terceiros, 9-Sem Frete
    
    -- ===== GRUPO infAdic - Informações Adicionais =====
    informacoes_complementares TEXT,
    informacoes_fisco TEXT,
    
    -- ===== GRUPO exporta - Exportação =====
    uf_saida_pais CHAR(2),
    local_exportacao VARCHAR(60),
    local_despacho VARCHAR(60),
    
    -- ===== GRUPO compra - Compra =====
    nota_empenho VARCHAR(22),
    pedido_compra VARCHAR(60),
    contrato_compra VARCHAR(90),
    
    -- ===== GRUPO cana - Cana de açúcar =====
    safra VARCHAR(9),
    mes_ano_referencia VARCHAR(7),
    
    -- ===== Protocolo de Autorização =====
    status VARCHAR(20) CHECK (status IN ('emitida', 'autorizada', 'cancelada', 'denegada', 'rejeitada', 'inutilizada')),
    tipo_ambiente_protocolo CHAR(1),
    versao_aplicativo_recepcao VARCHAR(20),
    numero_protocolo VARCHAR(15),
    digest_value VARCHAR(28),
    data_hora_recebimento TIMESTAMP,
    codigo_status VARCHAR(3),
    motivo_status VARCHAR(255),
    
    -- Cancelamento
    data_hora_cancelamento TIMESTAMP,
    protocolo_cancelamento VARCHAR(15),
    justificativa_cancelamento VARCHAR(255),
    
    -- Carta de Correção
    -- (armazenada em tabela separada nf_cce)
    
    -- ===== XML e Assinatura =====
    xml_completo TEXT,
    xml_assinado TEXT,
    
    -- ===== Responsável Técnico =====
    resp_tecnico_cnpj VARCHAR(14),
    resp_tecnico_contato VARCHAR(60),
    resp_tecnico_email VARCHAR(60),
    resp_tecnico_telefone VARCHAR(14),
    
    -- Controle
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Referências a outras notas
CREATE TABLE nf_referencias (
    id SERIAL PRIMARY KEY,
    nota_fiscal_id INTEGER REFERENCES notas_fiscais(id) ON DELETE CASCADE,
    
    -- Tipo de referência
    tipo VARCHAR(10) CHECK (tipo IN ('nfe', 'nfce', 'modelo1', 'cte', 'nfp', 'ecf')),
    
    -- NFe/NFCe referenciada
    chave_acesso_referenciada VARCHAR(44),
    
    -- NF modelo 1/1A referenciada
    ref_uf CHAR(2),
    ref_ano_mes VARCHAR(4), -- AAMM
    ref_cnpj VARCHAR(14),
    ref_modelo VARCHAR(2),
    ref_serie VARCHAR(3),
    ref_numero_nf INTEGER,
    
    -- NF de Produtor Rural referenciada
    ref_cpf_cnpj_produtor VARCHAR(14),
    ref_inscricao_estadual VARCHAR(14),
    
    -- CTe referenciado
    chave_acesso_cte VARCHAR(44),
    
    -- ECF referenciado
    ref_modelo_ecf VARCHAR(20),
    ref_numero_ecf INTEGER,
    ref_numero_coo INTEGER,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Itens/Produtos da Nota Fiscal
CREATE TABLE nf_itens (
    id SERIAL PRIMARY KEY,
    nota_fiscal_id INTEGER REFERENCES notas_fiscais(id) ON DELETE CASCADE,
    numero_item INTEGER NOT NULL,
    
    -- ===== GRUPO prod - Produto =====
    codigo_produto VARCHAR(60) NOT NULL,
    codigo_ean VARCHAR(14),
    descricao VARCHAR(120) NOT NULL,
    ncm VARCHAR(8), -- Nomenclatura Comum do Mercosul
    nve VARCHAR(6), -- Nomenclatura de Valor Aduaneiro e Estatística
    cest VARCHAR(7), -- Código Especificador da Substituição Tributária
    codigo_ex_tipi VARCHAR(3),
    cfop VARCHAR(4) NOT NULL, -- Código Fiscal de Operações e Prestações
    unidade_comercial VARCHAR(6) NOT NULL,
    quantidade_comercial DECIMAL(15,4) NOT NULL,
    valor_unitario_comercial DECIMAL(21,10) NOT NULL,
    valor_total_bruto DECIMAL(15,2) NOT NULL,
    codigo_ean_tributavel VARCHAR(14),
    unidade_tributavel VARCHAR(6) NOT NULL,
    quantidade_tributavel DECIMAL(15,4) NOT NULL,
    valor_unitario_tributavel DECIMAL(21,10) NOT NULL,
    valor_frete DECIMAL(15,2) DEFAULT 0,
    valor_seguro DECIMAL(15,2) DEFAULT 0,
    valor_desconto DECIMAL(15,2) DEFAULT 0,
    valor_outras_despesas DECIMAL(15,2) DEFAULT 0,
    indicador_total CHAR(1) DEFAULT '1', -- 0-Não compõe, 1-Compõe total
    
    -- DI - Declaração de Importação
    -- (armazenada em tabela separada nf_itens_di)
    
    -- Detalhamento Específico
    numero_pedido_compra VARCHAR(15),
    item_pedido_compra INTEGER,
    numero_fci VARCHAR(36), -- Ficha de Conteúdo de Importação
    
    -- Rastreabilidade de produtos
    -- (armazenada em tabela separada nf_itens_rastreabilidade)
    
    -- Medicamentos
    numero_lote_medicamento VARCHAR(20),
    quantidade_lote_medicamento DECIMAL(11,3),
    data_fabricacao_medicamento DATE,
    data_validade_medicamento DATE,
    preco_maximo_consumidor DECIMAL(15,2),
    
    -- Combustível
    codigo_anp VARCHAR(9),
    descricao_anp VARCHAR(95),
    percentual_glp DECIMAL(5,2),
    percentual_gas_natural_nacional DECIMAL(5,2),
    percentual_gas_natural_importado DECIMAL(5,2),
    valor_partida DECIMAL(15,2),
    registro_codif VARCHAR(21),
    uf_consumo CHAR(2),
    
    -- Veículos novos
    tipo_operacao_veiculo CHAR(1),
    chassi VARCHAR(17),
    cor_veiculo VARCHAR(4),
    descricao_cor VARCHAR(40),
    potencia_motor VARCHAR(4),
    cilindradas VARCHAR(4),
    peso_liquido VARCHAR(9),
    peso_bruto VARCHAR(9),
    serie VARCHAR(9),
    tipo_combustivel VARCHAR(2),
    numero_motor VARCHAR(21),
    capacidade_maxima_tracao DECIMAL(9,4),
    distancia_eixos VARCHAR(4),
    ano_modelo VARCHAR(4),
    ano_fabricacao VARCHAR(4),
    tipo_pintura VARCHAR(1),
    tipo_veiculo VARCHAR(2),
    especie_veiculo VARCHAR(1),
    condicao_vin VARCHAR(1),
    condicao_veiculo VARCHAR(1),
    codigo_marca_modelo VARCHAR(6),
    codigo_cor_denatran VARCHAR(2),
    lotacao INTEGER,
    restricao_veiculo VARCHAR(1),
    
    -- Armamentos
    tipo_arma VARCHAR(1),
    numero_serie_arma VARCHAR(15),
    numero_serie_cano VARCHAR(15),
    descricao_arma VARCHAR(256),
    
    -- ===== GRUPO imposto - Tributos =====
    valor_total_tributos DECIMAL(15,2) DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de ICMS dos Itens
CREATE TABLE nf_itens_icms (
    id SERIAL PRIMARY KEY,
    nf_item_id INTEGER REFERENCES nf_itens(id) ON DELETE CASCADE,
    
    origem VARCHAR(1) NOT NULL, -- 0-Nacional, 1-Estrangeira Importação direta, etc
    cst VARCHAR(3), -- Código Situação Tributária
    csosn VARCHAR(4), -- Código Situação Operação Simples Nacional
    
    -- Modalidade de determinação da BC
    modalidade_bc VARCHAR(1), -- 0-Margem Valor Agregado, 1-Pauta, 2-Preço Tabelado, 3-Valor da operação
    percentual_reducao_bc DECIMAL(5,2),
    valor_bc DECIMAL(15,2) DEFAULT 0,
    aliquota DECIMAL(5,2),
    valor_icms DECIMAL(15,2) DEFAULT 0,
    valor_icms_desonerado DECIMAL(15,2) DEFAULT 0,
    motivo_desoneracao VARCHAR(2),
    
    -- FCP - Fundo de Combate à Pobreza
    percentual_fcp DECIMAL(5,2),
    valor_fcp DECIMAL(15,2) DEFAULT 0,
    
    -- ICMS Substituição Tributária
    modalidade_bc_st VARCHAR(1),
    percentual_mva_st DECIMAL(5,2), -- Margem de Valor Agregado
    percentual_reducao_bc_st DECIMAL(5,2),
    valor_bc_st DECIMAL(15,2) DEFAULT 0,
    aliquota_st DECIMAL(5,2),
    valor_icms_st DECIMAL(15,2) DEFAULT 0,
    
    -- FCP retido por ST
    percentual_fcp_st DECIMAL(5,2),
    valor_fcp_st DECIMAL(15,2) DEFAULT 0,
    
    -- ICMS Efetivo
    percentual_bc_operacao DECIMAL(5,2),
    aliquota_icms_uf_destino DECIMAL(5,2),
    aliquota_interestadual DECIMAL(5,2),
    percentual_provisorio DECIMAL(5,2),
    valor_icms_efetivo DECIMAL(15,2) DEFAULT 0,
    
    -- Crédito ICMS SN
    aliquota_credito_sn DECIMAL(5,2),
    valor_credito_sn DECIMAL(15,2) DEFAULT 0,
    
    -- ICMS Monofásico
    quantidade_bc_mono DECIMAL(15,4),
    aliquota_icms_mono DECIMAL(5,2),
    valor_icms_mono DECIMAL(15,2) DEFAULT 0,
    
    -- ICMS Operação Própria UF Destino
    valor_bc_uf_destino DECIMAL(15,2) DEFAULT 0,
    valor_bc_fcp_uf_destino DECIMAL(15,2) DEFAULT 0,
    percentual_fcp_uf_destino DECIMAL(5,2),
    aliquota_interna_uf_destino DECIMAL(5,2),
    aliquota_interestadual_uf_envolvidas DECIMAL(5,2),
    percentual_provisorio_partilha DECIMAL(5,2),
    valor_icms_uf_destino DECIMAL(15,2) DEFAULT 0,
    valor_icms_uf_remetente DECIMAL(15,2) DEFAULT 0,
    valor_fcp_uf_destino DECIMAL(15,2) DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de IPI dos Itens
CREATE TABLE nf_itens_ipi (
    id SERIAL PRIMARY KEY,
    nf_item_id INTEGER REFERENCES nf_itens(id) ON DELETE CASCADE,
    
    cnpj_produtor VARCHAR(14),
    codigo_selo_controle VARCHAR(60),
    quantidade_selo_controle INTEGER,
    codigo_enquadramento_legal VARCHAR(3),
    
    cst VARCHAR(2) NOT NULL,
    
    -- IPI Tributado
    valor_bc DECIMAL(15,2) DEFAULT 0,
    quantidade_unidade DECIMAL(15,4),
    aliquota DECIMAL(5,2),
    valor_unidade DECIMAL(15,4),
    valor_ipi DECIMAL(15,2) DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de II (Imposto de Importação) dos Itens
CREATE TABLE nf_itens_ii (
    id SERIAL PRIMARY KEY,
    nf_item_id INTEGER REFERENCES nf_itens(id) ON DELETE CASCADE,
    
    valor_bc DECIMAL(15,2) NOT NULL,
    valor_despesas_aduaneiras DECIMAL(15,2) DEFAULT 0,
    valor_iof DECIMAL(15,2) DEFAULT 0,
    valor_ii DECIMAL(15,2) NOT NULL,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de PIS dos Itens
CREATE TABLE nf_itens_pis (
    id SERIAL PRIMARY KEY,
    nf_item_id INTEGER REFERENCES nf_itens(id) ON DELETE CASCADE,
    
    cst VARCHAR(2) NOT NULL,
    
    -- PIS Tributado
    valor_bc DECIMAL(15,2) DEFAULT 0,
    aliquota DECIMAL(5,2),
    quantidade_vendida DECIMAL(15,4),
    aliquota_reais DECIMAL(15,4),
    valor_pis DECIMAL(15,2) DEFAULT 0,
    
    -- PIS ST
    valor_bc_st DECIMAL(15,2) DEFAULT 0,
    aliquota_st DECIMAL(5,2),
    quantidade_vendida_st DECIMAL(15,4),
    aliquota_reais_st DECIMAL(15,4),
    valor_pis_st DECIMAL(15,2) DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de COFINS dos Itens
CREATE TABLE nf_itens_cofins (
    id SERIAL PRIMARY KEY,
    nf_item_id INTEGER REFERENCES nf_itens(id) ON DELETE CASCADE,
    
    cst VARCHAR(2) NOT NULL,
    
    -- COFINS Tributado
    valor_bc DECIMAL(15,2) DEFAULT 0,
    aliquota DECIMAL(5,2),
    quantidade_vendida DECIMAL(15,4),
    aliquota_reais DECIMAL(15,4),
    valor_cofins DECIMAL(15,2) DEFAULT 0,
    
    -- COFINS ST
    valor_bc_st DECIMAL(15,2) DEFAULT 0,
    aliquota_st DECIMAL(5,2),
    quantidade_vendida_st DECIMAL(15,4),
    aliquota_reais_st DECIMAL(15,4),
    valor_cofins_st DECIMAL(15,2) DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de ISSQN (ISS) dos Itens
CREATE TABLE nf_itens_issqn (
    id SERIAL PRIMARY KEY,
    nf_item_id INTEGER REFERENCES nf_itens(id) ON DELETE CASCADE,
    
    valor_bc DECIMAL(15,2) NOT NULL,
    aliquota DECIMAL(5,2) NOT NULL,
    valor_issqn DECIMAL(15,2) NOT NULL,
    codigo_municipio_incidencia VARCHAR(7),
    codigo_servico VARCHAR(20), -- Lista de serviços LC 116/2003
    valor_deducao DECIMAL(15,2) DEFAULT 0,
    valor_outras_retencoes DECIMAL(15,2) DEFAULT 0,
    valor_desconto_incondicionado DECIMAL(15,2) DEFAULT 0,
    valor_desconto_condicionado DECIMAL(15,2) DEFAULT 0,
    valor_retencao_iss DECIMAL(15,2) DEFAULT 0,
    indicador_iss VARCHAR(1), -- 1-Exigível, 2-Não incidência, etc
    codigo_servico_municipio VARCHAR(20),
    codigo_municipio_geracao_credito VARCHAR(7),
    codigo_pais VARCHAR(4),
    numero_processo VARCHAR(30),
    indicador_incentivo_fiscal VARCHAR(1), -- 1-Sim, 2-Não
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Declaração de Importação dos Itens
CREATE TABLE nf_itens_di (
    id SERIAL PRIMARY KEY,
    nf_item_id INTEGER REFERENCES nf_itens(id) ON DELETE CASCADE,
    
    numero_di VARCHAR(12) NOT NULL,
    data_registro DATE NOT NULL,
    local_desembaraco VARCHAR(60) NOT NULL,
    uf_desembaraco CHAR(2) NOT NULL,
    data_desembaraco DATE NOT NULL,
    tipo_via_transporte VARCHAR(1), -- 1-Marítima, 2-Fluvial, etc
    valor_afrmm DECIMAL(15,2), -- Adicional de Frete para Renovação da Marinha Mercante
    tipo_intermediacao VARCHAR(1), -- 1-Importação por conta própria, 2-Por conta e ordem, 3-Encomenda
    cnpj_adquirente VARCHAR(14),
    uf_adquirente CHAR(2),
    codigo_exportador VARCHAR(60),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Adições da DI
CREATE TABLE nf_itens_di_adicoes (
    id SERIAL PRIMARY KEY,
    di_id INTEGER REFERENCES nf_itens_di(id) ON DELETE CASCADE,
    
    numero_adicao INTEGER NOT NULL,
    numero_sequencial INTEGER NOT NULL,
    codigo_fabricante VARCHAR(60),
    valor_desconto DECIMAL(15,2),
    numero_drawback INTEGER,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Rastreabilidade dos Itens
CREATE TABLE nf_itens_rastreabilidade (
    id SERIAL PRIMARY KEY,
    nf_item_id INTEGER REFERENCES nf_itens(id) ON DELETE CASCADE,
    
    numero_lote VARCHAR(20) NOT NULL,
    quantidade_lote DECIMAL(11,3) NOT NULL,
    data_fabricacao DATE NOT NULL,
    data_validade DATE NOT NULL,
    codigo_agregacao VARCHAR(20),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Transporte
CREATE TABLE nf_transporte (
    id SERIAL PRIMARY KEY,
    nota_fiscal_id INTEGER REFERENCES notas_fiscais(id) ON DELETE CASCADE,
    
    modalidade_frete CHAR(1) NOT NULL, -- 0-Emitente, 1-Destinatário, 2-Terceiros, 9-Sem Frete
    
    -- Transportadora
    transportadora_cpf_cnpj VARCHAR(14),
    transportadora_nome VARCHAR(60),
    transportadora_inscricao_estadual VARCHAR(14),
    transportadora_endereco VARCHAR(60),
    transportadora_municipio VARCHAR(60),
    transportadora_uf CHAR(2),
    
    -- Retenção ICMS Transporte
    valor_servico DECIMAL(15,2),
    valor_bc_retencao_icms DECIMAL(15,2),
    aliquota_retencao DECIMAL(5,2),
    valor_icms_retido DECIMAL(15,2),
    cfop_transporte VARCHAR(4),
    codigo_municipio_ocorrencia VARCHAR(7),
    
    -- Veículo de Transporte
    placa_veiculo VARCHAR(8),
    uf_veiculo CHAR(2),
    rntc VARCHAR(20), -- Registro Nacional Transportador de Carga
    
    -- Reboque/Vagão
    -- (armazenado em tabela separada nf_transporte_reboque)
    
    -- Identificação Balsa/Vagão/Container
    identificacao VARCHAR(20),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Reboques/Vagões do Transporte
CREATE TABLE nf_transporte_reboque (
    id SERIAL PRIMARY KEY,
    transporte_id INTEGER REFERENCES nf_transporte(id) ON DELETE CASCADE,
    
    placa VARCHAR(8) NOT NULL,
    uf CHAR(2) NOT NULL,
    rntc VARCHAR(20),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Volumes Transportados
CREATE TABLE nf_transporte_volumes (
    id SERIAL PRIMARY KEY,
    transporte_id INTEGER REFERENCES nf_transporte(id) ON DELETE CASCADE,
    
    quantidade INTEGER,
    especie VARCHAR(60),
    marca VARCHAR(60),
    numeracao VARCHAR(60),
    peso_liquido DECIMAL(15,3),
    peso_bruto DECIMAL(15,3),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Lacres dos Volumes
CREATE TABLE nf_transporte_volumes_lacres (
    id SERIAL PRIMARY KEY,
    volume_id INTEGER REFERENCES nf_transporte_volumes(id) ON DELETE CASCADE,
    
    numero_lacre VARCHAR(60) NOT NULL,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Cobrança/Fatura
CREATE TABLE nf_cobranca (
    id SERIAL PRIMARY KEY,
    nota_fiscal_id INTEGER REFERENCES notas_fiscais(id) ON DELETE CASCADE,
    
    numero_fatura VARCHAR(60),
    valor_original DECIMAL(15,2),
    valor_desconto DECIMAL(15,2),
    valor_liquido DECIMAL(15,2),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Duplicatas
CREATE TABLE nf_duplicatas (
    id SERIAL PRIMARY KEY,
    cobranca_id INTEGER REFERENCES nf_cobranca(id) ON DELETE CASCADE,
    
    numero_duplicata VARCHAR(60),
    data_vencimento DATE,
    valor DECIMAL(15,2) NOT NULL,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Pagamentos
CREATE TABLE nf_pagamentos (
    id SERIAL PRIMARY KEY,
    nota_fiscal_id INTEGER REFERENCES notas_fiscais(id) ON DELETE CASCADE,
    
    indicador_pagamento VARCHAR(1), -- 0-À Vista, 1-A Prazo
    forma_pagamento VARCHAR(2) NOT NULL, -- 01-Dinheiro, 02-Cheque, 03-Cartão Crédito, etc
    valor_pagamento DECIMAL(15,2) NOT NULL,
    
    -- Dados do Cartão (se aplicável)
    tipo_integracao VARCHAR(1), -- 1-Integrado, 2-Não integrado
    cnpj_credenciadora VARCHAR(14),
    bandeira_cartao VARCHAR(2), -- 01-Visa, 02-Mastercard, etc
    numero_autorizacao VARCHAR(20),
    
    -- Pagamento Instantâneo (PIX)
    cnpj_psp VARCHAR(14),
    end_to_end_id VARCHAR(60),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Carta de Correção Eletrônica (CCe)
CREATE TABLE nf_cce (
    id SERIAL PRIMARY KEY,
    nota_fiscal_id INTEGER REFERENCES notas_fiscais(id) ON DELETE CASCADE,
    
    sequencia_evento INTEGER NOT NULL,
    data_hora_evento TIMESTAMP NOT NULL,
    correcao TEXT NOT NULL,
    
    -- Protocolo do evento
    tipo_ambiente VARCHAR(1),
    versao_aplicativo VARCHAR(20),
    numero_protocolo VARCHAR(15),
    data_hora_recebimento TIMESTAMP,
    codigo_status VARCHAR(3),
    motivo_status VARCHAR(255),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Processamento/Lote
CREATE TABLE nf_processamento (
    id SERIAL PRIMARY KEY,
    nota_fiscal_id INTEGER REFERENCES notas_fiscais(id),
    
    tipo_processamento VARCHAR(20) CHECK (tipo_processamento IN ('autorizacao', 'cancelamento', 'inutilizacao', 'cce')),
    numero_lote VARCHAR(15),
    numero_recibo VARCHAR(15),
    data_hora_envio TIMESTAMP,
    tempo_medio INTEGER, -- em segundos
    
    -- Status do processamento
    codigo_status VARCHAR(3),
    motivo_status VARCHAR(255),
    
    xml_enviado TEXT,
    xml_retorno TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Informações de Combustível (específico)
CREATE TABLE nf_itens_combustivel (
    id SERIAL PRIMARY KEY,
    nf_item_id INTEGER REFERENCES nf_itens(id) ON DELETE CASCADE,
    
    codigo_anp VARCHAR(9) NOT NULL,
    percentual_glp DECIMAL(5,2),
    percentual_gas_natural_nacional DECIMAL(5,2),
    percentual_gas_natural_importado DECIMAL(5,2),
    valor_partida DECIMAL(15,2),
    codigo_if VARCHAR(21), -- CODIF
    uf_consumo CHAR(2),
    
    base_calculo_cide DECIMAL(15,2),
    aliquota_cide DECIMAL(15,4),
    valor_cide DECIMAL(15,2),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- ÍNDICES PARA PERFORMANCE
-- ============================================================================

-- Empresas
CREATE INDEX idx_empresas_cpf_cnpj ON empresas(cpf_cnpj);
CREATE INDEX idx_empresas_tipo ON empresas(tipo_pessoa);

-- Notas Fiscais
CREATE INDEX idx_nf_chave_acesso ON notas_fiscais(chave_acesso);
CREATE INDEX idx_nf_numero ON notas_fiscais(numero_nf, serie, modelo);
CREATE INDEX idx_nf_emitente ON notas_fiscais(emitente_id);
CREATE INDEX idx_nf_destinatario ON notas_fiscais(destinatario_id);
CREATE INDEX idx_nf_data_emissao ON notas_fiscais(data_hora_emissao);
CREATE INDEX idx_nf_status ON notas_fiscais(status);
CREATE INDEX idx_nf_tipo_operacao ON notas_fiscais(tipo_operacao);
CREATE INDEX idx_nf_finalidade ON notas_fiscais(finalidade_emissao);
CREATE INDEX idx_nf_valor ON notas_fiscais(valor_total_nota);

-- Itens
CREATE INDEX idx_nf_itens_nota ON nf_itens(nota_fiscal_id);
CREATE INDEX idx_nf_itens_produto ON nf_itens(codigo_produto);
CREATE INDEX idx_nf_itens_ncm ON nf_itens(ncm);
CREATE INDEX idx_nf_itens_cfop ON nf_itens(cfop);

-- Impostos
CREATE INDEX idx_nf_itens_icms_item ON nf_itens_icms(nf_item_id);
CREATE INDEX idx_nf_itens_ipi_item ON nf_itens_ipi(nf_item_id);
CREATE INDEX idx_nf_itens_pis_item ON nf_itens_pis(nf_item_id);
CREATE INDEX idx_nf_itens_cofins_item ON nf_itens_cofins(nf_item_id);

-- Pagamentos
CREATE INDEX idx_nf_pagamentos_nota ON nf_pagamentos(nota_fiscal_id);
CREATE INDEX idx_nf_pagamentos_forma ON nf_pagamentos(forma_pagamento);

-- Transporte
CREATE INDEX idx_nf_transporte_nota ON nf_transporte(nota_fiscal_id);

-- ============================================================================
-- TRIGGERS
-- ============================================================================

-- Trigger para atualizar updated_at automaticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_empresas_updated_at 
    BEFORE UPDATE ON empresas
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_notas_fiscais_updated_at 
    BEFORE UPDATE ON notas_fiscais
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- VIEWS ÚTEIS
-- ============================================================================

-- View com resumo das notas fiscais
CREATE OR REPLACE VIEW vw_notas_fiscais_resumo AS
SELECT 
    nf.id,
    nf.chave_acesso,
    nf.numero_nf,
    nf.serie,
    nf.data_hora_emissao,
    nf.natureza_operacao,
    nf.tipo_operacao,
    nf.status,
    e_emit.razao_social AS emitente,
    e_emit.cpf_cnpj AS emitente_cpf_cnpj,
    e_dest.razao_social AS destinatario,
    e_dest.cpf_cnpj AS destinatario_cpf_cnpj,
    nf.valor_total_produtos,
    nf.valor_total_nota,
    nf.valor_icms,
    nf.valor_ipi,
    nf.valor_pis,
    nf.valor_cofins,
    COUNT(i.id) AS quantidade_itens
FROM notas_fiscais nf
LEFT JOIN empresas e_emit ON nf.emitente_id = e_emit.id
LEFT JOIN empresas e_dest ON nf.destinatario_id = e_dest.id
LEFT JOIN nf_itens i ON nf.id = i.nota_fiscal_id
GROUP BY 
    nf.id, e_emit.razao_social, e_emit.cpf_cnpj, 
    e_dest.razao_social, e_dest.cpf_cnpj;

-- View com itens detalhados
CREATE OR REPLACE VIEW vw_nf_itens_completo AS
SELECT 
    nf.chave_acesso,
    nf.numero_nf,
    nf.serie,
    i.numero_item,
    i.codigo_produto,
    i.descricao,
    i.ncm,
    i.cfop,
    i.quantidade_comercial,
    i.valor_unitario_comercial,
    i.valor_total_bruto,
    icms.valor_bc AS icms_bc,
    icms.valor_icms,
    ipi.valor_ipi,
    pis.valor_pis,
    cofins.valor_cofins
FROM nf_itens i
INNER JOIN notas_fiscais nf ON i.nota_fiscal_id = nf.id
LEFT JOIN nf_itens_icms icms ON i.id = icms.nf_item_id
LEFT JOIN nf_itens_ipi ipi ON i.id = ipi.nf_item_id
LEFT JOIN nf_itens_pis pis ON i.id = pis.nf_item_id
LEFT JOIN nf_itens_cofins cofins ON i.id = cofins.nf_item_id;

-- ============================================================================
-- COMENTÁRIOS NAS TABELAS
-- ============================================================================

COMMENT ON TABLE notas_fiscais IS 'Tabela principal de Notas Fiscais Eletrônicas (NF-e) - Layout 4.00';
COMMENT ON TABLE empresas IS 'Cadastro de empresas (emitentes e destinatários)';
COMMENT ON TABLE nf_itens IS 'Itens/Produtos das Notas Fiscais';
COMMENT ON TABLE nf_itens_icms IS 'Dados de ICMS dos itens';
COMMENT ON TABLE nf_itens_ipi IS 'Dados de IPI dos itens';
COMMENT ON TABLE nf_itens_pis IS 'Dados de PIS dos itens';
COMMENT ON TABLE nf_itens_cofins IS 'Dados de COFINS dos itens';
COMMENT ON TABLE nf_pagamentos IS 'Formas de pagamento da nota fiscal';
COMMENT ON TABLE nf_transporte IS 'Informações de transporte';
COMMENT ON TABLE nf_cobranca IS 'Dados de cobrança/fatura';
COMMENT ON TABLE nf_duplicatas IS 'Duplicatas da nota fiscal';
COMMENT ON TABLE nf_cce IS 'Cartas de Correção Eletrônica';



ALTER TABLE nf_itens_ipi ALTER COLUMN cst DROP NOT NULL;

-- PIS - tornar CST opcional
ALTER TABLE nf_itens_pis ALTER COLUMN cst DROP NOT NULL;

-- COFINS - tornar CST opcional
ALTER TABLE nf_itens_cofins ALTER COLUMN cst DROP NOT NULL;

-- ISSQN - tornar campos opcionais
ALTER TABLE nf_itens_issqn ALTER COLUMN valor_bc DROP NOT NULL;
ALTER TABLE nf_itens_issqn ALTER COLUMN aliquota DROP NOT NULL;
ALTER TABLE nf_itens_issqn ALTER COLUMN valor_issqn DROP NOT NULL;

-- ============================================================================
-- FIM DO SCHEMA
-- ============================================================================
