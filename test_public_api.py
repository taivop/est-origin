#!/usr/bin/env python3
import requests
import json

test_word = "peegel"

# Test 3: Sõnaveeb public API without auth
print("Testing Sõnaveeb PUBLIC API (no auth)")
print("="*70)
url = "https://sonaveeb.ee/api/public/v1/word-search"

try:
    r = requests.get(url, params={"word": test_word}, timeout=10)
    print(f"Status Code: {r.status_code}")
    print(f"Content-Type: {r.headers.get('Content-Type')}")
    print(f"\nResponse (first 2000 chars):")
    print(r.text[:2000])

    if r.status_code == 200:
        try:
            data = r.json()
            print(f"\n\nJSON Structure:")
            print(json.dumps(data, indent=2, ensure_ascii=False)[:3000])
        except:
            pass
except Exception as e:
    print(f"ERROR: {e}")

# Also test if we can reach the domain at all
print("\n\n" + "="*70)
print("Testing if we can reach sonaveeb.ee at all...")
try:
    r2 = requests.get("https://sonaveeb.ee", timeout=10)
    print(f"Main site Status Code: {r2.status_code}")
except Exception as e:
    print(f"Cannot reach main site: {e}")
