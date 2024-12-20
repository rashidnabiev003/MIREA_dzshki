import numpy as np
import pygame
import sys
import pickle

# Константы
colors = [(0, 0, 0), (255, 0, 0), (0, 255, 0), (0, 0, 255)]  # Цвета состояний
R = 35  # Радиус узла
WIDTH, HEIGHT = 1000, 800  # Размеры окна

tasks = []  # Список задач
ts0, ts1 = None, None  # Соединяемые задачи

# Вспомогательные функции
def dist(p1, p2):
    """Евклидово расстояние между двумя точками."""
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    return np.sqrt(dx ** 2 + dy ** 2)

pygame.font.init()
font = pygame.font.SysFont('Comic Sans MS', 20)

def drawText(screen, s, x, y):
    """Отрисовка текста на экране."""
    surf = font.render(s, True, (0, 0, 0))
    screen.blit(surf, (x, y))

# Класс задачи
class Task:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.state = 0  # 0: недоступна, 1: доступна, 2: выполняется, 3: завершена
        self.inps = []  # Входные связи
        self.outs = []  # Выходные связи

    def getPos(self):
        """Получение координат задачи."""
        return (self.x, self.y)

    def draw(self, screen):
        """Отрисовка задачи и её связей."""
        for ts in self.inps:
            x1, y1 = ts.getPos()
            x2, y2 = self.getPos()
            dx, dy = x2 - x1, y2 - y1
            dist = np.sqrt(dx ** 2 + dy ** 2)
            if dist > 0:
                x1_edge = x1 + R * dx / dist
                y1_edge = y1 + R * dy / dist
                x2_edge = x2 - R * dx / dist
                y2_edge = y2 - R * dy / dist
                pygame.draw.line(screen, (100, 100, 100), (x1_edge, y1_edge), (x2_edge, y2_edge), 2)


        pygame.draw.ellipse(screen, colors[self.state],
                            [self.x - R, self.y - R, 2 * R, 2 * R], 2)
        drawText(screen, f"T{self.id}", self.x - 15, self.y - 15)


def findTask(pos, r):
    for ts in tasks:
        if dist(pos, ts.getPos()) < r:
            return ts


def findPossibleTasks():
    for ts in tasks:
        if ts.state == 0:
            if len(ts.inps) == 0 or all(inp.state == 3 for inp in ts.inps):
                ts.state = 1


def performTasks():
    for ts in tasks:
        if ts.state == 1:
            ts.state = 2
        elif ts.state == 2:
            ts.state = 3


def executeScenario():
    steps = 0
    max_steps = 100
    while any(ts.state != 3 for ts in tasks):
        if steps >= max_steps:
            print("Ошибка: превышено максимальное количество шагов. Проверьте зависимости задач.")
            break
        findPossibleTasks()
        performTasks()
        steps += 1
    return steps


def visualizeScenario(screen):
    screen.fill((255, 255, 255))
    if tasks:
        for ts in tasks:
            ts.draw(screen)
    else:
        drawText(screen, "No tasks to display. Please add tasks manually.", WIDTH // 2 - 200, HEIGHT // 2)
    pygame.display.flip()

# Основная функция
def main():
    global tasks, ts0, ts1

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Lab2: Manual Task Management")
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                ts0 = findTask(event.pos, R)
                if ts0 is None:
                    ts = Task(len(tasks), *event.pos)
                    tasks.append(ts)

            if event.type == pygame.MOUSEBUTTONUP:
                ts1 = findTask(event.pos, R)
                if ts0 and ts1 and ts0 != ts1:
                    ts0.outs.append(ts1)
                    ts1.inps.append(ts0)
                ts0, ts1 = None, None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:  # Найти доступные задачи
                    findPossibleTasks()
                if event.key == pygame.K_2:  # Выполнить доступные задачи
                    performTasks()
                if event.key == pygame.K_3:  # Полный шаг (поиск + выполнение)
                    findPossibleTasks()
                    performTasks()

        visualizeScenario(screen)
        clock.tick(30)

if __name__ == "__main__":
    main()
