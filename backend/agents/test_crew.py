"""
Test script for NFeCrew implementation

This script tests the basic functionality of the NFeCrew without
actually calling the OpenAI API or database.
"""

import sys
import os
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

# Set dummy environment variables for testing
os.environ.setdefault("OPENAI_API_KEY", "sk-test-key-for-testing")
os.environ.setdefault("SUPABASE_URL", "https://test.supabase.co")
os.environ.setdefault("SUPABASE_SERVICE_KEY", "test-service-key")
os.environ.setdefault("ENABLE_SEMANTIC_SEARCH", "false")  # Disable for testing

from agents.crew import NFeCrew


def test_crew_initialization():
    """Test that NFeCrew can be initialized"""
    print("Testing NFeCrew initialization...")
    
    try:
        crew = NFeCrew()
        print("✓ NFeCrew initialized successfully")
        
        # Check that configurations were loaded
        assert crew.agents_config is not None, "Agents config not loaded"
        assert crew.tasks_config is not None, "Tasks config not loaded"
        print("✓ Configurations loaded successfully")
        
        # Check that tools were initialized
        assert crew.db_tool is not None, "DatabaseQueryTool not initialized"
        assert crew.schema_tool is not None, "SchemaInfoTool not initialized"
        print("✓ Tools initialized successfully")
        
        return True
    except Exception as e:
        print(f"✗ Error initializing NFeCrew: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_agent_creation():
    """Test that agents can be created"""
    print("\nTesting agent creation...")
    
    try:
        crew = NFeCrew()
        
        # Test SQL Specialist
        sql_agent = crew.sql_specialist()
        assert sql_agent is not None, "SQL Specialist not created"
        assert len(sql_agent.tools) == 4, f"SQL Specialist should have 4 tools, has {len(sql_agent.tools)}"
        print("✓ SQL Specialist created successfully")
        
        # Test Conversation Specialist
        conv_agent = crew.conversation_specialist()
        assert conv_agent is not None, "Conversation Specialist not created"
        assert len(conv_agent.tools) == 0, "Conversation Specialist should have no tools"
        print("✓ Conversation Specialist created successfully")
        
        # Test coordenador
        coord_agent = crew.coordenador()
        assert coord_agent is not None, "coordenador not created"
        assert coord_agent.allow_delegation == True, "coordenador should allow delegation"
        print("✓ coordenador created successfully")
        
        return True
    except Exception as e:
        print(f"✗ Error creating agents: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_task_creation():
    """Test that tasks can be created"""
    print("\nTesting task creation...")
    
    try:
        crew = NFeCrew()
        
        # Test all tasks
        tasks = [
            ("analyze_intent_task", crew.analyze_intent_task),
            ("execute_sql_query_task", crew.execute_sql_query_task),
            ("format_response_task", crew.format_response_task),
            ("direct_conversation_task", crew.direct_conversation_task)
        ]
        
        for task_name, task_method in tasks:
            task = task_method()
            assert task is not None, f"{task_name} not created"
            print(f"✓ {task_name} created successfully")
        
        return True
    except Exception as e:
        print(f"✗ Error creating tasks: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_crew_creation():
    """Test that the crew can be created"""
    print("\nTesting crew creation...")
    
    try:
        nfe_crew = NFeCrew()
        crew_instance = nfe_crew.crew()
        
        assert crew_instance is not None, "Crew not created"
        # In hierarchical process, manager is separate from agents list
        assert len(crew_instance.agents) == 2, f"Crew should have 2 agents (manager is separate), has {len(crew_instance.agents)}"
        print("✓ Crew created successfully with 2 agents + 1 manager")
        
        # Check hierarchical process
        from crewai import Process
        assert crew_instance.process == Process.hierarchical, "Crew should use hierarchical process"
        print("✓ Crew configured with hierarchical process")
        
        # Check memory enabled
        assert crew_instance.memory == True, "Crew should have memory enabled"
        print("✓ Crew memory enabled")
        
        return True
    except Exception as e:
        print(f"✗ Error creating crew: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_schema_summary():
    """Test that schema summary can be generated"""
    print("\nTesting schema summary generation...")
    
    try:
        crew = NFeCrew()
        schema = crew._get_schema_summary()
        
        assert schema is not None, "Schema summary not generated"
        assert "empresas" in schema, "Schema should mention empresas table"
        assert "notas_fiscais" in schema, "Schema should mention notas_fiscais table"
        assert "nf_itens" in schema, "Schema should mention nf_itens table"
        print("✓ Schema summary generated successfully")
        
        return True
    except Exception as e:
        print(f"✗ Error generating schema summary: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("NFeCrew Implementation Tests")
    print("=" * 60)
    
    tests = [
        test_crew_initialization,
        test_agent_creation,
        test_task_creation,
        test_crew_creation,
        test_schema_summary
    ]
    
    results = []
    for test in tests:
        result = test()
        results.append(result)
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("\n✓ All tests passed!")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())

