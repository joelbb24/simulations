import pygame
import math

# --- Setup ---
WIDTH, HEIGHT = 800, 400
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
pygame.display.set_caption("Cricket Ball Simulation with Bat")

# --- Physics ---
GRAVITY = 0.5
FRICTION = 0.99
BALL_DELAY = 2000  # 2 seconds

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
        self.vy += GRAVITY
        self.x += self.vx
        self.y += self.vy

        # Collision with pitch
        if self.y + self.radius >= HEIGHT - 50:
            self.y = HEIGHT - 50 - self.radius
            self.vy = -self.vy * 0.8
            self.vx *= FRICTION

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

# --- Bat Class ---
class Bat:
    def __init__(self, x, y, width=10, height=150):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.angle = -45  # starting swing angle
        self.swinging = False

    def swing(self):
        self.swinging = True
        self.angle = -45  # reset swing angle

    def update(self):
        if self.swinging:
            self.angle += 5  # swing speed
            if self.angle >= 40:  # swing finished
                self.swinging = False
                self.angle = -45

    def draw(self, screen):
        # Create the bat surface
        bat_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        bat_surface.fill((139, 69, 19))  # brown bat

        # Rotate the bat
        rotated_bat = pygame.transform.rotate(bat_surface, self.angle)
        rect = rotated_bat.get_rect(center=(self.x + self.width//2, self.y - self.height//2))

        screen.blit(rotated_bat, rect.topleft)



    def hit_ball(self, ball):
        # Simple collision: if ball near bat's rectangle
        bat_rect = pygame.Rect(self.x, self.y - self.height, self.width, self.height)
        if bat_rect.collidepoint(ball.x, ball.y):
            ball.vx = 10  # reflect forward
            ball.vy = -5  # give upward bounce

# --- Main Loop ---
balls = []
last_spawn_time = pygame.time.get_ticks()
bat = Bat(x=WIDTH-100, y=HEIGHT-50 - 20)  # batsman near end of pitch

running = True
while running:
    screen.fill((0, 128, 0))  # green field

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Spawn balls every 2 seconds
    current_time = pygame.time.get_ticks()
    if current_time - last_spawn_time >= BALL_DELAY:
        balls.append(Ball(x=100, y=100, vx=10, vy=0))
        last_spawn_time = current_time

    # Draw pitch
    pygame.draw.rect(screen, (210, 180, 140), (0, HEIGHT-50, WIDTH, 50))

    # Update and draw balls
    for ball in balls[:]:
        ball.update()
        bat.hit_ball(ball)  # check collision with bat
        ball.draw(screen)
        # Remove balls that stop
        if abs(ball.vx) < 0.1 and abs(ball.vy) < 0.1 and ball.y + ball.radius >= HEIGHT-50:
            balls.remove(ball)

    # Update and draw bat
    bat.update()
    bat.draw(screen)

    # Auto swing if ball close to bat
    for ball in balls:
        if ball.x > bat.x - 50 and not bat.swinging:
            bat.swing()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
