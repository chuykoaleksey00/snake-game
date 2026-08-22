# Snake

Классическая игра «Змейка» на Python и Pygame.

## Возможности

- Управление стрелками или WASD
- Счёт и постепенное ускорение игры
- Экран Game Over с рестартом (Enter / Space)

## Установка и запуск

Требуется Python 3.10+.

```bash
git clone https://github.com/<username>/snake-game.git
cd snake-game
pip install -r requirements.txt
python main.py
```

## Управление

| Клавиша | Действие |
| --- | --- |
| Стрелки / WASD | Движение змейки |
| Enter / Space | Рестарт после проигрыша |
| Esc | Выход из игры |

## Сборка exe (опционально)

```bash
pip install pyinstaller
pyinstaller --onefile --windowed main.py
```

Готовый файл появится в папке `dist/`.
