import pygame




def add_mute_button(sprite_group, x, y, mute_img_path, unmute_img_path):
    # Load the mute and unmute images
    mute_img = pygame.image.load(mute_img_path).convert_alpha()
    unmute_img = pygame.image.load(unmute_img_path).convert_alpha()

    # Define the MuteButton sprite class
    class MuteButton(pygame.sprite.Sprite):
        def __init__(self, x, y, image1, image2):
            super().__init__()
            self.images = [image1, image2]
            self.image = self.images[0]
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.y = y
            self.is_muted = False

        def toggle_mute(self):
            self.is_muted = not self.is_muted
            if self.is_muted:
                self.image = self.images[1]
            else:
                self.image = self.images[0]

    # Create an instance of the MuteButton sprite
    mute_button = MuteButton(x, y, mute_img, unmute_img)

    # Add the sprite to the group
    sprite_group.add(mute_button)

import pygame

# Initialize Pygame
pygame.init()

# Set the window size and create the display surface
screen_width = 640
screen_height = 480
screen = pygame.display.set_mode((screen_width, screen_height))

# Create a sprite group for the mute button
mute_button_group = pygame.sprite.Group()

# Add the mute button to the sprite group
add_mute_button(mute_button_group, 100, 100, "Sprites/mute.png", "Sprites/unmute.png")

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                # Check if the mouse click is on the mute button
                if mute_button_group.sprites()[0].rect.collidepoint(event.pos):
                    mute_button_group.sprites()[0].toggle_mute()

    # Clear the screen
    screen.fill((255, 255, 255))

    # Draw the sprites
    mute_button_group.draw(screen)

    # Update the screen
    pygame.display.update()

# Quit Pygame
pygame.quit()
