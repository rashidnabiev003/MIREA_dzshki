import sys
import pygame
import numpy as np
import math
import time

# Constants
sz = (800, 600)
fps = 20
pygame.font.init()
font = pygame.font.SysFont('Comic Sans MS', 20)

# Helper functions
def dist(p1, p2):
    return np.linalg.norm(np.subtract(p1, p2))

def rot(v, ang):
    s, c = math.sin(ang), math.cos(ang)
    return [v[0] * c - v[1] * s, v[0] * s + v[1] * c]

def rotArr(vv, ang):
    return [rot(v, ang) for v in vv]

def drawText(screen, s, x, y):
    surf = font.render(s, True, (0, 0, 0))
    screen.blit(surf, (x, y))

def drawRotRect(screen, color, pc, w, h, ang):
    pts = [[-w / 2, -h / 2], [+w / 2, -h / 2], [+w / 2, +h / 2], [-w / 2, +h / 2]]
    pts = rotArr(pts, ang)
    pts = np.add(pts, pc)
    pygame.draw.polygon(screen, color, pts, 2)

# Classes
class Bullet:
    def __init__(self, x, y, ang):
        self.x = x
        self.y = y
        self.ang = ang
        self.vx = 200
        self.L = 10
        self.exploded = False

    def getPos(self):
        return [self.x, self.y]

    def draw(self, screen):
        p0 = self.getPos()
        p1 = rot([-self.L / 2, 0], self.ang)
        p2 = rot([+self.L / 2, 0], self.ang)
        pygame.draw.line(screen, (0, 0, 0), np.add(p0, p1), np.add(p0, p2), 3)

    def sim(self, dt):
        vec = [self.vx, 0]
        vec = rot(vec, self.ang)
        self.x += vec[0] * dt
        self.y += vec[1] * dt

class Tank:
    def __init__(self, id, x, y, ang):
        self.id = id
        self.x = x
        self.y = y
        self.ang = ang
        self.angGun = 0
        self.L = 70
        self.W = 45
        self.vx = 0
        self.vy = 0
        self.va = 0
        self.vaGun = 0
        self.health = 100
        self.active = True

    def fire(self, target_pos=None, target_velocity=None, dt=0.1):
        if not self.active:
            return None
        r = self.W / 2.3
        LGun = self.L / 2

        if target_pos and target_velocity:  # Predictive firing
            predicted_pos = [
                target_pos[0] + target_velocity[0] * dt,
                target_pos[1] + target_velocity[1] * dt
            ]
            dx, dy = predicted_pos[0] - self.x, predicted_pos[1] - self.y
        elif target_pos:  # Direct firing
            dx, dy = target_pos[0] - self.x, target_pos[1] - self.y
        else:
            return None

        self.angGun = math.atan2(dy, dx) - self.ang
        p2 = rot([r + LGun, 0], self.ang + self.angGun)
        p2 = np.add(self.getPos(), p2)
        return Bullet(*p2, self.ang + self.angGun)

    def getPos(self):
        return [self.x, self.y]

    def draw(self, screen):
        if not self.active:
            return
        pts = [[self.L / 2, self.W / 2], [self.L / 2, -self.W / 2], [-self.L / 2, -self.W / 2], [-self.L / 2, self.W / 2]]
        pts = rotArr(pts, self.ang)
        pts = np.add(pts, self.getPos())
        pygame.draw.polygon(screen, (0, 0, 0), pts, 2)
        r = self.W / 2.3
        pygame.draw.circle(screen, (0, 0, 0), self.getPos(), r, 2)
        LGun = self.L / 2
        p0 = self.getPos()
        p1 = rot([r, 0], self.ang + self.angGun)
        p2 = rot([r + LGun, 0], self.ang + self.angGun)
        pygame.draw.line(screen, (0, 0, 0), np.add(p0, p1), np.add(p0, p2), 3)
        drawText(screen, f"{self.id} ({self.health})", self.x, self.y - self.L / 2 - 12)

    def sim(self, dt):
        if not self.active:
            return
        vec = [self.vx, self.vy]
        vec = rot(vec, self.ang)
        self.x += vec[0] * dt
        self.y += vec[1] * dt
        self.ang += self.va * dt
        self.angGun += self.vaGun * dt
        if self.health <= 0:
            self.active = False

# Main function
def main():
    screen = pygame.display.set_mode(sz)
    timer = pygame.time.Clock()

    # Create tanks
    n = 0  # Example variant number
    team1 = [Tank(i, 200 + n * 5, 100 + i * 100, 0) for i in range(4)]
    team2 = [Tank(i + 4, 600 + n * 5, 100 + i * 100, math.pi) for i in range(4)]

    for t in team1:
        t.vx = 20
        t.va = 0.5
    for t in team2:
        t.vx = -20
        t.va = -0.5

    bullets = []
    start_time = time.time()

    strategy_1 = "prediction"  # "simple" or "prediction"
    strategy_2 = "prediction"  # "simple" or "prediction"


    while any(t.active for t in team1) and any(t.active for t in team2):
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                sys.exit(0)

        dt = 1 / fps

        # Simulate tanks
        for t in team1:
            t.sim(dt)
            if t.active:
                target = min(team2, key=lambda e: dist(t.getPos(), e.getPos()) if e.active else float('inf'))
                if target.active and np.random.rand() < 0.05:
                    if strategy_1 == "prediction":
                        target_velocity = [target.vx, target.vy]
                        bullet = t.fire(target.getPos(), target_velocity, dt)
                    else:
                        bullet = t.fire(target.getPos())
                    if bullet:
                        bullets.append(bullet)

        for t in team2:
            t.sim(dt)
            if t.active:
                target = min(team1, key=lambda e: dist(t.getPos(), e.getPos()) if e.active else float('inf'))
                if target.active and np.random.rand() < 0.05:
                    if strategy_2 == "prediction":
                        target_velocity = [target.vx, target.vy]
                        bullet = t.fire(target.getPos(), target_velocity, dt)
                    else:
                        bullet = t.fire(target.getPos())
                    if bullet:
                        bullets.append(bullet)

        # Simulate bullets
        for b in bullets:
            b.sim(dt)
            for t in team1 + team2:
                if t.active and dist(t.getPos(), b.getPos()) < t.L / 2:
                    b.exploded = True
                    t.health -= 10
                    break

        bullets = [b for b in bullets if not b.exploded]

        # Draw everything
        screen.fill((255, 255, 255))
        for t in team1 + team2:
            t.draw(screen)
        for b in bullets:
            b.draw(screen)
        pygame.display.flip()
        timer.tick(fps)

    # Determine results
    elapsed_time = time.time() - start_time
    team1_health = sum(t.health for t in team1 if t.active)
    team2_health = sum(t.health for t in team2 if t.active)

    print(f"Battle duration: {elapsed_time:.2f} seconds")
    print(f"Team 1 remaining health: {team1_health}")
    print(f"Team 2 remaining health: {team2_health}")
    if team1_health > team2_health:
        print("Team 1 wins!")
    elif team2_health > team1_health:
        print("Team 2 wins!")
    else:
        print("It's a draw!")

if __name__ == "__main__":
    main()
