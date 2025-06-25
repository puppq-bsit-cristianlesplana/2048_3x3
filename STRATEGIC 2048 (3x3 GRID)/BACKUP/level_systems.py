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

def check_adventure_lose(level, moves_used, grid):
    """
    Check if the adventure level is lost (max moves exceeded without completing targets).
    
    Args:
        level: The level definition
        moves_used: Number of moves used so far
        grid: The current game grid
    
    Returns:
        str or None: "lose" if the level is failed, None otherwise
    """
    if moves_used >= level["max_moves"]:
        # Check if targets are met
        if check_adventure_win(level, grid) != "win":
            return "lose"
    return None

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
    if score >= level["target_score"]:
        return "win"
    return None

def check_swift_lose(level, score, elapsed_time):
    """
    Check if the swift level is lost (time limit exceeded without reaching target score).
    
    Args:
        level: The level definition
        score: The current score
        elapsed_time: The elapsed time in seconds
    
    Returns:
        str or None: "lose" if the level is failed, None otherwise
    """
    if elapsed_time >= level["time_limit"]:
        if score < level["target_score"]:
            return "lose"
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

def draw_adventure_info_boards(screen, level_number, score, moves_used, max_moves, targets, grid):
    """
    Draw separate information boards for adventure mode
    
    Args:
        screen: The pygame screen surface
        level_number: Current level number
        score: Current score
        moves_used: Number of moves used
        max_moves: Maximum moves allowed
        targets: List of target tiles and counts
        grid: Current game grid
    """
    # Level and Score Board
    level_score_x = 20
    level_score_y = 60
    board_width = 150
    board_height = 100
    
    # Draw level and score board
    pygame.draw.rect(screen, (100, 100, 100), 
                    (level_score_x, level_score_y, board_width, board_height), 
                    width=3, border_radius=10)
    pygame.draw.rect(screen, (240, 230, 210), 
                    (level_score_x, level_score_y, board_width, board_height), 
                    border_radius=10)
    
    # Level and score text
    font_label = pygame.font.Font(None, 28)
    font_value = pygame.font.Font(None, 24)
    
    level_label = font_label.render("LEVEL", True, (119, 110, 101))
    level_value = font_value.render(str(level_number), True, (0, 0, 0))
    score_label = font_label.render("SCORE", True, (119, 110, 101))
    score_value = font_value.render(str(score), True, (0, 0, 0))
    
    # Position text in level/score board
    screen.blit(level_label, (level_score_x + 10, level_score_y + 10))
    screen.blit(level_value, (level_score_x + 10, level_score_y + 30))
    screen.blit(score_label, (level_score_x + 10, level_score_y + 55))
    screen.blit(score_value, (level_score_x + 10, level_score_y + 75))
    
    # Moves Board
    moves_x = 190
    moves_y = 60
    
    # Draw moves board
    pygame.draw.rect(screen, (100, 100, 100), 
                    (moves_x, moves_y, board_width, board_height), 
                    width=3, border_radius=10)
    
    # Color code the moves board based on remaining moves
    remaining_moves = max_moves - moves_used
    if remaining_moves <= 5:
        board_color = (255, 200, 200)  # Light red for low moves
    elif remaining_moves <= 10:
        board_color = (255, 255, 200)  # Light yellow for medium moves
    else:
        board_color = (240, 230, 210)  # Normal color
    
    pygame.draw.rect(screen, board_color, 
                    (moves_x, moves_y, board_width, board_height), 
                    border_radius=10)
    
    # Moves text
    moves_label = font_label.render("MOVES", True, (119, 110, 101))
    moves_used_text = font_value.render(f"Used: {moves_used}", True, (0, 0, 0))
    moves_left_text = font_value.render(f"Left: {remaining_moves}", True, (0, 0, 0))
    
    # Position text in moves board
    screen.blit(moves_label, (moves_x + 10, moves_y + 10))
    screen.blit(moves_used_text, (moves_x + 10, moves_y + 35))
    screen.blit(moves_left_text, (moves_x + 10, moves_y + 60))
    
    # Targets Board
    targets_x = 360
    targets_y = 60
    targets_width = 200
    targets_height = 120
    
    # Draw targets board
    pygame.draw.rect(screen, (100, 100, 100), 
                    (targets_x, targets_y, targets_width, targets_height), 
                    width=3, border_radius=10)
    pygame.draw.rect(screen, (240, 230, 210), 
                    (targets_x, targets_y, targets_width, targets_height), 
                    border_radius=10)
    
    # Targets text
    targets_label = font_label.render("TARGETS", True, (119, 110, 101))
    screen.blit(targets_label, (targets_x + 10, targets_y + 10))
    
    # Display each target
    y_offset = 35
    all_targets_met = True
    
    for target in targets:
        target_tile = target["tile"]
        target_count = target["count"]
        current_count = sum(row.count(target_tile) for row in grid)
        
        # Color code based on completion
        if current_count >= target_count:
            text_color = (0, 150, 0)  # Green for completed
        else:
            text_color = (0, 0, 0)    # Black for incomplete
            all_targets_met = False
        
        target_text = font_value.render(f"{target_tile}: {current_count}/{target_count}", True, text_color)
        screen.blit(target_text, (targets_x + 10, targets_y + y_offset))
        y_offset += 25
    
    # Add completion indicator (green border when all targets met)
    if all_targets_met:
        pygame.draw.rect(screen, (0, 255, 0), 
                        (targets_x - 2, targets_y - 2, targets_width + 4, targets_height + 4), 
                        width=3, border_radius=12)

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

