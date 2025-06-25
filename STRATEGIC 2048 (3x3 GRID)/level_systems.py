import pygame
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
    # Add more levels as needed
]

# Swift level definitions
swift_levels = [
    {"target_score": 64, "time_limit": 120},
    {"target_score": 128, "time_limit": 150},
    {"target_score": 512, "time_limit": 180},
    # Add more levels as needed
]

# Global dictionary to track target achievements
current_session_targets = {}
current_level_number = None

def set_current_level(level_number):
    """Set the current level for merge tracking"""
    global current_level_number
    current_level_number = level_number

def on_tile_merged(tile_value):
    """Called whenever tiles are merged - tracks tile creation"""
    global current_session_targets, current_level_number
    
    if current_level_number is None or current_level_number not in current_session_targets:
        return
    
    # Track this tile creation
    if tile_value in current_session_targets[current_level_number]:
        target_info = current_session_targets[current_level_number][tile_value]
        target_info["created_count"] += 1
        
        # Update achieved count
        target_info["achieved"] = target_info["created_count"]
        
        # Mark as completed if we've achieved the required count
        if target_info["achieved"] >= target_info["required"]:
            target_info["completed"] = True
        
        print(f"Created tile {tile_value}! Total created: {target_info['created_count']}/{target_info['required']}")

def get_unlocked_level(mode):
    """Gets the highest unlocked level for a specific game mode."""
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT level FROM unlocked_levels WHERE mode = ?", (mode,))
        row = c.fetchone()
        conn.close()
        return row[0] if row else 1
    except:
        return 1  # Default to level 1 if database error

def unlock_next_level(mode, current_level):
    """Unlock the next level for the given mode"""
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO unlocked_levels (mode, level) VALUES (?, ?)", 
                  (mode, current_level + 1))
        conn.commit()
        conn.close()
    except:
        pass  # Ignore database errors for now

def is_level_previously_completed(mode, level_number):
    """Check if a level has been previously completed"""
    unlocked_level = get_unlocked_level(mode)
    return level_number < unlocked_level

def is_final_level(mode, level):
    """Checks if the given level is the final level for the mode."""
    if mode == "adventure":
        return level >= len(adventure_levels)
    elif mode == "swift":
        return level >= len(swift_levels)
    return True

def reset_target_tracking(level_number):
    """Reset target tracking for a specific level"""
    global current_session_targets
    if level_number in current_session_targets:
        del current_session_targets[level_number]

def initialize_level_targets(level_number, level_data):
    """Initialize target tracking for a level"""
    global current_session_targets
    current_session_targets[level_number] = {}
    
    for target in level_data["targets"]:
        tile_value = target["tile"]
        required_count = target["count"]
        current_session_targets[level_number][tile_value] = {
            "required": required_count,
            "achieved": 0,
            "completed": False,
            "created_count": 0  # Track how many times this tile was created
        }
    
    # Set up merge tracking
    set_current_level(level_number)
    from move import set_merge_callback
    set_merge_callback(on_tile_merged)

def check_adventure_win(level_number, level_data, grid):
    """Check if all target tiles have been achieved in this session"""
    global current_session_targets
    
    # Check if level exists in tracking
    if level_number not in current_session_targets:
        return None
    
    # Check if all targets are completed
    for tile_value in current_session_targets[level_number]:
        if not current_session_targets[level_number][tile_value]["completed"]:
            return None
    
    return "win"

def check_swift_win(level, score, elapsed_time):
    """Check if the target score is reached within the time limit for swift mode."""
    if score >= level["target_score"] and elapsed_time <= level["time_limit"]:
        return "win"
    return None

def draw_adventure_info_board(screen, font, level_number, level_data, grid, moves_used):
    """Draw information board for adventure mode"""
    # Draw level info
    level_text = font.render(f"Level {level_number}", True, (0, 0, 0))
    screen.blit(level_text, (50, 50))
    
    # Draw moves info
    moves_remaining = level_data["max_moves"] - moves_used
    moves_color = (255, 0, 0) if moves_remaining <= 5 else (0, 0, 0)
    moves_text = font.render(f"Moves: {moves_used}/{level_data['max_moves']}", True, moves_color)
    screen.blit(moves_text, (50, 80))
    
    # Draw target progress
    y_offset = 110
    if level_number in current_session_targets:
        progress = current_session_targets[level_number]
        
        for target in level_data["targets"]:
            tile_value = target["tile"]
            required_count = target["count"]
            
            if tile_value in progress:
                created_count = progress[tile_value]["created_count"]
                is_completed = progress[tile_value]["completed"]
                
                color = (0, 255, 0) if is_completed else (0, 0, 0)
                
                target_text = font.render(f"Create {tile_value}: {created_count}/{required_count}", True, color)
                screen.blit(target_text, (50, y_offset))
                
                if is_completed:
                    check_text = font.render("✓", True, (0, 255, 0))
                    screen.blit(check_text, (300, y_offset))
            
            y_offset += 30

