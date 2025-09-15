import pygame
import math

# --- Setup ---
WIDTH, HEIGHT = 800, 400
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
pygame.display.set_caption("Cricket Ball Pseudo-3D Simulation")

# --- Camera Settings ---
camX, camY, camZ = WIDTH//2, HEIGHT//2, -300  # camera behind the bowler
f = 250  # focal length for perspective

# --- Physics ---
GRAVITY = 0.6
PITCH_HEIGHT = 0  # z=0 is pitch level

# --- Ball Class ---
class Ball:
    def __init__(self, x, y, z, vx, vy, vz, radius=8):
        self.x = x
        self.y = y
        self.z = z
        self.vx = vx
        self.vy = vy
        self.vz = vz
        self.radius = radius
        self.color = (255, 0, 0)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.z += self.vz
        self.vz -= GRAVITY  # gravity pulls ball down

        # Bounce on pitch
        if self.z <= PITCH_HEIGHT:
            self.z = PITCH_HEIGHT
            self.vz = -self.vz * 0.7  # bounce with damping
            self.vx *= 0.99  # friction slows forward
            self.vy *= 0.95  # spin effect reduces lateral velocity

    def draw(self, screen):
        # Simple perspective projection
        scale = f / (self.z + f + 1e-5)
        screen_x = int(camX + (self.x - camX) * scale)
        screen_y = int(camY + (self.y - camY) * scale)
        radius = max(1, int(self.radius * scale))
        pygame.dr
