"""Smoke tests for the pygame wiring."""

from __future__ import annotations

from pathlib import Path

import pygame
from snake_game.app import Game
from snake_game.config import GameConfig
from snake_game.core import Direction
from snake_game.storage import HighScoreTable


def test_renders_a_frame_headless(tmp_path: Path) -> None:
    game = Game(
        GameConfig(grid_width=8, grid_height=6),
        seed=0,
        scores_path=tmp_path / "scores.json",
    )
    try:
        game.state.food = (1, 1)

        game.renderer.draw(game.state, best=0, paused=False)

        surface = pygame.display.get_surface()
        assert surface is not None
        assert surface.get_size() == (8 * 20, 6 * 20 + 36)
    finally:
        pygame.quit()


def test_pause_stops_updates_and_blocks_turns(tmp_path: Path) -> None:
    game = Game(
        GameConfig(grid_width=10, grid_height=8),
        seed=0,
        scores_path=tmp_path / "scores.json",
    )
    try:
        head_before = game.state.head

        game._handle_key(pygame.K_p)
        assert game.paused

        game._handle_key(pygame.K_UP)
        game._update()
        assert game.state.head == head_before
        assert game.state.pending_direction is Direction.RIGHT

        game._handle_key(pygame.K_p)
        assert not game.paused

        game._update()
        assert game.state.head != head_before
    finally:
        pygame.quit()


def test_restart_after_death(tmp_path: Path) -> None:
    game = Game(
        GameConfig(grid_width=4, grid_height=4),
        seed=0,
        scores_path=tmp_path / "scores.json",
    )
    try:
        game.state.alive = False
        game.state.score = 7
        game.paused = True

        game._handle_key(pygame.K_RETURN)

        assert game.state.alive
        assert game.state.score == 0
        assert not game.paused
    finally:
        pygame.quit()


def test_score_is_persisted_once_after_death(tmp_path: Path) -> None:
    path = tmp_path / "scores.json"
    game = Game(GameConfig(grid_width=4, grid_height=4), seed=0, scores_path=path)
    try:
        game.state.food = None
        game.state.score = 3

        for _ in range(20):
            game._update()
            if not game.state.alive:
                break
        game._update()  # a dead snake must not record the score twice

        assert not game.state.alive
        entries = HighScoreTable(path).entries
        assert [entry.score for entry in entries] == [3]
    finally:
        pygame.quit()
