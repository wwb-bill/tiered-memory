"""CLI for tiered-memory."""

from __future__ import annotations

import json
import sys

from .store import TieredMemory


def _utf8_stdout() -> None:
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


def main(argv: list[str] | None = None) -> None:
    args = list(argv) if argv is not None else sys.argv[1:]
    if not args or args[0] in ("--help", "-h"):
        print("tiered-memory — hot/warm/cold tiered agent memory")
        print("\nUsage:")
        print("  tiered-memory add '<content>' [--importance 0.8] [--tier hot|warm|cold]")
        print("  tiered-memory recall [--top-hot N] [--cold N] [--json]")
        print("  tiered-memory consolidate [--out summary.jsonl]")
        print("  tiered-memory search '<keyword>'")
        print("  tiered-memory report [--json]")
        sys.exit(0)

    store = TieredMemory()
    cmd = args[0]

    if cmd == "add" and len(args) >= 2:
        importance = 0.5
        tier = "hot"
        for i, a in enumerate(args):
            if a == "--importance" and i + 1 < len(args): importance = float(args[i + 1])
            elif a == "--tier" and i + 1 < len(args): tier = args[i + 1]
        it = store.add(args[1], importance=importance, tier=tier)
        print(f"added to {it.tier}: {it.content[:60]}")

    elif cmd == "recall":
        top_hot = None
        cold = 0
        json_out = "--json" in args
        for i, a in enumerate(args):
            if a == "--top-hot" and i + 1 < len(args): top_hot = int(args[i + 1])
            elif a == "--cold" and i + 1 < len(args): cold = int(args[i + 1])
        items = store.recall(top_hot=top_hot, include_cold=cold)
        if json_out:
            print(json.dumps([it.to_dict() for it in items], indent=2, ensure_ascii=False))
        else:
            for it in items:
                print(f"  [{it.tier}] {it.content[:70]}")

    elif cmd == "consolidate":
        removed = store.consolidate()
        print(f"consolidated {removed} cold items into warm summary")

    elif cmd == "search" and len(args) >= 2:
        hits = store.search_cold(args[1])
        for it in hits:
            print(f"  [{it.tier}] {it.content[:70]}")
        sys.exit(0 if hits else 1)

    elif cmd == "report":
        r = store.report()
        if "--json" in args:
            print(json.dumps([s.to_dict() for s in r.stats], indent=2))
        else:
            for s in r.stats:
                print(f"  {s.tier:5s}: {s.count:4d} items ({s.total_chars} chars)")

    else:
        print(f"Unknown: {cmd}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    _utf8_stdout()
    main()
