"""Tests for TieredMemory."""

from pathlib import Path

from tiered_memory import TieredMemory


class TestIngestion:
    def test_hot_window(self, tmp_path: Path):
        m = TieredMemory(hot_size=3, path=str(tmp_path / "c.jsonl"))
        for i in range(5):
            m.add(f"item {i}")
        assert len(m.hot) == 3
        assert m.hot[-1].content == "item 4"

    def test_overflow_goes_cold(self, tmp_path: Path):
        m = TieredMemory(hot_size=2, path=str(tmp_path / "c.jsonl"))
        for i in range(4):
            m.add(f"item {i}")
        assert len(m.cold()) == 2  # items 0,1 overflowed

    def test_direct_cold_add(self, tmp_path: Path):
        m = TieredMemory(path=str(tmp_path / "c.jsonl"))
        m.add("permanent", tier="cold")
        assert len(m.cold()) == 1
        assert m.cold()[0].tier == "cold"

    def test_warm_add(self, tmp_path: Path):
        m = TieredMemory(path=str(tmp_path / "c.jsonl"))
        m.add("summary", tier="warm")
        assert len(m.warm) == 1


class TestRecall:
    def test_recall_order(self, tmp_path: Path):
        m = TieredMemory(hot_size=3, path=str(tmp_path / "c.jsonl"))
        m.add("a")
        m.add("b")
        items = m.recall(top_hot=2)
        assert [i.content for i in items] == ["a", "b"]

    def test_recall_includes_warm(self, tmp_path: Path):
        m = TieredMemory(path=str(tmp_path / "c.jsonl"))
        m.add("w", tier="warm")
        assert len(m.recall(include_warm=True)) == 1
        assert m.recall(include_warm=False) == []

    def test_recall_cold_limit(self, tmp_path: Path):
        m = TieredMemory(path=str(tmp_path / "c.jsonl"))
        for i in range(5):
            m.add(f"c{i}", tier="cold")
        items = m.recall(include_cold=2)
        cold = [i for i in items if i.tier == "cold"]
        assert len(cold) == 2


class TestColdPersistence:
    def test_survives_restart(self, tmp_path: Path):
        p = str(tmp_path / "c.jsonl")
        TieredMemory(path=p).add("remember me", tier="cold")
        m2 = TieredMemory(path=p)
        assert len(m2.cold()) == 1
        assert m2.cold()[0].content == "remember me"

    def test_search_cold(self, tmp_path: Path):
        p = str(tmp_path / "c.jsonl")
        m = TieredMemory(path=p)
        m.add("user prefers dark mode", tier="cold")
        m.add("user likes python", tier="cold")
        hits = m.search_cold("dark")
        assert len(hits) == 1
        assert "dark" in hits[0].content

    def test_clear(self, tmp_path: Path):
        p = str(tmp_path / "c.jsonl")
        m = TieredMemory(path=p)
        m.add("x", tier="cold")
        m.clear()
        assert m.cold() == []
        assert m.hot == [] and m.warm == []


class TestConsolidate:
    def test_consolidates_cold(self, tmp_path: Path):
        m = TieredMemory(path=str(tmp_path / "c.jsonl"))
        for i in range(4):
            m.add(f"fact number {i} about the system", tier="cold")
        removed = m.consolidate()
        assert removed == 4
        assert len(m.warm) == 1
        assert "fact" in m.warm[0].content

    def test_custom_summarizer(self, tmp_path: Path):
        m = TieredMemory(path=str(tmp_path / "c.jsonl"))
        m.add("one", tier="cold")
        m.consolidate(summarizer=lambda items: "CUSTOM: " + str(len(items)))
        assert m.warm[0].content == "CUSTOM: 1"

    def test_empty_consolidate(self, tmp_path: Path):
        m = TieredMemory(path=str(tmp_path / "c.jsonl"))
        assert m.consolidate() == 0


class TestReport:
    def test_summary(self, tmp_path: Path):
        m = TieredMemory(hot_size=2, path=str(tmp_path / "c.jsonl"))
        m.add("a")
        m.add("b")
        m.add("c")  # overflow -> cold
        m.add("w", tier="warm")
        s = m.report().summary()
        assert s["hot"] == 2
        assert s["warm"] == 1
        assert s["cold"] == 1
