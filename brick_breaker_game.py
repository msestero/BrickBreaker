import pygame
import random
import sys

# Initialize pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

# Game constants
PADDLE_WIDTH = 100
PADDLE_HEIGHT = 20
BALL_RADIUS = 10
BRICK_WIDTH = 60
BRICK_HEIGHT = 20
BRICK_GAP = 5
FPS = 60
MAX_ENLARGEMENTS = 2
POWERUP_PROBABILITY = 0.05

# Initialize screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Brick Breaker")

# Clock
clock = pygame.time.Clock()

# Paddle class
class Paddle(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.base_width = PADDLE_WIDTH
        self.image = pygame.Surface((self.base_width, PADDLE_HEIGHT))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.midbottom = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30)
        self.speed = 7
        self.enlargements = 0
        self.enlarge_timer = 0

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.speed
        self.rect.x = max(0, min(SCREEN_WIDTH - self.rect.width, self.rect.x))

        if self.enlarge_timer > 0:
            self.enlarge_timer -= 1
            if self.enlarge_timer == 0:
                self.shrink()

    def enlarge(self):
        if self.enlargements < MAX_ENLARGEMENTS:
            self.enlargements += 1
            self.rect.width += 50
            self.image = pygame.Surface((self.rect.width, PADDLE_HEIGHT))
            self.image.fill(WHITE)
            self.enlarge_timer = FPS * 10  # 10 seconds

    def shrink(self):
        if self.enlargements > 0:
            self.enlargements -= 1
            self.rect.width -= 50
            self.image = pygame.Surface((self.rect.width, PADDLE_HEIGHT))
            self.image.fill(WHITE)

# Ball class
class Ball(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((BALL_RADIUS * 2, BALL_RADIUS * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, RED, (BALL_RADIUS, BALL_RADIUS), BALL_RADIUS)
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.speed_x = random.choice([-4, 4])
        self.speed_y = -4

    def update(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        if self.rect.left <= 0 or self.rect.right >= SCREEN_WIDTH:
            self.speed_x = -self.speed_x
        if self.rect.top <= 0:
            self.speed_y = -self.speed_y

    def bounce(self, paddle):
        # Determine bounce angle based on hit position
        hit_pos = (self.rect.centerx - paddle.rect.left) / paddle.rect.width
        angle = hit_pos - 0.5  # Normalize to range [-0.5, 0.5]
        self.speed_x = angle * 8
        self.speed_y = -abs(self.speed_y)

# Brick class
class Brick(pygame.sprite.Sprite):
    def __init__(self, x, y, hits):
        super().__init__()
        self.hits = hits
        self.image = pygame.Surface((BRICK_WIDTH, BRICK_HEIGHT))
        self.update_color()
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def update_color(self):
        if self.hits == 1:
            self.image.fill(BLUE)
        elif self.hits == 2:
            self.image.fill(RED)
        else:
            self.image.fill(GREEN)

    def hit(self):
        self.hits -= 1
        if self.hits > 0:
            self.update_color()
        else:
            self.kill()

# Power-up class
class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, effect):
        super().__init__()
        self.image = pygame.Surface((20, 20))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed_y = 3
        self.effect = effect

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

# Functions

def generate_level(level):
    bricks = pygame.sprite.Group()
    rows = random.randint(4, 6)
    for row in range(rows):
        for col in range(SCREEN_WIDTH // (BRICK_WIDTH + BRICK_GAP)):
            x = col * (BRICK_WIDTH + BRICK_GAP)
            y = row * (BRICK_HEIGHT + BRICK_GAP) + 50
            hits = 1 + level // 2  # Bricks require more hits as levels increase
            brick = Brick(x, y, hits)
            bricks.add(brick)
    return bricks

def spawn_ball(all_sprites, balls, x, y):
    new_ball = Ball()
    new_ball.rect.center = (x, y)
    all_sprites.add(new_ball)
    balls.add(new_ball)

def main():
    paddle = Paddle()
    ball = Ball()
    level = 1
    bricks = generate_level(level)

    all_sprites = pygame.sprite.Group()
    balls = pygame.sprite.Group()
    all_sprites.add(paddle, ball, *bricks)
    balls.add(ball)

    powerups = pygame.sprite.Group()

    score = 0
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Update
        all_sprites.update()

        # Ball collision with paddle
        for ball in balls:
            if ball.rect.colliderect(paddle.rect):
                ball.bounce(paddle)

        # Ball collision with bricks
        for ball in balls:
            hit_bricks = pygame.sprite.spritecollide(ball, bricks, False)
            for brick in hit_bricks:
                ball.speed_y = -ball.speed_y
                brick.hit()
                score += 100
                if random.random() < POWERUP_PROBABILITY:  # 5% chance to spawn a power-up
                    effect = random.choice(["enlarge", "multi_ball"])
                    powerup = PowerUp(brick.rect.centerx, brick.rect.centery, effect)
                    all_sprites.add(powerup)
                    powerups.add(powerup)

        # Power-up collision with paddle
        for powerup in pygame.sprite.spritecollide(paddle, powerups, True):
            if powerup.effect == "enlarge":
                paddle.enlarge()
            elif powerup.effect == "multi_ball":
                for _ in range(2):  # Spawn two additional balls
                    spawn_ball(all_sprites, balls, paddle.rect.centerx, paddle.rect.top - 10)

        # Ball goes out of bounds
        for ball in list(balls):
            if ball.rect.top > SCREEN_HEIGHT:
                balls.remove(ball)
                all_sprites.remove(ball)

        if not balls:
            print("Game Over")
            running = False

        # Check if all bricks are destroyed
        if not bricks:
            print("Level Complete!")
            level += 1
            bricks = generate_level(level)
            all_sprites.add(*bricks)

        # Draw
        screen.fill(BLACK)
        all_sprites.draw(screen)

        # Display score
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
