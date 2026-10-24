# Snake

Классическая игра «Змейка» на Python и Pygame.

## Возможности

- Управление стрелками или WASD
- Пауза по `P`
- Счёт, рекорд и постепенное ускорение: 8 FPS на старте, +1 FPS каждые 3 очка, максимум 20
- Топ-10 результатов сохраняется между запусками
- Экран Game Over с рестартом (Enter / Space)
- Чистое игровое ядро без pygame — пригодится для веб-версии и автотестов

## Установка и запуск

Требуется Python 3.10+.

```bash
git clone https://github.com/chuykoaleksey00/snake-game.git
cd snake-game
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux / macOS
pip install -e ".[dev]"
python main.py
```

Для запуска без инструментов разработки достаточно `pip install -r requirements.txt`.

Флаги командной строки:

```bash
python main.py                      # обычный запуск
python main.py --scores ./my.json   # другой файл рекордов
python main.py --version            # версия
```

После установки пакета доступна команда `snake-game`.

## Управление

| Клавиша | Действие |
| --- | --- |
| Стрелки / WASD | Движение змейки |
| P | Пауза и продолжение |
| Enter / Space | Рестарт после проигрыша |
| Esc | Выход из игры |

## Рекорды

Результаты хранятся в JSON, топ-10, с датой каждой попытки:

- Windows: `%APPDATA%\snake-game\scores.json`
- Linux / macOS: `$XDG_DATA_HOME/snake-game/scores.json` или `~/.local/share/snake-game/scores.json`

Путь можно переопределить переменной `SNAKE_SCORES_PATH` или флагом `--scores`.
Запись атомарная (временный файл + `os.replace`), поэтому прерванное сохранение не
испортит существующую таблицу. Нечитаемый файл переименовывается в
`scores.json.corrupt-<timestamp>` вместо перезаписи.

## Структура проекта

```
main.py              точка входа
snake_game/
  app.py             игровой цикл, обработка ввода, связка с pygame
  core.py            чистая логика: состояние, шаги, коллизии (без pygame)
  render.py          отрисовка поля, HUD и оверлеев
  storage.py         сохранение и загрузка рекордов
  config.py          геометрия поля, темп и палитра
tests/               pytest: ядро, хранение, headless-смоук
```

## Разработка

```bash
pip install -e ".[dev]"

ruff check .            # линтер
ruff format --check .   # форматирование
mypy                    # типы (strict)
python -m pytest --cov  # тесты и покрытие
```

CI (`.github/workflows/ci.yml`) прогоняет линтер, форматирование, mypy и тесты
на Python 3.11 и 3.13 с headless-драйвером SDL.

## Сборка exe

```bash
pip install -e ".[build]"
pyinstaller snake-game.spec
```

Готовый файл появится в `dist/snake-game.exe`.

## Лицензия

Файл лицензии в репозитории отсутствует — при публикации его нужно добавить.
