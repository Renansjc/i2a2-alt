"""
Teste rápido da SQL Query Tool
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

def test_sql_connection():
    """Testa conexão direta ao PostgreSQL"""
    print("=" * 60)
    print("Teste da SQL Query Tool")
    print("=" * 60)
    print()
    
    try:
        from agents.tools.sql_query_tool import SQLQueryTool
        
        tool = SQLQueryTool()
        
        # Teste 1: Contar todas as notas
        print("📊 Teste 1: Contar todas as notas fiscais")
        print("-" * 60)
        query1 = "SELECT COUNT(*) as total FROM notas_fiscais"
        print(f"Query: {query1}")
        result1 = tool._run(query1)
        print(f"Resultado:\n{result1}\n")
        
        # Teste 2: Contar notas autorizadas
        print("📊 Teste 2: Contar notas autorizadas")
        print("-" * 60)
        query2 = "SELECT COUNT(*) as total FROM notas_fiscais WHERE status = 'autorizada'"
        print(f"Query: {query2}")
        result2 = tool._run(query2)
        print(f"Resultado:\n{result2}\n")
        
        # Teste 3: Somar valores
        print("📊 Teste 3: Somar valores das notas")
        print("-" * 60)
        query3 = "SELECT SUM(valor_total_nota) as total FROM notas_fiscais"
        print(f"Query: {query3}")
        result3 = tool._run(query3)
        print(f"Resultado:\n{result3}\n")
        
        # Teste 4: Consulta com JOIN
        print("📊 Teste 4: Notas por empresa (com JOIN)")
        print("-" * 60)
        query4 = """
        SELECT 
            e.razao_social,
            COUNT(nf.id) as total_notas
        FROM empresas e
        LEFT JOIN notas_fiscais nf ON e.id = nf.emitente_id
        GROUP BY e.razao_social
        ORDER BY total_notas DESC
        LIMIT 5
        """
        print(f"Query: {query4}")
        result4 = tool._run(query4)
        print(f"Resultado:\n{result4}\n")
        
        print("=" * 60)
        print("✅ Todos os testes concluídos!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_sql_connection()
    sys.exit(0 if success else 1)
