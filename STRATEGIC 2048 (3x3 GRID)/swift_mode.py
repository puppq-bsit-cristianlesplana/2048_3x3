import pygame
import time
from level_systems import swift_levels, level_selection_loop
from move import move_left, move_right, move_up, move_down, initialize_grid, add_new_tile, game_over, can_move
from draw import draw_board
from button import Button

def run_swift_mode(screen, font):
    background_image = pygame.image.load(r"C:/Users/cristian/Documents/STRATEGIC 2048 (3x3 GRID)/LOGO/backgroundswift.png")
    background_image = pygame.transform.scale(background_image, (700, 700))
    grid = initialize_grid(3)
    grid = add_new_tile(grid)
    grid = add_new_tile(grid)
    score = 0
    selected_level = level_selection_loop(screen, "swift")
    if not selected_level:
        return
    level_data = swift_levels[selected_level - 1]
    timer_duration = level_data.get("time_limit", 60)
    start_time = time.time()
    home_btn = Button(None, (450, 180), "Home", font, "Black", "Red")
    restart_btn = Button(None, (580, 180), "Restart", font, "Black", "Red")

    def restart():
        new_grid = initialize_grid(3)
        return add_new_tile(add_new_tile(new_grid)), 0, time.time()

    def show_fail_screen():
        screen.fill((255, 255, 255))
        fail_text = pygame.font.Font(None, 80)
        retry_text = pygame.font.Font(None, 40)
        fail_text = font.render("Game Over!", True, (255, 0, 0))
        retry_text = font.render("Press R to Restart or H for Home", True, (0, 0, 0))
        screen.blit(fail_text, (300, 300))
        screen.blit(retry_text, (200, 360))
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

    while True:
        screen.fill((255, 255, 255))
        screen.blit(background_image, (0, 0))  # ✅ Draw background  # ✅ Draw logo in top-left

        time_elapsed = time.time() - start_time
        time_left = max(0, int(timer_duration - time_elapsed))
        if time_left <= 0:
            return

        draw_board(
            screen, grid, score, time_left, font,
            is_time=True, home_btn=home_btn, restart_btn=restart_btn,
            show_score=False
        )
        box_x, box_y = 400, 20
        box_width, box_height = 250, 130
        pygame.draw.rect(screen, (100, 100, 100), (box_x, box_y, box_width, box_height), width=12,border_radius=12)
        pygame.draw.rect(screen, (240, 230, 210), (box_x, box_y, box_width, box_height), border_radius=12)
        info_font = pygame.font.Font(None, 36)
        screen.blit(info_font.render(f"Target Score: {level_data['target_score']}", True, (0, 0, 0)), (box_x + 10, box_y + 10))
        screen.blit(info_font.render(f"Time Left: {time_left}", True, (0, 0, 0)), (box_x + 10, box_y + 50))
        screen.blit(info_font.render(f"Your Score: {score}", True, (0, 0, 0)), (box_x + 10, box_y + 90))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

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

                    if not can_move(grid) or game_over(grid):
                        result = show_fail_screen()
                        if result == "retry":
                            grid, score, start_time = restart()
                            continue
                        elif result == "home" or result == "quit":
                            return "home"

                    if score >= level_data["target_score"]:
                        return  # ✅ Level complete

        pygame.display.flip()
        pygame.time.Clock().tick(60)
