# 🧊 tiered-memory

[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![CI](https://github.com/wwb-bill/tiered-memory/actions/workflows/ci.yml/badge.svg)](https://github.com/wwb-bill/tiered-memory/actions/workflows/ci.yml)
[![No Dependencies](https://img.shields.io/badge/dependencies-zero-brightgreen)](#)

**Hot/warm/cold tiered agent memory.** The 2026 production prescription — Hot (last 3–5 turns), Warm (compressed summary), Cold (persistent retrieval) memory tiers with sliding-window-plus-summarization — is prescribed everywhere but not packaged as a library primitive. This is that primitive.

Complements [agent-memory](https://github.com/wwb-bill/agent-memory) (single-layer JSONL+TF-IDF) — tiered-memory adds the three-tier lifecycle.

> Zero dependencies. Pure Python stdlib.

## Quick Start

```bash
pip install tiered-memory
```

## Usage

```python
from tiered_memory import TieredMemory

mem = TieredMemory(hot_size=5, path="cold.jsonl")
mem.add("user prefers dark mode", importance=0.9)
mem.add("remember this permanently", tier="cold")

for item in mem.recall(top_hot=5, include_cold=3):
    print(item.tier, item.content)

mem.consolidate()  # cold items -> compressed warm summary
```

## CLI

```bash
tiered-memory add 'user prefers dark mode' --importance 0.9
tiered-memory recall --top-hot 5 --cold 3 --json
tiered-memory consolidate
tiered-memory search 'dark'
tiered-memory report
```

## Tiers

| Tier | What | Backed by |
|------|------|-----------|
| hot | last N items (window) | memory |
| warm | compressed summary of cold | memory |
| cold | everything, persistent | JSONL (survives restarts) |

## License

MIT © [wwb-bill](https://github.com/wwb-bill)
