import random
from copy import deepcopy
import time

global even_n1
global odd_n1
even_n1 = [[0, -1], [-1, 0], [1, 0], [-1, 1], [0, 1], [1, 1]]
odd_n1 = [[0, 1], [0, -1], [-1, 0], [1, 0], [-1, -1], [1, -1]]

global even_n2
global odd_n2
even_n2 = [[0, -2], [-1, -1], [1, -1], [-2, -1], [2, -1], [-2, 0], [2, 0], [-2, 1], [-1, 2], [0, 2], [1, 2], [2, 1]]
odd_n2 = [[0, 2], [-1, 1], [1, 1], [-2, 1], [2, 1], [-2, 0], [2, 0], [-2, -1], [-1, -2], [0, -2], [1, -2], [2, -1]]

global total_tiles
total_tiles = 58 # unsure if this is correct

class Node:
	"""
	A node in the game tree, represents a complete board state with the player who's turn it is to move, 
	the move that led to this state, the parent node and the children nodes, the score for the node's grid
	"""
	def __init__(self, grid, player, move=None, parent=None, score=None):
		self.player = player  # The player who's turn it is to move at this node
		self.score = score  # The score for the node's grid
		self.move = move  # The move that got us to this node - "None" for the root node
		self.parent = parent  # The parent node of this node
		self.children = []  # The children nodes of this node
		self.grid = grid  # The grid of the game at this node

def two_layer(tiled_grid):
	"""
	This is an evolution of the one_layer bot, it uses a two layer search to find the best move.
	First, all the possible moves and then for each move, the opponents one layer "best" response is played out.
	Then, the score is calculated and the node with the best score is picked
	Finally, we can go back up the tree to the root node and pick the move that eventually led to that best score
	"""
	#clock to measure execution time for debug purposes
	#start_time = time.time()
	
	#cleaned_grid = deepcopy(tiled_grid) - for debug purposes
	cleaned_grid = []
	for line in tiled_grid:
		cleaned_grid.append([])
		for el in line:
			tile = el["tile"]
			del el["tile"]
			cleaned_grid[-1].append(deepcopy(el))
			el["tile"] = tile

	def get_moves(grid, current_player):
		"""
		Get all the untried moves from the current state
		"""
		possible_moves = []
		for line in grid:
			for el in line:
				if el["status"] == current_player:
					x, y = line.index(el), grid.index(line)
					for el in even_n1 if x % 2 == 0 else odd_n1:
						try: 
							if grid[y + el[1]][x + el[0]]["status"] == 0 and (0 <= (y + el[1]) <= 8) and (0 <= (x + el[0]) <= 8):
								possible_moves.append([1, x, y, x + el[0], y + el[1]]) #1 = clone, x, y coords of selected tile,  x + el[0], y + el[1] coords of cloned to tile
						except IndexError:
							pass
					for el in even_n2 if x % 2 == 0 else odd_n2:
						try: 
							if grid[y + el[1]][x + el[0]]["status"] == 0 and (0 <= (y + el[1]) <= 8) and (0 <= (x + el[0]) <= 8):
								possible_moves.append([2, x, y, x + el[0], y + el[1]]) #2 = jump, x, y coords of selected tile,  x + el[0], y + el[1] coords of jumped to tile
						except IndexError:
							pass
		return possible_moves

	def get_score(grid):
		"""
		Get the score for the current grid, same as the main game's score system
		"""
		score = [0, 0]
		for line in grid:
			for el in line:
				if el["status"] == 1 or el["status"] == 2:
					score[el["status"] - 1] += 1
		return score


	def add_child(node, move):
		"""
		add a child node to the current node 
		with the given move, calculated score, parent node, player, and the copy of the board with the played move that was generated
		"""
		grid = apply_move(node.grid, move, node.player)
		child = Node(grid, abs(node.player - 3), move=move, parent=node, score=get_score(grid))
		node.children.append(child)
	
	def apply_move(grid, move, current_player):
		"""
		apply the given move to the given grid, return the new grid
		"""

		new_grid = deepcopy(grid)
		def update_neighbours(x, y, current_player):
			"""
			update the neighbours of the given tile with the given player
			"""
			for el in even_n1 if x % 2 == 0 else odd_n1:
				try: 
					if new_grid[y + el[1]][x + el[0]]["status"] == abs(current_player - 3) and (0 <= (y + el[1]) <= 8) and (0 <= (x + el[0]) <= 8):
						new_grid[y + el[1]][x + el[0]]["status"] = current_player
				except IndexError: # if the tile is out of bounds
					pass

		if move[0] == 1:
			new_grid[move[4]][move[3]]["status"] = current_player
			update_neighbours(move[3], move[4], current_player)
		elif move[0] == 2:
			new_grid[move[2]][move[1]]["status"] = 0
			new_grid[move[4]][move[3]]["status"] = current_player
			update_neighbours(move[3], move[4], current_player)

		return new_grid

	def get_best_move(grid, player, moves):
		"""
		Get the best move from the given list of moves using the 1 layer greedy algorithm
		"""
		for move in moves:
			score = 0
			if move[0] == 1:
				score += 1

			for el in even_n1 if move[3] % 2 == 0 else odd_n1:
				try: 
					if grid[move[4] + el[1]][move[3] + el[0]]["status"] == abs(player - 3) and (0 <= (move[4] + el[1]) <= 8) and (0 <= (move[3] + el[0]) <= 8):
						score += 1
				except IndexError:
					pass
			move.append(score)
		moves.sort(key=lambda x: int(x[5]), reverse=True)
		best_moves = [[el for el in moves if el == moves[0]]]
		return random.choice(best_moves)

	root_node = Node(cleaned_grid, 2, score=get_score(cleaned_grid))  # Start from the root state
	available_moves = get_moves(root_node.grid, 2) #1 layer all moves
	for move in available_moves:
		add_child(root_node, move) 
		for node in root_node.children:
			available_opp_moves = get_moves(node.grid, 1) #all possible opponent moves to answer all the moves we could have made
			if available_opp_moves:
				best_moves = get_best_move(node.grid, 1, available_opp_moves) #answers with the "best" (1 layer) opponent move
				add_child(node, random.choice(best_moves))
				"""
				# this part was used to test a potential 3 layer algorithm, unfortunately, runtime was far too long
				for node2 in node.children:
					available_moves = get_moves(node2.grid, 2)
					for move in available_moves:
						add_child(node2, move)
				"""

	best_score = float('-inf')
	for node in root_node.children:
		for child in node.children:
			#for child2 in child.children:
			score = child.score[1]
			if score > best_score:
				best_score = score
				#best_node = child


	best_nodes = []
	for node in root_node.children:
		for child in node.children:
			if child.score[1] == best_score:
				best_nodes.append(child)

	best_node = random.choice(best_nodes)
	
	while best_node.parent != None:
		prev = best_node
		best_node = best_node.parent
	
	best_node = prev
	
	
	#print execution time - for debugging
	#print("--- %s seconds ---" % (time.time() - start_time))

	return best_node.move


