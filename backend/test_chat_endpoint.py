"""Test script for chat endpoint implementation

This script tests the chat endpoint functionality without running the full server.
It verifies that all components work together correctly.
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from api.routes.chat import router, initialize_chat_services
from api.models.requests import ChatRequest
from agents.crew import NFeCrew
from memory.chat_memory import ChatMemory
from utils.logger import get_logger

logger = get_logger(__name__)


def test_chat_endpoint_initialization():
    """Test that chat services can be initialized"""
    print("=" * 60)
    print("Test 1: Chat Services Initialization")
    print("=" * 60)
    
    try:
        # Initialize services
        crew = NFeCrew()
        memory = ChatMemory()
        
        # Initialize chat services
        initialize_chat_services(crew, memory)
        
        print("✓ NFeCrew initialized successfully")
        print("✓ ChatMemory initialized successfully")
        print("✓ Chat services initialized successfully")
        print()
        return True
        
    except Exception as e:
        print(f"✗ Initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_chat_request_validation():
    """Test that ChatRequest validation works"""
    print("=" * 60)
    print("Test 2: ChatRequest Validation")
    print("=" * 60)
    
    try:
        # Valid request
        valid_request = ChatRequest(
            session_id="test-session-123",
            message="Quantas notas fiscais foram emitidas?"
        )
        print(f"✓ Valid request created: {valid_request.session_id}")
        
        # Test validation - empty message
        try:
            invalid_request = ChatRequest(
                session_id="test-session",
                message="   "  # Only whitespace
            )
            print("✗ Should have failed validation for empty message")
            return False
        except Exception as e:
            print(f"✓ Correctly rejected empty message: {type(e).__name__}")
        
        # Test validation - empty session_id
        try:
            invalid_request = ChatRequest(
                session_id="   ",  # Only whitespace
                message="Test message"
            )
            print("✗ Should have failed validation for empty session_id")
            return False
        except Exception as e:
            print(f"✓ Correctly rejected empty session_id: {type(e).__name__}")
        
        print()
        return True
        
    except Exception as e:
        print(f"✗ Validation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_memory_integration():
    """Test that memory integration works"""
    print("=" * 60)
    print("Test 3: Memory Integration")
    print("=" * 60)
    
    try:
        memory = ChatMemory()
        session_id = "test-session-memory"
        
        # Add messages
        memory.add_message(session_id, "user", "Olá")
        memory.add_message(session_id, "assistant", "Olá! Como posso ajudar?")
        memory.add_message(session_id, "user", "Quantas notas fiscais existem?")
        
        print(f"✓ Added 3 messages to session '{session_id}'")
        
        # Get history
        history = memory.get_history(session_id)
        print(f"✓ Retrieved history: {len(history)} messages")
        
        # Verify history format
        assert len(history) == 3, f"Expected 3 messages, got {len(history)}"
        assert history[0]["role"] == "user", "First message should be from user"
        assert history[0]["content"] == "Olá", "First message content mismatch"
        
        print("✓ History format is correct")
        
        # Test context summary
        summary = memory.get_context_summary(session_id)
        print(f"✓ Context summary generated ({len(summary)} chars)")
        
        # Test session exists
        assert memory.session_exists(session_id), "Session should exist"
        print(f"✓ Session exists check works")
        
        # Test message count
        count = memory.get_message_count(session_id)
        assert count == 3, f"Expected 3 messages, got {count}"
        print(f"✓ Message count is correct: {count}")
        
        # Test clear session
        cleared = memory.clear_session(session_id)
        assert cleared, "Session should be cleared"
        assert not memory.session_exists(session_id), "Session should not exist after clear"
        print(f"✓ Session cleared successfully")
        
        print()
        return True
        
    except Exception as e:
        print(f"✗ Memory integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_crew_initialization():
    """Test that NFeCrew can be initialized"""
    print("=" * 60)
    print("Test 4: NFeCrew Initialization")
    print("=" * 60)
    
    try:
        crew = NFeCrew()
        
        print("✓ NFeCrew instance created")
        
        # Check that agents are configured
        assert crew.agents_config is not None, "Agents config should be loaded"
        print(f"✓ Agents config loaded: {list(crew.agents_config.keys())}")
        
        # Check that tasks are configured
        assert crew.tasks_config is not None, "Tasks config should be loaded"
        print(f"✓ Tasks config loaded: {list(crew.tasks_config.keys())}")
        
        # Check that tools are initialized
        assert crew.db_tool is not None, "DatabaseQueryTool should be initialized"
        assert crew.schema_tool is not None, "SchemaInfoTool should be initialized"
        print("✓ Tools initialized successfully")
        
        print()
        return True
        
    except Exception as e:
        print(f"✗ Crew initialization test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_router_configuration():
    """Test that router is configured correctly"""
    print("=" * 60)
    print("Test 5: Router Configuration")
    print("=" * 60)
    
    try:
        # Check router prefix
        assert router.prefix == "/api/chat", f"Expected prefix '/api/chat', got '{router.prefix}'"
        print(f"✓ Router prefix is correct: {router.prefix}")
        
        # Check router tags
        assert "chat" in router.tags, "Router should have 'chat' tag"
        print(f"✓ Router tags are correct: {router.tags}")
        
        # Check routes
        print(f"✓ Router has {len(router.routes)} routes:")
        for route in router.routes:
            methods = ", ".join(route.methods) if hasattr(route, 'methods') else "N/A"
            print(f"  - {route.path} [{methods}]")
        
        # Verify main endpoint exists
        # The main POST endpoint should exist
        main_endpoint_exists = any(
            "/api/chat" in route.path and hasattr(route, 'methods') and "POST" in route.methods
            for route in router.routes
        )
        assert main_endpoint_exists, "Main POST chat endpoint should exist"
        print("✓ Main POST chat endpoint exists")
        
        print()
        return True
        
    except Exception as e:
        print(f"✗ Router configuration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("CHAT ENDPOINT IMPLEMENTATION TESTS")
    print("=" * 60 + "\n")
    
    results = []
    
    # Run tests
    results.append(("Initialization", test_chat_endpoint_initialization()))
    results.append(("Request Validation", test_chat_request_validation()))
    results.append(("Memory Integration", test_memory_integration()))
    results.append(("Crew Initialization", test_crew_initialization()))
    results.append(("Router Configuration", test_router_configuration()))
    
    # Print summary
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{status}: {test_name}")
    
    print()
    print(f"Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ All tests passed! Chat endpoint implementation is working correctly.")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed. Please review the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
