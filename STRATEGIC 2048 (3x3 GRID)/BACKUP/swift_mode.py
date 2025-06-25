import pygame
import time
from level_systems import (
    swift_levels,
    level_selection_loop,
    show_level_complete_message,
    show_game_over_message,
    unlock_next_level,
    is_final_level,
    draw_swift_info_boards  # Add this import
)
from move import move_left, move_right, move_up, move_down, initialize_grid, add_new_tile, game_over, can_move
from draw import draw_board
from button import Button

def run_swift_mode(screen, font):
    background_image = pygame.image.load(r"C:/Users/cristian/Documents/STRATEGIC 2048 (3x3 GRID)/LOGO/backgroundswift.png")
    background_image = pygame.transform.scale(background_image, (700, 700))
    
    # Level selection
    selected_level = level_selection_loop(screen, "swift")
    if not selected_level:
        return "home"
    
    current_level = selected_level
    
    while current_level <= len(swift_levels):
        # Initialize game state for current level
        grid = initialize_grid(3)
        grid = add_new_tile(grid)
        grid = add_new_tile(grid)
        score = 0
        
        level_data = swift_levels[current_level - 1]
        timer_duration = level_data.get("time_limit", 60)
        start_time = time.time()
        
        home_btn = Button(None, (450, 190), "Home", font, "Black", "Red")
        restart_btn = Button(None, (580, 190), "Restart", font, "Black", "Red")
        
        def restart():
            new_grid = initialize_grid(3)
            return add_new_tile(add_new_tile(new_grid)), 0, time.time()
        
        # Main game loop for current level
        level_running = True
        while level_running:
            screen.fill((255, 255, 255))
            screen.blit(background_image, (0, 0))
            
            time_elapsed = time.time() - start_time
            time_left = max(0, int(timer_duration - time_elapsed))
            
            # Check for time limit exceeded
            if time_left <= 0 and score < level_data["target_score"]:
                result = show_game_over_message(screen, font, "swift", current_level)
                if result == "retry":
                    grid, score, start_time = restart()
                    continue
                elif result == "home":
                    return "home"
                elif result == "level_select":
                    selected_level = level_selection_loop(screen, "swift")
                    if not selected_level:
                        return "home"
                    current_level = selected_level
                    break
            
            # Check for level completion
            if score >= level_data["target_score"]:
                # Unlock next level
                if not is_final_level("swift", current_level):
                    unlock_next_level("swift", current_level)
                
                result = show_level_complete_message(screen, font, "swift", current_level)
                if result == "next_level" and not is_final_level("swift", current_level):
                    current_level += 1
                    level_running = False  # Exit current level loop to start next level
                    continue
                else:
                    return "home"
            
            # Draw separate information boards (REPLACE the old info box)
            draw_swift_info_boards(
                screen, 
                current_level, 
                score, 
                level_data["target_score"], 
                time_left, 
                timer_duration
            )
            
            # Draw the game board WITHOUT any score/time display from draw.py
            draw_board(
                screen, grid, 0, None, font,  # Pass 0 for score, None for time
                is_time=False,  # Disable time display
                home_btn=home_btn, 
                restart_btn=restart_btn,
                show_score=False  # Explicitly disable score display
            )
            
            # REMOVE the old info box code completely - it's replaced by draw_swift_info_boards above
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return "quit"
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    if home_btn.checkforinput(pos):
                        return "home"
                    elif restart_btn.checkforinput(pos):
                        grid, score, start_time = restart()
                elif event.type == pygame.KEYDOWN and time_left > 0:
                    moved = False
                    gained = 0
                    if event.key == pygame.K_LEFT:
                        grid, moved, gained = move_left(grid)
                    elif event.key == pygame.K_RIGHT:
                        grid, moved, gained = move_right(grid)
                    elif event.key == pygame.K_UP:
                        grid, moved, gained = move_up(grid)
                    elif event.key == pygame.K_DOWN:
                        grid, moved, gained = move_down(grid)
                    
                    if moved:
                        score += gained
                        grid = add_new_tile(grid)
                        
                        # Check for game over (no moves left)
                        if not can_move(grid) or game_over(grid):
                            if score < level_data["target_score"]:
                                result = show_game_over_message(screen, font, "swift", current_level, "No more moves available!")
                                if result == "retry":
                                    grid, score, start_time = restart()
                                    continue
                                elif result == "home":
                                    return "home"
                                elif result == "level_select":
                                    selected_level = level_selection_loop(screen, "swift")
                                    if not selected_level:
                                        return "home"
                                    current_level = selected_level
                                    level_running = False
                                    break
            
            pygame.display.flip()
            pygame.time.Clock().tick(60)
    
    return "home"
