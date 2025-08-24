import pygame
import random
import math

# -----------------------------------------------------------------------------
# 4. Visualizer Effects - class Particle in particle.py
# -----------------------------------------------------------------------------
class Particle:
    def __init__(self, x, y, vx=0, vy=0, life=60, color=(255, 255, 255)):
        self.x, self.y = x, y
        self.vx = vx + random.uniform(-2, 2)
        self.vy = vy + random.uniform(-2, 2)
        self.life = self.max_life = life
        self.color = color
        self.size = random.uniform(1, 4)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.1
        self.vx *= 0.99
        self.vy *= 0.99
        self.life -= 1
        return self.life > 0

    def draw(self, screen):
        if self.life > 0:
            alpha = self.life / self.max_life
            color = tuple(int(c * alpha) for c in self.color)
            size = max(1, int(self.size * alpha))
            pygame.draw.circle(screen, color, (int(self.x), int(self.y)), size)
