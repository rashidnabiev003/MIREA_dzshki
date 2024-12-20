import itertools
import sys
import pygame
import numpy as np
import math

colors = [[0, 255, 0], [255, 0, 255], [0, 127, 255],
          [255, 127, 0], [127, 191, 127], [106, 42, 137],
          [75, 118, 2], [213, 0, 9], [227, 127, 252], [0, 0, 255]]

sz = (800, 600)

pygame.font.init()
font = pygame.font.SysFont('Comic Sans MS', 20)

def drawText(screen, s, x, y):
    surf = font.render(s, True, (0, 0, 0))
    screen.blit(surf, (x, y))

class Axis:
    def __init__(self, id, x, y, lx, ly):
        self.id, self.x, self.y, self.lx, self.ly = id, x, y, lx, ly
        self.taskIds = []

    def draw(self, screen, tasks):
        dx, kt, h, gap = 20, 2, 25, 7
        pygame.draw.line(screen, (0, 0, 0), [self.x, self.y + 50], [self.x + self.lx, self.y + 50], 2)
        pygame.draw.line(screen, (0, 0, 0), [self.x, self.y + 50], [self.x, self.y - self.ly + 50], 2)
        drawText(screen, f"{self.id}", self.x - 20, self.y - self.ly + 50)

        shift = 0
        for i in self.taskIds:
            t = tasks[i] * kt
            pygame.draw.rect(screen, colors[i], [self.x + shift + gap / 2, self.y - h - 5 + 50, t - gap / 2, h], 0)
            drawText(screen, f"{i}", self.x + shift + t / 2 - 10, self.y - self.ly * 0.83 + 50)
            shift += t

    def getTotalTime(self, tasks):
        return sum(tasks[i] for i in self.taskIds)

def getPartitions(lst, numGroups, recursionLevel=0):
    if len(lst) == 0:
        return [[]]
    result = []
    for i in range(1, len(lst) + 1):
        for group in itertools.combinations(lst, i):
            remaining = [x for x in lst if x not in group]
            for p in getPartitions(remaining, -1, recursionLevel + 1):
                tmpResult = [list(group)] + p
                if recursionLevel == 0 and numGroups > 0 and len(tmpResult) != numGroups:
                    continue
                result.append(tmpResult)
    return result

def calcTime(tasks, axes):
    return max(a.getTotalTime(tasks) for a in axes)

def getBestPartition(axes, tasks):
    ii = np.arange(len(tasks))
    pp = getPartitions(ii, len(axes), 0)
    bestT = float('inf')
    bestPartition = None
    for p in pp:
        for i in range(len(axes)):
            axes[i].taskIds = p[i]
        t = calcTime(tasks, axes)
        if t < bestT:
            bestT = t
            bestPartition = p
    # Преобразование np.int64 в int
    bestPartition = [[int(x) for x in group] for group in bestPartition]
    return bestPartition, bestT

def getWorstPartition(axes, tasks):
    ii = np.arange(len(tasks))
    pp = getPartitions(ii, len(axes), 0)
    worstT = 0
    worstPartition = None
    for p in pp:
        if all(len(group) > 0 for group in p):
            for i in range(len(axes)):
                axes[i].taskIds = p[i]
            t = calcTime(tasks, axes)
            if t > worstT:
                worstT = t
                worstPartition = p
    # Преобразование np.int64 в int
    worstPartition = [[int(x) for x in group] for group in worstPartition]
    return worstPartition, worstT

def main():
    screen = pygame.display.set_mode(sz)
    timer = pygame.time.Clock()
    fps = 20

    # Выбор количества роботов
    num_robots = int(input("Введите количество роботов: "))
    tasks = [12, 50, 25, 70, 40, 58]

    axes = [
        Axis(i, 100, 200 + i * 70, 300, 70) for i in range(num_robots)
    ]

    for i, axis in enumerate(axes):
        axis.taskIds = [j for j in range(i, len(tasks), num_robots)]

    initial_time = calcTime(tasks, axes)
    print("Initial time: ", initial_time)

    bestPartition, bestT = getBestPartition(axes, tasks)
    print("Best time: ", bestT)
    print("Best partition: ", bestPartition)

    for i in range(len(axes)):
        axes[i].taskIds = bestPartition[i]

    worstPartition, worstT = getWorstPartition(axes, tasks)
    print("Worst time: ", worstT)
    print("Worst partition: ", worstPartition)

    # Цикл отрисовки
    running = True
    while running:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False

        screen.fill((255, 255, 255))  # Заливка фона

        # Отрисовка осей и задач
        for a in axes:
            a.draw(screen, tasks)

        # Вывод текстовой информации
        drawText(screen, f"Initial time: {initial_time}", 10, 10)
        drawText(screen, f"Best time: {bestT}", 10, 40)
        drawText(screen, f"Worst time: {worstT}", 10, 70)
        drawText(screen, f"Best Partition: {bestPartition}", 10, 100)
        drawText(screen, f"Worst Partition: {worstPartition}", 10, 130)

        pygame.display.flip()
        timer.tick(fps)

    pygame.quit()
    sys.exit(0)

if __name__ == "__main__":
    main()
