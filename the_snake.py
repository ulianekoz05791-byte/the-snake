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
        pg.draw.rect(screen, BORDER_COLOR, rect, 1)

    def draw(self):
        """Базовый draw — просто рисует объект в self.position."""
        self.draw_cell(self.position)


class Apple(GameObject):
    """Модель яблока — еды для змейки."""

    def __init__(self, occupied_positions=None):
        """Создаёт яблоко и бросает его в случайное место на поле."""
        super().__init__(body_color=APPLE_COLOR)
        self.randomize_position(occupied_positions or set())

    def randomize_position(self, occupied_positions):
        """Выбирает новый случайный квадрат на сетке для яблока."""
        all_positions = [
            (x * GRID_SIZE, y * GRID_SIZE)
            for x in range(GRID_WIDTH)
            for y in range(GRID_HEIGHT)
        ]
        free_positions = [pos for pos in all_positions
                          if pos not in occupied_positions]
        if free_positions:
            self.position = free_positions[randint(0, len(free_positions) - 1)]
        else:
            self.position = None

    def draw(self):
        """Рисует яблоко – красный квадрат с голубой рамкой."""
        self.draw_cell(self.position, self.body_color)


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
        self.reset()  # Последняя удалённая клетка головы для стирания

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
        new_head = (
            (head_x + dx * GRID_SIZE) % SCREEN_WIDTH,
            (head_y + dy * GRID_SIZE) % SCREEN_HEIGHT,
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
        if new_direction is not None:
            if new_direction != OPPOSITE_DIRECTIONS.get(self.direction):
                self.direction = new_direction

    def check_self_collision(self):
        """
        Проверяет, не врезалась ли змейка в собственное тело.
        Возвращает True, если голова пересекается с другими сегментами.
        """
        head = self.get_head_position()
        return head in self.positions[2:]

    def reset(self):
        """
        Возвращает змейку в изначальное положение и задаёт начальные параметры.
        Используется после само-столкновения или рестарта игры.
        """
        self.length = 1
        self.positions = [CENTER]
        self.direction = RIGHT

    def draw(self):
        """
        Отталкиваясь от текущих позиций змейки, рисует каждый сегмент.
        Также очищает хвостовой квадрат последнего перемещения.
        """
        if self.last is not None:
            self.draw_cell(self.last, BOARD_BACKGROUND_COLOR)  # затираем хвост
            self.draw_cell(self.positions[0])  # рисуем новую голову
        else:
            for pos in self.positions:
                self.draw_cell(pos)


def handle_keys(snake):
    """
    Отслеживает нажатия клавиш и задаёт новое направление змейке.
    При нажатии стрелок меняет направление движения объекта.
    """
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            raise SystemExit
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                pg.quit()
                raise SystemExit
            elif event.key == pg.K_UP:
                snake.update_direction(UP)
            elif event.key == pg.K_DOWN:
                snake.update_direction(DOWN)
            elif event.key == pg.K_LEFT:
                snake.update_direction(LEFT)
            elif event.key == pg.K_RIGHT:
                snake.update_direction(RIGHT)


def draw_grid():
    """Рисуем клеточки на поле, по которым перемещается змейка."""
    for x in range(0, SCREEN_WIDTH, GRID_SIZE):
        pg.draw.line(screen, BORDER_COLOR, (x, 0), (x, SCREEN_HEIGHT))
    for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
        pg.draw.line(screen, BORDER_COLOR, (0, y), (SCREEN_WIDTH, y))


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
        ate_apple = False
        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.randomize_position(snake.positions)
            ate_apple = True  # запомнили факт поедания яблока

        if not ate_apple and snake.check_self_collision():
            snake.reset()
            screen.fill(BOARD_BACKGROUND_COLOR)
            apple.randomize_position(snake.positions)

        update_caption(snake.length, SPEED)

        draw_grid()
        snake.draw()
        apple.draw()
        pg.display.update()


if __name__ == '__main__':
    main()
