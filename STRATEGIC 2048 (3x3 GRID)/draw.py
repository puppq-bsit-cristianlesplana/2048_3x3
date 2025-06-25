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
    
    # Score box section removed as requested
    
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

    # Text colors for better contrast
    text_colors = {
        0: (119, 110, 101),
        2: (119, 110, 101),
        4: (119, 110, 101),
        8: (249, 246, 242),
        16: (249, 246, 242),
        32: (249, 246, 242),
        64: (249, 246, 242),
        128: (249, 246, 242),
        256: (249, 246, 242),
        512: (249, 246, 242),
        1024: (249, 246, 242),
        2048: (249, 246, 242),
        4096: (249, 246, 242),
    }

    # Draw the game grid with square tiles
    for row in range(rows):
        for col in range(cols):
            value = grid[row][col]
            color = tile_colors.get(value, (60, 58, 50))
            x = board_left + col * (tile_size + tile_spacing)
            y = board_top + row * (tile_size + tile_spacing)
            
            # Create square tile (no border_radius for square corners)
            rect = pygame.Rect(x, y, tile_size, tile_size)
            pygame.draw.rect(screen, color, rect)  # Fill tile
            pygame.draw.rect(screen, (0, 0, 0), rect, 2)  # Border (square)

            if value != 0:
                # Use appropriate text color for contrast
                font_color = text_colors.get(value, (249, 246, 242))
                
                # Adjust font size based on tile value for better fit
                if value < 100:
                    tile_font = pygame.font.Font(None, 55)
                elif value < 1000:
                    tile_font = pygame.font.Font(None, 50)
                else:
                    tile_font = pygame.font.Font(None, 45)
                
                value_text = tile_font.render(str(value), True, font_color)
                text_rect = value_text.get_rect(center=rect.center)
                screen.blit(value_text, text_rect)

    # Draw adventure targets info box (if provided) - also with square corners
    if adventure_targets and tile_created_count is not None:
        info_box_x = board_left + 200
        info_box_y = board_top - 210
        box_width = 300
        box_height = 120

        info_box_rect = pygame.Rect(info_box_x, info_box_y, box_width, box_height)
        pygame.draw.rect(screen, (230, 220, 200), info_box_rect)  # Square corners
        pygame.draw.rect(screen, (0, 0, 0), info_box_rect, 2)  # Square border

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

    # Draw buttons
    if home_btn:
        home_btn.update(screen)
    if restart_btn:
        restart_btn.update(screen)
    if undo_btn:
        undo_btn.update(screen)
