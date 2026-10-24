"""Static game configuration and colour palette."""

from __future__ import annotations

from dataclasses import dataclass

Color = tuple[int, int, int]


@dataclass(frozen=True)
class GameConfig:
    """Board geometry and pacing.

    All values are plain integers so the core logic can be tested without
    pygame: the renderer derives pixel sizes from them.
    """

    grid_width: int = 32
    grid_height: int = 24
    cell_size: int = 20
    hud_height: int = 36
    initial_length: int = 3
    base_fps: int = 8
    max_fps: int = 20
    speedup_every: int = 3
    wrap_around: bool = False

    def __post_init__(self) -> None:
        if self.grid_width < 2 or self.grid_height < 2:
            raise ValueError("grid must be at least 2x2 cells")
        if self.cell_size < 2:
            raise ValueError("cell_size must be at least 2 pixels")
        if self.hud_height < 0:
            raise ValueError("hud_height must not be negative")
        if not 1 <= self.initial_length <= self.grid_width:
            raise ValueError("initial_length must fit the grid width")
        if self.base_fps < 1 or self.max_fps < self.base_fps:
            raise ValueError("expected 1 <= base_fps <= max_fps")
        if self.speedup_every < 1:
            raise ValueError("speedup_every must be positive")


@dataclass(frozen=True)
class Palette:
    """Colours used by the renderer."""

    background: Color = (18, 18, 18)
    grid: Color = (30, 30, 30)
    hud_background: Color = (24, 24, 24)
    snake_body: Color = (80, 200, 120)
    snake_head: Color = (150, 240, 180)
    food: Color = (232, 72, 72)
    text: Color = (235, 235, 235)
