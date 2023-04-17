# Import standard modules.
import sys
# Import non-standard modules.
import pygame
from pygame.locals import *

# Set up the window, this needs to be outside of the main function because the Tile class needs access to the screen
# and classes are loaded before everything else in python for some reason
width, height = 800, 600
global screen
screen = pygame.display.set_mode((width, height))

class Tile(pygame.sprite.Sprite):
	def __init__(self, grid_el):
		super(Tile, self).__init__()
		self.update(grid_el)
		self.rect = self.image.get_rect()
		self.rect.x, self.rect.y = grid_el["x"], grid_el["y"]
		self.mask = pygame.mask.from_surface(self.image)


	def update(self, grid_el):
		if grid_el["status"] == 0:
			self.image = pygame.image.load("Sprites/empty.png").convert_alpha()
		if grid_el["status"] == 1:
			self.image = pygame.image.load("Sprites/red.png").convert_alpha()
		if grid_el["status"] == 2:
			self.image = pygame.image.load("Sprites/blue.png").convert_alpha()
		if grid_el["status"] == -1:
			self.image = pygame.image.load("Sprites/hidden.png").convert_alpha()
		
	


def create_board():
	"""
	Create the hexxagon board.
	"""
	x_size = 38
	y_size = 45
	# grid: coord x, coord y, status, outlined, tile (the tile is only available for the grid items that are not out of bounds)
	# state: -1 for empty, 0 for activated, 1 for player 1, 2 for player 2
	# outlined: 0 for not outlined, 1 for clonable, 2 for jumpable
	grid = [[{"x": x*x_size, "y": y*y_size, "status": -1, "outline": 0} for x in range(9)] for y in range(9)]
	
	x_margin = 225
	y_margin = 50
	# offset every second row by 25 on the y
	for line in grid:
		for el in line:
			if int(el["x"] /x_size) % 2 == 0:
				el["y"] += 23
			el["x"] += x_margin
			el["y"] += y_margin

	activated = [[2, 7], [2, 8], [1, 8], [1, 9], [0, 9], [1, 9], [1, 8], [2, 8], [2, 7]]

	for i in range(len(activated)):
		for j in range(activated[i][0], activated[i][1]):
			grid[j][i]["status"] = 0

	group = pygame.sprite.RenderPlain()

	for line in grid:
		for el in line:
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
		grid[el[1]][el[0]]["tile"].update(grid[el[1]][el[0]])
		#grid[el[1]][el[0]]["tile"].kill()
		#del grid[el[1]][el[0]]["tile"]
		
	return grid, group
	

def check_cloneable(x, y, cloneable):
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

def clear_outlines():
	for line in grid:
		for el in line:
			el["outline"] = 0

def get_score():
	score = [0, 0]
	for line in grid:
		for el in line:
			if el["status"] >= 1:
				score[el["status"] - 1] += 1
	return score

def get_total_tiles():
	total_tiles = 0
	for line in grid:
		for el in line:
			if el["status"] != -1:
				total_tiles += 1
	return total_tiles

def check_victory(score):
	if score[0] == 0:
		return 1 #p1 win
	if score[1] == 0:
		return 2 #p2 win
	if score[0] + score[1] == total_tiles: #number of sprites in sprite group = number of active tiles (has tile object in its dictionary)
		if score[0] > score[1]:
			return 1  #p1 win
		if score[1] > score[0]:
			return 2 #p2 win
		else: # score[0] == score[1]
			return 3 #tie
	return None #no current winner

def moves_left(current_player):
	moves = []
	for line in grid:
		for el in line:
			x, y = line.index(el), grid.index(line)
			for el in even_n1 if x % 2 == 0 else odd_n1:
				try: 
					if grid[y + el[1]][x + el[0]]["status"] == 0 and (0 <= (y + el[1]) <= 8) and (0 <= (x + el[0]) <= 8):
						moves.append(1)
				except IndexError: # not shit code tkt
					pass
			if moves == []:
				print("no more moves")
				return False
	return True

def end_turn(cloneable, jumpable, current_player):
	global in_game
	global in_menu
	clear_outlines()
	cloneable = []
	jumpable = []
	score = get_score()
	print(f"score: {score}")
	current_player = abs(current_player - 3)
	if check_victory(score) != None or moves_left(current_player): #order of these matters as the victory check has to come first if not a winning player may not play the last move and lose
		print("Victory not fully implemented")
		draw() #displays the last move
		pygame.display.flip() #pushes update to screen for last move
		in_game = False
		in_menu = True
		global grid
		global group
		group.empty()
		grid, group = create_board()
		current_player = 1
	return cloneable, jumpable, current_player

def has_neighbour(x, y):
	#check if a tile (grid inddex x, y) has a neighbour with status that is not -1
	total_neighbours = 0
	for el in even_n1 if x % 2 == 0 else odd_n1:
		try:
			if grid[y + el[1]][x + el[0]]["status"] != -1 and (0 <= (y + el[1]) <= 8) and (0 <= (x + el[0]) <= 8):
				total_neighbours += 1
		except IndexError:
			pass
	if total_neighbours > 0:
		return True
	else:
		return False
	
