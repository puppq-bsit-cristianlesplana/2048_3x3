import pygame
from button import Button
from draw import draw_board
from move import (
    move_left, move_right, move_up, move_down,
    initialize_grid, add_new_tile, can_move
)
from level_systems import (
    adventure_levels,
    level_selection_loop,
    show_level_complete_message,
    show_game_over_message,
    unlock_next_level,
    is_final_level,
    draw_adventure_info_board,
    is_level_previously_completed,
    reset_target_tracking,
    initialize_level_targets,
    check_adventure_win
)

def run_adventure_mode(screen, font):
    """Run the adventure mode game loop"""
    background_image = pygame.image.load(r"C:/Users/cristian/Documents/STRATEGIC 2048 (3x3 GRID)/LOGO/backgroundadventure.png")
    background_image = pygame.transform.scale(background_image, (700, 700))
    
    # Level selection
    current_level = level_selection_loop(screen, "adventure")
    if current_level is None:
        return "home"
    
    # Get level data
    if current_level > len(adventure_levels):
        return "home"
    
    level_data = adventure_levels[current_level - 1].copy()
    level_data["level_number"] = current_level
    
    # Initialize target tracking
    initialize_level_targets(current_level, level_data)
    
    # Initialize game state
    grid = initialize_grid(3)
    grid = add_new_tile(add_new_tile(grid))
    score = 0
    moves_used = 0
    
    # Create buttons
    button_font = pygame.font.Font(None, 36)
    home_btn = Button(None, (430, 190), "Home", button_font, "Black", "Red")
    restart_btn = Button(None, (570, 190), "Restart", button_font, "Black", "Red")
    
    def restart_level():
        """Restart current level"""
        reset_target_tracking(current_level)
        initialize_level_targets(current_level, level_data)
        new_grid = initialize_grid(3)
        return add_new_tile(add_new_tile(new_grid)), 0, 0
    
    clock = pygame.time.Clock()
    
    while True:
        screen.fill((250, 248, 239))
        screen.blit(background_image, (0, 0))
        # Draw the game board
        draw_board(screen, grid, score, "", font, show_score=True)
        
        # Draw adventure info
        draw_adventure_info_board(screen, font, current_level, level_data, grid, moves_used)
        
        # Draw buttons
        home_btn.update(screen)
        restart_btn.update(screen)
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "home"
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if home_btn.checkforinput(event.pos):
                    return "home"
                elif restart_btn.checkforinput(event.pos):
                    grid, score, moves_used = restart_level()
            
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
                    grid, score, moves_used = restart_level()
                    continue
                elif event.key == pygame.K_ESCAPE:  # ESC key for home
                    return "home"
                
                if moved:
                    score += gained
                    moves_used += 1
                    grid = add_new_tile(grid)
                    
                    # Check win condition
                    if check_adventure_win(current_level, level_data, grid) == "win":
                        is_replay = is_level_previously_completed("adventure", current_level)
                        
                        if not is_final_level("adventure", current_level):
                            unlock_next_level("adventure", current_level)
                        
                        result = show_level_complete_message(
                            screen, font, "adventure", current_level, 
                            score, moves_used, is_replay=is_replay
                        )
                        
                        if result == "next_level" and not is_final_level("adventure", current_level):
                            # Go to next level
                            current_level += 1
                            if current_level <= len(adventure_levels):
                                level_data = adventure_levels[current_level - 1].copy()
                                level_data["level_number"] = current_level
                                initialize_level_targets(current_level, level_data)
                                grid, score, moves_used = restart_level()
                            else:
                                return "home"
                        elif result == "retry":
                            grid, score, moves_used = restart_level()
                        elif result == "home":
                            return "home"
                        
                        continue
                    
                    # Check game over conditions
                    if moves_used >= level_data["max_moves"]:
                        result = show_game_over_message(screen, font, "adventure", current_level, "No more moves left!")
                        if result == "retry":
                            grid, score, moves_used = restart_level()
                        elif result == "home":
                            return "home"
                        continue
                    
                    if not can_move(grid):
                        result = show_game_over_message(screen, font, "adventure", current_level, "No more moves possible!")
                        if result == "retry":
                            grid, score, moves_used = restart_level()
                        elif result == "home":
                            return "home"
                        continue
        
        pygame.display.flip()
        clock.tick(60)