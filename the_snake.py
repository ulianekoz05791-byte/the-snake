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

ALL_POSITIONS = [
    (x * GRID_SIZE, y * GRID_SIZE)
    for x in range(GRID_WIDTH)
    for y in range(GRID_HEIGHT)
]

BOARD_BACKGROUND_COLOR = (220, 220, 220)
BORDER_COLOR = (93, 216, 228)
APPLE_COLOR = (255, 0, 0)
SNAKE_COLOR = (0, 255, 0)

SPEED = 20


def update_caption(length, speed):
    """Заголовок окна, показывая длину змейки, скорость и как выйти."""
    caption = f'Змейка | Длина: {length} | Скорость: {speed} | Выход: ESC'
    pg.display.set_caption(caption)


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

    def draw(self):
        """Базовый draw — просто рисует объект в self.position."""
        pass


class Apple(GameObject):
    """Модель яблока — еды для змейки."""

    def __init__(self, occupied_positions=None):
        """Создаёт яблоко и бросает его в случайное место на поле."""
        super().__init__(body_color=APPLE_COLOR)
        self.randomize_position(occupied_positions or set())

    def randomize_position(self, occupied_positions):
        """Выбирает новый случайный квадрат на сетке для яблока."""
        free_positions = list(set(ALL_POSITIONS) - set(occupied_positions))
        self.position = free_positions[randint(0, len(free_positions) - 1)]

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
        new_head = (
            (self.get_head_position()[0]
             + self.direction[0] * GRID_SIZE) % SCREEN_WIDTH,
            (self.get_head_position()[1]
             + self.direction[1] * GRID_SIZE) % SCREEN_HEIGHT,
        )

        self.positions.insert(0, new_head)
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
        return self.get_head_position() in self.positions[3:]

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
        if self.last is not None:
            self.draw_cell(self.last, BOARD_BACKGROUND_COLOR)

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
    """
    Главная функция запуска игры.
    Создаёт змейку и яблоко, запускает игровой цикл,
    обрабатывает ввод, обновляет состояние и отрисовывает всё.
    """
    pg.init()
    screen.fill(BOARD_BACKGROUND_COLOR)  # заливка фона один раз в начале

    snake = Snake()
    apple = Apple(snake.positions)

    while True:
        clock.tick(SPEED)
        handle_keys(snake)
        snake.move()

        # Проверка съедания яблока
        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.randomize_position(snake.positions)
        elif snake.check_self_collision():
            snake.reset()
            screen.fill(BOARD_BACKGROUND_COLOR)
            apple.randomize_position(snake.positions)

        update_caption(snake.length, SPEED)

        snake.draw()
        apple.draw()
        pg.display.update()


if __name__ == '__main__':
    main()
