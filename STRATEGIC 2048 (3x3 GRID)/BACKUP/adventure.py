import pygame
import time
from level_systems import (
    adventure_levels,
    level_selection_loop,
    unlock_next_level,
    get_adventure_level,
    show_level_complete_message,
    show_game_over_message,
    is_final_level,
    draw_adventure_info_boards
)
from move import move_left, move_right, move_up, move_down, initialize_grid, add_new_tile, game_over, can_move
from draw import draw_board
from button import Button

def run_adventure_mode(screen, font):
    background_image = pygame.image.load(r"C:/Users/cristian/Documents/STRATEGIC 2048 (3x3 GRID)/LOGO/backgroundadventure.png")
    background_image = pygame.transform.scale(background_image, (700, 700))
    
    # Level selection
    selected_level = level_selection_loop(screen, "adventure")
    if selected_level is None:
        return "home"
    
    current_level = selected_level
    
    while current_level <= len(adventure_levels):
        # Initialize game state for current level
        grid = initialize_grid(3)
        grid = add_new_tile(grid)
        grid = add_new_tile(grid)
        score = 0
        
        level_data = get_adventure_level(current_level)
        max_moves = level_data["max_moves"]
        moves_used = 0
        
        # History stack for undo functionality
        move_history = []
        max_history = 10
        
        home_btn = Button(None, (450, 190), "Home", font, "Black", "Red")
        restart_btn = Button(None, (580, 190), "Restart", font, "Black", "Red")
        undo_btn = Button(None, (320, 190), "Undo", font, "Black", "Red")
        
        def restart():
            nonlocal move_history
            move_history.clear()
            return add_new_tile(add_new_tile(initialize_grid(3))), 0, 0
        
        def save_state(grid, score, moves_used):
            """Save current state to history before making a move"""
            nonlocal move_history
            grid_copy = [row[:] for row in grid]
            move_history.append((grid_copy, score, moves_used))
            
            if len(move_history) > max_history:
                move_history.pop(0)
        
        def undo():
            """Undo the last move by restoring previous state from history"""
            nonlocal move_history
            if move_history:
                prev_grid, prev_score, prev_moves = move_history.pop()
                return [row[:] for row in prev_grid], prev_score, prev_moves
            else:
                return [row[:] for row in grid], score, moves_used
        
        def can_undo():
            """Check if undo is available"""
            return len(move_history) > 0
        
        def check_level_completion():
            """Check if all targets are met"""
            for target in level_data["targets"]:
                target_tile = target["tile"]
                target_count = target["count"]
                current_count = sum(row.count(target_tile) for row in grid)
                if current_count < target_count:
                    return False
            return True
        
        # Main game loop for current level
        level_running = True
        while level_running:
            screen.fill((255, 255, 255))
            screen.blit(background_image, (0, 0))
            
            # Draw separate information boards
            draw_adventure_info_boards(
                screen, 
                current_level, 
                score, 
                moves_used, 
                max_moves, 
                level_data["targets"], 
                grid
            )
            
            # Update undo button appearance based on availability
            if can_undo():
                undo_btn.rect_color = "LightGray"
                undo_btn.text_color = "Black"
            else:
                undo_btn.rect_color = "DarkGray"
                undo_btn.text_color = "Gray"
            
            # Draw the game board WITHOUT any score display from draw.py
            draw_board(
                screen, grid, 0, None, font,  # Pass 0 for score to hide it
                is_time=False, 
                home_btn=home_btn, 
                restart_btn=restart_btn, 
                undo_btn=undo_btn,
                show_score=False,  # Explicitly disable score display
                high_score=0  # Pass 0 for high score
            )
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return "quit"
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    if home_btn.checkforinput(pos):
                        return "home"
                    elif restart_btn.checkforinput(pos):
                        grid, score, moves_used = restart()
                    elif undo_btn.checkforinput(pos) and can_undo():
                        grid, score, moves_used = undo()
                elif event.type == pygame.KEYDOWN and moves_used < max_moves:
                    moved = False
                    gained = 0
                    
                    # Save state before making a move
                    if event.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN):
                        save_state(grid, score, moves_used)
                    
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
                        moves_used += 1
                        
                        # Check for level completion
                        if check_level_completion():
                            # Unlock next level
                            if not is_final_level("adventure", current_level):
                                unlock_next_level("adventure", current_level)
                            
                            result = show_level_complete_message(screen, font, "adventure", current_level)
                            if result == "next_level" and not is_final_level("adventure", current_level):
                                current_level += 1
                                level_running = False  # Exit current level loop to start next level
                                break
                            else:
                                return "home"
                        
                        # Check for game over (no moves left but board is full)
                        if not can_move(grid) or game_over(grid):
                            if not check_level_completion():
                                result = show_game_over_message(screen, font, "adventure", current_level, "No more moves available!")
                                if result == "retry":
                                    grid, score, moves_used = restart()
                                    continue
                                elif result == "home":
                                    return "home"
                                elif result == "level_select":
                                    selected_level = level_selection_loop(screen, "adventure")
                                    if not selected_level:
                                        return "home"
                                    current_level = selected_level
                                    level_running = False
                                    break
                    else:
                        # If no move was made, remove the saved state
                        if move_history:
                            move_history.pop()
            
            # Check if moves are exhausted
            if moves_used >= max_moves:
                if not check_level_completion():
                    result = show_game_over_message(screen, font, "adventure", current_level, "Maximum moves exceeded!")
                    if result == "retry":
                        grid, score, moves_used = restart()
                        continue
                    elif result == "home":
                        return "home"
                    elif result == "level_select":
                        selected_level = level_selection_loop(screen, "adventure")
                        if not selected_level:
                            return "home"
                        current_level = selected_level
                        level_running = False
                        break
            
            pygame.display.flip()
            pygame.time.Clock().tick(60)
    
    return "home"