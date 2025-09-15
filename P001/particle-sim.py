import pygame
import random

# --- Setup ---
WIDTH, HEIGHT = 800, 600
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
pygame.display.set_caption("Particle Simulation")

# --- Particle Class ---
class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = random.uniform(-2, 2)  # horizontal velocity
        self.vy = random.uniform(-2, 0)  # vertical velocity
        self.life = 100  # lifespan of particle
        self.size = random.randint(2, 5)
        self.color = (255, random.randint(100, 255), 0)  # orange-ish

    def update(self):
        self.vy += 0.1  # gravity
        self.x += self.vx
        self.y += self.vy
        self.life -= 1  # decrease lifespan

    def draw(self, screen):
        alpha = max(0, int(255 * (self.life / 100)))  # fade out
        surface = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
        pygame.draw.circle(surface, (*self.color, alpha), (self.size, self.size), self.size)
        screen.blit(surface, (self.x, self.y))

# --- Main Loop ---
particles = []

running = True
while running:
    screen.fill((0, 0, 0))  # black background

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Spawn new particles at mouse position
    mouse_x, mouse_y = pygame.mouse.get_pos()
    for _ in range(1):  # number of particles per frame
        particles.append(Particle(mouse_x, mouse_y))

    # Update and draw particles
    for particle in particles[:]:
        particle.update()
        particle.draw(screen)
        if particle.life <= 0:
            particles.remove(particle)

    pygame.display.flip()
    clock.tick(60)  # 60 FPS

pygame.quit()
