# Import standard modules.
import sys
import random
from time import sleep
from copy import deepcopy
# Import non-standard modules.
import bots.mcts_bot
import bots.layer_bot
from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1' # removes the pygame welcome message
import pygame
from pygame.locals import *
from pygame import mixer

# Set up the window, this needs to be outside of the main function because the Tile class needs access to the screen
# and classes are loaded before everything else in python.
width, height = 800, 600
global screen
screen = pygame.display.set_mode((width, height))

class Tile(pygame.sprite.Sprite):
	"""
	A class to represent a tile on the board.
	"""
	def __init__(self, grid_el):
		"""
		dict --> None
		Initialise the tile.
		"""
		super(Tile, self).__init__()
		self.update(grid_el)
		self.rect = self.image.get_rect()
		self.rect.x, self.rect.y = grid_el["x"], grid_el["y"]
		self.mask = pygame.mask.from_surface(self.image)


	def update(self, grid_el):
		"""
		dict --> None
		Update the tile with the corresponding image based on its status
		"""
		if grid_el["status"] == 0:
			self.image = pygame.image.load("Sprites/empty.png").convert_alpha()
		if grid_el["status"] == 1:
			self.image = pygame.image.load("Sprites/red.png").convert_alpha()
		if grid_el["status"] == 2:
			self.image = pygame.image.load("Sprites/blue.png").convert_alpha()
		if grid_el["status"] == -1:
			self.image = pygame.image.load("Sprites/hidden.png").convert_alpha()

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
		self.rect.x, self.rect.y = 700, 500
		self.mask = pygame.mask.from_surface(self.image)

	def Vupdate(self):
		"""
		None --> None
		Update the mute button with the corresponding image based on its status
		"""
		self.image_index = 1 - self.image_index
		self.image = self.images[self.image_index]
		if self.image_index == 1:
			mixer.music.play(-1)
		if self.image_index == 0:
			mixer.music.stop()



def create_board():
	"""
	Create the hexagon board.
	"""
	x_size = 38
	y_size = 45
	# grid: coord x, coord y, status, outlined, tile (the tile is only available for the grid items that are not out of bounds)
	# state: -1 for empty, 0 for activated, 1 for player 1, 2 for player 2
	# outlined: 0 for not outlined, 1 for clonable, 2 for jumpable
	grid = [[{"x": x*x_size, "y": y*y_size, "status": -1, "outline": 0} for x in range(9)] for y in range(9)]
	
	x_margin = 225
	y_margin = 50
	# offset every second row by 23px on the y axis
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
	starting_p1 = [[0, 2], [4, 8], [8, 2]]
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
		
	return grid, group



def check_cloneable(x, y, cloneable):
	"""
	int, int, list --> list
	Returns a list of all the tiles that the player can clone to from a specific tiles grid coordinates.
	"""
	cloneable = []
	for el in even_n1 if x % 2 == 0 else odd_n1:
		try: 
			if grid[y + el[1]][x + el[0]]["status"] == 0 and (0 <= (y + el[1]) <= 8) and (0 <= (x + el[0]) <= 8):
				cloneable.append(grid[y + el[1]][x + el[0]])
				grid[y + el[1]][x + el[0]]["outline"] = 1
		except IndexError: # if the tile is out of bounds
			pass
	return cloneable

def check_jumpable(x, y, jumpable):
	"""
	int, int, list --> list
	Returns a list of all the tiles that the player can jump to from a specific tiles grid coordinates.
	"""
	jumpable = []
	for el in even_n2 if x % 2 == 0 else odd_n2:
		try:
			if grid[y + el[1]][x + el[0]]["status"] == 0 and (0 <= (y + el[1]) <= 8) and (0 <= (x + el[0]) <= 8):
				jumpable.append(grid[y + el[1]][x + el[0]])
				grid[y + el[1]][x + el[0]]["outline"] = 2
		except IndexError:  # if the tile is out of bounds
			pass
	return jumpable

