import pygame
from utils import init_db, load_high_score, save_high_score, load_unlocked_level, save_unlocked_level
import sys
import sqlite3
from button import Button
import adventure
import swift_mode
import classic
import random
import math
from level_systems import adventure_levels, level_selection_loop, unlock_next_level

SCREEN_SIZE = (700, 700)
BG_COLOR = (245, 240, 230)  # Light beige background

pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption("2048")
clock = pygame.time.Clock()

# Initialize database
init_db()

# Load and play background music
try:
    pygame.mixer.music.load("bg_music.mp3")
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)
except:
    pass  # Continue without music if file not found

music_on = True
sound_on = True

# Fonts
title_font = pygame.font.Font(None, 120)
button_font = pygame.font.Font(None, 40)
icon_font = pygame.font.Font(None, 30)

# Colors
ORANGE = (255, 165, 0)
DARK_ORANGE = (255, 140, 0)
HEADER_ORANGE = (255, 140, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_GRAY = (200, 200, 200)

# Create modern rounded buttons with custom styling
class ModernButton(Button):
    def __init__(self, pos, text, font, text_color, rect_color, width=300, height=50):
        super().__init__(None, pos, text, font, text_color, rect_color)
        # Override the button rect to have custom width and height
        self.button_rect = pygame.Rect(
            self.x_pos - width // 2,
            self.y_pos - height // 2,
            width,
            height
        )
        self.text_rect = self.text_surface.get_rect(center=(self.x_pos, self.y_pos))

classic_btn = ModernButton((350, 450), "CLASSIC", button_font, WHITE, ORANGE)
adventure_btn = ModernButton((350, 520), "ADVENTURE", button_font, WHITE, ORANGE)
swift_btn = ModernButton((350, 590), "SWIFT", button_font, WHITE, ORANGE)

# Background numbers for decoration
background_numbers = []
for _ in range(50):
    x = random.randint(0, SCREEN_SIZE[0])
    y = random.randint(100, SCREEN_SIZE[1])
    number = random.choice([2, 4, 8, 16, 32, 64, 128, 256, 512, 1024])
    size = random.randint(20, 40)
    alpha = random.randint(30, 80)
    background_numbers.append({'x': x, 'y': y, 'number': number, 'size': size, 'alpha': alpha})

def draw_header():
    """Draw the orange header bar with window controls"""
    header_rect = pygame.Rect(0, 0, SCREEN_SIZE[0], 40)
    pygame.draw.rect(screen, HEADER_ORANGE, header_rect)

    # Window controls (minimize and close)
    # Minimize button
    minimize_rect = pygame.Rect(SCREEN_SIZE[0] - 80, 10, 20, 20)
    pygame.draw.rect(screen, WHITE, minimize_rect, border_radius=3)
    pygame.draw.line(screen, BLACK, (minimize_rect.x + 5, minimize_rect.centery),
                     (minimize_rect.x + 15, minimize_rect.centery), 2)

    # Close button
    close_rect = pygame.Rect(SCREEN_SIZE[0] - 50, 10, 20, 20)
    pygame.draw.rect(screen, WHITE, close_rect, border_radius=3)
    pygame.draw.line(screen, BLACK, (close_rect.x + 5, close_rect.y + 5),
                     (close_rect.x + 15, close_rect.y + 15), 2)
    pygame.draw.line(screen, BLACK, (close_rect.x + 15, close_rect.y + 5),
                     (close_rect.x + 5, close_rect.y + 15), 2)

    return close_rect

def draw_control_icons():
    """Draw music and sound control icons in top right"""
    global music_on, sound_on
    
    # Music note icon
    music_rect = pygame.Rect(SCREEN_SIZE[0] - 150, 60, 30, 30)
    music_color = ORANGE if music_on else LIGHT_GRAY
    pygame.draw.circle(screen, music_color, (music_rect.x + 10, music_rect.y + 20), 8, 2)
    pygame.draw.line(screen, music_color, (music_rect.x + 18, music_rect.y + 12),
                     (music_rect.x + 18, music_rect.y + 5), 2)

    # Sound icon
    sound_rect = pygame.Rect(SCREEN_SIZE[0] - 110, 60, 30, 30)
    sound_color = ORANGE if sound_on else LIGHT_GRAY
    pygame.draw.polygon(screen, sound_color, [
        (sound_rect.x + 5, sound_rect.y + 10),
        (sound_rect.x + 10, sound_rect.y + 10),
        (sound_rect.x + 15, sound_rect.y + 5),
        (sound_rect.x + 15, sound_rect.y + 25),
        (sound_rect.x + 10, sound_rect.y + 20),
        (sound_rect.x + 5, sound_rect.y + 20)
    ])
    if sound_on:
        pygame.draw.arc(screen, sound_color, (sound_rect.x + 16, sound_rect.y + 8, 10, 14),
                        -0.5, 0.5, 2)

    # Settings icon
    settings_rect = pygame.Rect(SCREEN_SIZE[0] - 70, 60, 30, 30)
    pygame.draw.circle(screen, ORANGE, settings_rect.center, 10, 2)
    for i in range(8):
        angle = i * math.pi / 4
        x1 = settings_rect.centerx + 6 * math.cos(angle)
        y1 = settings_rect.centery + 6 * math.sin(angle)
        x2 = settings_rect.centerx + 12 * math.cos(angle)
        y2 = settings_rect.centery + 12 * math.sin(angle)
        pygame.draw.line(screen, ORANGE, (x1, y1), (x2, y2), 2)

    return music_rect, sound_rect, settings_rect

def draw_background_numbers():
    """Draw decorative background numbers"""
    for num_data in background_numbers:
        font = pygame.font.Font(None, num_data['size'])
        text = font.render(str(num_data['number']), True, (*LIGHT_GRAY, num_data['alpha']))
        screen.blit(text, (num_data['x'], num_data['y']))

def draw_title():
    """Draw the large 2048 title with gradient effect"""
    title_text = title_font.render("2048", True, ORANGE)
    title_rect = title_text.get_rect(center=(SCREEN_SIZE[0] // 2, 200))

    # Create shadow effect
    shadow_text = title_font.render("2048", True, DARK_ORANGE)
    shadow_rect = shadow_text.get_rect(center=(SCREEN_SIZE[0] // 2 + 3, 203))
    screen.blit(shadow_text, shadow_rect)
    screen.blit(title_text, title_rect)

# Main game loop
running = True
while running:
    screen.fill(BG_COLOR)

    # Draw background elements
    draw_background_numbers()

    # Draw header and get close button rect
    close_rect = draw_header()

    # Draw control icons and get their rects
    music_rect, sound_rect, settings_rect = draw_control_icons()

    # Draw main title
    draw_title()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()

            # Check header controls
            if close_rect.collidepoint(mouse_pos):
                running = False
            elif music_rect.collidepoint(mouse_pos):
                music_on = not music_on
                if music_on:
                    try:
                        pygame.mixer.music.unpause()
                    except:
                        pass
                else:
                    try:
                        pygame.mixer.music.pause()
                    except:
                        pass
            elif sound_rect.collidepoint(mouse_pos):
                sound_on = not sound_on

            # Check game mode buttons
            elif classic_btn.checkforinput(mouse_pos):
                classic.run_classic_mode(screen, button_font)
                if not pygame.display.get_init():
                    running = False
                    break
            elif adventure_btn.checkforinput(mouse_pos):
                adventure.run_adventure_mode(screen, button_font)
                if not pygame.display.get_init():
                    running = False
                    break
            elif swift_btn.checkforinput(mouse_pos):
                swift_mode.run_swift_mode(screen, button_font)
                if not pygame.display.get_init():
                    running = False
                    break

    # Update and draw buttons
    classic_btn.update(screen)
    adventure_btn.update(screen)
    swift_btn.update(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
