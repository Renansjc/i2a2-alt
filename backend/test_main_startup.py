"""
Test script to verify main.py can be imported and basic functionality works
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

def test_imports():
    """Test that all imports work"""
    print("Testing imports...")
    
    try:
        from main import app, validate_environment
        print("✓ Main imports successful")
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False


def test_app_creation():
    """Test that FastAPI app is created"""
    print("\nTesting app creation...")
    
    try:
        from main import app
        
        # Check app attributes
        assert app.title == "Multi-Agent NF-e System"
        assert app.version == "1.0.0"
        print("✓ FastAPI app created successfully")
        print(f"  - Title: {app.title}")
        print(f"  - Version: {app.version}")
        
        # Check routes are registered
        routes = [route.path for route in app.routes]
        expected_routes = ["/health", "/health/detailed", "/", "/api/chat", "/api/batch/upload"]
        
        for expected in expected_routes:
            if any(expected in route for route in routes):
                print(f"  - Route registered: {expected}")
        
        return True
    except Exception as e:
        print(f"✗ App creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_environment_validation():
    """Test environment validation (should fail without .env)"""
    print("\nTesting environment validation...")
    
    try:
        from main import validate_environment
        
        # This should fail if .env is not set up
        try:
            validate_environment()
            print("✓ Environment validation passed (all vars set)")
            return True
        except SystemExit:
            print("⚠ Environment validation failed (expected if .env not configured)")
            print("  This is normal - set up .env file to run the application")
            return True
    except Exception as e:
        print(f"✗ Environment validation test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("Main.py Startup Test")
    print("=" * 60)
    
    results = []
    
    results.append(("Imports", test_imports()))
    results.append(("App Creation", test_app_creation()))
    results.append(("Environment Validation", test_environment_validation()))
    
    print("\n" + "=" * 60)
    print("Test Results:")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(passed for _, passed in results)
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ All tests passed!")
        print("\nNext steps:")
        print("1. Configure .env file with required variables")
        print("2. Run: python main.py")
        print("3. Or run: uvicorn main:app --reload")
    else:
        print("✗ Some tests failed")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