def update_neighbours(x, y, current_player):
	"""
	int, int, int --> None
	Updates the direct neighbours (n1) of a tile that has been cloned or jumped to.
	This is called at the end of each turn because after a move has been played, the new tiles neighbours must be converted to the current players colour.
	"""
	for el in even_n1 if x % 2 == 0 else odd_n1:
		try: 
			if grid[y + el[1]][x + el[0]]["status"] == abs(current_player - 3) and (0 <= (y + el[1]) <= 8) and (0 <= (x + el[0]) <= 8):
				grid[y + el[1]][x + el[0]]["status"] = current_player
				grid[y + el[1]][x + el[0]]["tile"].update(grid[y + el[1]][x + el[0]])
		except IndexError: # if the tile is out of bounds
			pass

def clear_outlines():
	"""
	None --> None
	Resets the outline value of all tiles to 0
	when a move is played or a new tile is clicked on, all tiles must be cleared of there outline status before new ones are assigned
	"""
	for line in grid:
		for el in line:
			el["outline"] = 0



def get_score():
	"""
	None --> list[int, int]
	Returns a list representing the current score of the game.
	score[0] is the p1 score
	score[1] is the p2 score
	"""
	score = [0, 0]
	for line in grid:
		for el in line:
			if el["status"] >= 1:
				score[el["status"] - 1] += 1
	return score

def display_scores(score):
	"""
	None --> None
	Displays the current score of the game on the screen
	"""
	
	for i in range(score[1]):
		blue = pygame.image.load("Sprites/blue_score.png").convert_alpha()
		x = 50 + i * 7
		y = 30
		screen.blit(blue, (x,y))
		
		
	for i in range(score[0]):
		red = pygame.image.load("Sprites/orange_score.png").convert_alpha()
		x = 50 + i * 7
		y = 42
		screen.blit(red, (x,y))
	

def get_total_tiles():
	"""
	None --> int
	Returns the total number of tiles that are not hidden on the board
	This is used to check if the game is over and since the board can be modified, the number of total tiles can change from game to game
	"""
	total_tiles = 0
	for line in grid:
		for el in line:
			if el["status"] != -1:
				total_tiles += 1
	return total_tiles

def check_victory(score):
	"""
	list[int, int] --> int
	Returns an integer representing the winner of the game. (1 = p1, 2 = p2, 3 = tie) or None if the game is not over
	"""
	if (score[0] + score[1]) == total_tiles: #number of sprites in sprite group = number of active tiles (has tile object in its dictionary)
		if score[0] > score[1]:
			return 1  #p1 win
		if score[1] > score[0]:
			return 2 #p2 win
		elif score[1] == score[0]: # score[0] == score[1]
			return 3 #tie
	return None #no current winner



def available_moves(current_player):
	"""
	int --> list[list]
	Returns a list of all the available moves for a certain player
	Used to check if a player is out of moves and for various bots
	"""
	#returns all available moves for a certain player
	moves = []
	for line in grid:
		for el in line:
			if el["status"] == current_player:
				x, y = line.index(el), grid.index(line)
				for el in even_n1 if x % 2 == 0 else odd_n1:
					try: 
						if grid[y + el[1]][x + el[0]]["status"] == 0 and (0 <= (y + el[1]) <= 8) and (0 <= (x + el[0]) <= 8):
							moves.append([1, x, y, x + el[0], y + el[1]]) #1 = clone, x, y coords of selected tile,  x + el[0], y + el[1] coords of cloned to tile
					except IndexError:  # if the tile is out of bounds
						pass
				for el in even_n2 if x % 2 == 0 else odd_n2:
					try: 
						if grid[y + el[1]][x + el[0]]["status"] == 0 and (0 <= (y + el[1]) <= 8) and (0 <= (x + el[0]) <= 8):
							moves.append([2, x, y, x + el[0], y + el[1]]) #2 = jump, x, y coords of selected tile,  x + el[0], y + el[1] coords of jumped to tile
					except IndexError:  # if the tile is out of bounds
						pass
	return moves

def moves_left(current_player):
	"""
	int --> bool
	Returns False if a player has no moves left to play, True otherwise
	"""
	#checks if a player has any moves left to play
	moves = available_moves(current_player)
	if moves == []:
		return False
	return True

