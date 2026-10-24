"""Tests for the pure game core."""

from __future__ import annotations

import random

from snake_game.config import GameConfig
from snake_game.core import Direction, GameState


def test_initial_state_is_centred_and_alive() -> None:
    state = GameState()
    assert state.alive
    assert state.score == 0
    assert state.fps == state.config.base_fps
    assert len(state.snake) == state.config.initial_length
    assert state.head == (state.config.grid_width // 2, state.config.grid_height // 2)
    assert state.food is not None
    assert state.food not in state.snake


def test_step_moves_head_and_keeps_length() -> None:
    state = GameState(GameConfig(grid_width=10, grid_height=8))
    state.food = (9, 0)
    before = list(state.snake)

    result = state.step()

    assert not result.died
    assert state.head == (before[0][0] + 1, before[0][1])
    assert len(state.snake) == len(before)
    assert state.snake[1] == before[0]


def test_wall_collision_kills_the_snake() -> None:
    state = GameState(GameConfig(grid_width=4, grid_height=4))
    state.food = None

    died = False
    for _ in range(10):
        died = state.step().died
        if died:
            break

    assert died
    assert not state.alive


def test_self_collision_kills_the_snake() -> None:
    state = GameState()
    state.food = None
    state.snake = [(5, 5), (4, 5), (4, 6), (5, 6), (6, 6)]
    state.direction = Direction.DOWN
    state.pending_direction = Direction.DOWN

    result = state.step()

    assert result.died
    assert not state.alive


def test_moving_onto_the_tail_cell_is_safe() -> None:
    state = GameState()
    state.food = None
    state.snake = [(5, 5), (4, 5), (4, 6), (5, 6)]
    state.direction = Direction.DOWN
    state.pending_direction = Direction.DOWN

    result = state.step()

    assert not result.died
    assert state.head == (5, 6)


def test_eating_food_scores_and_grows() -> None:
    state = GameState(GameConfig(grid_width=10, grid_height=8))
    head_x, head_y = state.head
    state.food = (head_x + 1, head_y)
    length_before = len(state.snake)

    result = state.step()

    assert result.ate_food
    assert state.score == 1
    assert len(state.snake) == length_before + 1
    assert state.food != (head_x + 1, head_y)


def test_speed_increases_every_three_foods() -> None:
    state = GameState(GameConfig(grid_width=20, grid_height=10))
    base_fps = state.fps
    speedup_every = state.config.speedup_every

    for expected_score in range(1, 7):
        head_x, head_y = state.head
        state.food = (head_x + 1, head_y)

        assert state.step().ate_food
        assert state.score == expected_score
        assert state.fps == min(
            state.config.max_fps,
            base_fps + expected_score // speedup_every,
        )


def test_reverse_turn_is_rejected() -> None:
    state = GameState()

    assert not state.request_direction(Direction.LEFT)
    assert state.pending_direction is Direction.RIGHT


def test_rapid_turn_cannot_reverse_the_snake() -> None:
    """Regression: Right -> Up -> Left within one frame must not reverse.

    Validating against the pending direction would accept the third press and
    drive the head into the neck on the next tick.
    """
    state = GameState()

    assert state.request_direction(Direction.UP)
    assert not state.request_direction(Direction.LEFT)
    assert state.pending_direction is Direction.UP

    state.step()
    assert state.direction is Direction.UP


def test_second_perpendicular_turn_replaces_the_pending_one() -> None:
    state = GameState()

    assert state.request_direction(Direction.UP)
    assert state.request_direction(Direction.DOWN)
    assert state.pending_direction is Direction.DOWN

    state.step()
    assert state.direction is Direction.DOWN


def test_wrap_around_mode_crosses_the_border() -> None:
    state = GameState(GameConfig(grid_width=5, grid_height=5, wrap_around=True))
    state.food = None
    state.snake = [(4, 2), (3, 2), (2, 2)]

    result = state.step()

    assert not result.died
    assert state.head == (0, 2)


def test_full_board_has_no_food() -> None:
    state = GameState(GameConfig(grid_width=3, grid_height=2, initial_length=3))
    state.snake = [(x, y) for x in range(3) for y in range(2)]

    assert state.spawn_food() is None


def test_food_spawn_is_deterministic_with_seed() -> None:
    first = GameState(rng=random.Random(42)).food
    second = GameState(rng=random.Random(42)).food

    assert first == second


def test_reset_restores_the_initial_state() -> None:
    state = GameState()
    state.score = 5
    state.alive = False
    state.fps = 15
    state.snake = [(0, 0)]

    state.reset()

    assert state.alive
    assert state.score == 0
    assert state.fps == state.config.base_fps
    assert len(state.snake) == state.config.initial_length
