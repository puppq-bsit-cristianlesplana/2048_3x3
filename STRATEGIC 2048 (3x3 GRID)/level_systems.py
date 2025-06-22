import pygame
import time
import sqlite3
from utils import DB_FILE

# Adventure level definitions
adventure_levels = [
    {
        "targets": [
            {"tile": 16, "count": 4},
            {"tile": 32, "count": 1}
        ],
        "max_moves": 40
    },
    {
        "targets": [
            {"tile": 64, "count": 3},
            {"tile": 128, "count": 1}
        ],
        "max_moves": 50
    },
    {
        "targets": [
            {"tile": 128, "count": 1}
        ],
        "max_moves": 40
    },
    {
        "targets": [
            {"tile": 256, "count": 1}
        ],
        "max_moves": 50
    },
    {
        "targets": [
            {"tile": 512, "count": 1}
        ],
        "max_moves": 60
    },
    {
        "targets": [
            {"tile": 1024, "count": 1}
        ],
        "max_moves": 70
    },
    {
        "targets": [
            {"tile": 2048, "count": 1}
        ],
        "max_moves": 80
    },
    {
        "targets": [
            {"tile": 4096, "count": 1}
        ],
        "max_moves": 90
    },
    {
        "targets": [
            {"tile": 8192, "count": 1}
        ],
        "max_moves": 100
    },
    {
        "targets": [
            {"tile": 16384, "count": 1}
        ],
        "max_moves": 110
    },
    {
        "targets": [
            {"tile": 32768, "count": 1}
        ],
        "max_moves": 120
    },
    {
        "targets": [
            {"tile": 65536, "count": 1}
        ],
        "max_moves": 130
    },
    {
        "targets": [
            {"tile": 131072, "count": 1}
        ],
        "max_moves": 140
    },
    {
        "targets": [
            {"tile": 262144, "count": 1}
        ],
        "max_moves": 150
    },
    {
        "targets": [
            {"tile": 524288, "count": 1}
        ],
        "max_moves": 160
    },
]

# Swift level definitions
swift_levels = [
    {"target_score": 64, "time_limit": 120},
    {"target_score": 128, "time_limit": 150},
    {"target_score": 512, "time_limit": 180},
    {"target_score": 1024, "time_limit": 210},
    {"target_score": 2048, "time_limit": 240},
    {"target_score": 4096, "time_limit": 270},
    {"target_score": 8192, "time_limit": 300}
]

def get_unlocked_level(mode):
    """
    Gets the highest unlocked level for a specific game mode.
    
    Args:
        mode: The game mode (e.g., 'adventure', 'swift')
    
    Returns:
        int: The highest unlocked level
    """
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT level FROM unlocked_levels WHERE mode = ?", (mode,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else 1  # Default to level 1 if no record exists

def save_unlocked_level(mode, level):
    """
    Saves the highest unlocked level for a specific game mode.
    
    Args:
        mode: The game mode (e.g., 'adventure', 'swift')
        level: The level to save
    """
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO unlocked_levels (mode, level) VALUES (?, ?)", (mode, level))
    conn.commit()
    conn.close()

