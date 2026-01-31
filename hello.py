import pygame
import math
import sys

pygame.init()

# --------------------------------------------------
# SETTINGS
# --------------------------------------------------
WIDTH, HEIGHT = 900, 600
GROUND_Y = HEIGHT - 80

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bubble Shooter")

# BACKGROUND
background = pygame.image.load("background.jpg").convert()
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

clock = pygame.time.Clock()

# MUSIC
pygame.mixer.music.load("background.mp3")
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(1.0)

WHITE = (240, 240, 240)
BLACK = (20, 20, 20)
GRAY = (120, 120, 120)
GREEN = (60, 200, 60)
RED = (220, 70, 70)

FONT = pygame.font.SysFont(None, 42)

# --------------------------------------------------
# CLASSES
# --------------------------------------------------

class Wall:
    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)

    def draw(self):
        pygame.draw.rect(screen, BLACK, self.rect)
        


class Bullet:
    SPEED = 10
    LIFE = 6000

    def __init__(self, x, y, angle):
        rad = math.radians(angle)
        self.x = float(x)
        self.y = float(y)
        self.vx = math.cos(rad) * self.SPEED
        self.vy = -math.sin(rad) * self.SPEED
        self.spawn_time = pygame.time.get_ticks()
        self.alive = True

    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), 15, 15)

    def update(self, walls):
        self.x += self.vx
        self.y += self.vy

        r = self.rect()

        if r.left <= 0 or r.right >= WIDTH:
            self.vx *= -1
        if r.top <= 0 or r.bottom >= GROUND_Y:
            self.vy *= -1

        for w in walls:
            if r.colliderect(w.rect):
                if abs(r.right - w.rect.left) < 6 or abs(r.left - w.rect.right) < 6:
                    self.vx *= -1
                else:
                    self.vy *= -1

        if pygame.time.get_ticks() - self.spawn_time > self.LIFE:
            self.alive = False

    def draw(self):
        pygame.draw.circle(screen, GREEN, (int(self.x), int(self.y)), 15)


class Zombie:
    def __init__(self, x, y, speed=0, left=None, right=None):
        self.rect = pygame.Rect(x, y, 30, 35)
        self.speed = speed
        self.left = left
        self.right = right
        self.dir = 1
        self.alive = True

    def update(self):
        if not self.alive or self.speed == 0:
            return
        self.rect.x += self.speed * self.dir
        if self.rect.x < self.left or self.rect.x > self.right:
            self.dir *= -1

    def draw(self):
        if self.alive:
            pygame.draw.rect(screen, RED, self.rect)


class Player:
    def __init__(self):
        self.rect = pygame.Rect(40, GROUND_Y - 50, 30, 50)
        self.speed = 5
        self.angle = 45

    def update(self, keys):
        if keys[pygame.K_a]:
            self.rect.x -= self.speed
        if keys[pygame.K_d]:
            self.rect.x += self.speed

        self.rect.x = max(0, min(WIDTH - self.rect.width, self.rect.x))

        if keys[pygame.K_j]:
            self.angle += 2
        if keys[pygame.K_l]:
            self.angle -= 2

        self.angle %= 360

    def draw(self):
        pygame.draw.rect(screen, WHITE, self.rect)
        rad = math.radians(self.angle)
        for i in range(10, 220, 15):
            x = self.rect.centerx + math.cos(rad) * i
            y = self.rect.centery - math.sin(rad) * i
            pygame.draw.circle(screen, WHITE, (int(x), int(y)), 3)


# --------------------------------------------------
# LEVEL DATA
# --------------------------------------------------

def load_level():
    walls = [
        Wall(200, GROUND_Y - 180, 350, 20),
        Wall(520, GROUND_Y - 90, 120, 20),
        Wall(420, GROUND_Y - 200, 20, 150)
    ]

    zombies = [
        Zombie(220, GROUND_Y - 215, speed=1, left=210, right=520),
        Zombie(540, GROUND_Y - 125)
    ]

    return walls, zombies, 3


def reset():
    return Player(), *load_level(), [], "PLAY"


player, walls, zombies, bullets_left, bullets, state = reset()

# --------------------------------------------------
# MAIN LOOP
# --------------------------------------------------

while True:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and state == "PLAY" and bullets_left > 0:
                bullets.append(Bullet(player.rect.centerx, player.rect.centery, player.angle))
                bullets_left -= 1

            if event.key == pygame.K_r:
                player, walls, zombies, bullets_left, bullets, state = reset()

    keys = pygame.key.get_pressed()

    if state == "PLAY":
        player.update(keys)
        for z in zombies:
            z.update()
        for b in bullets:
            b.update(walls)

        bullets = [b for b in bullets if b.alive]

        for b in bullets:
            for z in zombies:
                if z.alive and b.rect().colliderect(z.rect):
                    z.alive = False

        if all(not z.alive for z in zombies):
            state = "WIN"
        elif bullets_left == 0 and not bullets:
            state = "LOSE"

    # --------------------------------------------------
    # DRAW
    # --------------------------------------------------
    screen.blit(background, (0, 0))
    pygame.draw.rect(screen, (80, 80, 80), (0, GROUND_Y, WIDTH, HEIGHT))

    for w in walls:
        w.draw()
    for z in zombies:
        z.draw()
    for b in bullets:
        b.draw()
    player.draw()

    screen.blit(FONT.render(f"Bullets: {bullets_left}", True, WHITE), (20, 20))

    if state == "WIN":
        screen.blit(FONT.render("YOU WIN! (R to restart)", True, GREEN),
                    (WIDTH // 2 - 180, HEIGHT // 2))

    if state == "LOSE":
        screen.blit(FONT.render("TRY AGAIN (R to restart)", True, RED),
                    (WIDTH // 2 - 190, HEIGHT // 2))

    pygame.display.flip()
