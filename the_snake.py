"""Модуль игры «Змейка»."""
from random import randint
import pygame


# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 20

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pygame.display.set_caption('Змейка')

# Настройка времени:
clock = pygame.time.Clock()


class GameObject:
    """
    Общий шаблон для всех объектов на игровом поле.
    Содержит позицию и цвет объекта.
    Всё, что рисуется на экране — наследуется от этого класса.
    """

    def __init__(self, position=None, body_color=None):
        """
        Инициализирует объект с заданной позицией и цветом.
        Если позиция не указана — ставит объект в центр игрового окна.
        """
        if position is None:
            center_x = (GRID_WIDTH // 2) * GRID_SIZE
            center_y = (GRID_HEIGHT // 2) * GRID_SIZE
            position = (center_x, center_y)
        self.position = position
        self.body_color = body_color

    def draw(self, surface):
        """
        Рисует объект на переданной поверхности.
        Должен быть конкретно реализован в классах-наследниках.
        """
        pass


class Apple(GameObject):
    """Модель яблока — еды для змейки."""

    def __init__(self):
        """Создаёт яблоко и бросает его в случайное место на поле."""
        super().__init__(body_color=APPLE_COLOR)
        self.randomize_position()

    def randomize_position(self):
        """Выбирает новый случайный квадрат на сетке для яблока."""
        rand_x = randint(0, GRID_WIDTH - 1) * GRID_SIZE
        rand_y = randint(0, GRID_HEIGHT - 1) * GRID_SIZE
        self.position = (rand_x, rand_y)

    def draw(self, surface):
        """Рисует яблоко – красный квадрат с голубой рамкой."""
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(surface, self.body_color, rect)
        pygame.draw.rect(surface, BORDER_COLOR, rect, 1)


class Snake(GameObject):
    """
    Игровая змейка, которой управляет игрок.
    Хранит тело как список координат сегментов и текущее движение.
    """

    def __init__(self):
        """
        Инициализирует змейку длиной один сегмент по центру экрана.
        Змея движется вправо в начале игры.
        """
        center_x = (GRID_WIDTH // 2) * GRID_SIZE
        center_y = (GRID_HEIGHT // 2) * GRID_SIZE
        start_position = (center_x, center_y)
        super().__init__(body_color=SNAKE_COLOR, position=start_position)
        self.length = 1
        self.positions = [start_position]
        self.direction = RIGHT
        self.next_direction = None
        self.last = None  # Последняя удалённая клетка головы для стирания

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
        new_x = (head_x + dx * GRID_SIZE) % SCREEN_WIDTH
        new_y = (head_y + dy * GRID_SIZE) % SCREEN_HEIGHT
        new_head = (new_x, new_y)
        self.positions.insert(0, new_head)
        if len(self.positions) > self.length:
            self.last = self.positions.pop()
        else:
            self.last = None

    def update_direction(self):
        """
        Применяет введённое пользователем направление, если не противоположно.
        Не даём змейке развернуться и съесть сама себя резко.
        """
        if self.next_direction is not None:
            opposite = {UP: DOWN, DOWN: UP, LEFT: RIGHT, RIGHT: LEFT}
            if self.next_direction != opposite.get(self.direction):
                self.direction = self.next_direction
            self.next_direction = None

    def check_self_collision(self):
        """
        Проверяет, не врезалась ли змейка в собственное тело.
        Возвращает True, если голова пересекается с другими сегментами.
        """
        head = self.get_head_position()
        return head in self.positions[1:]

    def reset(self):
        """
        Возвращает змейку в изначальное положение и задаёт начальные параметры.
        Используется после само-столкновения или рестарта игры.
        """
        center_x = (GRID_WIDTH // 2) * GRID_SIZE
        center_y = (GRID_HEIGHT // 2) * GRID_SIZE
        start_position = (center_x, center_y)
        self.length = 1
        self.positions = [start_position]
        self.direction = RIGHT
        self.next_direction = None
        self.last = None

    def draw(self, surface):
        """
        Отталкиваясь от текущих позиций змейки, рисует каждый сегмент.
        Также очищает хвостовой квадрат последнего перемещения.
        """
        if self.last is not None:
            last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(surface, BOARD_BACKGROUND_COLOR, last_rect)

        for pos in self.positions:
            rect = pygame.Rect(pos, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(surface, self.body_color, rect)
            pygame.draw.rect(surface, BORDER_COLOR, rect, 1)


def handle_keys(snake):
    """
    Отслеживает нажатия клавиш и задаёт новое направление змейке.
    При нажатии стрелок меняет направление движения объекта.
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                snake.next_direction = UP
            elif event.key == pygame.K_DOWN:
                snake.next_direction = DOWN
            elif event.key == pygame.K_LEFT:
                snake.next_direction = LEFT
            elif event.key == pygame.K_RIGHT:
                snake.next_direction = RIGHT


def main():
    """
    Главная функция запуска игры.
    Создаёт змейку и яблоко, запускает игровой цикл,
    обрабатывает ввод, обновляет состояние и отрисовывает всё.
    """
    pygame.init()

    snake = Snake()
    apple = Apple()

    while True:
        clock.tick(SPEED)
        handle_keys(snake)
        snake.update_direction()
        snake.move()

        # Проверка съедания яблока
        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.randomize_position()

            # Проверка столкновения змейки с собой
        if snake.check_self_collision():
            snake.reset()
            screen.fill(BOARD_BACKGROUND_COLOR)
            snake.draw(screen)
            apple.draw(screen)
            pygame.display.update()
            continue  # Перейти в начало цикла (рестарт)

        screen.fill(BOARD_BACKGROUND_COLOR)
        snake.draw(screen)
        apple.draw(screen)
        pygame.display.update()


if __name__ == '__main__':
    main()
