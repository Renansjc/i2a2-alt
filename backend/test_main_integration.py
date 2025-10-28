"""
Integration test for main.py - tests actual startup and endpoints
"""

import sys
import os
import asyncio

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))


async def test_lifespan_startup():
    """Test that lifespan startup works"""
    print("Testing lifespan startup...")
    
    try:
        from main import app, nfe_crew, chat_memory, batch_processor, job_manager
        from fastapi.testclient import TestClient
        
        # Create test client (this triggers lifespan)
        with TestClient(app) as client:
            print("✓ Application started successfully")
            
            # Test health endpoint
            response = client.get("/health")
            assert response.status_code == 200
            data = response.json()
            print(f"  - Health check: {data['status']}")
            
            # Test detailed health endpoint
            response = client.get("/health/detailed")
            assert response.status_code == 200
            data = response.json()
            print(f"  - Detailed health: {data['status']}")
            
            # Check services
            services = data.get("services", {})
            
            if "crewai" in services:
                crewai_status = services["crewai"]
                print(f"  - CrewAI initialized: {crewai_status.get('initialized', False)}")
                if crewai_status.get('initialized'):
                    print(f"    Agents: {', '.join(crewai_status.get('agents', []))}")
                    print(f"    Model: {crewai_status.get('model', 'unknown')}")
            
            if "memory" in services:
                memory_status = services["memory"]
                print(f"  - Memory initialized: {memory_status.get('initialized', False)}")
                if memory_status.get('initialized'):
                    print(f"    Active sessions: {memory_status.get('active_sessions', 0)}")
            
            if "batch_processor" in services:
                batch_status = services["batch_processor"]
                print(f"  - Batch processor initialized: {batch_status.get('initialized', False)}")
                if batch_status.get('initialized'):
                    print(f"    Active jobs: {batch_status.get('active_jobs', 0)}")
            
            # Test root endpoint
            response = client.get("/")
            assert response.status_code == 200
            data = response.json()
            print(f"  - Root endpoint: {data['message']}")
            
            return True
            
    except Exception as e:
        print(f"✗ Lifespan startup failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run integration tests"""
    print("=" * 60)
    print("Main.py Integration Test")
    print("=" * 60)
    print()
    
    # Run async test
    result = asyncio.run(test_lifespan_startup())
    
    print("\n" + "=" * 60)
    if result:
        print("✓ Integration test passed!")
        print("\nThe application is ready to run:")
        print("  python main.py")
        print("  or")
        print("  uvicorn main:app --reload")
    else:
        print("✗ Integration test failed")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
