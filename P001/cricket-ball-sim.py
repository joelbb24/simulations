import pygame
import time

# --- Setup ---
WIDTH, HEIGHT = 800, 400
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
pygame.display.set_caption("Cricket Ball Simulation")

# --- Physics ---
GRAVITY = 0.5
FRICTION = 0.99  # slows horizontal motion after bounce
BALL_DELAY = 2000  # milliseconds (2 seconds)

# --- Ball Class ---
class Ball:
    def __init__(self, x, y, vx, vy, radius=10):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = radius
        self.color = (255, 0, 0)

    def update(self):
        self.vy += GRAVITY  # gravity
        self.x += self.vx
        self.y += self.vy

        # Collision with pitch (ground)
        if self.y + self.radius >= HEIGHT - 50:  # pitch at y = HEIGHT-50
            self.y = HEIGHT - 50 - self.radius
            self.vy = -self.vy * 0.8  # bounce with damping
            self.vx *= FRICTION  # friction reduces horizontal speed

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

# --- Main Loop ---
balls = []
last_spawn_time = pygame.time.get_ticks()  # current time in milliseconds

running = True
while running:
    screen.fill((0, 128, 0))  # green pitch background

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Spawn new ball every 2 seconds
    current_time = pygame.time.get_ticks()
    if current_time - last_spawn_time >= BALL_DELAY:
        balls.append(Ball(x=100, y=100, vx=10, vy=0))
        last_spawn_time = current_time

    # Draw pitch
    pygame.draw.rect(screen, (210, 180, 140), (0, HEIGHT-50, WIDTH, 50))  # brown pitch

    # Update and draw all balls
    for ball in balls[:]:  # iterate over a copy
        ball.update()
        ball.draw(screen)
        # Optional: remove balls that have stopped moving (if desired)
        if abs(ball.vx) < 0.1 and abs(ball.vy) < 0.1 and ball.y + ball.radius >= HEIGHT - 50:
            balls.remove(ball)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
