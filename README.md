# Estonian Word Origin Tagger

A tool for identifying the etymological origin of Estonian words in text.

## Overview

This tool analyzes Estonian text and determines whether each word is:
- Native Finnic/Uralic origin
- A loanword from German, Swedish, Russian, Latin, etc.
- Unknown origin

## Quick Start

```bash
uv run origin_tag.py --in test_input.txt --out output.jsonl
```

## Features

- **Tokenization & Lemmatization**: Uses EstNLTK for accurate Estonian NLP
- **Etymology Lookup**: Queries Wiktionary (EKI/Ekilex support planned)
- **Local Caching**: SQLite cache to avoid repeated lookups
- **Offline Mode**: Can run without network access using cache
- **JSON Output**: Easy-to-parse JSONL format

## Installation

No installation needed! The script uses `uv` to manage dependencies automatically.

Requirements:
- Python 3.11+
- `uv` package manager

## Usage

### Basic usage
```bash
uv run origin_tag.py --in input.txt --out output.jsonl
```

### Options
- `--offline`: Disable API lookups (use cache only)
- `--no-compounds`: Skip compound word analysis
- `--min-conf 0.5`: Filter results below confidence threshold

### Example input
```
Tere, see on lihtne eesti lause.
```

### Example output
```json
{
  "token": "Tere",
  "lemma": "tere",
  "pos": "I",
  "origin": "unknown",
  "confidence": 0.2,
  "evidence": {
    "source": "none",
    "text": null
  },
  "components": []
}
```

## Architecture

1. **Tokenization**: EstNLTK splits text into tokens
2. **Lemmatization**: Get base form of each word
3. **Cache Lookup**: Check local SQLite cache
4. **Etymology Query**: Query Wiktionary API if not cached
5. **Normalization**: Parse etymology text into standard origin tags
6. **Output**: Write JSONL with origin data

## Origin Tags

- `native_finnic`: Native Finno-Ugric/Uralic words
- `loan:german`: German loanword
- `loan:swedish`: Swedish loanword
- `loan:russian`: Russian loanword
- `loan:low_german`: Low German loanword
- `loan:latin`: Latin loanword
- `loan:french`: French loanword
- `loan:english`: English loanword
- `loan:finnish`: Finnish loanword
- `loan:latvian`: Latvian loanword
- `loan:lithuanian`: Lithuanian loanword
- `loan:baltic`: Baltic loanword (unspecified)
- `loan:multiple`: Multiple possible origins
- `unknown`: Origin not determined

## Next Steps

1. **Enable EKI API**: Implement real Ekilex/Sõnaveeb queries
2. **Compound Analysis**: Add morpheme-level origin detection
3. **Evaluation**: Test against gold standard etymology data
4. **API Wrapper**: Optional FastAPI service for web integration

## Data Attribution

- Etymology data: © EKI (Eesti Keele Instituut), CC-BY 4.0
- Wiktionary data: CC-BY-SA 3.0
- Software: MIT License

## Testing

Test with the included sample:
```bash
uv run origin_tag.py --in test_input.txt --out output.jsonl
cat output.jsonl
```
