#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "estnltk",
#   "requests",
# ]
# ///

"""
Estonian Word Origin Tagger
---------------------------
Given an Estonian text, outputs each word's etymological origin.

Usage:
    uv run origin_tag.py --in input.txt --out output.jsonl
Options:
    --offline         Disable API lookups (use cache only)
    --no-compounds    Skip compound analysis
    --min-conf 0.5    Filter low-confidence results
"""

import argparse, json, re, sqlite3, time, os
from pathlib import Path
from estnltk import Text
import requests

DB_PATH = Path(".cache_origin.sqlite3")

LANG_MAP = {
    r"\b(soome-?ugri|fennougric|uralic|soome)\b": "native_finnic",
    r"\b(madal(s|-)?saksa|alamsaksa|low german)\b": "loan:low_german",
    r"\b(saksa|german)\b": "loan:german",
    r"\b(rootsi|swedish)\b": "loan:swedish",
    r"\b(vene|russian)\b": "loan:russian",
    r"\b(ladina|latin)\b": "loan:latin",
    r"\b(prantsuse|french)\b": "loan:french",
    r"\b(inglise|english)\b": "loan:english",
    r"\b(läti|latvian)\b": "loan:latvian",
    r"\b(leedu|lithuanian)\b": "loan:lithuanian",
    r"\b(balti|baltic)\b": "loan:baltic",
    r"\b(soome|finnish)\b": "loan:finnish",
}

def init_db():
    con = sqlite3.connect(DB_PATH)
    con.execute("""
      CREATE TABLE IF NOT EXISTS lexicon(
        lemma TEXT PRIMARY KEY,
        origin TEXT,
        source TEXT,
        evidence_text TEXT,
        updated_at REAL
      )
    """)
    con.commit()
    return con

def db_get(con, lemma):
    row = con.execute("SELECT origin,source,evidence_text FROM lexicon WHERE lemma=?", (lemma,)).fetchone()
    return {"origin": row[0], "source": row[1], "evidence_text": row[2]} if row else None

def db_put(con, lemma, origin, source, ev):
    con.execute("REPLACE INTO lexicon VALUES (?,?,?,?,?)",
                (lemma, origin, source, ev[:5000] if ev else None, time.time()))
    con.commit()

def normalize_origin(raw_text):
    if not raw_text: return None
    txt = raw_text.lower()
    for pat, tag in LANG_MAP.items():
        if re.search(pat, txt):
            return tag
    if re.search(r"\b(päris?eesti|omakeelne|algupärane)\b", txt):
        return "native_finnic"
    return None

def query_eki(lemma, api_key=None):
    """Query EKI/Ekilex API for etymological information."""
    if not api_key:
        return None

    try:
        # Try Ekilex API endpoint
        url = "https://ekilex.ee/api/etymology"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "User-Agent": "EstonianOriginTagger/1.0",
            "Accept": "application/json"
        }

        r = requests.get(url, params={"word": lemma}, headers=headers, timeout=8)

        if r.status_code == 200:
            data = r.json()
            # Parse EKI response - structure may vary
            if data and "etymology" in data:
                ety_text = data["etymology"]
                norm = normalize_origin(ety_text)
                if norm:
                    return {"origin": norm, "evidence_text": ety_text, "source": "EKI"}

        # Alternative: try Sõnaveeb API
        alt_url = "https://sonaveeb.ee/api/public/v1/word-search"
        r2 = requests.get(alt_url, params={
            "word": lemma,
            "datasets": "ety",
            "lang": "est"
        }, headers=headers, timeout=8)

        if r2.status_code == 200:
            data = r2.json()
            # Parse Sõnaveeb response
            if data and isinstance(data, dict):
                # Extract etymology information from response
                if "words" in data and data["words"]:
                    for word_entry in data["words"]:
                        if "etymology" in word_entry:
                            ety_text = word_entry["etymology"]
                            norm = normalize_origin(str(ety_text))
                            if norm:
                                return {"origin": norm, "evidence_text": str(ety_text), "source": "EKI"}

    except Exception as e:
        # Silently fail and fallback to Wiktionary
        pass

    return None

def query_wiktionary(lemma):
    try:
        url = "https://et.wiktionary.org/w/api.php"
        headers = {
            "User-Agent": "EstonianOriginTagger/1.0 (Educational/Research Tool)"
        }
        r = requests.get(url, params={"action":"query","prop":"extracts","explaintext":1,
                                      "titles":lemma,"format":"json"},
                        headers=headers, timeout=8)
        pages = r.json().get("query", {}).get("pages", {})
        text = next(iter(pages.values())).get("extract","")
        m = re.search(r"(?s)^Etümoloogia\s*(.+?)(?:^\w|\Z)", text, flags=re.MULTILINE)
        if not m: return None
        ety = m.group(1)
        norm = normalize_origin(ety)
        if norm:
            return {"origin": norm, "evidence_text": ety.strip(), "source": "Wiktionary"}
    except Exception:
        pass
    return None

def analyze_text(txt, offline=False, allow_compounds=True, min_conf=0.0, api_key=None):
    con = init_db()
    doc = Text(txt); doc.tag_layer(['morph_analysis'])
    out = []

    for t in doc.words:
        token = t.text
        # Access morphological analysis correctly
        if hasattr(t, 'morph_analysis') and len(t.morph_analysis.annotations) > 0:
            first_analysis = t.morph_analysis.annotations[0]
            lemma = first_analysis['lemma'].lower()
            pos = first_analysis.get('partofspeech')
        else:
            lemma = token.lower()
            pos = None

        hit = db_get(con, lemma)
        if hit:
            origin, source, ev, conf = hit["origin"], hit["source"], hit["evidence_text"], 0.9
        else:
            origin=source=ev=None; conf=0.0
            if not offline:
                r = query_eki(lemma, api_key) or query_wiktionary(lemma)
                if r:
                    origin, ev, source, conf = r["origin"], r["evidence_text"], r["source"], 0.9 if source=="EKI" else 0.6
                    db_put(con, lemma, origin, source, ev)
            if not origin:
                origin, source, ev, conf = "unknown", "none", None, 0.2

        if conf >= min_conf:
            out.append({
                "token": token, "lemma": lemma, "pos": pos,
                "origin": origin, "confidence": round(conf,2),
                "evidence": {"source": source, "text": ev},
                "components": []
            })
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", dest="outp", required=True)
    ap.add_argument("--offline", action="store_true")
    ap.add_argument("--no-compounds", action="store_true")
    ap.add_argument("--min-conf", type=float, default=0.0)
    ap.add_argument("--api-key", dest="api_key", help="EKI/Ekilex API key (or set ESTLEX_API_KEY env var)")
    args = ap.parse_args()

    # Get API key from argument or environment variable
    api_key = args.api_key or os.environ.get("ESTLEX_API_KEY")

    text = Path(args.inp).read_text(encoding="utf-8")
    results = analyze_text(text, offline=args.offline,
                           allow_compounds=not args.no_compounds,
                           min_conf=args.min_conf,
                           api_key=api_key)
    with open(args.outp, "w", encoding="utf-8") as f:
        for row in results:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(f"Tagged {len(results)} tokens. Attribution: EKI/Wiktionary where applicable.")

if __name__ == "__main__":
    main()
