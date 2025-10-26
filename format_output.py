#!/usr/bin/env python3
import json
import sys

print(f"{'TOKEN':<15} | {'LEMMA':<15} | {'POS':<4} | {'ORIGIN':<20} | {'CONF':<5} | {'SOURCE':<12}")
print("-" * 95)

with open(sys.argv[1]) as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        d = json.loads(line)
        print(f"{d['token']:<15} | {d['lemma']:<15} | {d['pos'] or 'N/A':<4} | {d['origin']:<20} | {d['confidence']:<5} | {d['evidence']['source']:<12}")
