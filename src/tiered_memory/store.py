"""Tiered memory store — hot (window), warm (summary), cold (persistent JSONL)."""

from __future__ import annotations

import json
import time
from pathlib import Path

from .types import MemoryItem, TierStats, TierReport


class TieredMemory:
    """Three-tier agent memory.

    - Hot: last N items (conversation window) — in memory.
    - Warm: compressed summary of older items — regenerated on consolidation.
    - Cold: persistent JSONL of everything (survives restarts).
    """

    def __init__(self, hot_size: int = 5, path: str | Path = "cold_memory.jsonl",
                 compress_ratio: float = 0.3):
        self.hot_size = hot_size
        self.compress_ratio = compress_ratio
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._hot: list[MemoryItem] = []
        self._warm: list[MemoryItem] = []
        self._cold_cache: list[MemoryItem] = []
        self._load_cold()

    # ── ingestion ──────────────────────────────────────────────

    def add(self, content: str, importance: float = 0.5, tier: str = "hot",
            metadata: dict | None = None) -> MemoryItem:
        item = MemoryItem(content=content, tier=tier, importance=importance,
                          metadata=metadata or {})
        if tier == "hot":
            self._hot.append(item)
            if len(self._hot) > self.hot_size:
                overflow = self._hot[: len(self._hot) - self.hot_size]
                self._hot = self._hot[-self.hot_size:]
                self._append_cold(overflow)
        elif tier == "warm":
            self._warm.append(item)
        else:
            self._append_cold([item])
        return item

    def _append_cold(self, items: list[MemoryItem]) -> None:
        with open(self.path, "a", encoding="utf-8") as f:
            for it in items:
                it.tier = "cold"
                f.write(json.dumps(it.to_dict(), ensure_ascii=False) + "\n")
                self._cold_cache.append(it)  # keep in-memory cache in sync

    def _load_cold(self) -> None:
        if not self.path.exists():
            return
        with open(self.path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    self._cold_cache.append(MemoryItem.from_dict(json.loads(line)))
                except (json.JSONDecodeError, TypeError):
                    continue

    # ── access ─────────────────────────────────────────────────

    @property
    def hot(self) -> list[MemoryItem]:
        return list(self._hot)

    @property
    def warm(self) -> list[MemoryItem]:
        return list(self._warm)

    def cold(self, limit: int | None = None) -> list[MemoryItem]:
        items = list(self._cold_cache)
        if limit:
            items = items[-limit:]
        return items

    def recall(self, top_hot: int | None = None, include_warm: bool = True,
               include_cold: int = 0) -> list[MemoryItem]:
        """Assemble the agent-visible memory context."""
        result: list[MemoryItem] = []
        result.extend(self._hot if top_hot is None else self._hot[-top_hot:])
        if include_warm:
            result.extend(self._warm)
        if include_cold > 0:
            result.extend(self.cold(limit=include_cold))
        return result

    def search_cold(self, keyword: str) -> list[MemoryItem]:
        """Simple keyword search over cold tier (fallback for TF-IDF-free)."""
        kw = keyword.lower()
        return [it for it in self._cold_cache if kw in it.content.lower()]

    # ── lifecycle ──────────────────────────────────────────────

    def consolidate(self, summarizer=None) -> int:
        """Move cold items into a warm summary. summarizer(items) -> str."""
        if not self._cold_cache:
            return 0
        if summarizer is None:
            summary = _default_summarize(self._cold_cache, self.compress_ratio)
        else:
            summary = summarizer(self._cold_cache)
        self._warm = [MemoryItem(content=summary, tier="warm", importance=1.0)]
        return len(self._cold_cache)

    def clear(self) -> None:
        self._hot.clear()
        self._warm.clear()
        self._cold_cache.clear()
        if self.path.exists():
            self.path.unlink()

    def report(self) -> TierReport:
        return TierReport(stats=[
            TierStats("hot", len(self._hot), sum(len(i.content) for i in self._hot)),
            TierStats("warm", len(self._warm), sum(len(i.content) for i in self._warm)),
            TierStats("cold", len(self._cold_cache), sum(len(i.content) for i in self._cold_cache)),
        ])


def _default_summarize(items: list[MemoryItem], ratio: float = 0.3) -> str:
    """Compression: keep most-important items' first sentences, capped by ratio."""
    ordered = sorted(items, key=lambda i: -i.importance)
    budget = max(1, int(sum(len(i.content) for i in items) * ratio))
    parts: list[str] = []
    used = 0
    for it in ordered:
        first = it.content.split(".")[0][:200]
        if used + len(first) > budget:
            break
        parts.append(first)
        used += len(first)
    return ". ".join(parts) + "."
