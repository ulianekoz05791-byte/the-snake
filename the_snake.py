"""Модуль игры «Змейка»."""

from random import randint

import pygame as pg

# Константы
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
CENTER = ((GRID_WIDTH // 2) * GRID_SIZE, (GRID_HEIGHT // 2) * GRID_SIZE)

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

OPPOSITE_DIRECTIONS = {
    UP: DOWN,
    DOWN: UP,
    LEFT: RIGHT,
    RIGHT: LEFT,
}

ALL_POSITIONS = set([
    (x * GRID_SIZE, y * GRID_SIZE)
    for x in range(GRID_WIDTH)
    for y in range(GRID_HEIGHT)
])

BOARD_BACKGROUND_COLOR = (220, 220, 220)
BORDER_COLOR = (93, 216, 228)
APPLE_COLOR = (255, 0, 0)
SNAKE_COLOR = (0, 255, 0)

SPEED = 20


def update_caption(length, high_score):
    """Заголовок окна, показывая длину змейки, скорость и как выйти."""
    caption = f'Змейка | Длина: {length} | Рекорд: {high_score} | Выход: ESC'
    pg.display.set_caption(caption)


def load_record(filename='record.txt'):
    """
    Загружает рекорд из файла.
    Если файл отсутствует или в нем что-то не так — возвращает 0.
    """
    try:
        with open(filename, 'r') as f:
            return int(f.read())
    except (FileNotFoundError, ValueError):
        return 0


def save_record(record, filename='record.txt'):
    """Сохраняет рекорд в указанный файл."""
    with open(filename, 'w') as f:
        f.write(str(record))


screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pg.display.set_caption('Змейка')
clock = pg.time.Clock()


class GameObject:
    """
    Общий шаблон для всех объектов на игровом поле.
    Содержит позицию и цвет объекта.
    Всё, что рисуется на экране — наследуется от этого класса.
    """

    def __init__(self, position=CENTER, body_color=None):
        """
        Инициализирует объект с заданной позицией и цветом.
        Если позиция не указана — ставит объект в центр игрового окна.
        """
        self.position = position
        self.body_color = body_color

    def draw_cell(self, position, color=None):
        """
        Рисует объект на переданной поверхности.
        Должен быть конкретно реализован в классах-наследниках.
        """
        rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, color or self.body_color, rect)
        pg.draw.rect(screen, BORDER_COLOR, rect, 1)

    def clear_cell(self, position):
        """
        Полностью очищает клетку на игровом поле:
        закрашивает указанную позицию цветом фона без рамки.
        Используется для корректного хвостового сегмента змейки без остатка.
        """
        rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, BOARD_BACKGROUND_COLOR, rect)


class Apple(GameObject):
    """Модель яблока — еды для змейки."""

    def __init__(self, occupied_positions=None, body_color=APPLE_COLOR):
        """Создаёт яблоко и бросает его в случайное место на поле."""
        super().__init__(body_color=body_color)
        self.randomize_position(occupied_positions or set())

    def randomize_position(self, occupied_positions):
        """Выбирает новый случайный квадрат на сетке для яблока."""
        self.position = list(ALL_POSITIONS - set(occupied_positions))[
            randint(0, len(ALL_POSITIONS - set(occupied_positions)) - 1)
        ]

    def draw(self):
        """Рисует яблоко – красный квадрат с голубой рамкой."""
        self.draw_cell(self.position)


class Snake(GameObject):
    """
    Игровая змейка, которой управляет игрок.
    Хранит тело как список координат сегментов и текущее движение.
    """

    def __init__(self, body_color=SNAKE_COLOR):
        """
        Инициализирует змейку длиной один сегмент по центру экрана.
        Змея движется вправо в начале игры.
        """
        super().__init__(body_color=body_color)
        self.reset()

    def get_head_position(self):
        """
        Возвращает координаты головы змейки — самого "первого" сегмента.
        Возвращаемая позиция нужна для столкновений и съедания яблока.
        """
        return self.positions[0]

    def move(self):
        """
        Сдвигает змейку шаг вперёд согласно текущему направлению.
        Новая голова добавляется спереди,
        если больше сегментов чем длина — хвост убирается,
        иначе хвост остаётся (змейка растёт).
        """
        head_x, head_y = self.get_head_position()
        dx, dy = self.direction
        self.positions.insert(
            0,
            (
                (head_x + dx * GRID_SIZE) % SCREEN_WIDTH,
                (head_y + dy * GRID_SIZE) % SCREEN_HEIGHT,
            )
        )
        self.last = (
            self.positions.pop()
            if len(self.positions) > self.length
            else None
        )

    def update_direction(self, new_direction):
        """
        Применяет введённое пользователем направление, если не противоположно.
        Не даём змейке развернуться и съесть сама себя резко.
        """
        if new_direction != OPPOSITE_DIRECTIONS[self.direction]:
            self.direction = new_direction

    def check_self_collision(self):
        """
        Проверяет, не врезалась ли змейка в собственное тело.
        Возвращает True, если голова пересекается с другими сегментами.
        """
        return self.get_head_position() in self.positions[4:]

    def reset(self):
        """
        Возвращает змейку в изначальное положение и задаёт начальные параметры.
        Используется после само-столкновения или рестарта игры.
        """
        self.length = 1
        self.positions = [CENTER]
        self.direction = RIGHT
        self.last = None

    def draw(self):
        """
        Отталкиваясь от текущих позиций змейки, рисует каждый сегмент.
        Также очищает хвостовой квадрат последнего перемещения.
        """
        if self.last:
            self.clear_cell(self.last)
        self.draw_cell(self.get_head_position())


def handle_keys(snake):
    """
    Отслеживает нажатия клавиш и задаёт новое направление змейке.
    При нажатии стрелок меняет направление движения объекта.
    """
    for event in pg.event.get():
        if (
            event.type == pg.QUIT
            or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE)
        ):
            pg.quit()
            raise SystemExit
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_UP:
                snake.update_direction(UP)
            elif event.key == pg.K_DOWN:
                snake.update_direction(DOWN)
            elif event.key == pg.K_LEFT:
                snake.update_direction(LEFT)
            elif event.key == pg.K_RIGHT:
                snake.update_direction(RIGHT)


def main():
    """Главная функция запуска игры."""
    pg.init()
    screen.fill(BOARD_BACKGROUND_COLOR)

    snake = Snake()
    apple = Apple(snake.positions)
    high_score = load_record()

    while True:
        clock.tick(SPEED)
        handle_keys(snake)
        snake.move()

    # Проверка съедания яблока
        if snake.get_head_position() == apple.position:
            snake.length += 1
            if snake.length > high_score:
                high_score = snake.length
                save_record(high_score)
            apple.randomize_position(snake.positions)
        elif snake.check_self_collision():
            if snake.length > high_score:
                high_score = snake.length
                save_record(high_score)
            snake.reset()
            screen.fill(BOARD_BACKGROUND_COLOR)
            apple.randomize_position(snake.positions)

        update_caption(snake.length, high_score)
        snake.draw()
        apple.draw()
        pg.display.update()


if __name__ == '__main__':
    main()
