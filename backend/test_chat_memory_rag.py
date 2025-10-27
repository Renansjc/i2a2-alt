"""Test script for ChatMemory with CrewAI RAG functionality"""

import sys
from pathlib import Path
import time
import os

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Verify OPENAI_API_KEY is set
if not os.getenv("OPENAI_API_KEY"):
    print("⚠️  WARNING: OPENAI_API_KEY not found in environment!")
    print("   CrewAI RAG features require OpenAI API key for embeddings.")
    print("   Please set OPENAI_API_KEY in your .env file.")
    print("   Continuing with limited functionality...\n")

from memory.chat_memory import ChatMemory


def test_basic_memory():
    """Test basic memory operations"""
    print("=" * 70)
    print("Test 1: Basic Memory Operations with RAG")
    print("=" * 70)
    
    memory = ChatMemory()
    session_id = "test-session-001"
    
    # Add messages
    print("\n✓ Adding messages to memory...")
    memory.add_message(session_id, "user", "Olá, quantas notas fiscais foram emitidas em janeiro?")
    memory.add_message(session_id, "assistant", "Foram emitidas 150 notas fiscais em janeiro de 2024.")
    memory.add_message(session_id, "user", "E qual foi o valor total?")
    memory.add_message(session_id, "assistant", "O valor total foi R$ 1.250.000,00.")
    
    # Get history
    history = memory.get_history(session_id)
    print(f"✓ Retrieved {len(history)} messages from history")
    
    # Get context summary
    print("\n--- Context Summary ---")
    summary = memory.get_context_summary(session_id)
    print(summary)
    
    return memory, session_id


def test_semantic_search(memory, session_id):
    """Test semantic search capabilities"""
    print("\n" + "=" * 70)
    print("Test 2: Semantic Search with RAG")
    print("=" * 70)
    
    # Add more context
    print("\n✓ Adding more messages about different topics...")
    memory.add_message(session_id, "user", "Quais empresas emitiram mais notas?")
    memory.add_message(session_id, "assistant", "As empresas que mais emitiram foram: Empresa ABC (45 notas) e Empresa XYZ (38 notas).")
    memory.add_message(session_id, "user", "Mostre os produtos mais vendidos")
    memory.add_message(session_id, "assistant", "Os produtos mais vendidos foram: Produto A (1200 unidades) e Produto B (980 unidades).")
    
    # Wait a bit for vectorization to complete
    print("✓ Waiting for vectorization...")
    time.sleep(2)
    
    # Test semantic search
    print("\n--- Semantic Search Results ---")
    
    queries = [
        "valores monetários",
        "empresas",
        "produtos vendidos"
    ]
    
    for query in queries:
        print(f"\nQuery: '{query}'")
        results = memory.search_relevant_context(session_id, query, max_results=3)
        
        if results:
            print(f"Found {len(results)} relevant messages:")
            for i, result in enumerate(results, 1):
                print(f"  {i}. [{result['role']}] {result['content'][:60]}...")
                print(f"     Relevance: {result.get('relevance_score', 'N/A')}")
        else:
            print("  No results found (RAG may need initialization)")


def test_entity_tracking(memory, session_id):
    """Test entity tracking"""
    print("\n" + "=" * 70)
    print("Test 3: Entity Tracking")
    print("=" * 70)
    
    # Add messages with entities
    print("\n✓ Adding messages with entities...")
    memory.add_message(
        session_id, 
        "user", 
        "Mostre as notas fiscais da empresa ACME Corp CNPJ 12.345.678/0001-90"
    )
    memory.add_message(
        session_id,
        "assistant",
        "Encontrei 23 notas fiscais da ACME Corp no valor total de R$ 450.000,00"
    )
    
    # Wait for entity extraction
    time.sleep(1)
    
    # Get entities
    print("\n--- Extracted Entities ---")
    entities = memory.get_session_entities(session_id)
    
    if entities:
        print(f"Found {len(entities)} entities:")
        for entity in entities:
            print(f"  - {entity[:80]}...")
    else:
        print("  No entities extracted yet (may need more processing time)")


def test_memory_stats(memory):
    """Test memory statistics"""
    print("\n" + "=" * 70)
    print("Test 4: Memory Statistics")
    print("=" * 70)
    
    stats = memory.get_memory_stats()
    
    print(f"\n✓ Total Sessions: {stats['total_sessions']}")
    print(f"✓ Total Cached Messages: {stats['total_cached_messages']}")
    print(f"✓ Storage Directory: {stats['storage_directory']}")
    print(f"✓ Max Recent Messages: {stats['max_recent_messages']}")
    
    print("\n--- Memory Systems ---")
    for system, status in stats['memory_systems'].items():
        print(f"  {system}: {status}")
    
    print("\n--- Session Details ---")
    for session_id, details in stats['sessions'].items():
        print(f"  {session_id}:")
        print(f"    Messages: {details['message_count']}")
        print(f"    Last Activity: {details['last_activity']}")


def test_history_limit(memory):
    """Test history limit enforcement"""
    print("\n" + "=" * 70)
    print("Test 5: History Limit (4 messages)")
    print("=" * 70)
    
    session_id = "test-session-limit"
    
    print("\n✓ Adding 6 messages (should keep only last 4)...")
    for i in range(6):
        role = "user" if i % 2 == 0 else "assistant"
        memory.add_message(session_id, role, f"Message number {i+1}")
    
    history = memory.get_history(session_id)
    print(f"✓ History contains {len(history)} messages (expected: 4)")
    
    if len(history) == 4:
        print("✓ History limit working correctly!")
        print("\nKept messages:")
        for msg in history:
            print(f"  - {msg['role']}: {msg['content']}")
    else:
        print(f"✗ ERROR: Expected 4 messages, got {len(history)}")


def test_multiple_sessions(memory):
    """Test multiple independent sessions"""
    print("\n" + "=" * 70)
    print("Test 6: Multiple Independent Sessions")
    print("=" * 70)
    
    sessions = ["session-A", "session-B", "session-C"]
    
    print("\n✓ Creating 3 independent sessions...")
    for session in sessions:
        memory.add_message(session, "user", f"Message in {session}")
        memory.add_message(session, "assistant", f"Response for {session}")
    
    print(f"✓ Total sessions: {memory.get_session_count()}")
    
    for session in sessions:
        count = memory.get_message_count(session)
        print(f"  {session}: {count} messages")


def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("ChatMemory with CrewAI RAG - Comprehensive Test Suite")
    print("=" * 70)
    
    try:
        # Test 1: Basic operations
        memory, session_id = test_basic_memory()
        
        # Test 2: Semantic search
        test_semantic_search(memory, session_id)
        
        # Test 3: Entity tracking
        test_entity_tracking(memory, session_id)
        
        # Test 4: Memory stats
        test_memory_stats(memory)
        
        # Test 5: History limit
        test_history_limit(memory)
        
        # Test 6: Multiple sessions
        test_multiple_sessions(memory)
        
        print("\n" + "=" * 70)
        print("All tests completed! ✓")
        print("=" * 70)
        
        print("\n📝 Note: Some RAG features (semantic search, entity extraction)")
        print("   may show limited results on first run. The vector database")
        print("   improves with more data and usage over time.")
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
