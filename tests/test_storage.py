"""Tests for high score persistence."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from snake_game.storage import (
    SCHEMA_VERSION,
    HighScoreTable,
    ScoreEntry,
    ScoreFormatError,
    default_scores_path,
)


def test_missing_file_starts_empty(tmp_path: Path) -> None:
    table = HighScoreTable(tmp_path / "scores.json")

    assert table.entries == []
    assert table.best == 0


def test_add_save_and_reload(tmp_path: Path) -> None:
    path = tmp_path / "scores.json"
    table = HighScoreTable(path)

    assert table.add(7)
    table.save()

    reloaded = HighScoreTable(path)
    assert [entry.score for entry in reloaded.entries] == [7]
    assert reloaded.best == 7
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["schema_version"] == SCHEMA_VERSION


def test_keeps_only_the_top_scores(tmp_path: Path) -> None:
    table = HighScoreTable(tmp_path / "scores.json", limit=3)

    for score in (5, 1, 9, 7):
        table.add(score)

    assert [entry.score for entry in table.entries] == [9, 7, 5]


def test_result_outside_the_table_is_not_stored(tmp_path: Path) -> None:
    table = HighScoreTable(tmp_path / "scores.json", limit=2)
    assert table.add(10)
    assert table.add(5)

    assert not table.add(1)
    assert [entry.score for entry in table.entries] == [10, 5]


def test_zero_and_negative_scores_are_ignored(tmp_path: Path) -> None:
    table = HighScoreTable(tmp_path / "scores.json")

    assert not table.add(0)
    assert not table.add(-3)
    assert table.entries == []


def test_corrupt_file_is_quarantined(tmp_path: Path) -> None:
    path = tmp_path / "scores.json"
    path.write_text("{not json", encoding="utf-8")

    table = HighScoreTable(path)

    assert table.entries == []
    assert not path.exists()
    assert list(tmp_path.glob("scores.json.corrupt-*"))


def test_unknown_schema_is_quarantined(tmp_path: Path) -> None:
    path = tmp_path / "scores.json"
    path.write_text(json.dumps({"schema_version": 999, "records": []}), encoding="utf-8")

    table = HighScoreTable(path)

    assert table.entries == []
    assert not path.exists()
    assert list(tmp_path.glob("scores.json.corrupt-*"))


def test_save_leaves_no_temporary_files(tmp_path: Path) -> None:
    table = HighScoreTable(tmp_path / "scores.json")
    table.add(3)

    table.save()

    assert not list(tmp_path.glob(".scores-*"))


def test_second_save_overwrites_the_first(tmp_path: Path) -> None:
    path = tmp_path / "scores.json"
    table = HighScoreTable(path)
    table.add(3)
    table.save()
    table.add(5)
    table.save()

    assert [entry.score for entry in HighScoreTable(path).entries] == [5, 3]


def test_score_entry_rejects_invalid_values() -> None:
    invalid_payloads = [
        "not an object",
        {"score": -1, "achieved_at": "2026-01-01T00:00:00+00:00"},
        {"score": 1.5, "achieved_at": "2026-01-01T00:00:00+00:00"},
        {"score": True, "achieved_at": "2026-01-01T00:00:00+00:00"},
        {"score": 1, "achieved_at": ""},
    ]

    for payload in invalid_payloads:
        try:
            ScoreEntry.from_dict(payload)
        except ScoreFormatError:
            continue
        raise AssertionError(f"expected ScoreFormatError for {payload!r}")


def test_default_path_can_be_overridden(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    override = tmp_path / "custom.json"
    monkeypatch.setenv("SNAKE_SCORES_PATH", str(override))

    assert default_scores_path() == override
