"""Pure game logic: no pygame imports, fully deterministic with a seeded RNG."""

from __future__ import annotations

import random
from dataclasses import dataclass
from enum import Enum

from .config import GameConfig

Position = tuple[int, int]

__all__ = ["Direction", "GameState", "Position", "StepResult"]


class Direction(Enum):
    """Movement vector of the snake head."""

    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

    @property
    def vector(self) -> Position:
        return self.value

    def is_opposite(self, other: Direction) -> bool:
        dx, dy = self.value
        other_dx, other_dy = other.value
        return dx == -other_dx and dy == -other_dy


@dataclass(frozen=True)
class StepResult:
    """What happened during a single tick."""

    ate_food: bool = False
    died: bool = False


class GameState:
    """Board, snake, food and score.

    The class knows nothing about rendering or input devices: callers feed it
    directions and call :meth:`step` once per tick.
    """

    def __init__(
        self,
        config: GameConfig | None = None,
        rng: random.Random | None = None,
    ) -> None:
        self.config = config or GameConfig()
        self._rng = rng or random.Random()
        self.snake: list[Position] = []
        self.direction = Direction.RIGHT
        self.pending_direction = Direction.RIGHT
        self.food: Position | None = None
        self.score = 0
        self.fps = self.config.base_fps
        self.alive = True
        self.reset()

    @property
    def head(self) -> Position:
        return self.snake[0]

    def reset(self) -> None:
        """Restart from the initial three-segment snake in the board centre."""
        config = self.config
        head_x = config.grid_width // 2
        head_y = config.grid_height // 2
        self.snake = [(head_x - offset, head_y) for offset in range(config.initial_length)]
        self.direction = Direction.RIGHT
        self.pending_direction = Direction.RIGHT
        self.score = 0
        self.fps = config.base_fps
        self.alive = True
        self.food = None
        self.spawn_food()

    def request_direction(self, direction: Direction) -> bool:
        """Queue a turn and return ``True`` when it was accepted.

        Validation is done against ``self.direction`` - the direction applied on
        the last tick - and not against the pending one. The body lies behind
        the head along the last applied direction, so only a reversal of that
        direction is dangerous. Comparing against the pending direction would
        allow Right -> Up -> Left within a single frame: each press looks legal
        on its own, but together they turn the head into its own neck.
        """
        if not self.alive or direction.is_opposite(self.direction):
            return False
        self.pending_direction = direction
        return True

    def spawn_food(self) -> Position | None:
        """Place food on a free cell; ``None`` means the board is full."""
        occupied = set(self.snake)
        free_cells = [
            (x, y)
            for x in range(self.config.grid_width)
            for y in range(self.config.grid_height)
            if (x, y) not in occupied
        ]
        self.food = self._rng.choice(free_cells) if free_cells else None
        return self.food

    def step(self) -> StepResult:
        """Advance the game by one tick."""
        if not self.alive:
            return StepResult()

        config = self.config
        self.direction = self.pending_direction
        head_x, head_y = self.snake[0]
        dx, dy = self.direction.vector
        new_head = (head_x + dx, head_y + dy)

        if config.wrap_around:
            new_head = (new_head[0] % config.grid_width, new_head[1] % config.grid_height)
            hit_wall = False
        else:
            hit_wall = not (
                0 <= new_head[0] < config.grid_width
                and 0 <= new_head[1] < config.grid_height
            )

        # The tail leaves its cell on the same tick unless the snake grows, so
        # the new head may safely move onto the current tail position.
        hits_self = new_head in self.snake[:-1]
        if hit_wall or hits_self:
            self.alive = False
            return StepResult(died=True)

        self.snake.insert(0, new_head)
        if new_head == self.food:
            self.score += 1
            if self.score % config.speedup_every == 0:
                self.fps = min(config.max_fps, self.fps + 1)
            self.spawn_food()
            return StepResult(ate_food=True)

        self.snake.pop()
        return StepResult()