def show_level_complete_message(screen, font, mode, current_level):
    """
    Shows a level completion message and handles progression to next level.
    
    Args:
        screen: The pygame screen surface
        font: The font to use for the message
        mode: The game mode
        current_level: The current level number
    
    Returns:
        str: 'next_level' to proceed to next level, 'home' to return home
    """
    # Create a semi-transparent overlay
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))  # Semi-transparent black
    
    # Create the completion text
    font_big = pygame.font.Font(None, 60)
    font_small = pygame.font.Font(None, 40)
    
    text1 = font_big.render("Level Complete!", True, (0, 255, 0))  # Green color
    text2 = font_small.render(f"Level {current_level} completed successfully!", True, (255, 255, 255))
    
    # Check if there's a next level
    if is_final_level(mode, current_level):
        text3 = font_small.render("All levels completed! Press any key to return home.", True, (255, 255, 255))
        next_action = "home"
    else:
        text3 = font_small.render("Press SPACE for next level or ESC for home", True, (255, 255, 255))
        next_action = "next_level"
    
    # Position the text in the center of the screen
    text1_rect = text1.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 60))
    text2_rect = text2.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 20))
    text3_rect = text3.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + 20))
    
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
            elif event.type == pygame.KEYDOWN:
                if is_final_level(mode, current_level):
                    return "home"
                elif event.key == pygame.K_SPACE:
                    return "next_level"
                elif event.key == pygame.K_ESCAPE:
                    return "home"
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if is_final_level(mode, current_level):
                    return "home"
                else:
                    return "next_level"
    
    return next_action

def show_game_over_message(screen, font, mode, current_level, reason=""):
    """
    Shows a game over message when a level is failed.
    
    Args:
        screen: The pygame screen surface
        font: The font to use for the message
        mode: The game mode
        current_level: The current level number
        reason: The reason for game over (optional)
    
    Returns:
        str: 'retry' to retry the level, 'home' to return home, or 'level_select' for level selection
    """
    # Create a semi-transparent overlay
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))  # Semi-transparent black
    
    # Create the game over text
    font_big = pygame.font.Font(None, 80)
    font_medium = pygame.font.Font(None, 50)
    font_small = pygame.font.Font(None, 40)
    
    text1 = font_big.render("GAME OVER", True, (255, 0, 0))  # Red color
    text2 = font_medium.render(f"Level {current_level} Failed", True, (255, 255, 255))
    
    # Add specific reason for failure
    if mode == "adventure":
        if reason:
            text3 = font_small.render(reason, True, (255, 255, 255))
        else:
            text3 = font_small.render("Max moves exceeded without completing targets!", True, (255, 255, 255))
    elif mode == "swift":
        if reason:
            text3 = font_small.render(reason, True, (255, 255, 255))
        else:
            text3 = font_small.render("Time limit exceeded without reaching target score!", True, (255, 255, 255))
    else:
        text3 = font_small.render(reason if reason else "Level failed!", True, (255, 255, 255))
    
    text4 = font_small.render("Press R to retry, H for home, or L for level select", True, (255, 255, 255))
    
    # Position the text in the center of the screen
    text1_rect = text1.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 80))
    text2_rect = text2.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 40))
    text3_rect = text3.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
    text4_rect = text4.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + 40))
    
    # Display the message
    screen.blit(overlay, (0, 0))
    screen.blit(text1, text1_rect)
    screen.blit(text2, text2_rect)
    screen.blit(text3, text3_rect)
    screen.blit(text4, text4_rect)
    pygame.display.flip()
    
    # Wait for user input
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return "home"
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return "retry"
                elif event.key == pygame.K_h:
                    return "home"
                elif event.key == pygame.K_l:
                    return "level_select"
            elif event.type == pygame.MOUSEBUTTONDOWN:
                return "retry"  # Default action on mouse click
    
    return "retry"

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
    cols = 4
    rows = (len(levels) + cols - 1) // cols
    box_size = 100
    gap = 10
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
            btn = Button(None, (x, y), "X", font, "Gray", "DarkGray")  # Locked
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

