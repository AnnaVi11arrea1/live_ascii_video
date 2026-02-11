import requests
import json

# Test 1: Check available models
print("=" * 50)
print("Test 1: Available Models")
print("=" * 50)
try:
    r = requests.get('http://localhost:11434/api/tags', timeout=5)
    print(f"Status: {r.status_code}")
    data = r.json()
    print(f"Models found: {len(data.get('models', []))}")
    for model in data.get('models', []):
        print(f"  - {model['name']}")
except Exception as e:
    print(f"Error: {e}")

# Test 2: Try to generate with llama3.2:1b
print("\n" + "=" * 50)
print("Test 2: Generate with llama3.2:1b")
print("=" * 50)
try:
    r = requests.post(
        'http://localhost:11434/api/generate',
        json={
            'model': 'llama3.2:1b',
            'prompt': 'Say hello in 3 words',
            'stream': False
        },
        timeout=30
    )
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text[:200]}")
    if r.status_code == 200:
        data = r.json()
        print(f"AI said: {data.get('response', 'No response')}")
except Exception as e:
    print(f"Error: {e}")

# Test 3: Try llama3.2 without :1b
print("\n" + "=" * 50)
print("Test 3: Generate with llama3.2")
print("=" * 50)
try:
    r = requests.post(
        'http://localhost:11434/api/generate',
        json={
            'model': 'llama3.2',
            'prompt': 'Say hello in 3 words',
            'stream': False
        },
        timeout=30
    )
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"AI said: {data.get('response', 'No response')}")
    else:
        print(f"Error: {r.text}")
except Exception as e:
    print(f"Error: {e}")
