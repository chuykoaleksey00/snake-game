"""Application loop and pygame wiring."""

from __future__ import annotations

import argparse
import os
import random
import sys
from pathlib import Path

import pygame

from . import __version__
from .config import GameConfig, Palette
from .core import Direction, GameState
from .render import Renderer
from .storage import HighScoreTable

__all__ = ["Game", "main"]

KEY_DIRECTIONS: dict[int, Direction] = {
    pygame.K_UP: Direction.UP,
    pygame.K_w: Direction.UP,
    pygame.K_DOWN: Direction.DOWN,
    pygame.K_s: Direction.DOWN,
    pygame.K_LEFT: Direction.LEFT,
    pygame.K_a: Direction.LEFT,
    pygame.K_RIGHT: Direction.RIGHT,
    pygame.K_d: Direction.RIGHT,
}


class Game:
    """Glue between input events, the pure :class:`GameState` and the renderer."""

    def __init__(
        self,
        config: GameConfig | None = None,
        *,
        seed: int | None = None,
        scores_path: Path | None = None,
    ) -> None:
        pygame.init()
        self.config = config or GameConfig()
        self.state = GameState(self.config, random.Random(seed))
        self.renderer = Renderer(self.config, Palette())
        self.scores = HighScoreTable(scores_path)
        self._running = True
        self.paused = False
        self._score_saved = False

    def run(self) -> None:
        while self._running:
            self._handle_events()
            self._update()
            self._draw()
            self.renderer.clock.tick(self.state.fps)

    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._running = False
            elif event.type == pygame.KEYDOWN:
                self._handle_key(event.key)

    def _handle_key(self, key: int) -> None:
        if key == pygame.K_ESCAPE:
            self._running = False
            return
        if not self.state.alive:
            if key in (pygame.K_RETURN, pygame.K_SPACE):
                self._restart()
            return
        if key in (pygame.K_p, pygame.K_PAUSE):
            self.paused = not self.paused
            return
        if self.paused:
            return
        direction = KEY_DIRECTIONS.get(key)
        if direction is not None:
            self.state.request_direction(direction)

    def _restart(self) -> None:
        self.state.reset()
        self.paused = False
        self._score_saved = False

    def _update(self) -> None:
        if self.paused or not self.state.alive:
            return
        if self.state.step().died:
            self._record_score()

    def _record_score(self) -> None:
        """Store the result once per run, ignoring storage failures."""
        if self._score_saved:
            return
        self._score_saved = True
        if not self.scores.add(self.state.score):
            return
        try:
            self.scores.save()
        except OSError:
            # A read-only profile must not crash a finished game.
            pass

    def _draw(self) -> None:
        self.renderer.draw(self.state, best=self.scores.best, paused=self.paused)


def _ensure_standard_streams() -> None:
    """Windowed PyInstaller builds start with ``sys.stdout`` set to ``None``."""
    for name in ("stdout", "stderr"):
        if getattr(sys, name) is None:
            setattr(sys, name, open(os.devnull, "w", encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    _ensure_standard_streams()
    parser = argparse.ArgumentParser(
        prog="snake-game",
        description="Classic snake game built on pygame.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    parser.add_argument(
        "--scores",
        type=Path,
        default=None,
        help="path to the JSON high score file",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help=argparse.SUPPRESS,
    )
    args = parser.parse_args(argv)

    try:
        Game(scores_path=args.scores, seed=args.seed).run()
    except KeyboardInterrupt:
        return 130
    finally:
        pygame.quit()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
