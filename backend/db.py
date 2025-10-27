"""
Script para importar XML de NF-e para Supabase
Usa service_role key para bypass de RLS
"""

import xml.etree.ElementTree as ET
from datetime import datetime
from decimal import Decimal
import requests
import json

# Configurações do Supabase

# Headers para requisições
HEADERS = {
    "apikey": SERVICE_KEY,
    "Authorization": f"Bearer {SERVICE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

# Namespace padrão da NF-e
NS = {'nfe': 'http://www.portalfiscal.inf.br/nfe'}


class SupabaseNFeImporter:
    def __init__(self):
        self.base_url = f"{SUPABASE_URL}/rest/v1"
    
    def get_text(self, element, path, default=None):
        """Busca texto em elemento XML com namespace"""
        if element is None:
            return default
        found = element.find(path, NS)
        return found.text if found is not None else default
    
    def parse_decimal(self, value, default="0"):
        """Converte string para string decimal (para JSON)"""
        if value is None or value == '':
            return default
        return value
    
    def parse_datetime(self, value):
        """Converte string ISO para formato PostgreSQL"""
        if not value:
            return None
        # Remove timezone para simplificar
        value = value.split('-03:00')[0].split('+')[0].split('Z')[0]
        return value
    
    def supabase_request(self, method, endpoint, data=None, params=None):
        """Faz requisição HTTP para Supabase"""
        url = f"{self.base_url}/{endpoint}"
        
        try:
            if method == "GET":
                response = requests.get(url, headers=HEADERS, params=params)
            elif method == "POST":
                response = requests.post(url, headers=HEADERS, json=data)
            elif method == "PATCH":
                response = requests.patch(url, headers=HEADERS, json=data)
            
            response.raise_for_status()
            return response.json() if response.text else None
        
        except requests.exceptions.RequestException as e:
            print(f"Erro na requisição: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Resposta: {e.response.text}")
            raise
    
    def insert_or_get_empresa(self, cnpj_cpf, dados_empresa):
        """Insere ou retorna ID da empresa usando Supabase"""
        # Verifica se empresa já existe
        result = self.supabase_request(
            "GET", 
            "empresas",
            params={"cpf_cnpj": f"eq.{cnpj_cpf}", "select": "id"}
        )
        
        if result and len(result) > 0:
            return result[0]['id']
        
        # Insere nova empresa
        result = self.supabase_request(
            "POST",
            "empresas",
            data=dados_empresa
        )
        
        return result[0]['id'] if result else None
    
    def parse_xml(self, xml_path):
        """Faz o parse do XML da NF-e"""
        tree = ET.parse(xml_path)
        root = tree.getroot()
        
        # Localiza o nó principal
        nfe = root.find('.//nfe:NFe', NS)
        inf_nfe = nfe.find('nfe:infNFe', NS)
        prot_nfe = root.find('.//nfe:protNFe', NS)
        
        return {
            'inf_nfe': inf_nfe,
            'prot_nfe': prot_nfe,
            'xml_completo': ET.tostring(root, encoding='unicode')
        }
    
    def import_nfe(self, xml_path):
        """Importa NF-e completa do XML para o Supabase"""
        try:
            print("🔄 Iniciando importação...")
            
            # Parse do XML
            parsed = self.parse_xml(xml_path)
            inf_nfe = parsed['inf_nfe']
            prot_nfe = parsed['prot_nfe']
            
            # ===== EXTRAIR DADOS DO XML =====
            
            # Identificação (ide)
            ide = inf_nfe.find('nfe:ide', NS)
            chave_acesso = inf_nfe.get('Id').replace('NFe', '')
            
            print(f"📄 Processando NF-e: {chave_acesso}")
            
            # Emitente (emit)
            emit = inf_nfe.find('nfe:emit', NS)
            emit_cnpj = self.get_text(emit, 'nfe:CNPJ')
            emit_cpf = self.get_text(emit, 'nfe:CPF')
            emit_doc = emit_cnpj or emit_cpf
            
            ender_emit = emit.find('nfe:enderEmit', NS)
            dados_emitente = {
                'tipo_pessoa': 'juridica' if emit_cnpj else 'fisica',
                'cpf_cnpj': emit_doc,
                'razao_social': self.get_text(emit, 'nfe:xNome'),
                'nome_fantasia': self.get_text(emit, 'nfe:xFant'),
                'inscricao_estadual': self.get_text(emit, 'nfe:IE'),
                'regime_tributario': self.get_text(emit, 'nfe:CRT'),
                'logradouro': self.get_text(ender_emit, 'nfe:xLgr'),
                'numero': self.get_text(ender_emit, 'nfe:nro'),
                'complemento': self.get_text(ender_emit, 'nfe:xCpl'),
                'bairro': self.get_text(ender_emit, 'nfe:xBairro'),
                'codigo_municipio': self.get_text(ender_emit, 'nfe:cMun'),
                'nome_municipio': self.get_text(ender_emit, 'nfe:xMun'),
                'uf': self.get_text(ender_emit, 'nfe:UF'),
                'cep': self.get_text(ender_emit, 'nfe:CEP'),
                'codigo_pais': self.get_text(ender_emit, 'nfe:cPais'),
                'nome_pais': self.get_text(ender_emit, 'nfe:xPais'),
                'telefone': self.get_text(ender_emit, 'nfe:fone'),
                'email': None,
                'indicador_ie_destinatario': None
            }
            
            print("🏢 Processando emitente...")
            emitente_id = self.insert_or_get_empresa(emit_doc, dados_emitente)
            
            # Destinatário (dest)
            dest = inf_nfe.find('nfe:dest', NS)
            dest_cnpj = self.get_text(dest, 'nfe:CNPJ')
            dest_cpf = self.get_text(dest, 'nfe:CPF')
            dest_doc = dest_cnpj or dest_cpf
            
            ender_dest = dest.find('nfe:enderDest', NS)
            dados_destinatario = {
                'tipo_pessoa': 'juridica' if dest_cnpj else 'fisica',
                'cpf_cnpj': dest_doc,
                'razao_social': self.get_text(dest, 'nfe:xNome'),
                'nome_fantasia': None,
                'inscricao_estadual': self.get_text(dest, 'nfe:IE'),
                'regime_tributario': None,
                'logradouro': self.get_text(ender_dest, 'nfe:xLgr'),
                'numero': self.get_text(ender_dest, 'nfe:nro'),
                'complemento': self.get_text(ender_dest, 'nfe:xCpl'),
                'bairro': self.get_text(ender_dest, 'nfe:xBairro'),
                'codigo_municipio': self.get_text(ender_dest, 'nfe:cMun'),
                'nome_municipio': self.get_text(ender_dest, 'nfe:xMun'),
                'uf': self.get_text(ender_dest, 'nfe:UF'),
                'cep': self.get_text(ender_dest, 'nfe:CEP'),
                'codigo_pais': self.get_text(ender_dest, 'nfe:cPais'),
                'nome_pais': self.get_text(ender_dest, 'nfe:xPais'),
                'telefone': self.get_text(ender_dest, 'nfe:fone'),
                'email': self.get_text(dest, 'nfe:email'),
                'indicador_ie_destinatario': self.get_text(dest, 'nfe:indIEDest')
            }
            
            print("👤 Processando destinatário...")
            destinatario_id = self.insert_or_get_empresa(dest_doc, dados_destinatario)
            
            # Totalizadores
            total = inf_nfe.find('nfe:total/nfe:ICMSTot', NS)
            
            # Informações Adicionais
            inf_adic = inf_nfe.find('nfe:infAdic', NS)
            
            # Protocolo
            inf_prot = prot_nfe.find('nfe:infProt', NS) if prot_nfe is not None else None
            
            # Responsável Técnico
            inf_resp_tec = inf_nfe.find('nfe:infRespTec', NS)
            
            # ===== INSERIR NOTA FISCAL =====
            print("💾 Inserindo nota fiscal...")
            
            nota_data = {
                'chave_acesso': chave_acesso,
                'codigo_uf': self.get_text(ide, 'nfe:cUF'),
                'codigo_numerico_aleatorio': self.get_text(ide, 'nfe:cNF'),
                'natureza_operacao': self.get_text(ide, 'nfe:natOp'),
                'modelo': self.get_text(ide, 'nfe:mod'),
                'serie': self.get_text(ide, 'nfe:serie'),
                'numero_nf': int(self.get_text(ide, 'nfe:nNF')),
                'data_hora_emissao': self.parse_datetime(self.get_text(ide, 'nfe:dhEmi')),
                'tipo_operacao': self.get_text(ide, 'nfe:tpNF'),
                'destino_operacao': self.get_text(ide, 'nfe:idDest'),
                'codigo_municipio_fato_gerador': self.get_text(ide, 'nfe:cMunFG'),
                'tipo_impressao': self.get_text(ide, 'nfe:tpImp'),
                'tipo_emissao': self.get_text(ide, 'nfe:tpEmis'),
                'digito_verificador': self.get_text(ide, 'nfe:cDV'),
                'tipo_ambiente': self.get_text(ide, 'nfe:tpAmb'),
                'finalidade_emissao': self.get_text(ide, 'nfe:finNFe'),
                'consumidor_final': self.get_text(ide, 'nfe:indFinal'),
                'presenca_comprador': self.get_text(ide, 'nfe:indPres'),
                'indicador_intermediador': self.get_text(ide, 'nfe:indIntermed'),
                'processo_emissao': self.get_text(ide, 'nfe:procEmi'),
                'versao_processo': self.get_text(ide, 'nfe:verProc'),
                'emitente_id': emitente_id,
                'destinatario_id': destinatario_id,
                'valor_total_produtos': self.parse_decimal(self.get_text(total, 'nfe:vProd')),
                'valor_frete': self.parse_decimal(self.get_text(total, 'nfe:vFrete')),
                'valor_seguro': self.parse_decimal(self.get_text(total, 'nfe:vSeg')),
                'valor_desconto': self.parse_decimal(self.get_text(total, 'nfe:vDesc')),
                'valor_imposto_importacao': self.parse_decimal(self.get_text(total, 'nfe:vII')),
                'valor_ipi': self.parse_decimal(self.get_text(total, 'nfe:vIPI')),
                'valor_ipi_devolvido': self.parse_decimal(self.get_text(total, 'nfe:vIPIDevol')),
                'valor_pis': self.parse_decimal(self.get_text(total, 'nfe:vPIS')),
                'valor_cofins': self.parse_decimal(self.get_text(total, 'nfe:vCOFINS')),
                'valor_outras_despesas': self.parse_decimal(self.get_text(total, 'nfe:vOutro')),
                'valor_total_nota': self.parse_decimal(self.get_text(total, 'nfe:vNF')),
                'base_calculo_icms': self.parse_decimal(self.get_text(total, 'nfe:vBC')),
                'valor_icms': self.parse_decimal(self.get_text(total, 'nfe:vICMS')),
                'valor_icms_desonerado': self.parse_decimal(self.get_text(total, 'nfe:vICMSDeson')),
                'valor_fcp': self.parse_decimal(self.get_text(total, 'nfe:vFCP')),
                'base_calculo_icms_st': self.parse_decimal(self.get_text(total, 'nfe:vBCST')),
                'valor_icms_st': self.parse_decimal(self.get_text(total, 'nfe:vST')),
                'valor_fcp_st': self.parse_decimal(self.get_text(total, 'nfe:vFCPST')),
                'valor_fcp_st_retido': self.parse_decimal(self.get_text(total, 'nfe:vFCPSTRet')),
                'informacoes_complementares': self.get_text(inf_adic, 'nfe:infCpl') if inf_adic is not None else None,
                'informacoes_fisco': self.get_text(inf_adic, 'nfe:infAdFisco') if inf_adic is not None else None,
                'modalidade_frete': self.get_text(inf_nfe.find('nfe:transp', NS), 'nfe:modFrete'),
                'status': 'autorizada' if inf_prot is not None else 'emitida',
                'tipo_ambiente_protocolo': self.get_text(inf_prot, 'nfe:tpAmb') if inf_prot is not None else None,
                'versao_aplicativo_recepcao': self.get_text(inf_prot, 'nfe:verAplic') if inf_prot is not None else None,
                'numero_protocolo': self.get_text(inf_prot, 'nfe:nProt') if inf_prot is not None else None,
                'digest_value': self.get_text(inf_prot, 'nfe:digVal') if inf_prot is not None else None,
                'data_hora_recebimento': self.parse_datetime(self.get_text(inf_prot, 'nfe:dhRecbto')) if inf_prot is not None else None,
                'codigo_status': self.get_text(inf_prot, 'nfe:cStat') if inf_prot is not None else None,
                'motivo_status': self.get_text(inf_prot, 'nfe:xMotivo') if inf_prot is not None else None,
                'resp_tecnico_cnpj': self.get_text(inf_resp_tec, 'nfe:CNPJ') if inf_resp_tec is not None else None,
                'resp_tecnico_contato': self.get_text(inf_resp_tec, 'nfe:xContato') if inf_resp_tec is not None else None,
                'resp_tecnico_email': self.get_text(inf_resp_tec, 'nfe:email') if inf_resp_tec is not None else None,
                'resp_tecnico_telefone': self.get_text(inf_resp_tec, 'nfe:fone') if inf_resp_tec is not None else None,
                'xml_completo': parsed['xml_completo']
            }
            
            result = self.supabase_request("POST", "notas_fiscais", data=nota_data)
            nf_id = result[0]['id'] if result else None
            
            if not nf_id:
                raise Exception("Erro ao inserir nota fiscal")
            
            # ===== INSERIR REFERÊNCIAS =====
            nf_refs = ide.findall('nfe:NFref', NS)
            for nf_ref in nf_refs:
                ref_nfe = self.get_text(nf_ref, 'nfe:refNFe')
                if ref_nfe:
                    self.supabase_request("POST", "nf_referencias", data={
                        'nota_fiscal_id': nf_id,
                        'tipo': 'nfe',
                        'chave_acesso_referenciada': ref_nfe
                    })
            
            # ===== INSERIR ITENS =====
            print("📦 Inserindo itens...")
            detalhes = inf_nfe.findall('nfe:det', NS)
            
            for det in detalhes:
                numero_item = int(det.get('nItem'))
                prod = det.find('nfe:prod', NS)
                imposto = det.find('nfe:imposto', NS)
                
                item_data = {
                    'nota_fiscal_id': nf_id,
                    'numero_item': numero_item,
                    'codigo_produto': self.get_text(prod, 'nfe:cProd'),
                    'codigo_ean': self.get_text(prod, 'nfe:cEAN'),
                    'descricao': self.get_text(prod, 'nfe:xProd'),
                    'ncm': self.get_text(prod, 'nfe:NCM'),
                    'cfop': self.get_text(prod, 'nfe:CFOP'),
                    'unidade_comercial': self.get_text(prod, 'nfe:uCom'),
                    'quantidade_comercial': self.parse_decimal(self.get_text(prod, 'nfe:qCom')),
                    'valor_unitario_comercial': self.parse_decimal(self.get_text(prod, 'nfe:vUnCom')),
                    'valor_total_bruto': self.parse_decimal(self.get_text(prod, 'nfe:vProd')),
                    'codigo_ean_tributavel': self.get_text(prod, 'nfe:cEANTrib'),
                    'unidade_tributavel': self.get_text(prod, 'nfe:uTrib'),
                    'quantidade_tributavel': self.parse_decimal(self.get_text(prod, 'nfe:qTrib')),
                    'valor_unitario_tributavel': self.parse_decimal(self.get_text(prod, 'nfe:vUnTrib')),
                    'valor_frete': self.parse_decimal(self.get_text(prod, 'nfe:vFrete')),
                    'valor_seguro': self.parse_decimal(self.get_text(prod, 'nfe:vSeg')),
                    'valor_desconto': self.parse_decimal(self.get_text(prod, 'nfe:vDesc')),
                    'valor_outras_despesas': self.parse_decimal(self.get_text(prod, 'nfe:vOutro')),
                    'indicador_total': self.get_text(prod, 'nfe:indTot', '1')
                }
                
                result = self.supabase_request("POST", "nf_itens", data=item_data)
                item_id = result[0]['id'] if result else None
                
                if not item_id:
                    continue
                
                # ICMS
                icms = imposto.find('.//nfe:ICMS/*', NS)
                if icms is not None:
                    icms_data = {
                        'nf_item_id': item_id,
                        'origem': self.get_text(icms, 'nfe:orig'),
                        'cst': self.get_text(icms, 'nfe:CST'),
                        'csosn': self.get_text(icms, 'nfe:CSOSN'),
                        'modalidade_bc': self.get_text(icms, 'nfe:modBC'),
                        'percentual_reducao_bc': self.parse_decimal(self.get_text(icms, 'nfe:pRedBC')),
                        'valor_bc': self.parse_decimal(self.get_text(icms, 'nfe:vBC')),
                        'aliquota': self.parse_decimal(self.get_text(icms, 'nfe:pICMS')),
                        'valor_icms': self.parse_decimal(self.get_text(icms, 'nfe:vICMS'))
                    }
                    self.supabase_request("POST", "nf_itens_icms", data=icms_data)
                
                # IPI
                ipi = imposto.find('.//nfe:IPI/*', NS)
                if ipi is not None:
                    ipi_data = {
                        'nf_item_id': item_id,
                        'cst': self.get_text(ipi, 'nfe:CST'),
                        'valor_bc': self.parse_decimal(self.get_text(ipi, 'nfe:vBC')),
                        'aliquota': self.parse_decimal(self.get_text(ipi, 'nfe:pIPI')),
                        'valor_ipi': self.parse_decimal(self.get_text(ipi, 'nfe:vIPI'))
                    }
                    self.supabase_request("POST", "nf_itens_ipi", data=ipi_data)
                
                # PIS
                pis = imposto.find('.//nfe:PIS/*', NS)
                if pis is not None:
                    pis_data = {
                        'nf_item_id': item_id,
                        'cst': self.get_text(pis, 'nfe:CST'),
                        'valor_bc': self.parse_decimal(self.get_text(pis, 'nfe:vBC')),
                        'aliquota': self.parse_decimal(self.get_text(pis, 'nfe:pPIS')),
                        'valor_pis': self.parse_decimal(self.get_text(pis, 'nfe:vPIS'))
                    }
                    self.supabase_request("POST", "nf_itens_pis", data=pis_data)
                
                # COFINS
                cofins = imposto.find('.//nfe:COFINS/*', NS)
                if cofins is not None:
                    cofins_data = {
                        'nf_item_id': item_id,
                        'cst': self.get_text(cofins, 'nfe:CST'),
                        'valor_bc': self.parse_decimal(self.get_text(cofins, 'nfe:vBC')),
                        'aliquota': self.parse_decimal(self.get_text(cofins, 'nfe:pCOFINS')),
                        'valor_cofins': self.parse_decimal(self.get_text(cofins, 'nfe:vCOFINS'))
                    }
                    self.supabase_request("POST", "nf_itens_cofins", data=cofins_data)
            
            # ===== INSERIR TRANSPORTE =====
            print("🚚 Inserindo transporte...")
            transp = inf_nfe.find('nfe:transp', NS)
            if transp is not None:
                transp_data = {
                    'nota_fiscal_id': nf_id,
                    'modalidade_frete': self.get_text(transp, 'nfe:modFrete')
                }
                
                result = self.supabase_request("POST", "nf_transporte", data=transp_data)
                transp_id = result[0]['id'] if result else None
                
                # Volume
                if transp_id:
                    vol = transp.find('nfe:vol', NS)
                    if vol is not None:
                        vol_data = {
                            'transporte_id': transp_id,
                            'quantidade': int(self.get_text(vol, 'nfe:qVol', '0') or '0'),
                            'especie': self.get_text(vol, 'nfe:esp'),
                            'peso_liquido': self.parse_decimal(self.get_text(vol, 'nfe:pesoL')),
                            'peso_bruto': self.parse_decimal(self.get_text(vol, 'nfe:pesoB'))
                        }
                        self.supabase_request("POST", "nf_transporte_volumes", data=vol_data)
            
            # ===== INSERIR PAGAMENTO =====
            print("💳 Inserindo pagamento...")
            pagamentos = inf_nfe.findall('nfe:pag/nfe:detPag', NS)
            for pag in pagamentos:
                pag_data = {
                    'nota_fiscal_id': nf_id,
                    'indicador_pagamento': self.get_text(pag, 'nfe:indPag'),
                    'forma_pagamento': self.get_text(pag, 'nfe:tPag'),
                    'valor_pagamento': self.parse_decimal(self.get_text(pag, 'nfe:vPag'))
                }
                self.supabase_request("POST", "nf_pagamentos", data=pag_data)
            
            print(f"✅ NF-e {chave_acesso} importada com sucesso! (ID: {nf_id})")
            return nf_id
            
        except Exception as e:
            print(f"❌ Erro ao importar NF-e: {str(e)}")
            import traceback
            traceback.print_exc()
            raise


# ===== EXEMPLO DE USO =====
if __name__ == "__main__":
    # Caminho do XML
    xml_path = '42250802314041001583650100000616501312602792.xml'
    
    # Importar NF-e
    print("=" * 60)
    print("🚀 IMPORTADOR DE NF-e PARA SUPABASE")
    print("=" * 60)
    print()
    
    importer = SupabaseNFeImporter()
    nf_id = importer.import_nfe(xml_path)
    
    print()
    print("=" * 60)
    print(f"✨ Importação concluída! ID da nota: {nf_id}")
    print("=" * 60)