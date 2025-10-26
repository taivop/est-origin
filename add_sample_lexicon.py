#!/usr/bin/env python3
"""
Add sample etymological data to the cache database for demonstration.
This simulates what would come from EKI/Wiktionary APIs.
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(".cache_origin.sqlite3")

# Sample etymological data - sourced from Estonian etymology references
SAMPLE_DATA = [
    # Native Finnic words
    ("mina", "native_finnic", "manual", "Soome-ugri algupära"),
    ("tema", "native_finnic", "manual", "Soome-ugri algupära"),
    ("käima", "native_finnic", "manual", "Soome-ugri algupära"),
    ("vaatama", "native_finnic", "manual", "Soome-ugri algupära"),
    ("oma", "native_finnic", "manual", "Soome-ugri algupära"),
    ("ja", "native_finnic", "manual", "Soome-ugri algupära"),
    ("järel", "native_finnic", "manual", "Soome-ugri algupära"),

    # German loanwords
    ("peegel", "loan:german", "manual", "Laen saksa keelest: Spiegel"),
    ("lasteaed", "loan:german", "manual", "Laen saksa keelest: Kindergarten"),

    # French loanwords
    ("siluett", "loan:french", "manual", "Laen prantsuse keelest: silhouette"),

    # English loanwords
    ("toddler", "loan:english", "manual", "Laen inglise keelest"),
]

def populate_lexicon():
    con = sqlite3.connect(DB_PATH)

    # Ensure table exists
    con.execute("""
      CREATE TABLE IF NOT EXISTS lexicon(
        lemma TEXT PRIMARY KEY,
        origin TEXT,
        source TEXT,
        evidence_text TEXT,
        updated_at REAL
      )
    """)

    import time
    now = time.time()

    for lemma, origin, source, evidence in SAMPLE_DATA:
        con.execute(
            "INSERT OR REPLACE INTO lexicon VALUES (?,?,?,?,?)",
            (lemma, origin, source, evidence, now)
        )

    con.commit()
    print(f"✓ Added {len(SAMPLE_DATA)} entries to lexicon cache")

    # Show what we added
    print("\nEntries in cache:")
    for row in con.execute("SELECT lemma, origin FROM lexicon ORDER BY lemma"):
        print(f"  {row[0]:15} → {row[1]}")

    con.close()

if __name__ == "__main__":
    populate_lexicon()
