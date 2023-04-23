# Import standard modules.
import sys
import random
from time import sleep
from copy import deepcopy
# Import non-standard modules.
import mcts_bot
import layer_bot
from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1' # removes the pygame welcome message
import pygame
from pygame.locals import *
from pygame import mixer

pygame.init()

# Set the window size and create the display surface
screen_width = 640
screen_height = 480
screen = pygame.display.set_mode((screen_width, screen_height))

class Volume(pygame.sprite.Sprite):
	"""
	A class to represent a mute button.
	"""
	def __init__(self):
		"""
		int, int --> None
		Initialise the mute button.
		"""
		super(Volume, self).__init__()
		self.images = [pygame.image.load("Sprites/mute.png").convert_alpha(),
					   pygame.image.load("Sprites/unmute.png").convert_alpha()]
		self.image_index = 1
		self.image = self.images[self.image_index]
		self.rect = self.image.get_rect()
		self.rect.x, self.rect.y = 100, 100
		self.mask = pygame.mask.from_surface(self.image)

	def update(self):
		"""
		None --> None
		Update the mute button with the corresponding image based on its status
		"""
		self.image_index = 1 - self.image_index
		self.image = self.images[self.image_index]
		return self.image_index
		

groupV = pygame.sprite.RenderPlain()
volume_button = Volume()  # Create a volume button at position (100, 100)
groupV.add(volume_button)
groupV.draw(screen)  # Draw the volume button on the screen

# Main game loop
while True:
    screen.fill((0, 0, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left mouse button clicked
            mouse_pos = pygame.mouse.get_pos()
            if volume_button.rect.collidepoint(mouse_pos):  # If the volume button is clicked
                volume_button.update()  # Toggle the image of the volume button

	# Update the screen
    groupV.draw(screen)
    pygame.display.flip()