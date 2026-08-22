import random
import sys

import pygame

CELL_SIZE = 20
GRID_WIDTH = 32
GRID_HEIGHT = 24
WINDOW_WIDTH = CELL_SIZE * GRID_WIDTH
WINDOW_HEIGHT = CELL_SIZE * GRID_HEIGHT
BASE_FPS = 8
MAX_FPS = 20

COLOR_BACKGROUND = (18, 18, 18)
COLOR_GRID = (30, 30, 30)
COLOR_SNAKE_BODY = (80, 200, 120)
COLOR_SNAKE_HEAD = (150, 240, 180)
COLOR_FOOD = (232, 72, 72)
COLOR_TEXT = (235, 235, 235)

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

KEY_DIRECTIONS = {
    pygame.K_UP: UP,
    pygame.K_w: UP,
    pygame.K_DOWN: DOWN,
    pygame.K_s: DOWN,
    pygame.K_LEFT: LEFT,
    pygame.K_a: LEFT,
    pygame.K_RIGHT: RIGHT,
    pygame.K_d: RIGHT,
}


def draw_cell(surface, position, color):
    rect = pygame.Rect(
        position[0] * CELL_SIZE + 1,
        position[1] * CELL_SIZE + 1,
        CELL_SIZE - 2,
        CELL_SIZE - 2,
    )
    pygame.draw.rect(surface, color, rect, border_radius=4)


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Snake")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("consolas", 22)
        self.big_font = pygame.font.SysFont("consolas", 48, bold=True)
        self.reset()

    def reset(self):
        start_x = GRID_WIDTH // 2
        start_y = GRID_HEIGHT // 2
        self.snake = [
            (start_x, start_y),
            (start_x - 1, start_y),
            (start_x - 2, start_y),
        ]
        self.direction = RIGHT
        self.pending_direction = RIGHT
        self.score = 0
        self.fps = BASE_FPS
        self.alive = True
        self.spawn_food()

    def spawn_food(self):
        occupied = set(self.snake)
        free_cells = [
            (x, y)
            for x in range(GRID_WIDTH)
            for y in range(GRID_HEIGHT)
            if (x, y) not in occupied
        ]
        self.food = random.choice(free_cells) if free_cells else None

    def quit(self):
        pygame.quit()
        sys.exit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()
            elif event.type == pygame.KEYDOWN:
                if not self.alive:
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self.reset()
                    elif event.key == pygame.K_ESCAPE:
                        self.quit()
                else:
                    new_direction = KEY_DIRECTIONS.get(event.key)
                    if new_direction and (
                        new_direction[0] != -self.direction[0]
                        or new_direction[1] != -self.direction[1]
                    ):
                        self.pending_direction = new_direction

    def update(self):
        if not self.alive:
            return
        self.direction = self.pending_direction
        head_x, head_y = self.snake[0]
        new_head = (head_x + self.direction[0], head_y + self.direction[1])

        hit_wall = not (
            0 <= new_head[0] < GRID_WIDTH and 0 <= new_head[1] < GRID_HEIGHT
        )
        hits_self = new_head in self.snake[:-1]

        if hit_wall or hits_self:
            self.alive = False
            return

        self.snake.insert(0, new_head)
        if new_head == self.food:
            self.score += 1
            if self.score % 3 == 0:
                self.fps = min(MAX_FPS, self.fps + 1)
            self.spawn_food()
        else:
            self.snake.pop()

    def draw(self):
        self.screen.fill(COLOR_BACKGROUND)

        for x in range(0, WINDOW_WIDTH, CELL_SIZE):
            pygame.draw.line(self.screen, COLOR_GRID, (x, 0), (x, WINDOW_HEIGHT))
        for y in range(0, WINDOW_HEIGHT, CELL_SIZE):
            pygame.draw.line(self.screen, COLOR_GRID, (0, y), (WINDOW_WIDTH, y))

        if self.food:
            draw_cell(self.screen, self.food, COLOR_FOOD)

        for index, segment in enumerate(self.snake):
            color = COLOR_SNAKE_HEAD if index == 0 else COLOR_SNAKE_BODY
            draw_cell(self.screen, segment, color)

        score_surface = self.font.render(f"Score: {self.score}", True, COLOR_TEXT)
        self.screen.blit(score_surface, (10, 8))

        if not self.alive:
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            self.screen.blit(overlay, (0, 0))

            center_x = WINDOW_WIDTH // 2
            center_y = WINDOW_HEIGHT // 2
            title = self.big_font.render("GAME OVER", True, COLOR_FOOD)
            final_score = self.font.render(
                f"Score: {self.score}", True, COLOR_TEXT
            )
            hint = self.font.render(
                "Enter / Space - restart, Esc - exit", True, COLOR_TEXT
            )
            self.screen.blit(
                title, title.get_rect(center=(center_x, center_y - 30))
            )
            self.screen.blit(
                final_score,
                final_score.get_rect(center=(center_x, center_y + 20)),
            )
            self.screen.blit(hint, hint.get_rect(center=(center_x, center_y + 55)))

        pygame.display.flip()

    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(self.fps)


if __name__ == "__main__":
    Game().run()
