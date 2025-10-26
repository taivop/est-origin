#!/usr/bin/env python3
import requests
import json

api_key = "d4d422d05f0c476a96f1ac6cd4d11c38"
test_word = "peegel"

print(f"Testing EKI API with word: {test_word}")
print(f"API Key: {api_key[:10]}...")
print("="*70)

# Test 1: Ekilex API
print("\n1. Testing Ekilex API (ekilex.ee)")
print("-"*70)
url1 = "https://ekilex.ee/api/etymology"
headers1 = {
    "Authorization": f"Bearer {api_key}",
    "User-Agent": "EstonianOriginTagger/1.0",
    "Accept": "application/json"
}

try:
    r1 = requests.get(url1, params={"word": test_word}, headers=headers1, timeout=8)
    print(f"Status Code: {r1.status_code}")
    print(f"Headers: {dict(r1.headers)}")
    print(f"\nResponse Body:")
    print(r1.text[:1000])
    if r1.status_code == 200:
        try:
            print(f"\nJSON Response:")
            print(json.dumps(r1.json(), indent=2, ensure_ascii=False))
        except:
            print("(Not valid JSON)")
except Exception as e:
    print(f"ERROR: {e}")

# Test 2: Sõnaveeb API
print("\n\n2. Testing Sõnaveeb API (sonaveeb.ee)")
print("-"*70)
url2 = "https://sonaveeb.ee/api/public/v1/word-search"
headers2 = {
    "Authorization": f"Bearer {api_key}",
    "User-Agent": "EstonianOriginTagger/1.0",
    "Accept": "application/json"
}

try:
    r2 = requests.get(url2, params={
        "word": test_word,
        "datasets": "ety",
        "lang": "est"
    }, headers=headers2, timeout=8)
    print(f"Status Code: {r2.status_code}")
    print(f"Headers: {dict(r2.headers)}")
    print(f"\nResponse Body:")
    print(r2.text[:1000])
    if r2.status_code == 200:
        try:
            print(f"\nJSON Response:")
            print(json.dumps(r2.json(), indent=2, ensure_ascii=False))
        except:
            print("(Not valid JSON)")
except Exception as e:
    print(f"ERROR: {e}")