#make a function that checks that a tile has a valid path of non -1 status tiles to the tile at 4, 4
def has_valid_path(x, y, visited):
	#check if a tile (grid inddex x, y) has a neighbour with status that is not -1
	visited.append((x, y))
	for el in even_n1 if x % 2 == 0 else odd_n1:
		try:
			if grid[y + el[1]][x + el[0]]["status"] != -1 and (0 <= (y + el[1]) <= 8) and (0 <= (x + el[0]) <= 8):
				if (x + el[0], y + el[1]) not in visited:
					if has_valid_path(x + el[0], y + el[1], visited):
						return True
		except IndexError:
			pass
	if (4, 4) in visited:
		return True
	else:
		return False


def board_editor():
	global in_board_editor
	global in_menu
	screen.fill((24, 24, 24))
	menu_rect = render_text("MENU", 100, 500, color=(241, 232, 205), size=50)

	for event in pygame.event.get():
		if event.type == QUIT:
			pygame.quit() # Opposite of pygame.init
			sys.exit() # Not including this line crashes the script on Windows. Possibly
			# on other operating systems too, but I don't know for sure.

		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_RETURN:
				#check that every tile has a valid path to the center tile
				for line in grid:
					for el in line:
						if el["status"] != -1:
							if not has_valid_path(line.index(el), grid.index(line), []):
								print("invalid board")
								return
				
				#check that both players have at least one tile
				score = get_score()
				if score[0] == 0 or score[1] == 0:
					print("invalid board")
					return
				
				in_board_editor = False
				in_menu = True
				return

		if event.type == MOUSEBUTTONDOWN and event.button == 1: 
			x,y = event.pos

			if menu_rect.collidepoint(x,y):
				in_board_editor = False
				in_menu = True

			for line in grid:
				for el in line:		
					
					if el["status"] == -1:
						pos_in_mask = x - el["tile"].rect.x, y - el["tile"].rect.y # position of mouse in image mask
						if el["tile"].rect.collidepoint(x,y) and el["tile"].mask.get_at(pos_in_mask): # checks that the position of the mouse when clicked is in the rect and the mask of the image
							el["status"] = 0
							el["tile"].update(el)

					elif el["status"] == 0:
						pos_in_mask = x - el["tile"].rect.x, y - el["tile"].rect.y
						if el["tile"].rect.collidepoint(x,y) and el["tile"].mask.get_at(pos_in_mask):
							el["status"] = 1
							el["tile"].update(el)
					
					elif el["status"] == 1:
						pos_in_mask = x - el["tile"].rect.x, y - el["tile"].rect.y
						if el["tile"].rect.collidepoint(x,y) and el["tile"].mask.get_at(pos_in_mask):
							el["status"] = 2
							el["tile"].update(el)
					
					elif el["status"] == 2:
						pos_in_mask = x - el["tile"].rect.x, y - el["tile"].rect.y
						if el["tile"].rect.collidepoint(x,y) and el["tile"].mask.get_at(pos_in_mask):
							if line.index(el) == 4 and grid.index(line) == 4: # the center tile can not be -1
								el["status"] = 0
								el["tile"].update(el)
								return
							el["status"] = -1
							el["tile"].update(el)



def game(cloneable, jumpable, selected_tile, current_player, score):
	global in_game
	global in_menu
	screen.fill((24, 24, 24))
	menu_rect = render_text("MENU", 100, 500, color=(241, 232, 205), size=50)
	# Go through events that are passed to the script by the window.
	for event in pygame.event.get():
		if event.type == QUIT:
			pygame.quit() # Opposite of pygame.init
			sys.exit() # Not including this line crashes the script on Windows. Possibly
			# on other operating systems too, but I don't know for sure.
	# Handle other events

		if event.type == MOUSEBUTTONDOWN and event.button == 1: 

			x,y = event.pos

			if menu_rect.collidepoint(x,y):
				in_game = False
				in_menu = True

			for line in grid:
				for el in line:

					# if one of current_player's tiles was clicked, highlight possible moves
					if el["status"] == current_player:
						pos_in_mask = x - el["tile"].rect.x, y - el["tile"].rect.y # position of mouse in image mask
						if el["tile"].rect.collidepoint(x,y) and el["tile"].mask.get_at(pos_in_mask): # checks that the position of the mouse when clicked is in the rect and the mask of the image
							clear_outlines()
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
							cloneable, jumpable, current_player = end_turn(cloneable, jumpable, current_player)

					
					elif el["outline"] == 2:
						pos_in_mask = x - el["tile"].rect.x, y - el["tile"].rect.y
						if el["tile"].rect.collidepoint(x,y) and el["tile"].mask.get_at(pos_in_mask): 
							el["status"] = current_player
							el["tile"].update(el)
							selected_tile["status"] = 0
							selected_tile["tile"].update(selected_tile)
							update_neighbours(line.index(el), grid.index(line), current_player)
							cloneable, jumpable, current_player = end_turn(cloneable, jumpable, current_player)

						
	return cloneable, jumpable, selected_tile, current_player, score
					