def random_move(current_player):
	"""
	int --> list
	Returns a random move for the current player chosen from every possible move this player has available
	This is used for the random bot
	"""
	#returns a random possible move for the current player chosen from every possible move this player has available
	moves = available_moves(current_player)
	if moves != []:
		return random.choice(moves)
	return None

def one_layer_best_move(current_player):
	"""
	int --> list
	Returns the "best" move for the current player chosen from every possible move this player has available
	The function tries every move the player currently has available and returns the move that will result in the highest score for the player
	If there are several moves that yield the same best score, the function will return a random move from the "best" moves
	This is a greedy algorithm and has a lot of flaws, it is therefore used for the easy bot
	"""
	moves = available_moves(current_player)
	for move in moves:
		score = 0
		if move[0] == 1:
			score += 1

		for el in even_n1 if move[3] % 2 == 0 else odd_n1:
			try: 
				if grid[move[4] + el[1]][move[3] + el[0]]["status"] == abs(current_player - 3) and (0 <= (move[4] + el[1]) <= 8) and (0 <= (move[3] + el[0]) <= 8):
					score += 1
			except IndexError: # if the tile is out of bounds
				pass
		move.append(score)
	moves.sort(key=lambda x: int(x[5]), reverse=True)
	best_moves = [el for el in moves if el == moves[0]]
	return random.choice(best_moves)

def bot_move(move):
	"""
	list --> None
	Given a move (move = [move_type, x1, y1, x2, y2]), the function will update the grid and the neighbours
	Is used to carry out a bot's move
	"""
	if move[0] == 1:
		grid[move[4]][move[3]]["status"] = 2
		grid[move[4]][move[3]]["tile"].update(grid[move[4]][move[3]])
		update_neighbours(move[3], move[4], 2)
	elif move[0] == 2:
		grid[move[2]][move[1]]["status"] = 0
		grid[move[2]][move[1]]["tile"].update(grid[move[2]][move[1]])
		grid[move[4]][move[3]]["status"] = 2
		grid[move[4]][move[3]]["tile"].update(grid[move[4]][move[3]])
		update_neighbours(move[3], move[4], 2)



def end_turn(cloneable, jumpable, current_player):
	"""
	list, list, int --> None
	Takes in a list of cloneable tiles, a list of jumpable tiles and the current player
	Checks if the opponent player has any moves left, if not, the function will fill in all empty tiles with the current player's color 
	(this is done when the player manages to trap there opponent and block all its possible moves)
	Then the function will check if the game is over and if so, it will display the winner
	Called after the player has played a move and the neighbours have been updated
	"""
	global in_game
	global in_menu
	global score
	clear_outlines()
	cloneable = []
	jumpable = []
	opponent = abs(current_player - 3)
	#if the opponent has no more moves left, fill in all tiles with current_player
	if moves_left(opponent) == False:
		for line in grid:
			for el in line:
				if el['status'] == 0:
					el['status'] = current_player
					el["tile"].update(el)
	
	score = get_score()
	winner = check_victory(score)
	if winner == 1:
		render_text(f"ORANGE WON", 400, 550, color=(247,150,23), size=25, center=True)
		victory_sound = mixer.Sound('Sounds/victory.wav')
		victory_sound.play()
	elif winner == 2:
		render_text(f"BLUE WON", 400, 550, color=(77,155,230), size=25, center=True)
		victory_sound = mixer.Sound('Sounds/victory.wav')
		victory_sound.play()
	elif winner == 3:
		render_text(f"TIE", 400, 550, color=(171, 148, 122), size=25, center=True)
		victory_sound = mixer.Sound('Sounds/victory.wav')
		victory_sound.play()
	current_player = abs(current_player - 3)
	
	if winner != None:
		draw() #displays the last move
		pygame.display.flip() #pushes update to screen to display last move
		sleep(4)
		in_game = False
		in_menu = True
	
	return cloneable, jumpable, current_player

def has_valid_path(x, y, visited):
	"""
	int, int, list --> bool
	Recursive function, returns True if the tile (grid index x, y) has a path to the center tile (4, 4) that is not blocked by -1 tiles
	This is similar to how one would search through an undirected graph
	"""
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



