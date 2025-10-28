"""
Test script for CrewAI Tools

This script tests the DatabaseQueryTool and SchemaInfoTool to ensure
they work correctly with the Supabase database.

Run this script to verify the tools are functioning properly before
integrating them into the CrewAI agents.
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from agents.tools.database_tool import DatabaseQueryTool, DatabaseJoinQueryTool
from agents.tools.schema_tool import SchemaInfoTool, SchemaSearchTool
import json


def print_section(title: str):
    """Print a formatted section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def print_result(result: str):
    """Print a formatted result"""
    try:
        parsed = json.loads(result)
        print(json.dumps(parsed, ensure_ascii=False, indent=2))
    except:
        print(result)


def test_schema_info_tool():
    """Test SchemaInfoTool"""
    print_section("Testing SchemaInfoTool")
    
    tool = SchemaInfoTool()
    
    # Test 1: Get list of tables
    print("Test 1: Get list of main tables")
    result = tool._run(query_type="tables")
    print_result(result)
    
    # Test 2: Get info about specific table
    print("\nTest 2: Get info about 'notas_fiscais' table")
    result = tool._run(query_type="table", table_name="notas_fiscais")
    print_result(result)
    
    # Test 3: Get relationships
    print("\nTest 3: Get table relationships")
    result = tool._run(query_type="relationships")
    print_result(result)
    
    # Test 4: Get common queries
    print("\nTest 4: Get common query examples")
    result = tool._run(query_type="queries")
    print_result(result)


def test_schema_search_tool():
    """Test SchemaSearchTool"""
    print_section("Testing SchemaSearchTool")
    
    tool = SchemaSearchTool()
    
    # Test 1: Search for ICMS
    print("Test 1: Search for 'icms'")
    result = tool._run(search_term="icms")
    print_result(result)
    
    # Test 2: Search for payment
    print("\nTest 2: Search for 'pagamento'")
    result = tool._run(search_term="pagamento")
    print_result(result)


def test_database_query_tool():
    """Test DatabaseQueryTool"""
    print_section("Testing DatabaseQueryTool")
    
    tool = DatabaseQueryTool()
    
    # Test 1: Query empresas table
    print("Test 1: Query empresas table (limit 5)")
    result = tool._run(
        table="empresas",
        select="id,cpf_cnpj,razao_social,nome_fantasia",
        limit=5
    )
    print_result(result)
    
    # Test 2: Query notas_fiscais with filters
    print("\nTest 2: Query notas_fiscais with status filter (limit 5)")
    result = tool._run(
        table="notas_fiscais",
        select="id,numero_nf,serie,valor_total_nota,status,data_hora_emissao",
        filters={"status": "eq.autorizada"},
        order="data_hora_emissao.desc",
        limit=5
    )
    print_result(result)
    
    # Test 3: Query with value filter
    print("\nTest 3: Query notas_fiscais with value > 1000 (limit 5)")
    result = tool._run(
        table="notas_fiscais",
        select="numero_nf,serie,valor_total_nota,data_hora_emissao",
        filters={"valor_total_nota": "gt.1000"},
        order="valor_total_nota.desc",
        limit=5
    )
    print_result(result)
    
    # Test 4: Query nf_itens
    print("\nTest 4: Query nf_itens (limit 5)")
    result = tool._run(
        table="nf_itens",
        select="id,nota_fiscal_id,numero_item,descricao,quantidade_comercial,valor_total_bruto",
        order="id.desc",
        limit=5
    )
    print_result(result)


def test_database_join_query_tool():
    """Test DatabaseJoinQueryTool"""
    print_section("Testing DatabaseJoinQueryTool")
    
    tool = DatabaseJoinQueryTool()
    
    # Test 1: Query notas_fiscais with emitente data
    print("Test 1: Query notas_fiscais with emitente data (limit 3)")
    result = tool._run(
        base_table="notas_fiscais",
        select="id,numero_nf,serie,valor_total_nota,empresas!emitente_id(razao_social,cpf_cnpj)",
        filters={"status": "eq.autorizada"},
        order="data_hora_emissao.desc",
        limit=3
    )
    print_result(result)
    
    # Test 2: Query nf_itens with nota fiscal data
    print("\nTest 2: Query nf_itens with nota fiscal data (limit 3)")
    result = tool._run(
        base_table="nf_itens",
        select="id,numero_item,descricao,valor_total_bruto,notas_fiscais(numero_nf,serie)",
        order="id.desc",
        limit=3
    )
    print_result(result)


def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("  CrewAI Tools Test Suite")
    print("  Testing Database and Schema Tools")
    print("=" * 80)
    
    try:
        # Test schema tools first (no database connection needed)
        test_schema_info_tool()
        test_schema_search_tool()
        
        # Test database tools (requires Supabase connection)
        test_database_query_tool()
        test_database_join_query_tool()
        
        print_section("All Tests Completed Successfully! ✅")
        
    except Exception as e:
        print_section("Test Failed ❌")
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
