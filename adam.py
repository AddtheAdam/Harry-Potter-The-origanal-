import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("The World's Hardest Game Clone")

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
GRAY = (128, 128, 128)  # Color for barriers

# Player
player_size = 30
player_x = 50
player_y = HEIGHT // 2
player_speed = 3

# Enemies
enemy_size = 50
enemies = []
enemy_speed_multiplier = 1
# Load enemy sprite
enemy_sprite = pygame.image.load('security.png')
enemy_sprite = pygame.transform.scale(enemy_sprite, (enemy_size, enemy_size))

# Barriers
barrier_height = 50  # Height of top and bottom barriers
barrier_width = 30

# Increase the height of only the spawn barrier
spawn_barrier_height = 240  # New height for the spawn barrier

# Spawn barrier 2 blocks in front of the player (assuming "in front" means to the right)
spawn_barrier_x = player_x + 2 * barrier_width
spawn_barrier_y = player_y - spawn_barrier_height // 2
spawn_barrier = pygame.Rect(spawn_barrier_x, spawn_barrier_y, barrier_width, spawn_barrier_height)

# Top and Bottom Barriers
top_barrier = pygame.Rect(0, 100, WIDTH, barrier_height)
bottom_barrier = pygame.Rect(0, HEIGHT - 150, WIDTH, barrier_height)

# Set a single speed for both groups
group_speed_x = random.randint(5, 5) * enemy_speed_multiplier

# Spawn 3 enemies on the left side, 1 block apart
start_y = top_barrier.bottom + 25
for i in range(3):
    enemy = pygame.Rect(0, start_y + i * (enemy_size * 2), enemy_size, enemy_size)
    enemies.append({
        "rect": enemy, 
        "speed_x": group_speed_x,
        "speed_y": 0,
        "group": "left"
    })

# Spawn 2 enemies on the right side
right_start_y = (top_barrier.bottom + bottom_barrier.top) // 2 - enemy_size
for i in range(2):
    enemy = pygame.Rect(WIDTH - enemy_size, right_start_y + i * (enemy_size * 2), enemy_size, enemy_size)
    enemies.append({
        "rect": enemy, 
        "speed_x": -group_speed_x,  # Moving in opposite direction
        "speed_y": 0,
        "group": "right"
    })

