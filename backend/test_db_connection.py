"""
Teste direto de conexão PostgreSQL
"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

# Pegar variáveis do .env
supabase_url = os.getenv('SUPABASE_URL')
db_password = os.getenv('SUPABASE_DB_PASSWORD')

# Extrair project ref da URL
project_ref = supabase_url.replace('https://', '').replace('http://', '').split('.')[0]

print("=" * 60)
print("Teste de Conexão PostgreSQL")
print("=" * 60)
print(f"Project Ref: {project_ref}")
print(f"Password: {db_password}")
print(f"Host: db.{project_ref}.supabase.co")
print()

# Tentar diferentes formatos de connection string
connection_strings = [
    # Formato 1: URL completa
    f"postgresql://postgres:{db_password}@db.{project_ref}.supabase.co:5432/postgres",
    
    # Formato 2: Com parâmetros separados
    {
        'host': f'db.{project_ref}.supabase.co',
        'port': 5432,
        'database': 'postgres',
        'user': 'postgres',
        'password': db_password
    }
]

for i, conn_str in enumerate(connection_strings, 1):
    print(f"Tentativa {i}:")
    print("-" * 60)
    
    try:
        if isinstance(conn_str, dict):
            print(f"Conectando com parâmetros: {conn_str['host']}")
            conn = psycopg2.connect(**conn_str)
        else:
            print(f"Conectando com URL: {conn_str[:50]}...")
            conn = psycopg2.connect(conn_str)
        
        # Testar query simples
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM notas_fiscais")
        result = cursor.fetchone()
        
        print(f"✅ SUCESSO! Total de notas: {result[0]}")
        
        cursor.close()
        conn.close()
        
        print()
        break
        
    except Exception as e:
        print(f"❌ ERRO: {e}")
        print()

print("=" * 60)
