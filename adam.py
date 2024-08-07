import pygame
import sys
import math
import random
import time

# Initialize Pygame
pygame.init()

# Set up the display
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Wizard's Hat vs Barbarians")

# Wizard hat properties
wizard_x = width // 2
wizard_y = height // 2
wizard_speed = 5
wizard_size = 80  # Increased size for better visibility
wand_angle = 0

# Wand properties
wand_length = 70
wand_thickness = 8

# Slash wave properties
slash_waves = []
wave_speed = 15
wave_lifetime = 30
wave_width = 60
wave_length = 30

# Enemy properties
enemies = []
enemy_size = 50
enemy_speed = 2
max_enemies = 10
spawn_interval = 10  # seconds
last_spawn_time = time.time()
enemies_to_spawn = 1

# Kill counter
kill_count = 0

# Game state
game_over = False
invincible = False

# Arrow key press counters
up_arrow_press_count = 0
down_arrow_press_count = 0
arrow_press_time = 2  # seconds to press 10 times
last_arrow_press_time = 0

# Slash animation properties
current_slash = 0
slash_duration = 20  # Duration of the slash effect
slash_angle = 90     # Angle range of the slash

# Colors
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
SILVER = (192, 192, 192)
GOLD = (255, 215, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
BROWN = (139, 69, 19)
SKIN = (255, 224, 189)
GREEN = (0, 255, 0)

# Game loop
running = True
clock = pygame.time.Clock()

def draw_wizards_hat(surface, x, y, size):
    # Hat cone
    pygame.draw.polygon(surface, BLUE, [
        (int(x - size/2), int(y + size/2)),
        (int(x), int(y - size/2)),
        (int(x + size/2), int(y + size/2))
    ])
    
    # Hat brim
    pygame.draw.ellipse(surface, BLUE, (int(x - size/1.5), int(y + size/2), int(size*1.33), int(size/4)))
    
    # Hat band
    pygame.draw.rect(surface, GOLD, (int(x - size/2), int(y + size/3), int(size), int(size/10)))
    
    # Stars on the hat
    star_color = GOLD
    star_size = size // 10
    for i in range(3):
        star_x = x - size/3 + (i * size/3)
        star_y = y
        pygame.draw.polygon(surface, star_color, [
            (int(star_x), int(star_y - star_size)),
            (int(star_x + star_size/4), int(star_y - star_size/4)),
            (int(star_x + star_size), int(star_y)),
            (int(star_x + star_size/4), int(star_y + star_size/4)),
            (int(star_x), int(star_y + star_size)),
            (int(star_x - star_size/4), int(star_y + star_size/4)),
            (int(star_x - star_size), int(star_y)),
            (int(star_x - star_size/4), int(star_y - star_size/4))
        ])

def draw_wand(surface, x, y, angle):
    wand_start_x = x
    wand_start_y = y + wizard_size // 2  # Start from the bottom of the hat
    wand_end_x = wand_start_x + math.cos(math.radians(angle)) * wand_length
    wand_end_y = wand_start_y - math.sin(math.radians(angle)) * wand_length
    
    # Draw wand
    pygame.draw.line(surface, GOLD, (int(wand_start_x), int(wand_start_y)), (int(wand_end_x), int(wand_end_y)), wand_thickness)
    
    # Draw wand tip
    wand_tip_radius = wand_thickness * 1.5
    pygame.draw.circle(surface, GREEN, (int(wand_end_x), int(wand_end_y)), wand_tip_radius)

def create_slash_wave(x, y, angle):
    dx = math.cos(math.radians(angle)) * wave_speed
    dy = -math.sin(math.radians(angle)) * wave_speed
    return [x, y, dx, dy, wave_lifetime]

def create_enemy():
    side = random.choice(['top', 'bottom', 'left', 'right'])
    if side == 'top':
        x = random.randint(0, width)
        y = -enemy_size
    elif side == 'bottom':
        x = random.randint(0, width)
        y = height + enemy_size
    elif side == 'left':
        x = -enemy_size
        y = random.randint(0, height)
    else:  # right
        x = width + enemy_size
        y = random.randint(0, height)
    return [x, y]

def draw_enemy(surface, x, y, size):
    # Body
    pygame.draw.rect(surface, BROWN, (int(x - size/3), int(y - size/2), int(size/1.5), int(size/1.2)))
    
    # Head
    pygame.draw.circle(surface, SKIN, (int(x), int(y - size/2)), int(size/4))
    
    # Eyes
    eye_size = size // 10
    pygame.draw.circle(surface, BLACK, (int(x - size/8), int(y - size/2)), eye_size)
    pygame.draw.circle(surface, BLACK, (int(x + size/8), int(y - size/2)), eye_size)
    
    # Mouth
    pygame.draw.arc(surface, BLACK, (int(x - size/6), int(y - size/2), int(size/3), int(size/4)), 3.14, 2*3.14, 2)
    
    # Arms
    arm_width = size // 8
    pygame.draw.line(surface, SKIN, (int(x - size/2), int(y - size/4)), (int(x - size), int(y + size/4)), arm_width)
    pygame.draw.line(surface, SKIN, (int(x + size/2), int(y - size/4)), (int(x + size), int(y + size/4)), arm_width)
    
    # Legs
    leg_width = size // 6
    pygame.draw.line(surface, BROWN, (int(x - size/4), int(y + size/3)), (int(x - size/3), int(y + size)), leg_width)
    pygame.draw.line(surface, BROWN, (int(x + size/4), int(y + size/3)), (int(x + size/3), int(y + size)), leg_width)
    
    # Weapon (staff)
    staff_handle = size // 2
    staff_head = size // 3
    pygame.draw.line(surface, DARK_GRAY, (int(x + size), int(y)), (int(x + size + staff_handle), int(y - staff_handle)), 4)
    pygame.draw.polygon(surface, SILVER, [
        (int(x + size + staff_handle), int(y - staff_handle)),
        (int(x + size + staff_handle + staff_head), int(y - staff_handle - staff_head/2)),
        (int(x + size + staff_handle + staff_head), int(y - staff_handle + staff_head/2))
    ])

def check_collision(rect1, rect2):
    return rect1.colliderect(rect2)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and current_slash == 0 and not game_over:
                current_slash = slash_duration
                slash_waves.append(create_slash_wave(wizard_x, wizard_y, wand_angle))
            elif event.key == pygame.K_r and game_over:
                # Reset the game
                wizard_x = width // 2
                wizard_y = height // 2
                enemies = []
                slash_waves = []
                kill_count = 0
                game_over = False
                last_spawn_time = time.time()
                enemies_to_spawn = 1
                invincible = False
                up_arrow_press_count = 0
                down_arrow_press_count = 0
                current_slash = 0  # Reset slash animation
            elif event.key == pygame.K_UP and not game_over:
                current_time = time.time()
                if current_time - last_arrow_press_time <= arrow_press_time:
                    up_arrow_press_count += 1
                else:
                    up_arrow_press_count = 1
                last_arrow_press_time = current_time
                if up_arrow_press_count >= 10:
                    invincible = True
                    up_arrow_press_count = 0
            elif event.key == pygame.K_DOWN and not game_over:
                current_time = time.time()
                if current_time - last_arrow_press_time <= arrow_press_time:
                    down_arrow_press_count += 1
                else:
                    down_arrow_press_count = 1
                last_arrow_press_time = current_time
                if down_arrow_press_count >= 10:
                    invincible = False
                    down_arrow_press_count = 0

    if not game_over:
        # Handle key presses for movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            wizard_x -= wizard_speed
        if keys[pygame.K_d]:
            wizard_x += wizard_speed
        if keys[pygame.K_w]:
            wizard_y -= wizard_speed
        if keys[pygame.K_s]:
            wizard_y += wizard_speed

        # Handle key presses for wand rotation
        if keys[pygame.K_LEFT]:
            wand_angle += 5
        if keys[pygame.K_RIGHT]:
            wand_angle -= 5

        # Keep the wizard within the screen boundaries
        wizard_x = max(wizard_size//2, min(width - wizard_size//2, wizard_x))
        wizard_y = max(wizard_size//2, min(height - wizard_size//2, wizard_y))

        # Update slash animation
        if current_slash > 0:
            current_slash -= 1

        # Update slash waves
        for wave in slash_waves:
            wave[0] += wave[2]
            wave[1] += wave[3]
            wave[4] -= 1
        slash_waves = [wave for wave in slash_waves if wave[4] > 0]

        # Spawn enemies
        current_time = time.time()
        if current_time - last_spawn_time >= spawn_interval and len(enemies) < max_enemies:
            for _ in range(enemies_to_spawn):
                enemies.append(create_enemy())
            last_spawn_time = current_time
            enemies_to_spawn = min(enemies_to_spawn + 1, max_enemies)

        # Update enemies
        for enemy in enemies:
            dx = wizard_x - enemy[0]
            dy = wizard_y - enemy[1]
            distance = math.hypot(dx, dy)
            if distance != 0:
                enemy[0] += (dx / distance) * enemy_speed
                enemy[1] += (dy / distance) * enemy_speed

            # Check for collision with wizard
            if not invincible:
                wizard_rect = pygame.Rect(wizard_x - wizard_size/2, wizard_y - wizard_size/2, wizard_size, wizard_size)
                enemy_rect = pygame.Rect(enemy[0] - enemy_size/2, enemy[1] - enemy_size/2, enemy_size, enemy_size)
                if check_collision(wizard_rect, enemy_rect):
                    game_over = True

        # Check for collisions between slash waves and enemies
        for wave in slash_waves:
            wave_rect = pygame.Rect(wave[0] - wave_length / 2, wave[1] - wave_width / 2, wave_length, wave_width)
            for enemy in enemies[:]:
                enemy_rect = pygame.Rect(enemy[0] - enemy_size / 2, enemy[1] - enemy_size / 2, enemy_size, enemy_size)
                if check_collision(wave_rect, enemy_rect):
                    enemies.remove(enemy)
                    kill_count += 1

    # Fill the screen with white
    screen.fill(WHITE)

    # Draw the wizard's hat
    draw_wizards_hat(screen, wizard_x, wizard_y, wizard_size)
    
    # Draw the wand
    if current_slash == 0:
        draw_wand(screen, wizard_x, wizard_y, wand_angle)
    else:
        # Animate the slash
        slash_progress = (slash_duration - current_slash) / slash_duration
        current_angle = wand_angle - (slash_angle / 2) + (slash_angle * slash_progress)
        draw_wand(screen, wizard_x, wizard_y, current_angle)

    # Draw slash waves
    for wave in slash_waves:
        wave_angle = math.atan2(-wave[3], wave[2])
        start_x = wave[0] - math.cos(wave_angle) * wave_length / 2
        start_y = wave[1] + math.sin(wave_angle) * wave_length / 2
        end_x = wave[0] + math.cos(wave_angle) * wave_length / 2
        end_y = wave[1] - math.sin(wave_angle) * wave_length / 2
        pygame.draw.line(screen, BLUE, (int(start_x), int(start_y)), (int(end_x), int(end_y)), int(wave_width * (wave[4] / wave_lifetime)))

    # Draw enemies
    for enemy in enemies:
        draw_enemy(screen, enemy[0], enemy[1], enemy_size)

    # Draw kill counter
    font = pygame.font.SysFont(None, 36)
    kill_text = font.render(f"Kills: {kill_count}", True, BLACK)
    screen.blit(kill_text, (10, 10))

    if game_over:
        game_over_font = pygame.font.SysFont(None, 72)
        game_over_text = game_over_font.render("Game Over", True, RED)
        retry_text = font.render("Press 'R' to try again", True, BLACK)
        screen.blit(game_over_text, (width//2 - game_over_text.get_width()//2, height//2 - game_over_text.get_height()//2))
        screen.blit(retry_text, (width//2 - retry_text.get_width()//2, height//2 + game_over_text.get_height()))

    if invincible:
        invincible_text = font.render("Invincible!"), True, GOLD