# Goal
goal = pygame.Rect(WIDTH - 70, HEIGHT // 2 - 25, 50, 50)

# Font for displaying messages
font = pygame.font.SysFont(None, 55)

# Confetti class
class Confetti:
    def __init__(self):
        self.particles = []
        self.colors = [RED, BLUE, GREEN]
    
    def generate(self, x, y):
        self.particles = []  # Clear previous particles
        for _ in range(1000):  # Create 1000 confetti particles
            color = random.choice(self.colors)
            size = random.randint(5, 10)
            dx = random.uniform(-5, 5)
            dy = random.uniform(-5, 5)
            self.particles.append({'x': x, 'y': y, 'dx': dx, 'dy': dy, 'size': size, 'color': color})
    
    def update(self):
        for particle in self.particles:
            particle['x'] += particle['dx']
            particle['y'] += particle['dy']
            particle['dy'] += 0.1  # Gravity effect
    
    def draw(self, screen):
        for particle in self.particles:
            pygame.draw.circle(screen, particle['color'], (int(particle['x']), int(particle['y'])), particle['size'])

# Button class
class Button:
    def __init__(self, x, y, width, height, text, color, text_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.font = pygame.font.SysFont(None, 32)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

# Initialize confetti
confetti = Confetti()
confetti_active = False
message_displayed = False

# Create a Next Level button (initially hidden)
next_level_button = Button(WIDTH // 2 - 75, HEIGHT // 2 + 50, 150, 50, "Next Level", GREEN, WHITE)

# Add a level counter
current_level = 1

# Game loop
clock = pygame.time.Clock()

def maintain_group_distance(group):
    for i in range(len(group) - 1):
        current = group[i]["rect"]
        next_enemy = group[i + 1]["rect"]
        distance = next_enemy.top - current.bottom
        if distance != enemy_size:
            move = (enemy_size - distance) / 2
            current.y -= move
            next_enemy.y += move

def display_message(message):
    text = font.render(message, True, (0, 0, 0))
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(text, text_rect)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if confetti_active and next_level_button.is_clicked(event.pos):
                # Reset the game for the next level
                current_level += 1
                player_x, player_y = 50, HEIGHT // 2
                confetti_active = False
                message_displayed = False
                
                # Increase difficulty (e.g., increase enemy speed)
                enemy_speed_multiplier += 0.5
                for enemy in enemies:
                    enemy["speed_x"] = abs(enemy["speed_x"]) * (1 if enemy["speed_x"] > 0 else -1) * enemy_speed_multiplier

    # Player movement
    keys = pygame.key.get_pressed()
    new_player_x = player_x
    new_player_y = player_y
    
    if keys[pygame.K_LEFT]:
        new_player_x -= player_speed
    if keys[pygame.K_RIGHT]:
        new_player_x += player_speed
    if keys[pygame.K_UP]:
        new_player_y -= player_speed
    if keys[pygame.K_DOWN]:
        new_player_y += player_speed

    # Check collision with barriers and screen edges
    new_player_rect = pygame.Rect(new_player_x, new_player_y, player_size, player_size)
    if not (new_player_rect.colliderect(top_barrier) or 
            new_player_rect.colliderect(bottom_barrier) or
            new_player_rect.colliderect(spawn_barrier) or  # Check spawn barrier collision
            new_player_x < 0 or 
            new_player_x > WIDTH - player_size or
            new_player_y < 0 or 
            new_player_y > HEIGHT - player_size):
        player_x = new_player_x
        player_y = new_player_y

    # Update enemy positions and handle collisions
    left_group = [enemy for enemy in enemies if enemy["group"] == "left"]
    right_group = [enemy for enemy in enemies if enemy["group"] == "right"]

    # Move and bounce both groups
    for group in [left_group, right_group]:
        # Move the group
        for enemy in group:
            enemy["rect"].x += enemy["speed_x"]
        
        # Bounce the group off screen edges
        if group[0]["rect"].left <= 0 or group[-1]["rect"].right >= WIDTH:
            for enemy in group:
                enemy["speed_x"] = -enemy["speed_x"]

    # Ensure groups maintain 1-block distance
    maintain_group_distance(left_group)
    maintain_group_distance(right_group)

    # Keep all enemies within vertical bounds
    for enemy in enemies:
        if enemy["rect"].top < top_barrier.bottom:
            enemy["rect"].top = top_barrier.bottom
        elif enemy["rect"].bottom > bottom_barrier.top:
            enemy["rect"].bottom = bottom_barrier.top

    # Check for collisions with player
    player_rect = pygame.Rect(player_x, player_y, player_size, player_size)
    if player_rect.collidelist([e["rect"] for e in enemies]) != -1:
        player_x, player_y = 50, HEIGHT // 2  # Reset player position

    # Check for goal
    if player_rect.colliderect(goal):
        if not message_displayed:
            screen.fill(WHITE)
            display_message(f"Congratulations! You completed level {current_level}!")
            pygame.display.flip()
            pygame.time.wait(2000)
            message_displayed = True
            confetti.generate(WIDTH // 2, HEIGHT // 2)
            confetti_active = True

    # Draw everything
    if not confetti_active:
        screen.fill(WHITE)
        pygame.draw.rect(screen, BLUE, (player_x, player_y, player_size, player_size))
        for enemy in enemies:
            screen.blit(enemy_sprite, enemy["rect"])
        pygame.draw.rect(screen, GREEN, goal)
        pygame.draw.rect(screen, GRAY, top_barrier)
        pygame.draw.rect(screen, GRAY, bottom_barrier)
        pygame.draw.rect(screen, GRAY, spawn_barrier)  # Draw the spawn barrier
    else:
        # Update and draw confetti
        confetti.update()
        confetti.draw(screen)
        
        # Draw the Next Level button
        next_level_button.draw(screen)

    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(60)