def save_board():
	"""
	None --> None
	Saves the current board to a global variable without its tile objects
	Is necessary because we can not use deepcopy on a pygame sprite object and the grid contains all the tile objects
	"""
	# save the edited board to a global variable without its tile objects
	global saved_board
	saved_board = []
	for line in grid:
		saved_board.append([])
		for el in line:
			del el["tile"]
			saved_board[-1].append(deepcopy(el))

def load_board():
	"""
	None --> None
	Loads the saved board to the global grid variable while adding back the tile objects
	"""
	# load the saved board
	global grid
	global group
	group.empty()
	grid = deepcopy(saved_board)
	for line in grid:
		for el in line:
			tile = Tile(el)
			el["tile"] = tile
			group.add(tile)

def board_editor():
	"""
	None --> None
	Allows the user to edit the board by clicking on tiles to cycle through states
	Is called continuously while in_board_editor is True
	The created board can not include any tiles that are not connected to the rest of the board
	and the board must have at least one tile with status 1 (red) and one tile with status 2 (blue)
	"""
	global in_board_editor
	global in_menu
	global group
	global grid

#------------ Rendering

	screen.fill((44, 34, 46))

	menu_rect,x_menu,y_menu,menu_image = sprite_show("menu")
	screen.blit(menu_image,(x_menu,y_menu))
	x_menu,y_menu,menuP_image = sprite_show("menu_pressed")

	reset_rect,x_reset,y_reset,reset_image = sprite_show("reset")
	screen.blit(reset_image,(x_reset,y_reset))
	x_reset,y_reset,resetP_image = sprite_show("reset_pressed")

#------------ Event checking

	for event in pygame.event.get():
		if event.type == QUIT:
			pygame.quit() # Opposite of pygame.init
			sys.exit() # Not including this line crashes the script on Windows. Possibly
			# on other operating systems too, but I don't know for sure.

		if event.type == MOUSEBUTTONDOWN and event.button == 1: 
			x,y = event.pos

		#------------ Error checking

			if menu_rect.collidepoint(x,y):
				#check that every tile has a valid path to the center tile
				for line in grid:
					for el in line:
						if el["status"] != -1:
							if not has_valid_path(line.index(el), grid.index(line), []):
								render_text("INVALID BOARD", 400, 300, color=(189, 60, 32), size=50, center=True)
								pygame.display.update()
								sleep(1)
								return
				
				#check that both players have at least one tile
				score = get_score()
				if score[0] == 0 or score[1] == 0:
					render_text("INVALID BOARD", 400, 300, color=(189, 60, 32), size=50, center=True)
					pygame.display.update()
					sleep(1)
					return
				
				save_board()

				draw()
				screen.blit(menuP_image,(x_menu,y_menu))
				pygame.display.flip()
				draw()
				pygame.time.wait(250) 
				screen.blit(menu_image,(x_menu,y_menu))
				pygame.display.flip()
				pygame.time.wait(350)  

				in_board_editor = False
				
				menu_sound = mixer.Sound('Sounds/menu_leave.mp3')
				menu_sound.set_volume(0.5)
				menu_sound.play()
				
				in_menu = True
				return
			
			if reset_rect.collidepoint(x,y):
				group.empty()

				screen.blit(resetP_image,(x_reset,y_reset))
				pygame.display.flip()
				pygame.time.wait(250) 
				screen.blit(reset_image,(x_reset,y_reset))
				pygame.display.flip()
				pygame.time.wait(350)  

				grid, group = create_board()
				reset_sound = mixer.Sound('Sounds/reset.wav')
				reset_sound.play()
				
				return

#------------  Board update

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

