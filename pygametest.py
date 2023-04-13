# Import standard modules.
import sys
# Import non-standard modules.
import pygame
from pygame.locals import *

# Set up the window, this needs to be outside of the main loop because the Tile class needs access to the screen
# and classes are loaded before everything else in python for some reason
width, height = 800, 600
global screen
screen = pygame.display.set_mode((width, height))

class Tile(pygame.sprite.Sprite):
	def __init__(self, grid_el):
		super(Tile, self).__init__()
		self.image = pygame.image.load("Sprites/resized_HEX.png").convert_alpha()
		self.rect = self.image.get_rect()
		self.rect.x, self.rect.y = grid_el["x"], grid_el["y"]
		self.mask = pygame.mask.from_surface(self.image)


	def update(self, grid_el):
		print(grid_el)
		if grid_el["status"] == 0:
			self.image = pygame.image.load("Sprites/resized_HEX.png").convert_alpha()
		if grid_el["status"] == 1:
			self.image = pygame.image.load("Sprites/HEX_p1.png").convert_alpha()
		if grid_el["status"] == 2:
			self.image = pygame.image.load("Sprites/HEX_p2.png").convert_alpha()


def create_board():
	"""
	Create the hexxagon board.
	"""
	x_size = 36
	y_size = 50
	# grid: coord x, coord y, status, outlined, tile (the tile is only available for the grid items that are not out of bounds)
	# state: -1 for empty, 0 for activated, 1 for player 1, 2 for player 2
	# outlined: 0 for not outlined, 1 for clonable, 2 for jumpable
	grid = [[{"x": x*x_size, "y": y*y_size, "status": -1, "outline": 0} for x in range(9)] for y in range(9)]
	
	margin = 238
	for line in grid:
		for el in line:
			if int(el["x"] /x_size) % 2 == 0:
				el["y"] += 25
			el["x"] += margin

	activated = [[2, 7], [2, 8], [1, 8], [1, 9], [0, 9], [1, 9], [1, 8], [2, 8], [2, 7]]

	for i in range(len(activated)):
		for j in range(activated[i][0], activated[i][1]):
			grid[j][i]["status"] = 0

	group = pygame.sprite.RenderPlain()

	for line in grid:
		for el in line:
			if el["status"]!= -1:
				tile = Tile(el)
				el["tile"] = tile
				group.add(tile)

	
	hidden = [[4, 3], [3, 5], [5, 5]]
	starting_p1 = [[0, 2], [4, 8], [8, 2]] #[4, 4], [7, 4]
	starting_p2 = [[0, 6], [4, 0], [8, 6]]
	for el in starting_p1:
		# format: grid[y_index][x_index][status] = p1 or p2
		grid[el[1]][el[0]]["status"] = 1
		grid[el[1]][el[0]]["tile"].update(grid[el[1]][el[0]])
	
	for el in starting_p2:
		grid[el[1]][el[0]]["status"] = 2
		grid[el[1]][el[0]]["tile"].update(grid[el[1]][el[0]])
	
	for el in hidden:
		grid[el[1]][el[0]]["status"] = -1
		grid[el[1]][el[0]]["tile"].kill()
		del grid[el[1]][el[0]]["tile"]
		

	return grid, group
	


def check_cloneable(x, y, cloneable):
	# reset clone and jump outline
	for line in grid:
		for el in line:
			el["outline"] = 0

	cloneable = []
	for el in even_n1 if x % 2 == 0 else odd_n1:
		try: 
			if grid[y + el[1]][x + el[0]]["status"] == 0 and (0 <= (y + el[1]) <= 8) and (0 <= (x + el[0]) <= 8):
				cloneable.append(grid[y + el[1]][x + el[0]])
				grid[y + el[1]][x + el[0]]["outline"] = 1
		except IndexError: # not shit code tkt
			pass
	return cloneable

def check_jumpable(x, y, jumpable):

	jumpable = []
	for el in even_n2 if x % 2 == 0 else odd_n2:
		try:
			if grid[y + el[1]][x + el[0]]["status"] == 0 and (0 <= (y + el[1]) <= 8) and (0 <= (x + el[0]) <= 8):
				jumpable.append(grid[y + el[1]][x + el[0]])
				grid[y + el[1]][x + el[0]]["outline"] = 2
		except IndexError: # not shit code tkt
			pass
	return jumpable

def update_neighbours(x, y, current_player):
	for el in even_n1 if x % 2 == 0 else odd_n1:
		try: 
			if grid[y + el[1]][x + el[0]]["status"] == abs(current_player - 3) and (0 <= (y + el[1]) <= 8) and (0 <= (x + el[0]) <= 8):
				grid[y + el[1]][x + el[0]]["status"] = current_player
				grid[y + el[1]][x + el[0]]["tile"].update(grid[y + el[1]][x + el[0]])
		except IndexError: # not shit code tkt
			pass



