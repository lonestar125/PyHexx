# PyGame template.
 
# Import standard modules.
import sys
# Import non-standard modules.
import pygame
from pygame.locals import *

pygame.display.set_mode((800, 600))


class Tile(pygame.sprite.Sprite):
	def __init__(self, pos):
		super(Tile, self).__init__()
		self.image = pygame.image.load("resized_HEX.png").convert_alpha()
		self.rect = self.image.get_rect()
		self.rect.center = pos

	def update(self):
		pass

def create_board():
	"""
	Create the hexxagon board.
	"""
	x_size = 36
	y_size = 50
	#grid: coord x, coord y, state (-1, hidden, 0 = empty, 1 = player 1, 2 = player 2)
	grid = [[[x*x_size, y*y_size, -1] for x in range(9)] for y in range(9)]
	
	margin = 238
	for line in grid:
		for el in line:
			if int(el[0] /x_size) % 2 == 0:
				el[1] += 25
			el[0] += margin

	activated = [[2, 7], [2, 8], [1, 8], [1, 9], [0, 9], [1, 9], [1, 8], [2, 8], [2, 7]]

	for i in range(len(activated)):
		for j in range(activated[i][0], activated[i][1]):
			grid[j][i][2] = 0

	group = pygame.sprite.RenderPlain()
	for line in grid:
		for el in line:
			if el[2]!= -1:
				tile = Tile((el[0], el[1]))
				el.append(tile)
				group.add(tile)

	return grid, group
	
def update(dt, grid):
	"""
	Update game. Called once per frame.
	dt is the amount of time passed since last frame.
	If you want to have constant apparent movement no matter your framerate,
	what you can do is something like

	x += v * dt

	and this will scale your velocity based on time. Extend as necessary."""

	# Go through events that are passed to the script by the window.
	for event in pygame.event.get():
		if event.type == QUIT:
			pygame.quit() # Opposite of pygame.init
			sys.exit() # Not including this line crashes the script on Windows. Possibly
			# on other operating systems too, but I don't know for sure.
	# Handle other events as you wish.
		if event.type == MOUSEBUTTONDOWN: 
			x,y = event.pos

			for line in grid:
				for el in line:
					if el[2] != -1:
						if el[3].rect.collidepoint(x,y): 
							print("clicked tile at", el[0], el[1])
 
def draw(screen, grid, group):
	"""
	Draw things to the window. Called once per frame.
	"""
	screen.fill((0, 0, 0)) # Fill the screen with black.

	# Redraw screen here.
	group.draw(screen)
	# Flip the display so that the things we drew actually show up.
	pygame.display.flip()
 
def runPyGame():
	# Initialise PyGame.
	pygame.init()

	# Set up the clock. This will tick every frame and thus maintain a relatively constant framerate. Hopefully.
	fps = 60.0
	fpsClock = pygame.time.Clock()

	# Set up the window.
	width, height = 800, 600
	screen = pygame.display.set_mode((width, height))

	# screen is the surface representing the window.
	# PyGame surfaces can be thought of as screen sections that you can draw onto.
	# You can also draw surfaces onto other surfaces, rotate surfaces, and transform surfaces.

	# Main game loop.
	dt = 1/fps # dt is the time since last frame.
	grid, group = create_board()
	
	print(grid)
	while True: # Loop forever!
		update(dt, grid) # You can update/draw here, I've just moved the code for neatness.
		draw(screen, grid, group)

		dt = fpsClock.tick(fps)

runPyGame()
