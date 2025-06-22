import pygame

class Button:
    def __init__(self, image, pos, text, font, text_color, rect_color):
        self.image = image
        self.x_pos, self.y_pos = pos
        self.font = font
        self.text_input = text
        self.text_color = text_color
        self.rect_color = rect_color

        self.text_surface = self.font.render(self.text_input, True, self.text_color)
        self.text_rect = self.text_surface.get_rect(center=(self.x_pos, self.y_pos))
        padding_x = 40  # horizontal padding
        padding_y = 20  # vertical padding
        rect_width = self.text_surface.get_width() + padding_x
        rect_height = self.text_surface.get_height() + padding_y

        self.button_rect = pygame.Rect(
            self.x_pos - rect_width // 2, 
            self.y_pos - rect_height // 2, 
            rect_width, 
            rect_height
        )
    def update(self, screen):
        # Draw rounded rectangle with modern styling
        pygame.draw.rect(screen, self.rect_color, self.button_rect, border_radius=15)
        if self.image is not None:
            screen.blit(self.image, self.button_rect)
        screen.blit(self.text_surface, self.text_rect)

    def checkforinput(self, position):
        return self.button_rect.collidepoint(position)

    def changecolor(self, position, base_color, hover_color):
        if self.button_rect.collidepoint(position):
            self.text_surface = self.font.render(self.text_input, True, hover_color)
        else:
            self.text_surface = self.font.render(self.text_input, True, base_color)

    def update_rect(self, pos=None):
        """Update the button's position (center) and recalculate rect/text_rect."""
        if pos is not None:
            self.x_pos, self.y_pos = pos
        self.text_rect = self.text_surface.get_rect(center=(self.x_pos, self.y_pos))
        rect_width = self.button_rect.width
        rect_height = self.button_rect.height
        self.button_rect.topleft = (self.x_pos - rect_width // 2, self.y_pos - rect_height // 2)
