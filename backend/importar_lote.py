#!/usr/bin/env python3
"""
Script para importar múltiplas NF-e de um diretório para o Supabase
Uso: python importar_lote.py <diretorio_com_xmls>
"""

import os
import sys
import time
from datetime import datetime
from importar_nfe_supabase import SupabaseNFeImporter

def formatar_tempo(segundos):
    """Formata segundos em formato legível"""
    if segundos < 60:
        return f"{segundos:.1f}s"
    minutos = int(segundos // 60)
    segundos_rest = segundos % 60
    return f"{minutos}m {segundos_rest:.1f}s"

def main():
    if len(sys.argv) < 2:
        print("=" * 70)
        print("📦 IMPORTADOR EM LOTE DE NF-e PARA SUPABASE")
        print("=" * 70)
        print()
        print("Uso: python importar_lote.py <diretorio_com_xmls>")
        print()
        print("Exemplo:")
        print("  python importar_lote.py ./notas_fiscais/")
        print()
        sys.exit(1)
    
    xml_dir = sys.argv[1]
    
    if not os.path.isdir(xml_dir):
        print(f"❌ Erro: '{xml_dir}' não é um diretório válido")
        sys.exit(1)
    
    # Listar XMLs
    xml_files = [f for f in os.listdir(xml_dir) if f.endswith('.xml')]
    
    if not xml_files:
        print(f"❌ Nenhum arquivo XML encontrado em '{xml_dir}'")
        sys.exit(1)
    
    print("=" * 70)
    print("📦 IMPORTADOR EM LOTE DE NF-e PARA SUPABASE")
    print("=" * 70)
    print()
    print(f"📁 Diretório: {xml_dir}")
    print(f"📄 Total de XMLs encontrados: {len(xml_files)}")
    print()
    
    resposta = input("Deseja continuar com a importação? (s/n): ")
    if resposta.lower() != 's':
        print("Operação cancelada.")
        sys.exit(0)
    
    print()
    print("🚀 Iniciando importação...")
    print("=" * 70)
    print()
    
    # Criar importador
    importer = SupabaseNFeImporter()
    
    # Contadores
    sucesso = 0
    erros = 0
    duplicados = 0
    
    # Log de erros
    log_erros = []
    
    # Tempo inicial
    tempo_inicio = time.time()
    
    # Processar cada XML
    for i, filename in enumerate(sorted(xml_files), 1):
        xml_path = os.path.join(xml_dir, filename)
        
        print(f"[{i}/{len(xml_files)}] Processando: {filename}")
        
        try:
            nf_id = importer.import_nfe(xml_path)
            sucesso += 1
            print(f"    ✅ Importada com sucesso! ID: {nf_id}")
            
        except Exception as e:
            erro_str = str(e)
            
            # Verificar se é erro de duplicação
            if 'duplicate key' in erro_str.lower() or 'unique constraint' in erro_str.lower():
                duplicados += 1
                print(f"    ⚠️  Já existe no banco (duplicada)")
            else:
                erros += 1
                print(f"    ❌ Erro: {erro_str[:100]}...")
                log_erros.append({
                    'arquivo': filename,
                    'erro': erro_str
                })
        
        print()
    
    # Tempo total
    tempo_total = time.time() - tempo_inicio
    
    # Relatório final
    print("=" * 70)
    print("📊 RELATÓRIO FINAL")
    print("=" * 70)
    print()
    print(f"Total de arquivos processados: {len(xml_files)}")
    print(f"✅ Importadas com sucesso:     {sucesso}")
    print(f"⚠️  Duplicadas (já existiam):   {duplicados}")
    print(f"❌ Erros:                       {erros}")
    print()
    print(f"⏱️  Tempo total: {formatar_tempo(tempo_total)}")
    
    if len(xml_files) > 0:
        tempo_medio = tempo_total / len(xml_files)
        print(f"⏱️  Tempo médio por NF-e: {formatar_tempo(tempo_medio)}")
    
    print()
    
    # Mostrar detalhes dos erros
    if log_erros:
        print("=" * 70)
        print("❌ DETALHES DOS ERROS")
        print("=" * 70)
        print()
        
        for erro in log_erros:
            print(f"Arquivo: {erro['arquivo']}")
            print(f"Erro: {erro['erro']}")
            print("-" * 70)
            print()
        
        # Salvar log de erros
        log_filename = f"erros_importacao_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(log_filename, 'w', encoding='utf-8') as f:
            f.write("LOG DE ERROS - IMPORTAÇÃO DE NF-e\n")
            f.write("=" * 70 + "\n")
            f.write(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write(f"Diretório: {xml_dir}\n")
            f.write("=" * 70 + "\n\n")
            
            for erro in log_erros:
                f.write(f"Arquivo: {erro['arquivo']}\n")
                f.write(f"Erro: {erro['erro']}\n")
                f.write("-" * 70 + "\n\n")
        
        print(f"📝 Log de erros salvo em: {log_filename}")
        print()
    
    print("=" * 70)
    
    # Código de saída
    if erros > 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
