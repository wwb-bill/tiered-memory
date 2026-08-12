# 🧊 tiered-memory

[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

**Hot/Warm/Cold 三层 agent 记忆。** 2026 生产处方——Hot(最近 3-5 轮)、Warm(压缩摘要)、Cold(持久检索)三层记忆,滑动窗口 + 摘要——到处被推荐但无人封装成库原语。这就是那个原语。

配套 [agent-memory](https://github.com/wwb-bill/agent-memory)(单层 JSONL+TF-IDF)— tiered-memory 增加三层生命周期。零依赖。

```python
from tiered_memory import TieredMemory
mem = TieredMemory(hot_size=5, path="cold.jsonl")
mem.add("user prefers dark mode", importance=0.9)
for item in mem.recall(top_hot=5, include_cold=3):
    print(item.tier, item.content)
mem.consolidate()
```

```bash
pip install tiered-memory
tiered-memory add 'user prefers dark mode' --importance 0.9
tiered-memory recall --top-hot 5 --cold 3
tiered-memory consolidate
tiered-memory search 'dark'
```

MIT © [wwb-bill](https://github.com/wwb-bill)