def update(cloneable, jumpable, selected_tile, current_player):
	# Go through events that are passed to the script by the window.
	for event in pygame.event.get():
		if event.type == QUIT:
			pygame.quit() # Opposite of pygame.init
			sys.exit() # Not including this line crashes the script on Windows. Possibly
			# on other operating systems too, but I don't know for sure.
	# Handle other events

		if event.type == MOUSEBUTTONDOWN and event.button == 1: 

			x,y = event.pos

			for line in grid:
				for el in line:

					# if one of current_player's tiles was clicked, highlight possible moves
					if el["status"] == current_player:
						pos_in_mask = x - el["tile"].rect.x, y - el["tile"].rect.y # position of mouse in image mask
						if el["tile"].rect.collidepoint(x,y) and el["tile"].mask.get_at(pos_in_mask): # checks that the position of the mouse when clicked is in the rect and the mask of the image
							cloneable = check_cloneable(line.index(el), grid.index(line), cloneable)
							jumpable = check_jumpable(line.index(el), grid.index(line), jumpable)
							#print(f"x: {line.index(el)}, y: {grid.index(line)}")
							selected_tile = el

						
					# if one of the currently highlighted tiles was clicked, do stuff
					elif el["outline"] == 1:
						pos_in_mask = x - el["tile"].rect.x, y - el["tile"].rect.y
						if el["tile"].rect.collidepoint(x,y) and el["tile"].mask.get_at(pos_in_mask): 
							el["status"] = current_player
							el["tile"].update(el)
							update_neighbours(line.index(el), grid.index(line), current_player)
							for line in grid:
								for el in line:
									el["outline"] = 0
							cloneable = []
							jumpable = []
							current_player = abs(current_player - 3)

					
					elif el["outline"] == 2:
						pos_in_mask = x - el["tile"].rect.x, y - el["tile"].rect.y
						if el["tile"].rect.collidepoint(x,y) and el["tile"].mask.get_at(pos_in_mask): 
							el["status"] = current_player
							el["tile"].update(el)
							selected_tile["status"] = 0
							selected_tile["tile"].update(selected_tile)
							update_neighbours(line.index(el), grid.index(line), current_player)
							for line in grid:
								for el in line:
									el["outline"] = 0
							cloneable = []
							jumpable = []
							current_player = abs(current_player - 3)
						
	return cloneable, jumpable, selected_tile, current_player
					


def draw(cloneable, jumpable):
	"""
	Draw things to the window. Called once per frame.
	"""
	screen.fill((0, 0, 0)) # Fill the screen with black.
	group.draw(screen) # draw tile sprites from the Tile class
	
	#draw outlines
	for el in cloneable:
		img_i = pygame.image.load("Sprites/HEX_cloneable.png").convert_alpha()
		img = img_i.get_rect()
		img.x = el["x"]
		img.y = el["y"]
		screen.blit(img_i, (img.x, img.y))
	
	for el in jumpable:
		img_i = pygame.image.load("Sprites/HEX_jumpable.png").convert_alpha()
		img = img_i.get_rect()
		img.x = el["x"]
		img.y = el["y"]
		screen.blit(img_i, (img.x, img.y))
	
	pygame.display.flip() # Flip the display so that the things we drew actually show up.
 
def runPyGame():
	pygame.init()
	
	global group
	global grid
	grid, group = create_board()

	# current player, 1 or 2, 
	# end of turn: current_player = abs(current_player - 3)
	global current_player
	current_player = 1

	# neighboring tile deltas, [x, y]
	global even_n1
	global odd_n1
	even_n1 = [[0, -1], [-1, 0], [1, 0], [-1, 1], [0, 1], [1, 1]]
	odd_n1 = [[0, 1], [0, -1], [-1, 0], [1, 0], [-1, -1], [1, -1]]

	global even_n2
	global odd_n2
	even_n2 = [[0, -2], [-1, -1], [1, -1], [-2, -1], [2, -1], [-2, 0], [2, 0], [-2, 1], [-1, 2], [0, 2], [1, 2], [2, 1]]
	odd_n2 = [[0, 2], [-1, 1], [1, 1], [-2, 1], [2, 1], [-2, 0], [2, 0], [-2, -1], [-1, -2], [0, -2], [1, -2], [2, -1]]

	global selected_tile
	selected_tile = None

	# Main game loop.
	cloneable = []
	jumpable = []
	while True:
		cloneable, jumpable, selected_tile, current_player = update(cloneable, jumpable, selected_tile, current_player) 
		draw(cloneable, jumpable) # the draw function may be merged with the update function if it isnt used for much

runPyGame()