def game(cloneable, jumpable, selected_tile, current_player):
	"""
	list, list, Tile, int --> None
	Main game loop
	Is called continuously while in_game is True
	Handles both player and AI moves
	"""
	global in_game
	global in_menu
	
	screen.fill((44, 34, 46))
	#menu_rect = render_text("< MENU", 100, 550, color=(171, 148, 122), size=25)

	menu_rect,x_menu,y_menu,menu_image = sprite_show("menu")
	screen.blit(menu_image,(x_menu,y_menu))

	x_menu,y_menu,menuP_image = sprite_show("menu_pressed")

	if game_mode == 1:
		if current_player == 1:
			render_text(f"ORANGE'S TURN", 700, 50, color=(247,150,23), size=25, center=True)
		else:
			render_text(f"BLUE'S TURN", 700, 50, color=(77,155,230), size=25, center=True)
	
	# Go through events that are passed to the script by the window.
	for event in pygame.event.get():
		if event.type == QUIT:
			pygame.quit() # Opposite of pygame.init
			sys.exit() # Not including this line crashes the script on Windows. Possibly
			# on other operating systems too, but I don't know for sure.
	# Handle other events
		if game_mode == 1 or (game_mode != 1 and current_player == 1):
			if event.type == MOUSEBUTTONDOWN and event.button == 1: 

				x,y = event.pos
				if menu_rect.collidepoint(x,y):

					screen.blit(menuP_image,(x_menu,y_menu))
					draw()
					pygame.display.flip()
					pygame.time.wait(250) 
					screen.blit(menu_image,(x_menu,y_menu))
					pygame.display.flip()
					pygame.time.wait(350)  

					in_game = False
					
					menu_sound = mixer.Sound('Sounds/menu_leave.mp3')
					menu_sound.set_volume(0.5)
					menu_sound.play()
					
					in_menu = True

				for line in grid:
					for el in line:
						# if the game is in single player mode, or if it's the player's turn in 
							# if one of current_player's tiles was clicked, highlight possible moves
							if el["status"] == current_player:
								pos_in_mask = x - el["tile"].rect.x, y - el["tile"].rect.y # position of mouse in image mask
								if el["tile"].rect.collidepoint(x,y) and el["tile"].mask.get_at(pos_in_mask): # checks that the position of the mouse when clicked is in the rect and the mask of the image
									clear_outlines()
									cloneable = check_cloneable(line.index(el), grid.index(line), cloneable)
									jumpable = check_jumpable(line.index(el), grid.index(line), jumpable)
									selected_tile = el

								
							# if one of the currently highlighted tiles was clicked, do stuff
							elif el["outline"] == 1:
								pos_in_mask = x - el["tile"].rect.x, y - el["tile"].rect.y
								if el["tile"].rect.collidepoint(x,y) and el["tile"].mask.get_at(pos_in_mask): 
									el["status"] = current_player
									el["tile"].update(el)
									capture_sound = mixer.Sound('Sounds/capture.mp3')
									capture_sound.play()
									update_neighbours(line.index(el), grid.index(line), current_player)
									cloneable, jumpable, current_player = end_turn(cloneable, jumpable, current_player)
									return cloneable, jumpable, selected_tile, current_player
							
							elif el["outline"] == 2:
								pos_in_mask = x - el["tile"].rect.x, y - el["tile"].rect.y
								if el["tile"].rect.collidepoint(x,y) and el["tile"].mask.get_at(pos_in_mask): 
									el["status"] = current_player
									el["tile"].update(el)
									selected_tile["status"] = 0
									selected_tile["tile"].update(selected_tile)
									mouve_sound = mixer.Sound('Sounds/move-self.mp3')
									mouve_sound.play()
									update_neighbours(line.index(el), grid.index(line), current_player)
									cloneable, jumpable, current_player = end_turn(cloneable, jumpable, current_player)
									return cloneable, jumpable, selected_tile, current_player
								
	if current_player == 2 and game_mode != 1:
		if game_mode == 2:
			sleep(0.5)
			move = random_move(current_player)
			
		elif game_mode == 3:
			sleep(0.5)
			move = one_layer_best_move(current_player)
		
		elif game_mode == 4:
			move = bots.layer_bot.two_layer(grid)

		elif game_mode == 5:
			move = bots.mcts_bot.mcts(grid, total_tiles, num_iterations=50000, exploration_constant=1)

		bot_move(move)
		cloneable, jumpable, current_player = end_turn(cloneable, jumpable, current_player)
						
	return cloneable, jumpable, selected_tile, current_player
					