def unlock_next_level(mode, current_level):
    """Unlock the next level for the given mode"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO unlocked_levels (mode, level) VALUES (?, ?)", 
              (mode, current_level + 1))
    conn.commit()
    conn.close()

def check_adventure_win(level, grid):
    """
    Check if all target tiles exist in the grid with required counts.
    
    Args:
        level: The level definition
        grid: The current game grid
    
    Returns:
        str or None: "win" if the level is completed, None otherwise
    """
    for target in level["targets"]:
        tile = target["tile"]
        count = target["count"]
        found = sum(row.count(tile) for row in grid)
        if found < count:
            return None
    return "win"

def check_swift_win(level, score, elapsed_time):
    """
    Check if the target score is reached within the time limit for swift mode.
    
    Args:
        level: The level definition
        score: The current score
        elapsed_time: The elapsed time in seconds
    
    Returns:
        str or None: "win" if the level is completed, None otherwise
    """
    if score >= level["target_score"] and elapsed_time <= level["time_limit"]:
        return "win"
    return None

def get_adventure_level(level_number):
    """
    Get the adventure level definition for a specific level number.
    
    Args:
        level_number: The level number (1-based)
    
    Returns:
        dict or None: The level definition or None if the level doesn't exist
    """
    if 1 <= level_number <= len(adventure_levels):
        return adventure_levels[level_number - 1]
    return None

def get_swift_level(level_number):
    """
    Get the swift level definition for a specific level number.
    
    Args:
        level_number: The level number (1-based)
    
    Returns:
        dict or None: The level definition or None if the level doesn't exist
    """
    if 1 <= level_number <= len(swift_levels):
        return swift_levels[level_number - 1]
    return None

def is_final_level(mode, level):
    """
    Checks if the given level is the final level for the mode.
    
    Args:
        mode: The game mode (e.g., 'adventure', 'swift')
        level: The current level
    
    Returns:
        bool: True if it's the final level, False otherwise
    """
    if mode == "adventure":
        return level >= len(adventure_levels)
    elif mode == "swift":
        return level >= len(swift_levels)
    return True  # Default to true for unknown modes
def show_game_completed_message(screen, font, mode):
    """
    Shows a message when all levels in a mode are completed.
    
    Args:
        screen: The pygame screen surface
        font: The font to use for the message
        mode: The game mode that was completed
    
    Returns:
        str: 'home' to return to the home screen
    """
    # Create a semi-transparent overlay
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))  # Semi-transparent black
    
    # Create the completion text
    font_big = pygame.font.Font(None, 80)
    font_small = pygame.font.Font(None, 40)
    
    text1 = font_big.render(f"{mode.title()} Mode Completed!", True, (255, 215, 0))  # Gold color
    text2 = font_small.render("Congratulations! You've completed all levels!", True, (255, 255, 255))
    text3 = font_small.render("Press any key to return to the home screen", True, (255, 255, 255))
    
    # Position the text in the center of the screen
    text1_rect = text1.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 80))
    text2_rect = text2.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
    text3_rect = text3.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + 80))
    
    # Display the message
    screen.blit(overlay, (0, 0))
    screen.blit(text1, text1_rect)
    screen.blit(text2, text2_rect)
    screen.blit(text3, text3_rect)
    pygame.display.flip()
    
    # Wait for user input
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return "home"
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                waiting = False
    
    return "home"

def level_selection_loop(screen, mode):
    """
    Display a level selection screen for the given mode.
    
    Args:
        screen: The pygame screen surface
        mode: The game mode (e.g., 'adventure', 'swift')
    
    Returns:
        int or None: The selected level number or None if the user quit
    """
    from button import Button
    
    background_image = pygame.image.load(r"C:/Users/cristian/Documents/STRATEGIC 2048 (3x3 GRID)/LOGO/background.png")
    background_image = pygame.transform.scale(background_image, (700, 700))
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 50)
    
    levels = adventure_levels if mode == "adventure" else swift_levels
    unlocked_levels = get_unlocked_level(mode)
    
    buttons = []
    cols = 3
    rows = (len(levels) + cols - 1) // cols
    box_size = 100
    gap = 15
    start_x = screen.get_width() // 2 - (cols * box_size + (cols - 1) * gap) // 2
    start_y = 200
    
    for i, level in enumerate(levels):
        row = i // cols
        col = i % cols
        x = start_x + col * (box_size + gap)
        y = start_y + row * (box_size + gap)
        if i < unlocked_levels:
            btn = Button(None, (x, y), str(i + 1), font, "Black", "LightGray")
        else:
            btn = Button(None, (x, y), "🔒", font, "Gray", "DarkGray")  # Locked
        buttons.append(btn)
    
    # Add back button
    back_btn = Button(None, (100, 650), "Back", font, "Black", "LightGray")
    
    while True:
        screen.fill((230, 230, 230))
        screen.blit(background_image, (0, 0))  # Draw background
        
        title = font.render(f"Select {mode.title()} Level", True, (0, 0, 0))
        screen.blit(title, (screen.get_width() // 2 - title.get_width() // 2, 100))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                for idx, btn in enumerate(buttons):
                    if btn.checkforinput(pos) and idx < unlocked_levels:
                        return idx + 1  # Return as integer
                if back_btn.checkforinput(pos):
                    return None  # user pressed back
        
        for btn in buttons:
            btn.update(screen)
        
        back_btn.update(screen)
        
        pygame.display.flip()
        clock.tick(60)

def display_level_info(screen, level, font, grid, mode):
    """
    Display the current level's target information and progress.
    
    Args:
        screen: The pygame screen surface
        level: The level definition
        font: The font to use
        grid: The current game grid
        mode: The game mode (e.g., 'adventure', 'swift')
    """
    # Display current level number
    level_number = level.get("level_number", 1)  # Get level number with default 1
    level_text = font.render(f"Level {level_number}", True, (0, 0, 0))
    screen.blit(level_text, (300, 20))

    if mode == "adventure":
        targets = level["targets"]
        y_offset = 60
        all_targets_met = True
        
        for target in targets:
            target_tile = target["tile"]
            target_count = target["count"]
            target_text = font.render(f"Target: {target_tile} x{target_count}", True, (0, 0, 0))
            screen.blit(target_text, (300, y_offset))
            tile_count = sum(row.count(target_tile) for row in grid)
            progress_text = font.render(f"Current: {tile_count}/{target_count}", True, (0, 0, 0))
            screen.blit(progress_text, (300, y_offset + 30))
            y_offset += 60
            
            if tile_count < target_count:
                all_targets_met = False

        if all_targets_met:
            congrats_text = font.render("Congratulations! Level Complete!", True, (0, 255, 0))
            screen.blit(congrats_text, (screen.get_width()//2 - congrats_text.get_width()//2, screen.get_height()//2))
            pygame.display.flip()
            pygame.time.wait(2000)  # Wait for 2 seconds
            return True  # Signal level completion

    elif mode == "swift":
        target_score = level["target_score"]
        target_text = font.render(f"Target Score: {target_score}", True, (0, 0, 0))
        screen.blit(target_text, (300, 60))

        current_score = level.get("current_score", 0)
        score_text = font.render(f"Current Score: {current_score}", True, (0, 0, 0))
        screen.blit(score_text, (300, 90))

        if current_score >= target_score:
            congrats_text = font.render("Congratulations! Level Complete!", True, (0, 255, 0))
            screen.blit(congrats_text, (screen.get_width()//2 - congrats_text.get_width()//2, screen.get_height()//2))
            pygame.display.flip()
            pygame.time.wait(2000)  # Wait for 2 seconds
            return True  # Signal level completion
    
    return False  # Level not completed yet