"""tiered-memory — hot/warm/cold tiered agent memory.

2026 production prescription: Hot (last 3-5 turns), Warm (compressed
summary), Cold (persistent retrieval) memory tiers with sliding-window-plus-
summarization — prescribed everywhere but not packaged as a library
primitive. This is that primitive, zero-dependency.

Usage:
    from tiered_memory import TieredMemory

    mem = TieredMemory(hot_size=5, path="cold.jsonl")
    mem.add("user prefers dark mode", importance=0.9)
    for item in mem.recall(top_hot=5, include_cold=3):
        print(item.tier, item.content)
"""

from .types import MemoryItem, TierStats, TierReport
from .store import TieredMemory

__version__ = "0.1.0"

__all__ = [
    "MemoryItem",
    "TierStats",
    "TierReport",
    "TieredMemory",
]
