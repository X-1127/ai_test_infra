import sys


def check_dependencies():
    dependencies = {
        "fastapi": "FastAPI",
        "uvicorn": "Uvicorn", 
        "pydantic": "Pydantic",
        "pydantic_settings": "Pydantic Settings",
        "yaml": "PyYAML",
        "httpx": "httpx",
        "pytest": "pytest",
        "pytest_asyncio": "pytest-asyncio"
    }
    
    missing = []
    
    for module, name in dependencies.items():
        try:
            if module == "pydantic_settings":
                import pydantic_settings
                print(f"[OK] {name}: Installed")
            elif module == "yaml":
                import yaml
                print(f"[OK] {name}: Installed")
            else:
                mod = __import__(module)
                version = getattr(mod, "__version__", "Unknown")
                print(f"[OK] {name}: {version}")
        except ImportError as e:
            print(f"[FAIL] {name}: Not installed - {e}")
            missing.append(name)
    
    print(f"\nPython version: {sys.version}")
    
    if missing:
        print(f"\nMissing dependencies: {', '.join(missing)}")
        print("Install with: pip install -e .[dev]")
        return False
    else:
        print("\nAll dependencies checked successfully!")
        return True


if __name__ == "__main__":
    success = check_dependencies()
    sys.exit(0 if success else 1)