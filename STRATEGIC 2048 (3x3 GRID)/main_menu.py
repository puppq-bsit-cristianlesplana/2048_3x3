import pygame
import sys
import adventure
import swift_mode as swift
import classic  # import your classic mode module
from button import Button

pygame.init()
screen = pygame.display.set_mode((700, 700))
pygame.display.set_caption("")

font = pygame.font.Font(None, 70)
title_text = font.render("2048", True, (50, 50, 50))

button_font = pygame.font.Font(None, 40)
classic_btn = Button(None, (350, 300), "Classic Mode", button_font, "Black", "SkyBlue")
adventure_btn = Button(None, (350, 400), "Adventure Mode", button_font, "Black", "Orange")
swift_btn = Button(None, (350, 500), "Swift Mode", button_font, "Black", "Tomato")

running = True
while running:
    screen.fill((255, 255, 204))
    screen.blit(title_text, (screen.get_width() // 2 - title_text.get_width() // 2, 100))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if classic_btn.checkforinput(mouse_pos):
                classic.run_classic_mode(screen, button_font)
            elif adventure_btn.checkforinput(mouse_pos):
                adventure.run_adventure_mode(screen, button_font)
            elif swift_btn.checkforinput(mouse_pos):
                swift.run_swift_mode(screen, button_font)

    classic_btn.update(screen)
    adventure_btn.update(screen)
    swift_btn.update(screen)

    pygame.display.flip()
    pygame.time.Clock().tick(60)

pygame.quit()
sys.exit()
