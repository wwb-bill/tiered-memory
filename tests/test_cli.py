"""Tests for CLI."""

import json
import os

import pytest

from tiered_memory.cli import main


class TestCLI:
    def _setup(self, tmp_path):
        os.chdir(tmp_path)

    def test_add(self, tmp_path, capsys):
        self._setup(tmp_path)
        main(["add", "hello memory", "--importance", "0.9"])
        assert "added to hot" in capsys.readouterr().out

    def test_recall(self, tmp_path, capsys):
        self._setup(tmp_path)
        # hot is in-memory only (per-process) — recall tests use cold (persistent)
        main(["add", "fact one", "--tier", "cold"])
        main(["add", "fact two", "--tier", "cold"])
        main(["recall", "--cold", "5"])
        out = capsys.readouterr().out
        assert "fact one" in out and "fact two" in out

    def test_recall_json(self, tmp_path, capsys):
        self._setup(tmp_path)
        main(["add", "fact one", "--tier", "cold"])
        capsys.readouterr()  # discard add output
        main(["recall", "--cold", "5", "--json"])
        data = json.loads(capsys.readouterr().out)
        assert data[0]["content"] == "fact one"
        assert data[0]["tier"] == "cold"

    def test_consolidate(self, tmp_path, capsys):
        self._setup(tmp_path)
        main(["add", "old fact", "--tier", "cold"])
        main(["consolidate"])
        assert "consolidated 1" in capsys.readouterr().out

    def test_search_hit(self, tmp_path, capsys):
        self._setup(tmp_path)
        main(["add", "user prefers dark mode", "--tier", "cold"])
        with pytest.raises(SystemExit) as exc:
            main(["search", "dark"])
        assert exc.value.code == 0
        assert "dark" in capsys.readouterr().out

    def test_search_miss(self, tmp_path, capsys):
        self._setup(tmp_path)
        main(["add", "unrelated", "--tier", "cold"])
        with pytest.raises(SystemExit) as exc:
            main(["search", "zzz"])
        assert exc.value.code == 1

    def test_report(self, tmp_path, capsys):
        self._setup(tmp_path)
        main(["add", "a"])
        main(["report"])
        out = capsys.readouterr().out
        assert "hot" in out and "cold" in out
