import pygame
import random

pygame.init()

screen = pygame.display.set_mode((800, 600))

# Load the star image
star = pygame.image.load("star_sprite.png").convert_alpha()

# Get the star image size
star_rect = star.get_rect()

# Create a list to store the stars
stars = []

# Fill the list with stars at random positions
for i in range(100):
    x = random.randint(0, 800)
    y = random.randint(0, 600)
    stars.append((x, y))

# Start the game loop
running = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Clear the screen
    screen.fill((0, 0, 0))

    # Scroll the stars
    for i, (x, y) in enumerate(stars):
        x -= 1
        if x < -star_rect.width:
            x = 800
        stars[i] = (x, y)

    # Draw the stars
    for x, y in stars:
        screen.blit(star, (x, y))

    # Update the display
    pygame.display.update()
    
    pygame.time.wait(10)