def draw_outlines(cloneable, jumpable):
	"""
	list, list --> None
	Rendres the outlines of the cloneable and jumpable tiles
	"""
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

def draw():
	"""
	Render all the tiles and the score
	"""
	global in_game
	global in_board_editor
	global in_menu
	group.draw(screen) # draw tile sprites from the Tile class
	if in_game:
		#render_text(f"RED: {score[0]}", 93, 50, color=(189, 60, 32), size=25)
		#render_text(f"BLUE: {score[1]}", 100, 100, color=(80, 138, 169), size=25)
		display_scores(score)


def render_text(text, x, y, color=(0, 0, 0), size=32, border=False, center=False):
	'''
	str, int, int, tuple, int, bool --> pygame.Rect
	Renders text at a given position with a given color and size on the pygame screen
	'''
	font = pygame.font.Font('Fonts/pixeboy-font/Pixeboy-z8XGD.ttf', size)
	text = font.render(text, True, color)
	if center == True:
		textRect = text.get_rect(center=(x,y))
	elif center == False:
		textRect = text.get_rect(topleft=(x,y))
	#draw a box around text if the border option is set to True
	if border:
		pygame.draw.rect(screen, (0, 0, 0), (textRect.x-5, textRect.y-5, textRect.width+10, textRect.height+10), 5)
	screen.blit(text, textRect)
	return textRect
	
def menu():
	"""
	None --> None
	Renders the menu screen
	"""
	global in_board_editor
	global in_game
	global in_info
	global in_menu
	global game_mode
	global group_volume
	global volume_button

#------------ Rendering

	screen.fill((44, 34, 46))
	render_text("PyHexx", 400, 100, color=(201, 166, 131), size=75, center=True)
	
	info_rect,x_info,y_info,info_image = sprite_show("info")
	screen.blit(info_image,(x_info,y_info))
	x_info,y_info,infoP_image = sprite_show("info_pressed")

	play_rect,x_play,y_play,play_image = sprite_show("play")
	screen.blit(play_image,(x_play,y_play))
	x_play,y_play,playP_image = sprite_show("play_pressed")

	board_rect,x_board,y_board,board_image = sprite_show("BE")
	screen.blit(board_image,(x_board,y_board))	

	render_text("BOARD EDITOR", 335, 519, color=(44, 34, 46), size=25)
	board_rect = render_text("BOARD EDITOR", 337, 517, color=(171, 148, 122), size=25)

	gm_x, gm_y = 405,280
	if game_mode == 1:
		game_mode_rect = render_text("GAME MODE (player)", gm_x, gm_y, color=(171, 148, 122), size=25, center=True)
	elif game_mode == 2:
		game_mode_rect = render_text("GAME MODE (random)", gm_x, gm_y, color=(171, 148, 122), size=25, center=True)
	elif game_mode == 3:
		game_mode_rect = render_text("GAME MODE (easy)", gm_x, gm_y, color=(171, 148, 122), size=25, center=True)
	elif game_mode == 4:
		game_mode_rect = render_text("GAME MODE (normal)", gm_x, gm_y, color=(171, 148, 122), size=25, center=True)
	elif game_mode == 5:
		game_mode_rect = render_text("GAME MODE (mcts)", gm_x, gm_y, color=(171, 148, 122), size=25, center=True)

#------------ Event checking
	
	for event in pygame.event.get():
		if event.type == QUIT:
			pygame.quit() # Opposite of pygame.init
			sys.exit()
		if event.type == MOUSEBUTTONDOWN and event.button == 1:
			x,y = event.pos
			if volume_button.rect.collidepoint(x,y):
				volume_button.Vupdate()
			if play_rect.collidepoint(x,y):

				screen.blit(playP_image,(x_play,y_play))
				group_volume.draw(screen)
				pygame.display.flip()
				pygame.time.wait(250) 
				screen.blit(play_image,(x_play,y_play))
				group_volume.draw(screen)
				pygame.display.flip()
				pygame.time.wait(350)  

				in_menu = False
				in_game = True
			elif info_rect.collidepoint(x,y):

				screen.blit(infoP_image,(x_info,y_info))
				group_volume.draw(screen)
				pygame.display.flip()
				pygame.time.wait(250) 
				screen.blit(info_image,(x_info,y_info))
				group_volume.draw(screen)
				pygame.display.flip()
				pygame.time.wait(350)  

				in_menu = False
				in_info = True
			elif board_rect.collidepoint(x,y):
				in_menu = False
				in_board_editor = True
			elif game_mode_rect.collidepoint(x,y):
				if game_mode == 5:
					game_mode = 1
				else:
					game_mode += 1

