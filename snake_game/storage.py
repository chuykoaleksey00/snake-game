"""Persistent top-N high scores stored as JSON."""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

SCHEMA_VERSION = 1
DEFAULT_LIMIT = 10

__all__ = [
    "DEFAULT_LIMIT",
    "SCHEMA_VERSION",
    "HighScoreTable",
    "ScoreEntry",
    "ScoreFormatError",
    "default_scores_path",
]


class ScoreFormatError(ValueError):
    """Raised when a score record does not match the expected schema."""


@dataclass(frozen=True)
class ScoreEntry:
    score: int
    achieved_at: str

    def to_dict(self) -> dict[str, object]:
        return {"score": self.score, "achieved_at": self.achieved_at}

    @classmethod
    def from_dict(cls, raw: object) -> ScoreEntry:
        if not isinstance(raw, dict):
            raise ScoreFormatError("score entry must be an object")
        score = raw.get("score")
        achieved_at = raw.get("achieved_at")
        if not isinstance(score, int) or isinstance(score, bool) or score < 0:
            raise ScoreFormatError("score must be a non-negative integer")
        if not isinstance(achieved_at, str) or not achieved_at:
            raise ScoreFormatError("achieved_at must be a non-empty string")
        return cls(score=score, achieved_at=achieved_at)


def default_scores_path() -> Path:
    """Return the per-user location of the score file.

    ``SNAKE_SCORES_PATH`` overrides the location, which keeps tests and
    portable builds away from the real profile directory.
    """
    override = os.environ.get("SNAKE_SCORES_PATH")
    if override:
        return Path(override)
    if os.name == "nt":
        appdata = os.environ.get("APPDATA")
        root = Path(appdata) if appdata else Path.home() / "AppData" / "Roaming"
    else:
        data_home = os.environ.get("XDG_DATA_HOME")
        root = Path(data_home) if data_home else Path.home() / ".local" / "share"
    return root / "snake-game" / "scores.json"


class HighScoreTable:
    """Top-N table persisted as JSON with atomic replacement."""

    def __init__(self, path: Path | None = None, limit: int = DEFAULT_LIMIT) -> None:
        if limit < 1:
            raise ValueError("limit must be positive")
        self.path = path or default_scores_path()
        self.limit = limit
        self.entries: list[ScoreEntry] = []
        self.load()

    @property
    def best(self) -> int:
        return self.entries[0].score if self.entries else 0

    def load(self) -> None:
        try:
            text = self.path.read_text(encoding="utf-8")
        except (FileNotFoundError, OSError):
            self.entries = []
            return

        try:
            payload = json.loads(text)
        except json.JSONDecodeError:
            self._quarantine()
            self.entries = []
            return

        if not isinstance(payload, dict) or payload.get("schema_version") != SCHEMA_VERSION:
            self._quarantine()
            self.entries = []
            return

        records = payload.get("records")
        if not isinstance(records, list):
            self._quarantine()
            self.entries = []
            return

        try:
            entries = [ScoreEntry.from_dict(item) for item in records]
        except ScoreFormatError:
            self._quarantine()
            self.entries = []
            return

        self.entries = sorted(entries, key=lambda entry: entry.score, reverse=True)[: self.limit]

    def add(self, score: int) -> bool:
        """Insert a result and return ``True`` if it stayed in the table."""
        if score <= 0:
            return False
        entry = ScoreEntry(score=score, achieved_at=_now_iso())
        candidates = sorted([*self.entries, entry], key=lambda item: item.score, reverse=True)
        self.entries = candidates[: self.limit]
        return entry in self.entries

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "schema_version": SCHEMA_VERSION,
            "records": [entry.to_dict() for entry in self.entries],
        }
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=".scores-",
            suffix=".tmp",
            dir=self.path.parent,
        )
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
                json.dump(payload, handle, ensure_ascii=False, indent=2)
                handle.write("\n")
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary_name, self.path)
        except BaseException:
            Path(temporary_name).unlink(missing_ok=True)
            raise

    def _quarantine(self) -> None:
        """Move an unreadable file aside instead of crashing or overwriting it."""
        if not self.path.exists():
            return
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        target = self.path.with_name(f"{self.path.name}.corrupt-{stamp}")
        try:
            self.path.replace(target)
        except OSError:
            pass


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
