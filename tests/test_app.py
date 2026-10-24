"""Smoke test for the pygame wiring: one frame must render headlessly."""

from __future__ import annotations

import pygame

from snake_game.app import Game
from snake_game.config import GameConfig


def test_renders_a_frame_headless() -> None:
    game = Game(GameConfig(grid_width=8, grid_height=6), seed=0)
    try:
        game.state.food = (1, 1)

        game.renderer.draw(game.state)

        surface = pygame.display.get_surface()
        assert surface is not None
        assert surface.get_size() == (8 * 20, 6 * 20)
    finally:
        pygame.quit()


def test_restart_after_death() -> None:
    game = Game(GameConfig(grid_width=4, grid_height=4), seed=0)
    try:
        game.state.alive = False
        game.state.score = 7

        game._handle_key(pygame.K_RETURN)

        assert game.state.alive
        assert game.state.score == 0
    finally:
        pygame.quit()
