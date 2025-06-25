import pygame

def draw_board(
    screen, grid, score, extra_info, font,
    is_time=False, high_score=0,
    adventure_targets=None, tile_created_count=None,
    home_btn=None, restart_btn=None, undo_btn=None,
    show_score=True,
    board_left=None, board_top=None,
    logo_img=None  # New argument for logo image surface
):
    tile_size = 120
    tile_spacing = 5
    default_top_padding = 200

    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0

    grid_width = cols * tile_size + (cols - 1) * tile_spacing
    grid_height = rows * tile_size + (rows - 1) * tile_spacing

    screen_width, screen_height = screen.get_size()

    if board_left is None:
        board_left = (screen_width - grid_width) // 2
    if board_top is None:
        board_top = default_top_padding + 40

    small_font = pygame.font.Font(None, 36)
    if logo_img:
        logo_pos = (20, 20)
        screen.blit(logo_img, logo_pos)
    if show_score:
        score_box_x = screen_width - 330
        score_box_y = default_top_padding - 140
        score_box_w = 300
        score_box_h = 100

        score_box_rect = pygame.Rect(score_box_x, score_box_y, score_box_w, score_box_h)
        pygame.draw.rect(screen, (240, 230, 210), score_box_rect, border_radius=10)
        pygame.draw.rect(screen, (0, 0, 0), score_box_rect, 2, border_radius=10)

        score_text = small_font.render(f"Score: {score}", True, (0, 0, 0))
        high_score_text = small_font.render(f"High Score: {high_score}", True, (0, 0, 0))

        screen.blit(score_text, (score_box_x + 10, score_box_y + 10))
        screen.blit(high_score_text, (score_box_x + 10, score_box_y + 50))
    tile_colors = {
        0: (205, 193, 180),
        2: (238, 228, 218),
        4: (237, 224, 200),
        8: (242, 177, 121),
        16: (245, 149, 99),
        32: (246, 124, 95),
        64: (246, 94, 59),
        128: (237, 207, 114),
        256: (237, 204, 97),
        512: (237, 200, 80),
        1024: (237, 197, 63),
        2048: (237, 194, 46),
        4096: (237, 199, 50),
    }

    for row in range(rows):
        for col in range(cols):
            value = grid[row][col]
            color = tile_colors.get(value, (60, 58, 50))

            x = board_left + col * (tile_size + tile_spacing)
            y = board_top + row * (tile_size + tile_spacing)

            rect = pygame.Rect(x, y, tile_size, tile_size)
            pygame.draw.rect(screen, color, rect, border_radius=10)
            pygame.draw.rect(screen, (0, 0, 0), rect, 2, border_radius=10)

            if value != 0:
                font_color = (0, 0, 0)
                value_text = font.render(str(value), True, font_color)
                text_rect = value_text.get_rect(center=rect.center)
                screen.blit(value_text, text_rect)
    if adventure_targets and tile_created_count is not None:
        info_box_x = board_left + 200
        info_box_y = board_top - 210
        box_width = 300
        box_height = 120

        info_box_rect = pygame.Rect(info_box_x, info_box_y, box_width, box_height)
        pygame.draw.rect(screen, (230, 220, 200), info_box_rect, border_radius=12)
        pygame.draw.rect(screen, (0, 0, 0), info_box_rect, 2, border_radius=12)

        text_y = info_box_y + 10

        if extra_info is not None:
            moves_left_text = small_font.render(f"Moves Left: {extra_info}", True, (0, 0, 0))
            screen.blit(moves_left_text, (info_box_x + 10, text_y))
            text_y += 30

        for target in adventure_targets:
            tile = target["tile"]
            count = target["count"]
            progress = tile_created_count.get(tile, 0)

            target_text = font.render(f"{tile} x{count}", True, (0, 0, 0))
            progress_text = small_font.render(f"→ {progress}/{count}", True, (0, 0, 0))

            screen.blit(target_text, (info_box_x + 10, text_y))
            screen.blit(progress_text, (info_box_x + 110, text_y + 5))

            text_y += 40
    if home_btn:
        home_btn.update(screen)
    if restart_btn:
        restart_btn.update(screen)
    if undo_btn:
        undo_btn.update(screen)
