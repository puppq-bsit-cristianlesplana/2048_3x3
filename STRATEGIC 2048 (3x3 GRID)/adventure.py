import pygame
import time
from level_systems import adventure_levels, level_selection_loop, unlock_next_level
from move import move_left, move_right, move_up, move_down, initialize_grid, add_new_tile, game_over
from draw import draw_board
from button import Button

def run_adventure_mode(screen, font):
    background_image = pygame.image.load(r"C:/Users/cristian/Documents/STRATEGIC 2048 (3x3 GRID)/LOGO/backgroundadventure.png")
    background_image = pygame.transform.scale(background_image, (700, 700))
    grid = initialize_grid(3)
    grid = add_new_tile(grid)
    grid = add_new_tile(grid)
    score = 0
    selected_level = level_selection_loop(screen, "adventure")
    if selected_level is None:
        return  # User closed the level selection or didn't pick a level
    from level_systems import get_adventure_level
    level_data = get_adventure_level(selected_level)
    remaining_moves = level_data["max_moves"]
    tile_created_count = {}
    home_btn = Button(None, (450, 180), "Home", font, "Black", "Red")
    restart_btn = Button(None, (580, 180), "Restart", font, "Black", "Red")

    def restart():
        return add_new_tile(add_new_tile(initialize_grid(3))), 0, level_data["max_moves"], {}
    
    def show_level_complete_message(screen, font, current_level, next_level_callback):
        """
        Shows a congratulation message for 2 seconds and then proceeds to the next level.
        """
        # Save the current screen state
        background = screen.copy()

        # Create a semi-transparent overlay
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        
        # Create the congratulation text
        font_big = pygame.font.Font(None, 80)
        text = font_big.render(f"Level {current_level} Complete!", True, (255, 255, 0))
        text_rect = text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
        
        # Display the message
        screen.blit(background, (0, 0))
        screen.blit(overlay, (0, 0))
        screen.blit(text, text_rect)
        pygame.display.flip()
        
        # Wait for 2 seconds
        start_time = time.time()
        running = True
        while running and time.time() - start_time < 2:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
            pygame.time.delay(100)
        
        # Proceed to next level
        if running:
            next_level_callback()
        return running

    def start_next_level():
        return

    def show_fail_screen():
        screen.fill((255, 255, 255))
        font_big = pygame.font.Font(None, 80)
        font_small = pygame.font.Font(None, 40)
        text1 = font_big.render("Game Over!", True, (255, 0, 0))
        text2 = font_small.render("Press R to Restart or H for Home", True, (0, 0, 0))
        screen.blit(text1, (screen.get_width() // 2 - text1.get_width() // 2, 300))
        screen.blit(text2, (screen.get_width() // 2 - text2.get_width() // 2, 380))
        pygame.display.flip()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return "quit"
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        return "retry"
                    elif event.key == pygame.K_h:
                        return "home"

    while True:
        screen.fill((255, 255, 255))
        screen.blit(background_image, (0, 0))  # Draw background  # <-- Draw logo each frame here
        draw_board(
            screen, grid, score, remaining_moves, font,
            is_time=False, home_btn=home_btn, restart_btn=restart_btn,
            adventure_targets=level_data["targets"],
            tile_created_count=tile_created_count,
            show_score=False
        )  # Draw logo in top-left

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if home_btn.checkforinput(pos):
                    return "home"
                elif restart_btn.checkforinput(pos):
                    grid, score, remaining_moves, tile_created_count = restart()

            elif event.type == pygame.KEYDOWN and remaining_moves > 0:
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
                    remaining_moves -= 1
                    for row in grid:
                        for val in row:
                            if val > 0:
                                tile_created_count[val] = tile_created_count.get(val, 0) + 1
                    completed = True
                    for target in level_data["targets"]:
                        needed = target["count"]
                        made = tile_created_count.get(target["tile"], 0)
                        if made < needed:
                            completed = False
                            break

                    if completed:
                        unlock_next_level("adventure", selected_level)
                        show_level_complete_message(screen, font, selected_level, lambda: start_next_level())
                        return  # Win
                    if game_over(grid):
                        result = show_fail_screen()
                        if result == "retry":
                            grid, score, remaining_moves, tile_created_count = restart()
                        elif result == "home":
                            return "home"
        if remaining_moves <= 0:
            completed = True
            for target in level_data["targets"]:
                needed = target["count"]
                made = tile_created_count.get(target["tile"], 0)
                if made < needed:
                    completed = False
                    break
            if not completed:
                result = show_fail_screen()
                if result == "retry":
                    grid, score, remaining_moves, tile_created_count = restart()
                elif result == "home":
                    return "home"
                
        pygame.display.flip()
        pygame.time.Clock().tick(60)