def info():
	"""
	None --> None
	Renders the info screen
	"""
	
	global in_info
	global in_menu

	screen.fill((44, 34, 46))
#	menu_rect = render_text("< MENU", 700, 550, color=(201, 166, 131), size=25)

	menu_rect,x_menu,y_menu,menu_image = sprite_show("menu")
	screen.blit(menu_image,(x_menu,y_menu))

	x_menu,y_menu,menuP_image = sprite_show("menu_pressed")

	render_text("Instructions", 400, 100, color=(201, 166, 131), size=50, center=True) #MAIN TITLE
	render_text("GAMEPLAY", 80, 150, color=(158, 107, 58), size=20) #SUBTITILE
	render_text("PyHexx is a strategy game board where the goal is to cover as many spaces of the board ", 50, 175, color=(171, 148, 122), size=15) # +15 pixels per line
	render_text("with your color as possible. This is done by cloning, jumping, and converting your opponents tiles.", 50, 190, color=(171, 148, 122), size=15) # +40 per paragraph
	render_text("MOVEMENT", 80, 230, color=(158, 107, 58), size=20) # +25 per title and paragraph
	render_text("When it is your turn to move, simply select the tile that you wish to move by clicking on it.", 50, 255, color=(171, 148, 122), size=15)
	render_text("This will let you move one space in any direction or jump two spaces in any direction (as long ", 50, 270, color=(171, 148, 122), size=15)
	render_text("as that cell is empty). A player must make a move if one is available. Once a piece is ", 50, 285, color=(171, 148, 122), size=15)
	render_text("selected, you may choose from different options:", 50, 300, color=(171, 148, 122), size=15)
	render_text(" - If you move 1 space, you clone the piece", 75, 325, color=(171, 148, 122), size=15)
	render_text(" - If you jump 2 spaces, you move the piece", 75, 340, color=(171, 148, 122), size=15)
	render_text("CAPTURING PIECES", 80, 375, color=(158, 107, 58), size=20)
	render_text("After a player captures an empty space, any opponent pieces that are adjacent to that new", 50, 400, color=(171, 148, 122), size=15)
	render_text("location will also be captured (converted to your color).", 50, 415, color=(171, 148, 122), size=15)
	render_text("WINNING", 80, 455, color=(158, 107, 58), size=20)
	render_text("The game ends when there are no empty spaces or one player cannot move. If a player ", 50, 480, color=(171, 148, 122), size=15)
	render_text("cannot move, the remaining empty spaces are captured by the other player and the game ", 50, 495, color=(171, 148, 122), size=15)
	render_text("ends. The player with the majority of tiles on the board wins: 1 tile = 1 point", 50, 510, color=(171, 148, 122), size=15)

	for event in pygame.event.get():
		if event.type == QUIT:
			pygame.quit() # Opposite of pygame.init
			sys.exit() # Not including this line crashes the script on Windows. Possibly
		if event.type == MOUSEBUTTONDOWN and event.button == 1: 
			x,y = event.pos
			if menu_rect.collidepoint(x,y):

				screen.blit(menuP_image,(x_menu,y_menu))
				pygame.display.flip()
				pygame.time.wait(250) 
				screen.blit(menu_image,(x_menu,y_menu))
				pygame.display.flip()
				pygame.time.wait(350)  

				in_info = False
				
				menu_sound = mixer.Sound('Sounds/menu_leave.mp3')
				menu_sound.set_volume(0.5)
				menu_sound.play()

				in_menu = True