def draw_swift_info_boards(screen, level_number, score, target_score, time_left, total_time):
    """
    Draw separate information boards for swift mode
    
    Args:
        screen: The pygame screen surface
        level_number: Current level number
        score: Current score
        target_score: Target score to reach
        time_left: Time remaining in seconds
        total_time: Total time allowed for the level
    """
    # Level and Score Board
    level_score_x = 20
    level_score_y = 60
    board_width = 150
    board_height = 100
    
    # Draw level and score board
    pygame.draw.rect(screen, (100, 100, 100), 
                    (level_score_x, level_score_y, board_width, board_height), 
                    width=3, border_radius=10)
    pygame.draw.rect(screen, (240, 230, 210), 
                    (level_score_x, level_score_y, board_width, board_height), 
                    border_radius=10)
    
    # Level and score text
    font_label = pygame.font.Font(None, 28)
    font_value = pygame.font.Font(None, 24)
    
    level_label = font_label.render("LEVEL", True, (119, 110, 101))
    level_value = font_value.render(str(level_number), True, (0, 0, 0))
    score_label = font_label.render("SCORE", True, (119, 110, 101))
    score_value = font_value.render(str(score), True, (0, 0, 0))
    
    # Position text in level/score board
    screen.blit(level_label, (level_score_x + 10, level_score_y + 10))
    screen.blit(level_value, (level_score_x + 10, level_score_y + 30))
    screen.blit(score_label, (level_score_x + 10, level_score_y + 55))
    screen.blit(score_value, (level_score_x + 10, level_score_y + 75))
    
    # Target and Time Board
    target_time_x = 190
    target_time_y = 60
    target_time_width = 180
    target_time_height = 100  # Reduced height since no progress
    
    # Color code the board based on time remaining and target progress
    score_ratio = min(score / target_score, 1.0) if target_score > 0 else 0
    
    if time_left <= 10:
        board_color = (255, 200, 200)  # Light red for very low time
    elif time_left <= 30:
        board_color = (255, 255, 200)  # Light yellow for low time
    elif score >= target_score:
        board_color = (200, 255, 200)  # Light green for target reached
    else:
        board_color = (240, 230, 210)  # Normal color
    
    # Draw target and time board
    pygame.draw.rect(screen, (100, 100, 100), 
                    (target_time_x, target_time_y, target_time_width, target_time_height), 
                    width=3, border_radius=10)
    pygame.draw.rect(screen, board_color, 
                    (target_time_x, target_time_y, target_time_width, target_time_height), 
                    border_radius=10)
    
    # Target and time text
    target_label = font_label.render("TARGET", True, (119, 110, 101))
    target_value = font_value.render(str(target_score), True, (0, 0, 0))
    
    # Format time display (minutes:seconds)
    minutes = time_left // 60
    seconds = time_left % 60
    time_label = font_label.render("TIME LEFT", True, (119, 110, 101))
    time_value = font_value.render(f"{minutes:02d}:{seconds:02d}", True, (0, 0, 0))
    
    # Position text in target/time board (removed progress section)
    screen.blit(target_label, (target_time_x + 10, target_time_y + 10))
    screen.blit(target_value, (target_time_x + 10, target_time_y + 30))
    screen.blit(time_label, (target_time_x + 10, target_time_y + 55))
    screen.blit(time_value, (target_time_x + 10, target_time_y + 75))
    
    # Add completion indicator (green border when target is reached)
    if score >= target_score:
        pygame.draw.rect(screen, (0, 255, 0), 
                        (target_time_x - 2, target_time_y - 2, target_time_width + 4, target_time_height + 4), 
                        width=3, border_radius=12)
    
    # Add urgency indicator (red border when time is very low)
    elif time_left <= 10 and time_left > 0:
        pygame.draw.rect(screen, (255, 0, 0), 
                        (target_time_x - 2, target_time_y - 2, target_time_width + 4, target_time_height + 4), 
                        width=3, border_radius=12)