def draw_outlines(cloneable, jumpable):
	for el in cloneable:
		img_i = pygame.image.load("Sprites/clone.png").convert_alpha()
		img = img_i.get_rect()
		img.x = el["x"]
		img.y = el["y"] - 1
		screen.blit(img_i, (img.x, img.y))
	
	for el in jumpable:
		img_i = pygame.image.load("Sprites/jump.png").convert_alpha()
		img = img_i.get_rect()
		img.x = el["x"]
		img.y = el["y"] - 1
		screen.blit(img_i, (img.x, img.y))

def render_text(text, x, y, color=(0, 0, 0), size=32, border=False):
	'''
	fenetre pygame, str, int, int -> None
	options: color=(int,int,int), size=int, border=bool
	affiche du texte a la position x, y de taille size et de couleur color
	'''
	font = pygame.font.Font('freesansbold.ttf', size)
	text = font.render(text, True, color)
	textRect = text.get_rect(center=(x,y))
	#draw a box around text if the border option is set to True
	if border:
		pygame.draw.rect(screen, (0, 0, 0), (textRect.x-5, textRect.y-5, textRect.width+10, textRect.height+10), 5)
	screen.blit(text, textRect)
	return textRect
	
def menu():
	global in_board_editor
	global in_game
	global in_info
	global in_menu

	screen.fill((24, 24, 24))
	render_text("HEXXAGON", 400, 100, color=(241, 232, 205), size=50)
	info_rect = render_text("INFO", 400, 300, color=(241, 232, 205), size=50)
	board_rect = render_text("BOARD EDITOR", 400, 400, color=(241, 232, 205), size=50)
	play_rect = render_text("PLAY", 400, 500, color=(241, 232, 205), size=50)

	for event in pygame.event.get():
		if event.type == QUIT:
			pygame.quit() # Opposite of pygame.init
			sys.exit()
		if event.type == MOUSEBUTTONDOWN and event.button == 1:
			x,y = event.pos
			if play_rect.collidepoint(x,y):
				in_menu = False
				in_game = True
			elif info_rect.collidepoint(x,y):
				in_menu = False
				in_info = True
			elif board_rect.collidepoint(x,y):
				in_menu = False
				in_board_editor = True
				

def draw():
	"""
	Draw things to the window. Called once per frame.
	"""
	global in_game
	global in_board_editor
	global in_menu
	group.draw(screen) # draw tile sprites from the Tile class
	

 
def main():
	pygame.init()
	#pygame.font.init() #necessary for text rendering
	global group #pygame.sprite.Group object, contains all active tiles
	global grid
	global total_tiles

	# neighboring tile deltas [x, y], these are added to a tile to find its neighbors, global because they will not be modified in the rest of the code
	global even_n1
	global odd_n1
	even_n1 = [[0, -1], [-1, 0], [1, 0], [-1, 1], [0, 1], [1, 1]]
	odd_n1 = [[0, 1], [0, -1], [-1, 0], [1, 0], [-1, -1], [1, -1]]

	global even_n2
	global odd_n2
	even_n2 = [[0, -2], [-1, -1], [1, -1], [-2, -1], [2, -1], [-2, 0], [2, 0], [-2, 1], [-1, 2], [0, 2], [1, 2], [2, 1]]
	odd_n2 = [[0, 2], [-1, 1], [1, 1], [-2, 1], [2, 1], [-2, 0], [2, 0], [-2, -1], [-1, -2], [0, -2], [1, -2], [2, -1]]

	global in_menu
	global in_board_editor
	global in_game
	global in_info

	in_menu = True
	in_board_editor = False
	in_game = False
	in_info = False

	grid, group = create_board()
	while True:

		if in_menu: #MENU
			while in_menu:
				menu()
				pygame.display.flip()

		elif in_board_editor: #BOARD EDITOR
			while in_board_editor:
				board_editor()
				draw()
				pygame.display.flip()

		elif in_game: #MAIN GAMW LOOPs
			current_player = 1
			selected_tile = None
			score = get_score()
			cloneable = []
			jumpable = []
			#print("sprites: ", len(group.sprites()))
			total_tiles = get_total_tiles()
			#print(total_tiles)
			while in_game:
				cloneable, jumpable, selected_tile, current_player, score = game(cloneable, jumpable, selected_tile, current_player, score) 
				draw()
				draw_outlines(cloneable, jumpable)
				pygame.display.flip()

		elif in_info: #INFO SCREEN --> game rules, credits, NOT IMPLEMENTED, crashes the game currently
			while in_info:
				#info()
				pygame.display.flip()
				pass

if __name__ == "__main__":
	main()