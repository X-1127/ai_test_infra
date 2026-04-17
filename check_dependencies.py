import sys

try:
    import fastapi
    print(f"[OK] FastAPI: {fastapi.__version__}")
except ImportError as e:
    print(f"[FAIL] FastAPI: Not installed - {e}")

try:
    import uvicorn
    print(f"[OK] Uvicorn: {uvicorn.__version__}")
except ImportError as e:
    print(f"[FAIL] Uvicorn: Not installed - {e}")

try:
    import pydantic
    print(f"[OK] Pydantic: {pydantic.__version__}")
except ImportError as e:
    print(f"[FAIL] Pydantic: Not installed - {e}")

try:
    import yaml
    print(f"[OK] PyYAML: Installed")
except ImportError as e:
    print(f"[FAIL] PyYAML: Not installed - {e}")

try:
    import httpx
    print(f"[OK] httpx: {httpx.__version__}")
except ImportError as e:
    print(f"[FAIL] httpx: Not installed - {e}")

try:
    import pytest
    print(f"[OK] pytest: {pytest.__version__}")
except ImportError as e:
    print(f"[FAIL] pytest: Not installed - {e}")

try:
    import pytest_asyncio
    print(f"[OK] pytest-asyncio: Installed")
except ImportError as e:
    print(f"[FAIL] pytest-asyncio: Not installed - {e}")

print(f"\nPython version: {sys.version}")
print("All dependencies checked!")