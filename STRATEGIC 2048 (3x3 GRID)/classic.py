import pygame
from button import Button
from draw import draw_board
from move import (
    move_left, move_right, move_up, move_down,
    initialize_grid, add_new_tile, game_over, can_move
)
from utils import load_high_score, save_high_score

def run_classic_mode(screen, font):
    background_image = pygame.image.load(r"C:/Users/cristian/Documents/STRATEGIC 2048 (3x3 GRID)/LOGO/backgroundclassic.png")
    background_image = pygame.transform.scale(background_image, (700, 700))
    
    grid = initialize_grid(3)
    grid = add_new_tile(grid)
    grid = add_new_tile(grid)
    score = 0
    
    high_score = load_high_score("classic")
    
    # History stack for undo functionality (stores multiple previous states)
    move_history = []  # List of (grid, score) tuples
    max_history = 5   # Maximum number of moves to remember
    
    home_btn = Button(None, (410, 190), "Home", font, "Black", "Red")
    restart_btn = Button(None, (520, 190), "Restart", font, "Black", "Red")
    undo_btn = Button(None, (630, 190), "Undo", font, "Black", "Red")
    
    def restart():
        nonlocal move_history
        move_history.clear()  # Clear history on restart
        new_grid = initialize_grid(3)
        return add_new_tile(add_new_tile(new_grid)), 0
    
    def save_state(grid, score):
        """Save current state to history before making a move"""
        nonlocal move_history
        # Create deep copy of the grid
        grid_copy = [row[:] for row in grid]
        move_history.append((grid_copy, score))
        
        # Keep only the last max_history moves
        if len(move_history) > max_history:
            move_history.pop(0)
    
    def undo():
        """Undo the last move by restoring previous state from history"""
        nonlocal move_history
        if move_history:
            # Get the last saved state
            prev_grid, prev_score = move_history.pop()
            return [row[:] for row in prev_grid], prev_score
        else:
            # No moves to undo, return current state
            return [row[:] for row in grid], score
    
    def can_undo():
        """Check if undo is available"""
        return len(move_history) > 0
    
    def draw_score_boards(screen, current_score, high_score):
        """
        Draw separate score boards for current score and high score
        """
        # Current Score Board
        current_score_x = 20
        current_score_y = 60
        score_board_width = 150
        score_board_height = 80
        
        # Draw current score board
        pygame.draw.rect(screen, (100, 100, 100),
                        (current_score_x, current_score_y, score_board_width, score_board_height),
                        width=3, border_radius=10)
        pygame.draw.rect(screen, (240, 230, 210),
                        (current_score_x, current_score_y, score_board_width, score_board_height),
                        border_radius=10)
        
        # Current score text
        score_font = pygame.font.Font(None, 28)
        score_label_font = pygame.font.Font(None, 32)
        
        current_label = score_label_font.render("SCORE", True, (119, 110, 101))
        current_value = score_font.render(str(current_score), True, (0, 0, 0))
        
        # Center the text in the current score board
        current_label_rect = current_label.get_rect(center=(current_score_x + score_board_width//2, current_score_y + 20))
        current_value_rect = current_value.get_rect(center=(current_score_x + score_board_width//2, current_score_y + 50))
        
        screen.blit(current_label, current_label_rect)
        screen.blit(current_value, current_value_rect)
        
        # High Score Board
        high_score_x = 190
        high_score_y = 60
        
        # Draw high score board
        pygame.draw.rect(screen, (100, 100, 100),
                        (high_score_x, high_score_y, score_board_width, score_board_height),
                        width=3, border_radius=10)
        pygame.draw.rect(screen, (240, 230, 210),
                        (high_score_x, high_score_y, score_board_width, score_board_height),
                        border_radius=10)
        
        # High score text
        high_label = score_label_font.render("BEST", True, (119, 110, 101))
        high_value = score_font.render(str(high_score), True, (0, 0, 0))
        
        # Center the text in the high score board
        high_label_rect = high_label.get_rect(center=(high_score_x + score_board_width//2, high_score_y + 20))
        high_value_rect = high_value.get_rect(center=(high_score_x + score_board_width//2, high_score_y + 50))
        
        screen.blit(high_label, high_label_rect)
        screen.blit(high_value, high_value_rect)
        
        # Add a glow effect if current score equals high score
        if current_score == high_score and current_score > 0:
            pygame.draw.rect(screen, (255, 215, 0),
                            (high_score_x - 2, high_score_y - 2, score_board_width + 4, score_board_height + 4),
                            width=3, border_radius=12)
    
    def show_game_over_popup():
        """
        Shows an improved game over popup with modern styling (matching level complete message)
        """
        import math
        
        # Create a semi-transparent overlay
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))  # Semi-transparent black
        
        # Create the game over text
        font_big = pygame.font.Font(None, 80)
        font_medium = pygame.font.Font(None, 50)
        font_small = pygame.font.Font(None, 40)
        
        text1 = font_big.render("Game Over!", True, (255, 100, 100))  # Red color
        text2 = font_medium.render(f"Final Score: {score}", True, (255, 255, 255))
        
        # Check if it's a new high score
        if score >= high_score:
            text3 = font_medium.render("NEW HIGH SCORE!", True, (255, 215, 0))  # Gold color
        else:
            text3 = font_medium.render(f"High Score: {high_score}", True, (255, 255, 255))
        
        # Position the text in the center of the screen
        text1_rect = text1.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 120))
        text2_rect = text2.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 60))
        text3_rect = text3.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 20))
        
        # Create buttons with better styling
        button_font = pygame.font.Font(None, 36)
        
        # Determine which buttons to show based on undo availability
        if can_undo():
            restart_btn_popup = Button(None, (screen.get_width() // 2 - 120, screen.get_height() // 2 + 80), 
                                     "Restart", button_font, "White", "Crimson")
            undo_btn_popup = Button(None, (screen.get_width() // 2, screen.get_height() // 2 + 80), 
                                  "Undo", button_font, "Black", "Gold")
            home_btn_popup = Button(None, (screen.get_width() // 2 + 120, screen.get_height() // 2 + 80), 
                                  "Home", button_font, "Black", "LightGray")
            buttons = [restart_btn_popup, undo_btn_popup, home_btn_popup]
            button_actions = ["retry", "undo", "home"]
        else:
            restart_btn_popup = Button(None, (screen.get_width() // 2 - 80, screen.get_height() // 2 + 80), 
                                     "Restart", button_font, "White", "Crimson")
            home_btn_popup = Button(None, (screen.get_width() // 2 + 80, screen.get_height() // 2 + 80), 
                                  "Home", button_font, "Black", "LightGray")
            buttons = [restart_btn_popup, home_btn_popup]
            button_actions = ["retry", "home"]
        
        # Animation variables
        animation_time = 0
        clock = pygame.time.Clock()
        
        # Display the message and handle input
        while True:
            animation_time += clock.get_time() / 1000.0  # Convert to seconds
            
            # Create pulsing effect for "Game Over" text
            pulse = abs(math.sin(animation_time * 2)) * 0.3 + 0.7  # Pulse between 0.7 and 1.0
            pulsed_color = (int(255 * pulse), int(100 * pulse), int(100 * pulse))
            text1_pulsed = font_big.render("Game Over!", True, pulsed_color)
            
            # Draw everything
            screen.blit(overlay, (0, 0))
            
            # Draw a subtle border around the message area
            message_rect = pygame.Rect(screen.get_width() // 2 - 300, screen.get_height() // 2 - 150, 600, 280)
            pygame.draw.rect(screen, (50, 50, 50), message_rect, border_radius=20)
            pygame.draw.rect(screen, (100, 100, 100), message_rect, 3, border_radius=20)
            
            screen.blit(text1_pulsed, text1_rect)
            screen.blit(text2, text2_rect)
            screen.blit(text3, text3_rect)
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return "home"
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    for i, btn in enumerate(buttons):
                        if btn.checkforinput(pos):
                            return button_actions[i]
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:  # R for restart
                        return "retry"
                    elif event.key == pygame.K_u and can_undo():  # U for undo
                        return "undo"
                    elif event.key == pygame.K_ESCAPE or event.key == pygame.K_h:  # ESC or H for home
                        return "home"
            
            # Update and draw buttons with hover effects
            mouse_pos = pygame.mouse.get_pos()
            for btn in buttons:
                # Add hover effect
                if btn.checkforinput(mouse_pos):
                    btn.changecolor(mouse_pos, "White", "Black")
                else:
                    if btn == restart_btn_popup:
                        btn.changecolor(mouse_pos, "White", "White")
                    else:
                        btn.changecolor(mouse_pos, "Black", "Black")
                btn.update(screen)
            
            # Add keyboard hints
            hint_font = pygame.font.Font(None, 24)
            if can_undo():
                hint_text = hint_font.render("Press R to Restart, U to Undo, ESC for Home", True, (150, 150, 150))
            else:
                hint_text = hint_font.render("Press R to Restart, ESC for Home", True, (150, 150, 150))
            hint_rect = hint_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + 140))
            screen.blit(hint_text, hint_rect)
            
            pygame.display.flip()
            clock.tick(60)
    
    def show_2048_achievement():
        """
        Shows a congratulations message when player reaches 2048 (matching the new style)
        """
        # Create a semi-transparent overlay
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))  # Semi-transparent black
        
        # Create the achievement text
        font_big = pygame.font.Font(None, 80)
        font_medium = pygame.font.Font(None, 50)
        font_small = pygame.font.Font(None, 40)
        
        text1 = font_big.render("Congratulations!", True, (255, 215, 0))  # Gold color
        text2 = font_medium.render("You reached 2048!", True, (255, 255, 255))
        text3 = font_small.render("Classic Mode - Keep playing for higher scores!", True, (200, 200, 200))
        
        # Position the text in the center of the screen
        text1_rect = text1.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 120))
        text2_rect = text2.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 60))
        text3_rect = text3.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 20))
        
        # Create continue button
        button_font = pygame.font.Font(None, 36)
        continue_btn = Button(None, (screen.get_width() // 2, screen.get_height() // 2 + 80), 
                            "Continue Playing", button_font, "Black", "LightGreen")
        
        clock = pygame.time.Clock()
        
        # Display the message and handle input
        while True:
            # Draw everything
            screen.blit(overlay, (0, 0))
            
            # Draw a subtle border around the message area
            message_rect = pygame.Rect(screen.get_width() // 2 - 300, screen.get_height() // 2 - 150, 600, 280)
            pygame.draw.rect(screen, (50, 50, 50), message_rect, border_radius=20)
            pygame.draw.rect(screen, (255, 215, 0), message_rect, 3, border_radius=20)  # Gold border
            
            screen.blit(text1, text1_rect)
            screen.blit(text2, text2_rect)
            screen.blit(text3, text3_rect)
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if continue_btn.checkforinput(event.pos):
                        return True
                elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    return True
            
            # Update and draw continue button with hover effect
            mouse_pos = pygame.mouse.get_pos()
            if continue_btn.checkforinput(mouse_pos):
                continue_btn.changecolor(mouse_pos, "White", "Black")
            else:
                continue_btn.changecolor(mouse_pos, "Black", "Black")
            continue_btn.update(screen)
            
            pygame.display.flip()
            clock.tick(60)
    
    clock = pygame.time.Clock()
    achieved_2048 = False  # Track if player has reached 2048
    
    while True:
        screen.fill((255, 255, 255))
        screen.blit(background_image, (0, 0))
        
        # Draw separate score boards
        draw_score_boards(screen, score, high_score)
        
        # Update undo button appearance based on availability
        if can_undo():
            undo_btn.rect_color = "LightGray"
            undo_btn.text_color = "Black"
        else:
            undo_btn.rect_color = "DarkGray"
            undo_btn.text_color = "Gray"
        
        # Draw the game board without the built-in score display
        draw_board(
            screen, grid, score, None, font,
            is_time=False, high_score=high_score,
            home_btn=home_btn, restart_btn=restart_btn, undo_btn=undo_btn,
            show_score=False  # Disable built-in score display
        )
        
        # Check for 2048 achievement
        max_tile = max(max(row) for row in grid)
        if not achieved_2048 and max_tile >= 2048:
            achieved_2048 = True
            if not show_2048_achievement():
                return "home"
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return "home"
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if home_btn.checkforinput(event.pos):
                    return "home"
                elif restart_btn.checkforinput(event.pos):
                    grid, score = restart()
                    achieved_2048 = False  # Reset achievement flag
                elif undo_btn.checkforinput(event.pos) and can_undo():
                    grid, score = undo()
            elif event.type == pygame.KEYDOWN:
                moved = False
                gained = 0
                
                # Save state before making a move
                if event.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN):
                    save_state(grid, score)
                
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
                    
                    # Update high score
                    if score > high_score:
                        high_score = score
                        save_high_score("classic", high_score)
                    
                    # Check for game over
                    if game_over(grid) or not can_move(grid):
                        result = show_game_over_popup()
                        if result == "retry":
                            grid, score = restart()
                            achieved_2048 = False  # Reset achievement flag
                        elif result == "undo" and can_undo():
                            grid, score = undo()
                        elif result == "home":
                            return "home"
                else:
                    # If no move was made, remove the saved state
                    if move_history:
                        move_history.pop()
        
        pygame.display.flip()
        clock.tick(60)
