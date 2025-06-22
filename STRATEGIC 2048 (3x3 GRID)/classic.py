import pygame
from button import Button
from draw import draw_board
from move import (
    move_left, move_right, move_up, move_down,
    initialize_grid, add_new_tile, game_over
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

    prev_grid = [row[:] for row in grid]
    prev_score = score

    home_btn = Button(None, (410, 190), "Home", font, "Black", "Red")
    restart_btn = Button(None, (520, 190), "Restart", font, "Black", "Red")
    undo_btn = Button(None, (630, 190), "Undo", font, "Black", "Red")

    def restart():
        new_grid = initialize_grid(3)
        return add_new_tile(add_new_tile(new_grid)), 0

    def undo():
        return [row[:] for row in prev_grid], prev_score

    def show_game_over_popup():
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
                    return "home"
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        return "retry"
                    elif event.key == pygame.K_h:
                        return "home"

    clock = pygame.time.Clock()

    while True:
        screen.fill((255, 255, 255))
        screen.blit(background_image, (0, 0))

        draw_board(
            screen, grid, score, None, font,
            is_time=False, high_score=high_score,
            home_btn=home_btn, restart_btn=restart_btn, undo_btn=undo_btn,
            show_score=True
        )

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if home_btn.checkforinput(event.pos):
                    return "home"
                elif restart_btn.checkforinput(event.pos):
                    grid, score = restart()
                elif undo_btn.checkforinput(event.pos):
                    grid, score = undo()

            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN):
                    prev_grid = [row[:] for row in grid]
                    prev_score = score

                if event.key == pygame.K_LEFT:
                    grid, moved, gained = move_left(grid)
                elif event.key == pygame.K_RIGHT:
                    grid, moved, gained = move_right(grid)
                elif event.key == pygame.K_UP:
                    grid, moved, gained = move_up(grid)
                elif event.key == pygame.K_DOWN:
                    grid, moved, gained = move_down(grid)
                else:
                    moved = False
                    gained = 0

                if moved:
                    score += gained
                    grid = add_new_tile(grid)
                    if score > high_score:
                        high_score = score
                        save_high_score("classic", high_score)
                    if game_over(grid):
                        result = show_game_over_popup()
                        if result == "retry":
                            grid, score = restart()
                        elif result == "home":
                            return "home"

        pygame.display.flip()
        clock.tick(60)
