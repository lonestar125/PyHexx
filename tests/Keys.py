
import pygame

# Initialize Pygame
pygame.init()

# Set the window size and create the display surface
screen_width = 640
screen_height = 480
screen = pygame.display.set_mode((screen_width, screen_height))

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            key_name = pygame.key.name(event.key)
            print(key_name)
    # Update the screen
    pygame.display.update()

# Quit Pygame
pygame.quit()