# following code is used to test the algorithm during development
#board = [[{'x': 225, 'y': 73, 'status': -1, 'outline': 0}, {'x': 263, 'y': 50, 'status': -1, 'outline': 0}, {'x': 301, 'y': 73, 'status': -1, 'outline': 0}, {'x': 339, 'y': 50, 'status': -1, 'outline': 0}, {'x': 377, 'y': 73, 'status': 2, 'outline': 0}, {'x': 415, 'y': 50, 'status': -1, 'outline': 0}, {'x': 453, 'y': 73, 'status': -1, 'outline': 0}, {'x': 491, 'y': 50, 'status': -1, 'outline': 0}, {'x': 529, 'y': 73, 'status': -1, 'outline': 0}], [{'x': 225, 'y': 118, 'status': -1, 'outline': 0}, {'x': 263, 'y': 95, 'status': -1, 'outline': 0}, {'x': 301, 'y': 118, 'status': 0, 'outline': 0}, {'x': 339, 'y': 95, 'status': 0, 'outline': 0}, {'x': 377, 'y': 118, 'status': 0, 'outline': 0}, {'x': 415, 'y': 95, 'status': 0, 'outline': 0}, {'x': 453, 'y': 118, 'status': 0, 'outline': 0}, {'x': 491, 'y': 95, 'status': -1, 'outline': 0}, {'x': 529, 'y': 118, 'status': -1, 'outline': 0}], [{'x': 225, 'y': 163, 'status': 1, 'outline': 0}, {'x': 263, 'y': 140, 'status': 0, 'outline': 0}, {'x': 301, 'y': 163, 'status': 0, 'outline': 0}, {'x': 339, 'y': 140, 'status': 0, 'outline': 0}, {'x': 377, 'y': 163, 'status': 0, 'outline': 0}, {'x': 415, 'y': 140, 'status': 0, 'outline': 0}, {'x': 453, 'y': 163, 'status': 0, 'outline': 0}, {'x': 491, 'y': 140, 'status': 0, 'outline': 0}, {'x': 529, 'y': 163, 'status': 1, 'outline': 0}], [{'x': 225, 'y': 208, 'status': 0, 'outline': 0}, {'x': 263, 'y': 185, 'status': 0, 'outline': 0}, {'x': 301, 'y': 208, 'status': 0, 'outline': 0}, {'x': 339, 'y': 185, 'status': 0, 'outline': 0}, {'x': 377, 'y': 208, 'status': -1, 'outline': 0}, {'x': 415, 'y': 185, 'status': 0, 'outline': 0}, {'x': 453, 'y': 208, 'status': 0, 'outline': 0}, {'x': 491, 'y': 185, 'status': 0, 'outline': 0}, {'x': 529, 'y': 208, 'status': 0, 'outline': 0}], [{'x': 225, 'y': 253, 'status': 0, 'outline': 0}, {'x': 263, 'y': 230, 'status': 0, 'outline': 0}, {'x': 301, 'y': 253, 'status': 0, 'outline': 0}, {'x': 339, 'y': 230, 'status': 0, 'outline': 0}, {'x': 377, 'y': 253, 'status': 0, 'outline': 0}, {'x': 415, 'y': 230, 'status': 0, 'outline': 0}, {'x': 453, 'y': 253, 'status': 0, 'outline': 0}, {'x': 491, 'y': 230, 'status': 0, 'outline': 0}, {'x': 529, 'y': 253, 'status': 0, 'outline': 0}], [{'x': 225, 'y': 298, 'status': 0, 'outline': 0}, {'x': 263, 'y': 275, 'status': 0, 'outline': 0}, {'x': 301, 'y': 298, 'status': 0, 'outline': 0}, {'x': 339, 'y': 275, 'status': -1, 'outline': 0}, {'x': 377, 'y': 298, 'status': 0, 'outline': 0}, {'x': 415, 'y': 275, 'status': -1, 'outline': 0}, {'x': 453, 'y': 298, 'status': 0, 'outline': 0}, {'x': 491, 'y': 275, 'status': 0, 'outline': 0}, {'x': 529, 'y': 298, 'status': 0, 'outline': 0}], [{'x': 225, 'y': 343, 'status': 2, 'outline': 0}, {'x': 263, 'y': 320, 'status': 0, 'outline': 0}, {'x': 301, 'y': 343, 'status': 0, 'outline': 0}, {'x': 339, 'y': 320, 'status': 0, 'outline': 0}, {'x': 377, 'y': 343, 'status': 0, 'outline': 0}, {'x': 415, 'y': 320, 'status': 0, 'outline': 0}, {'x': 453, 'y': 343, 'status': 0, 'outline': 0}, {'x': 491, 'y': 320, 'status': 0, 'outline': 0}, {'x': 529, 'y': 343, 'status': 2, 'outline': 0}], [{'x': 225, 'y': 388, 'status': -1, 'outline': 0}, {'x': 263, 'y': 365, 'status': 0, 'outline': 0}, {'x': 301, 'y': 388, 'status': 0, 'outline': 0}, {'x': 339, 'y': 365, 'status': 0, 'outline': 0}, {'x': 377, 'y': 388, 'status': 0, 'outline': 0}, {'x': 415, 'y': 365, 'status': 0, 'outline': 0}, {'x': 453, 'y': 388, 'status': 0, 'outline': 0}, {'x': 491, 'y': 365, 'status': 0, 'outline': 0}, {'x': 529, 'y': 388, 'status': -1, 'outline': 0}], [{'x': 225, 'y': 433, 'status': -1, 'outline': 0}, {'x': 263, 'y': 410, 'status': -1, 'outline': 0}, {'x': 301, 'y': 433, 'status': -1, 'outline': 0}, {'x': 339, 'y': 410, 'status': 0, 'outline': 0}, {'x': 377, 'y': 433, 'status': 1, 'outline': 0}, {'x': 415, 'y': 410, 'status': 0, 'outline': 0}, {'x': 453, 'y': 433, 'status': -1, 'outline': 0}, {'x': 491, 'y': 410, 'status': -1, 'outline': 0}, {'x': 529, 'y': 433, 'status': -1, 'outline': 0}]]
#print(two_layer(board))