"""Core types for tiered-memory."""

from __future__ import annotations

import time
from dataclasses import dataclass, field, asdict
from typing import Any


@dataclass
class MemoryItem:
    """One memory unit in any tier."""

    content: str
    tier: str = "hot"  # hot | warm | cold
    ts: float = field(default_factory=time.time)
    importance: float = 0.5
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> MemoryItem:
        known = {f for f in cls.__dataclass_fields__}
        return cls(**{k: v for k, v in d.items() if k in known})


@dataclass
class TierStats:
    """Per-tier statistics."""

    tier: str
    count: int
    total_chars: int = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class TierReport:
    """Snapshot of all tiers."""

    stats: list[TierStats] = field(default_factory=list)

    def summary(self) -> dict[str, Any]:
        return {s.tier: s.count for s in self.stats}
