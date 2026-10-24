"""Pygame rendering layer."""

from __future__ import annotations

import pygame

from .config import GameConfig, Palette
from .core import GameState, Position

__all__ = ["Renderer"]

Color = tuple[int, int, int]


class Renderer:
    """Owns the window, fonts and all drawing routines."""

    def __init__(self, config: GameConfig, palette: Palette | None = None) -> None:
        self.config = config
        self.palette = palette or Palette()
        self.width = config.grid_width * config.cell_size
        self.height = config.grid_height * config.cell_size + config.hud_height
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Snake")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("consolas", 20)
        self.big_font = pygame.font.SysFont("consolas", 44, bold=True)
        self.small_font = pygame.font.SysFont("consolas", 17)

    def draw(self, state: GameState, *, best: int = 0, paused: bool = False) -> None:
        """Render a full frame and flip the display buffer."""
        self.screen.fill(self.palette.background)
        self._draw_grid()
        if state.food is not None:
            self._draw_cell(state.food, self.palette.food)
        for index, segment in enumerate(state.snake):
            color = self.palette.snake_head if index == 0 else self.palette.snake_body
            self._draw_cell(segment, color)
        self._draw_hud(state.score, best, paused)
        if not state.alive:
            self._draw_overlay(
                "GAME OVER",
                [
                    f"Score: {state.score}",
                    f"Best: {best}",
                    "Enter / Space - restart, Esc - exit",
                ],
                self.palette.food,
            )
        elif paused:
            self._draw_overlay(
                "PAUSED",
                ["P - resume, Esc - exit"],
                self.palette.text,
            )
        pygame.display.flip()

    def _draw_cell(self, position: Position, color: Color) -> None:
        x, y = position
        rect = pygame.Rect(
            x * self.config.cell_size + 1,
            y * self.config.cell_size + self.config.hud_height + 1,
            self.config.cell_size - 2,
            self.config.cell_size - 2,
        )
        pygame.draw.rect(self.screen, color, rect, border_radius=4)

    def _draw_grid(self) -> None:
        top = self.config.hud_height
        for x in range(0, self.width + 1, self.config.cell_size):
            pygame.draw.line(self.screen, self.palette.grid, (x, top), (x, self.height))
        for y in range(top, self.height + 1, self.config.cell_size):
            pygame.draw.line(self.screen, self.palette.grid, (0, y), (self.width, y))

    def _draw_hud(self, score: int, best: int, paused: bool) -> None:
        bar = pygame.Rect(0, 0, self.width, self.config.hud_height)
        pygame.draw.rect(self.screen, self.palette.hud_background, bar)

        score_surface = self.font.render(f"Score: {score}", True, self.palette.text)
        best_surface = self.font.render(f"Best: {best}", True, self.palette.text)
        self.screen.blit(score_surface, (10, 7))
        self.screen.blit(
            best_surface,
            (self.width - best_surface.get_width() - 10, 7),
        )

        if paused:
            paused_surface = self.small_font.render("PAUSED", True, self.palette.food)
            self.screen.blit(
                paused_surface,
                paused_surface.get_rect(
                    center=(self.width // 2, self.config.hud_height // 2),
                ),
            )

    def _draw_overlay(self, title_text: str, lines: list[str], color: Color) -> None:
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        self.screen.blit(overlay, (0, 0))

        center_x = self.width // 2
        center_y = self.height // 2
        title = self.big_font.render(title_text, True, color)
        self.screen.blit(title, title.get_rect(center=(center_x, center_y - 40)))
        for offset, line in enumerate(lines):
            rendered = self.small_font.render(line, True, self.palette.text)
            position = rendered.get_rect(center=(center_x, center_y + 10 + offset * 24))
            self.screen.blit(rendered, position)
