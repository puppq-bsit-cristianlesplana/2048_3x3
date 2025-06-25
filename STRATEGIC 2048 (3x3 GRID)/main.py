import pygame
from utils import init_db, load_high_score, save_high_score, load_unlocked_level, save_unlocked_level
import sys
import sqlite3
from button import Button  # Only import Button, not ModernButton
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

# Load move sound effect
move_sound = None
try:
    move_sound = pygame.mixer.Sound("move_sound.wav")
    move_sound.set_volume(0.3)
except:
    pass

# Load background image
background_image = None
try:
    background_image = pygame.image.load("C:/Users/cristian/Documents/STRATEGIC 2048 (3x3 GRID)/LOGO/background.png")
    background_image = pygame.transform.scale(background_image, SCREEN_SIZE)
    print("Background image loaded successfully!")
except Exception as e:
    print(f"Background image not found: {e}")
    pass

# Load logo image
logo_image = None
try:
    logo_image = pygame.image.load("C:/Users/cristian/Documents/STRATEGIC 2048 (3x3 GRID)/2048-logo.png")
    logo_image = pygame.transform.scale(logo_image, (1050, 650))
    print("Logo image loaded successfully!")
except Exception as e:
    print(f"Logo image not found: {e}")
    pass

music_on = True
sound_on = True

# Font size constants
FONT_SIZE_TITLE = 120
FONT_SIZE_BUTTON = 30
FONT_SIZE_ICON = 30

# Fonts
title_font = pygame.font.Font(None, FONT_SIZE_TITLE)
button_font = pygame.font.Font(None, FONT_SIZE_BUTTON)
icon_font = pygame.font.Font(None, FONT_SIZE_ICON)

# Colors
ORANGE = (255, 165, 0)
DARK_ORANGE = (255, 140, 0)
HEADER_ORANGE = (255, 140, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_GRAY = (200, 200, 200)

# Create rectangular buttons without rounded corners
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
        self.rect_color = rect_color
        self.text_color = text_color
    
    def update(self, screen):
        """Draw rectangular button without rounded corners and without border"""
        # Draw the rectangular button background
        pygame.draw.rect(screen, self.rect_color, self.button_rect)
        
        # Removed this line: pygame.draw.rect(screen, BLACK, self.button_rect, 2)  # No border
        
        # Draw the text
        screen.blit(self.text_surface, self.text_rect)
    
    def checkforinput(self, position):
        """Check if button is clicked"""
        if position[0] in range(self.button_rect.left, self.button_rect.right) and \
           position[1] in range(self.button_rect.top, self.button_rect.bottom):
            return True
        return False

# Button layout constants
BUTTON_WIDTH = 350
BUTTON_HEIGHT = 60
BUTTON_X = 350
BUTTON_SPACING = 90

# Y positions
CLASSIC_Y = 440
ADVENTURE_Y = CLASSIC_Y + BUTTON_SPACING
SWIFT_Y = ADVENTURE_Y + BUTTON_SPACING

# Create buttons
classic_btn = ModernButton((BUTTON_X, CLASSIC_Y), "CLASSIC", button_font, WHITE, ORANGE, 
                          width=BUTTON_WIDTH, height=BUTTON_HEIGHT)
adventure_btn = ModernButton((BUTTON_X, ADVENTURE_Y), "ADVENTURE", button_font, WHITE, ORANGE, 
                            width=BUTTON_WIDTH, height=BUTTON_HEIGHT)
swift_btn = ModernButton((BUTTON_X, SWIFT_Y), "SWIFT", button_font, WHITE, ORANGE, 
                        width=BUTTON_WIDTH, height=BUTTON_HEIGHT)

def draw_header():
    """Draw the orange header bar with window controls"""
    header_rect = pygame.Rect(0, 0, SCREEN_SIZE[0], 40)
    pygame.draw.rect(screen, HEADER_ORANGE, header_rect)

    # Window controls (minimize and close)
    # Minimize button - remove border_radius
    minimize_rect = pygame.Rect(SCREEN_SIZE[0] - 80, 10, 20, 20)
    pygame.draw.rect(screen, WHITE, minimize_rect)  # Removed border_radius=3
    pygame.draw.line(screen, BLACK, (minimize_rect.x + 5, minimize_rect.centery),
                     (minimize_rect.x + 15, minimize_rect.centery), 2)

    # Close button - remove border_radius
    close_rect = pygame.Rect(SCREEN_SIZE[0] - 50, 10, 20, 20)
    pygame.draw.rect(screen, WHITE, close_rect)  # Removed border_radius=3
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

def draw_background():
    """Draw the background image or solid color"""
    if background_image:
        screen.blit(background_image, (0, 0))
    else:
        screen.fill(BG_COLOR)

def draw_title():
    """Draw the logo image with optional shadow effect"""
    if logo_image:
        # Position for the logo
        logo_rect = logo_image.get_rect(center=(SCREEN_SIZE[0] // 2, 200))
        
        # Optional: Create a shadow effect for the logo
        shadow_offset = 3
        shadow_surface = logo_image.copy()
        shadow_surface.fill((0, 0, 0, 100), special_flags=pygame.BLEND_RGBA_MULT)
        shadow_rect = logo_rect.copy()
        shadow_rect.x += shadow_offset
        shadow_rect.y += shadow_offset
        
        # Draw shadow first, then logo
        screen.blit(shadow_surface, shadow_rect)
        screen.blit(logo_image, logo_rect)
    else:
        # Fallback text if no logo
        title_text = title_font.render("2048", True, ORANGE)
        title_rect = title_text.get_rect(center=(SCREEN_SIZE[0] // 2, 200))
        screen.blit(title_text, title_rect)

def play_move_sound():
    """Play move sound if sound is enabled"""
    if sound_on and move_sound:
        move_sound.play()

# Main game loop
running = True
while running:
    # Draw background (image or solid color)
    draw_background()

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