def draw_swift_info_boards(screen, font, level_number, level_data, score, elapsed_time):
    """Draw information boards for swift mode"""
    # Calculate time remaining
    time_remaining = max(0, level_data["time_limit"] - elapsed_time)
    
    # Draw level info
    level_text = font.render(f"Level {level_number}", True, (0, 0, 0))
    screen.blit(level_text, (50, 50))
    
    # Draw target score
    target_text = font.render(f"Target: {level_data['target_score']}", True, (0, 0, 0))
    screen.blit(target_text, (50, 80))
    
    # Draw current score
    score_color = (0, 255, 0) if score >= level_data["target_score"] else (0, 0, 0)
    score_text = font.render(f"Score: {score}", True, score_color)
    screen.blit(score_text, (50, 110))
    
    # Draw time remaining
    minutes = int(time_remaining // 60)
    seconds = int(time_remaining % 60)
    time_color = (255, 0, 0) if time_remaining <= 30 else (0, 0, 0)
    time_text = font.render(f"Time: {minutes:02d}:{seconds:02d}", True, time_color)
    screen.blit(time_text, (50, 140))

def level_selection_loop(screen, mode):
    """Display a level selection screen for the given mode."""
    from button import Button
    
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 50)
    
    levels = adventure_levels if mode == "adventure" else swift_levels
    unlocked_levels = get_unlocked_level(mode)
    
    buttons = []
    for i in range(min(len(levels), unlocked_levels)):
        btn = Button(None, (100 + (i % 4) * 120, 200 + (i // 4) * 80), 
                    str(i + 1), font, "Black", "LightGray")
        buttons.append(btn)
    
    back_btn = Button(None, (100, 600), "Back", font, "Black", "LightGray")
    
    while True:
        screen.fill((230, 230, 230))
        
        title = font.render(f"Select {mode.title()} Level", True, (0, 0, 0))
        screen.blit(title, (screen.get_width() // 2 - title.get_width() // 2, 100))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                for idx, btn in enumerate(buttons):
                    if btn.checkforinput(pos):
                        return idx + 1
                if back_btn.checkforinput(pos):
                    return None
        
        for btn in buttons:
            btn.update(screen)
        back_btn.update(screen)
        
        pygame.display.flip()
        clock.tick(60)

def show_level_complete_message(screen, font, mode, level, score=None, time_or_moves=None, is_replay=False):
    """Shows a message when a level is completed."""
    from button import Button
    
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    
    font_big = pygame.font.Font(None, 80)
    text1 = font_big.render("Level Complete!", True, (255, 215, 0))
    text1_rect = text1.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 80))
    
    button_font = pygame.font.Font(None, 36)
    
    if is_final_level(mode, level):
        retry_btn = Button(None, (screen.get_width() // 2 - 100, screen.get_height() // 2 + 60), 
                          "Retry", button_font, "Black", "LightBlue")
        home_btn = Button(None, (screen.get_width() // 2 + 100, screen.get_height() // 2 + 60), 
                         "Home", button_font, "Black", "LightGray")
        buttons = [retry_btn, home_btn]
        button_actions = ["retry", "home"]
    else:
        next_btn = Button(None, (screen.get_width() // 2 - 150, screen.get_height() // 2 + 60), 
                         "Next Level", button_font, "Black", "LightGreen")
        retry_btn = Button(None, (screen.get_width() // 2, screen.get_height() // 2 + 60), 
                          "Retry", button_font, "Black", "LightBlue")
        home_btn = Button(None, (screen.get_width() // 2 + 150, screen.get_height() // 2 + 60), 
                         "Home", button_font, "Black", "LightGray")
        buttons = [next_btn, retry_btn, home_btn]
        button_actions = ["next_level", "retry", "home"]
    
    clock = pygame.time.Clock()
    while True:
        screen.blit(overlay, (0, 0))
        screen.blit(text1, text1_rect)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "home"
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                for i, btn in enumerate(buttons):
                    if btn.checkforinput(pos):
                        return button_actions[i]
        
        for btn in buttons:
            btn.update(screen)
        
        pygame.display.flip()
        clock.tick(60)

def show_game_over_message(screen, font, mode, level, reason="Game Over!"):
    """Shows a message when the game is over."""
    from button import Button
    
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    
    font_big = pygame.font.Font(None, 80)
    font_small = pygame.font.Font(None, 40)
    
    text1 = font_big.render("Game Over!", True, (255, 100, 100))
    text1_rect = text1.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 100))
    
    text2 = font_small.render(reason, True, (255, 255, 255))
    text2_rect = text2.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 50))
    
    button_font = pygame.font.Font(None, 36)
    
    retry_btn = Button(None, (screen.get_width() // 2 - 120, screen.get_height() // 2 + 60), 
                      "Retry", button_font, "Black", "LightBlue")
    home_btn = Button(None, (screen.get_width() // 2 + 120, screen.get_height() // 2 + 60), 
                     "Home", button_font, "Black", "LightGray")
    
    buttons = [retry_btn, home_btn]
    button_actions = ["retry", "home"]
    
    clock = pygame.time.Clock()
    while True:
        screen.blit(overlay, (0, 0))
        screen.blit(text1, text1_rect)
        screen.blit(text2, text2_rect)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "home"
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                for i, btn in enumerate(buttons):
                    if btn.checkforinput(pos):
                        return button_actions[i]
        
        for btn in buttons:
            btn.update(screen)
        
        pygame.display.flip()
        clock.tick(60)

def display_adventure_targets(screen, font, level_number, level_data, grid):
    """Display target progress with visual indicators (alias for draw_adventure_info_board)"""
    # This is just an alias - the actual display is handled by draw_adventure_info_board
    pass