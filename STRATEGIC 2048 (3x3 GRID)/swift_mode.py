import pygame
from button import Button
from draw import draw_board
from move import (
    move_left, move_right, move_up, move_down,
    initialize_grid, add_new_tile, can_move
)
from level_systems import (
    swift_levels,
    level_selection_loop,
    show_level_complete_message,
    show_game_over_message,
    unlock_next_level,
    is_final_level,
    draw_swift_info_boards,
    is_level_previously_completed,
    check_swift_win
)
from timer import Timer

def run_swift_mode(screen, font):
    """Run the swift mode game loop"""
    background_image = pygame.image.load(r"C:/Users/cristian/Documents/STRATEGIC 2048 (3x3 GRID)/LOGO/backgroundswift.png")
    background_image = pygame.transform.scale(background_image, (700, 700))
    
    # Level selection
    current_level = level_selection_loop(screen, "swift")
    if current_level is None:
        return "home"
    
    # Get level data
    if current_level > len(swift_levels):
        return "home"
    
    level_data = swift_levels[current_level - 1].copy()
    level_data["level_number"] = current_level
    
    # Initialize game state
    grid = initialize_grid(3)
    grid = add_new_tile(add_new_tile(grid))
    score = 0
    
    # Initialize timer
    timer = Timer()
    timer.start()
    
    # Create buttons
    button_font = pygame.font.Font(None, 36)
    home_btn = Button(None, (430, 190), "Home", button_font, "Black", "Red")
    restart_btn = Button(None, (570, 190), "Restart", button_font, "Black", "Red")
    
    def restart_level():
        """Restart current level"""
        timer.reset()
        timer.start()
        new_grid = initialize_grid(3)
        return add_new_tile(add_new_tile(new_grid)), 0
    
    clock = pygame.time.Clock()
    
    while True:
        elapsed_time = timer.get_elapsed_time()
        screen.fill((250, 248, 239))
        screen.blit(background_image, (0, 0))
        
        # Draw the game board
        draw_board(screen, grid, score, "", font, show_score=True)
        
        # Draw swift info
        draw_swift_info_boards(screen, font, current_level, level_data, score, elapsed_time)
        
        # Draw buttons
        home_btn.update(screen)
        restart_btn.update(screen)
        
        # Check time limit first
        if elapsed_time >= level_data["time_limit"]:
            timer.stop()
            result = show_game_over_message(screen, font, "swift", current_level, "Time's up!")
            if result == "retry":
                grid, score = restart_level()
                continue
            elif result == "home":
                return "home"
            continue
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "home"
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if home_btn.checkforinput(event.pos):
                    return "home"
                elif restart_btn.checkforinput(event.pos):
                    grid, score = restart_level()
            
            elif event.type == pygame.KEYDOWN:
                moved = False
                gained = 0
                
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    grid, moved, gained = move_left(grid)
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    grid, moved, gained = move_right(grid)
                elif event.key == pygame.K_UP or event.key == pygame.K_w:
                    grid, moved, gained = move_up(grid)
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    grid, moved, gained = move_down(grid)
                elif event.key == pygame.K_r:  # R key for restart
                    grid, score = restart_level()
                    continue
                elif event.key == pygame.K_ESCAPE:  # ESC key for home
                    return "home"
                
                if moved:
                    score += gained
                    grid = add_new_tile(grid)
                    
                    # Check win condition
                    if check_swift_win(level_data, score, elapsed_time) == "win":
                        timer.stop()
                        is_replay = is_level_previously_completed("swift", current_level)
                        
                        if not is_final_level("swift", current_level):
                            unlock_next_level("swift", current_level)
                        
                        result = show_level_complete_message(
                            screen, font, "swift", current_level, 
                            score, int(elapsed_time), is_replay=is_replay
                        )
                        
                        if result == "next_level" and not is_final_level("swift", current_level):
                            # Go to next level
                            current_level += 1
                            if current_level <= len(swift_levels):
                                level_data = swift_levels[current_level - 1].copy()
                                level_data["level_number"] = current_level
                                grid, score = restart_level()
                            else:
                                return "home"
                        elif result == "retry":
                            grid, score = restart_level()
                        elif result == "home":
                            return "home"
                        
                        continue
                    
                    if not can_move(grid):
                        timer.stop()
                        result = show_game_over_message(screen, font, "swift", current_level, "No more moves possible!")
                        if result == "retry":
                            grid, score = restart_level()
                        elif result == "home":
                            return "home"
                        continue
        
        pygame.display.flip()
        clock.tick(60)