def sprite_show(sprite):
	'''	
	str --> rect,int,int,surface

	Function that helps with dispaying and organising sprite buttons
	'''
	if sprite == 'info' or sprite == 'info_pressed':
		x = 410
		y = 190
		if sprite == 'info':
			img = pygame.image.load('Sprites/IMG_B.PNG')
			rect = pygame.Rect(x, y, img.get_width(), img.get_height())
			return rect,x,y,img
		else:
			img = pygame.image.load('Sprites/IMG_A.PNG')
		return x,y,img

	if sprite == 'play' or sprite == 'play_pressed':
		x = 280
		y = 190
		if sprite == 'play':
			img = pygame.image.load('Sprites/IMG_2.PNG')
			rect = pygame.Rect(x, y, img.get_width(), img.get_height())
			return rect,x,y,img
		else:
			img = pygame.image.load('Sprites/IMG_1.PNG')
		return x,y,img

	if sprite == 'menu' or sprite == 'menu_pressed':
		x = 625
		y = 500
		if sprite == 'menu':
			img = pygame.image.load('Sprites/menu.PNG')
			rect = pygame.Rect(x, y, img.get_width(), img.get_height())
			return rect,x,y,img
		else:
			img = pygame.image.load('Sprites/menu-p.PNG')
		return x,y,img

	if sprite == 'reset' or sprite == 'reset_pressed':
		x = 75
		y = 500
		if sprite == 'reset':
			img = pygame.image.load('Sprites/reset.PNG')
			rect = pygame.Rect(x, y, img.get_width(), img.get_height())
			return rect,x,y,img
		else:
			img = pygame.image.load('Sprites/reset-p.PNG')
		return x,y,img

	if sprite == 'BE':
		img = pygame.image.load('Sprites/boardedit.PNG')
		x = 300
		y = 490
		rect = pygame.Rect(x, y, img.get_width(), img.get_height())
		return rect,x,y,img	

def main():
	"""
	None --> None
	Initialise important variables and triggers the launch of the menu screen
	"""
	icon = pygame.image.load("Sprites/red.png")
	
	pygame.init()
	pygame.display.set_caption("PyHexx")
	pygame.display.set_icon(icon)
	
	global group_volume # Volume button group
	global volume_button
	
	global group #pygame.sprite.Group object, contains all active tiles
	global grid
	global total_tiles

	# neighboring tile deltas [x, y], these are added to a tiles coordinates to find its neighbors, these will not be modified in the program
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

	global game_mode
	# 1 = 2 players, 2 = random bot, 3 = best move bot, 4 = MCTS bot
	game_mode = 1
	
	# Music
	mixer.music.load('Sounds/menu_music.mp3')
	mixer.music.play(-1)
	mixer.music.set_volume(0.5)
	mixer.music.pause()

	# Volume button
	group_volume = pygame.sprite.RenderPlain()
	volume_button = Volume()  
	group_volume.add(volume_button)


	grid, group = create_board()
	save_board()
	
	while True:
		
		if in_menu: #MENU
			mixer.music.unpause()
			
			while in_menu:
				menu()
				group_volume.draw(screen)
				pygame.display.flip()

		elif in_board_editor: #BOARD EDITOR
			# mixer.music.pause()
			load_board()

			while in_board_editor:
				board_editor()
				draw()
				pygame.display.flip()

		elif in_game: #MAIN GAMW LOOP
			
			# mixer.music.pause()
			play_sound = mixer.Sound('Sounds/game_init.mp3')
			play_sound.set_volume(0.5)
			play_sound.play()
			
			load_board()
			current_player = 1
			selected_tile = None
			global score
			score = get_score()
			cloneable = []
			jumpable = []
			total_tiles = get_total_tiles()

			while in_game:
				cloneable, jumpable, selected_tile, current_player = game(cloneable, jumpable, selected_tile, current_player) 
				draw()
				draw_outlines(cloneable, jumpable)
				pygame.display.flip()

		elif in_info: #INFO SCREEN --> game rules, credits, NOT IMPLEMENTED, crashes the game currently
			# mixer.music.pause()
			
			while in_info:
				info()
				pygame.display.flip()



if __name__ == "__main__":
	main()