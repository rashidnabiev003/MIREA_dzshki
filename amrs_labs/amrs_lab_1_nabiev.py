import numpy as np
import pygame, sys
import time
import matplotlib.pyplot as plt

WIDTH = 1000
HEIGHT = 800

def dist(p1, p2):
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    return np.sqrt(dx * dx + dy * dy)

class Obj:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.reservedRobot = None
        self.finished = False

    def getPos(self):
        return self.x, self.y

    def draw(self, screen):
        r = 10
        pygame.draw.ellipse(screen, self.color, [self.x - r, self.y - r, 2 * r, 2 * r], 2)

class Robot:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.attachedObj = None
        self.target = None

    def getPos(self):
        return self.x, self.y

    def draw(self, screen):
        r = 20
        pygame.draw.ellipse(screen, (255, 0, 0), [self.x - r, self.y - r, 2 * r, 2 * r], 2)

    def simulate(self):
        if self.target is not None:
            p1 = self.target
            p2 = (self.x, self.y)
            v = np.array(p1) - np.array(p2)
            d = dist(p1, p2)
            if d > 0:
                v = v / d
                self.x += v[0] * 20
                self.y += v[1] * 20
        if self.attachedObj is not None:
            self.attachedObj.x = self.x
            self.attachedObj.y = self.y

    def findNearestObj(self, objs, threshold=100500):
        res = None
        D = 100500
        for o in objs:
            if o.reservedRobot is not None and o.reservedRobot != self:
                continue
            if o.finished:
                continue
            dNew = dist(o.getPos(), self.getPos())
            if dNew < D:
                D = dNew
                res = o
        if D > threshold:
            res = None
        return res

    def take(self, obj):
        if obj is not None:
            self.attachedObj = obj

    def reset(self):
        self.attachedObj = None
        self.target = None
        self.x = 0
        self.y = 0

def distributeTasks(robots, objs, goal):
    for r in robots:
        if r.attachedObj is not None and dist(r.getPos(), goal.getPos()) < 20:
            r.attachedObj.finished = True
            r.attachedObj = None
            r.target = None
        else:
            if r.attachedObj is None:
                obj = r.findNearestObj(objs)
                if obj is not None and dist(r.getPos(), obj.getPos()) < 20:
                    r.take(obj)
                    r.target = goal.getPos()
                    return

        if r.target is None and r.attachedObj is None:
            obj = r.findNearestObj(objs)
            if obj is None:
                r.target = None  # No tasks left, robot stops moving
                continue
            if obj.reservedRobot is not None:
                continue
            r.target = obj.getPos()
            obj.reservedRobot = r

def checkMission(robots, objs, goal):
    if all(o.finished for o in objs):
        return True
    return False

def generateObjects(N):
    res = []
    for i in range(N):
        o = Obj(np.random.randint(50, WIDTH - 50), np.random.randint(50, HEIGHT - 50), (0, 255, 0))
        res.append(o)
    return res

def main(num_robots, num_objs):
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    start = time.time()

    objs = generateObjects(num_objs)
    goal = Obj(750, 450, (0, 0, 255))

    robots = [Robot(150 + i * 100, 150 + i * 100) for i in range(num_robots)]

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        if checkMission(robots, objs, goal):
            break

        screen.fill((255, 255, 255))

        distributeTasks(robots, objs, goal)

        for r in robots:
            r.simulate()
            r.draw(screen)

        for o in objs:
            o.draw(screen)

        goal.draw(screen)
        pygame.display.update()
        pygame.time.delay(50)

    end = time.time()
    return end - start

def resetRobots(robots):
    for r in robots:
        r.reset()


n_robots = [1, 2, 3, 4, 5, 6]
n_objs = [5, 10, 15]

results = []

for m in n_objs:
    T1_time = []
    T2_time = []
    robots = [Robot(150 + i * 100, 150 + i * 100) for i in range(max(n_robots))]
    for n in n_robots:
        resetRobots(robots)
        t = main(n, m)
        T1_time.append(t)
        T2_time.append(t * n)
    results.append((m, T1_time, T2_time))


for m, T1_time, T2_time in results:
    print(f"Results for M={m} objects:")
    print("Number of Robots:", n_robots)
    print("T1 Times:", T1_time)
    print("T2 Times:", T2_time)
    print()

    plt.figure()
    plt.plot(n_robots, T1_time, label=f'T1 (M={m})', marker='o', color='red')
    plt.plot(n_robots, T2_time, label=f'T2 (M={m})', marker='*', color='blue')
    plt.xlabel('Number of Robots')
    plt.ylabel('Time (s)')
    plt.title(f'Results for M={m} Objects')
    plt.legend()
    plt.grid()
    plt.show()
