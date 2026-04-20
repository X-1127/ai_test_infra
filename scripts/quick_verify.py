#!/usr/bin/env python3
"""
Quick verification script
"""
import requests
import time

BASE_URL = "http://localhost:8000"

def test_basic():
    print("Test 1: Basic chat")
    try:
        r = requests.post(f"{BASE_URL}/v1/chat/completions", json={
            "messages": [{"role": "user", "content": "Hello"}]
        }, timeout=5)
        if r.status_code == 200:
            print("PASS: Basic chat works")
            return True
        else:
            print(f"FAIL: Status {r.status_code}")
            return False
    except Exception as e:
        print(f"FAIL: {e}")
        return False

def test_yaml():
    print("\nTest 2: YAML config")
    try:
        # Enable
        r = requests.put(f"{BASE_URL}/v1/config/yaml/enable")
        if r.status_code != 200:
            print("FAIL: Could not enable YAML")
            return False
        
        # Check
        r = requests.get(f"{BASE_URL}/v1/config/yaml")
        data = r.json()
        
        if data["enabled"] and len(data["config"]["rules"]) > 0:
            print(f"PASS: YAML enabled with {len(data['config']['rules'])} rules")
            return True
        else:
            print("FAIL: YAML not properly enabled")
            return False
    except Exception as e:
        print(f"FAIL: {e}")
        return False

def test_rule():
    print("\nTest 3: Rule matching")
    try:
        r = requests.post(f"{BASE_URL}/v1/chat/completions", json={
            "messages": [{"role": "user", "content": "你好"}]
        }, timeout=5)
        
        if r.status_code == 200:
            content = r.json()["choices"][0]["message"]["content"]
            if "你好" in content or "帮助" in content:
                print(f"PASS: Rule matched - {content[:30]}...")
                return True
            else:
                print(f"FAIL: Rule not matched - {content}")
                return False
        else:
            print(f"FAIL: Status {r.status_code}")
            return False
    except Exception as e:
        print(f"FAIL: {e}")
        return False

def test_delay():
    print("\nTest 4: Delay injection")
    try:
        # Reset first
        requests.post(f"{BASE_URL}/v1/config/injection/reset")
        
        # Enable delay
        requests.put(f"{BASE_URL}/v1/config/injection", json={
            "delay": {"enabled": True, "min_delay_ms": 100, "max_delay_ms": 200}
        })
        
        # Test
        start = time.time()
        r = requests.post(f"{BASE_URL}/v1/chat/completions", json={
            "messages": [{"role": "user", "content": "Test"}]
        }, timeout=10)
        elapsed = (time.time() - start) * 1000
        
        # Reset
        requests.post(f"{BASE_URL}/v1/config/injection/reset")
        
        if 80 <= elapsed <= 300:
            print(f"PASS: Delay works ({elapsed:.0f}ms)")
            return True
        else:
            print(f"FAIL: Delay out of range ({elapsed:.0f}ms)")
            return False
    except Exception as e:
        print(f"FAIL: {e}")
        return False

def test_fault():
    print("\nTest 5: Fault injection")
    try:
        # Enable fault
        requests.put(f"{BASE_URL}/v1/config/injection", json={
            "fault": {
                "enabled": True,
                "fault_type": "http_error",
                "http_status_code": 503,
                "error_message": "Service unavailable",
                "probability": 1.0
            }
        })
        
        # Test
        r = requests.post(f"{BASE_URL}/v1/chat/completions", json={
            "messages": [{"role": "user", "content": "Test"}]
        }, timeout=5)
        
        # Reset
        requests.post(f"{BASE_URL}/v1/config/injection/reset")
        
        if r.status_code == 503:
            print("PASS: Fault injection works (503)")
            return True
        else:
            print(f"FAIL: Expected 503, got {r.status_code}")
            return False
    except Exception as e:
        print(f"FAIL: {e}")
        return False

def test_performance():
    print("\nTest 6: Performance")
    try:
        # Reset configs
        requests.post(f"{BASE_URL}/v1/config/injection/reset")
        requests.put(f"{BASE_URL}/v1/config/yaml/disable")
        
        start = time.time()
        for i in range(10):
            r = requests.post(f"{BASE_URL}/v1/chat/completions", json={
                "messages": [{"role": "user", "content": f"Test{i}"}]
            }, timeout=5)
            if r.status_code != 200:
                print(f"FAIL: Request {i} failed")
                return False
        
        total = time.time() - start
        avg = total / 10
        
        print(f"PASS: 10 requests in {total:.2f}s (avg {avg*1000:.0f}ms)")
        return avg < 1.0  # < 1 second average
    except Exception as e:
        print(f"FAIL: {e}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("Quick Verification")
    print("="*60)
    
    # Check server
    try:
        r = requests.get(f"{BASE_URL}/health", timeout=2)
        if r.status_code != 200:
            print("\nERROR: Server not healthy")
            exit(1)
    except:
        print("\nERROR: Server not running")
        print("Start with: uvicorn app.main:app --host 0.0.0.0 --port 8000")
        exit(1)
    
    # Run tests
    results = [
        ("Basic Chat", test_basic()),
        ("YAML Config", test_yaml()),
        ("Rule Matching", test_rule()),
        ("Delay Injection", test_delay()),
        ("Fault Injection", test_fault()),
        ("Performance", test_performance()),
    ]
    
    # Summary
    print("\n" + "="*60)
    print("Summary")
    print("="*60)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\nSUCCESS: All core features verified!")
    else:
        print(f"\nWARNING: {total - passed} test(s) failed")