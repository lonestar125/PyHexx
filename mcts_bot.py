import random
import math
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
	A node in the game tree.
	wins arw always from the viewpoint of player 2.
	"""
	def __init__(self, grid, player, explored_moves, move=None, parent=None):
		self.explored_moves = explored_moves  # The moves that have been explored from this node
		self.move = move  # The move that got us to this node - "None" for the root node
		self.player = player  # The player who made the move to reach this node
		self.parent = parent  # The parent node of this node
		self.children = []  # The children nodes of this node
		self.wins = 0  # The number of wins from simulations for this node
		self.visits = 0  # The number of visits to this node
		self.grid = grid  # The state of the game at this node
		

	def ucb_score(self, exploration_constant):
		"""
		Calculate the Upper Confidence Bound (UCB) score for this node.
		"""
		if self.visits == 0:
			return float('inf')  # Return infinity if the node has not been visited yet
		exploitation = self.wins / self.visits
		exploration = exploration_constant * math.sqrt(math.log(self.parent.visits) / self.visits)
		return exploitation + exploration

def mcts(tiled_grid, total_tiles, num_iterations=1000, exploration_constant=1):
	"""
	Run num_iterations of the Monte Carlo Tree Search algorithm starting to try and predict the best move for the bot
	This was in theory supposed to be the best and most complexe bot.
	Unfortunately, to get good results, it needs to run millions of iterations, which can easily take over 10 minutes or more
	so it is not really usable in a game as it is called everytime the bot needs to make a move
	This could potentially be improved by implementing a neural network to save results between games and therefore would not have to run iterations in real time
	but we do not possess the necessary time or resources to develop and train such a network
	"""

	#start_time = time.time() - for debugging

	cleaned_grid = []
	for line in tiled_grid:
		cleaned_grid.append([])
		for el in line:
			tile = el["tile"]
			del el["tile"]
			cleaned_grid[-1].append(deepcopy(el))
			el["tile"] = tile

	def get_untried_moves(grid, current_player, explored_moves):
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
						except IndexError: # if the tile is out of bounds
							pass
					for el in even_n2 if x % 2 == 0 else odd_n2:
						try: 
							if grid[y + el[1]][x + el[0]]["status"] == 0 and (0 <= (y + el[1]) <= 8) and (0 <= (x + el[0]) <= 8):
								possible_moves.append([2, x, y, x + el[0], y + el[1]]) #2 = jump, x, y coords of selected tile,  x + el[0], y + el[1] coords of jumped to tile
						except IndexError: # if the tile is out of bounds
							pass
		untried_moves = []
		for move in possible_moves:
			if move not in explored_moves:
				untried_moves.append(move)

		return untried_moves


	def add_child(node, move):
		"""
		Add a child node to the current node with the given move.
		"""
		grid = apply_move(node.grid, move, node.player)
		opponent = abs(node.player - 3)
		child = Node(grid, opponent, [], move=move, parent=node)
		node.children.append(child)

	
	
	def apply_move(grid, move, current_player):
		"""
		apply the given move to the given grid, return the new grid
		"""

		def update_neighbours(x, y, current_player):
			"""
			update the neighbours of the given tile with the given player
			"""
			for el in even_n1 if x % 2 == 0 else odd_n1:
				try: 
					if grid[y + el[1]][x + el[0]]["status"] == abs(current_player - 3) and (0 <= (y + el[1]) <= 8) and (0 <= (x + el[0]) <= 8):
						grid[y + el[1]][x + el[0]]["status"] = current_player
				except IndexError: # if the tile is out of bounds
					pass

		if move[0] == 1:
			grid[move[4]][move[3]]["status"] = current_player
			update_neighbours(move[3], move[4], current_player)
		elif move[0] == 2:
			grid[move[2]][move[1]]["status"] = 0
			grid[move[4]][move[3]]["status"] = current_player
			update_neighbours(move[3], move[4], current_player)

		return grid



	def simulate(node):
		"""
		Simulate a random game from the current node and return the result.
		"""
		current_player = deepcopy(node.player)
		simulated_grid = deepcopy(node.grid)
		#print(simulated_grid)

		def get_score(grid):
			score = [0, 0]
			for line in grid:
				for el in line:
					if el["status"] >= 1: #if tile status is 1 or 2
						score[el["status"] - 1] += 1
			return score

		def check_victory(score):
			"""
			check if the game is over and return the winner, same as in the main game
			"""
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

		over = False
		# Perform random playout until the game is over
		moves_played = 0
		while not over:
			# Get a list of valid moves for the current player
			moves = []
			for line in simulated_grid:
				for el in line:
					if el["status"] == current_player:
						x, y = line.index(el), simulated_grid.index(line)
						for el in even_n1 if x % 2 == 0 else odd_n1:
							try: 
								if simulated_grid[y + el[1]][x + el[0]]["status"] == 0 and (0 <= (y + el[1]) <= 8) and (0 <= (x + el[0]) <= 8):
									moves.append([1, x, y, x + el[0], y + el[1]]) #1 = clone, x, y coords of selected tile,  x + el[0], y + el[1] coords of cloned to tile
							except IndexError:  # if the tile is out of bounds
								pass
						for el in even_n2 if x % 2 == 0 else odd_n2:
							try: 
								if simulated_grid[y + el[1]][x + el[0]]["status"] == 0 and (0 <= (y + el[1]) <= 8) and (0 <= (x + el[0]) <= 8):
									moves.append([2, x, y, x + el[0], y + el[1]]) #2 = jump, x, y coords of selected tile,  x + el[0], y + el[1] coords of jumped to tile
							except IndexError:  # if the tile is out of bounds
								pass
			#print(moves)
			if moves == []:
				# no moves left, determine winner
				for line in simulated_grid:
					for el in line:
						if el['status'] == 0:
							el['status'] = abs(current_player - 3)
				score = get_score(simulated_grid)
				winner = check_victory(score)
				over = True

			# Choose a random move from the list of valid moves
			else:
				"""
				#this code was used when testing a version of the MCTS bot that used the 
				one layer best move algorithm during simulation instead of the random move algorithm,
				which is what the current version uses, unfortunately, this did not seem to greatly improve resultas and mostly made the algorithm slower

				for move in moves:
					score = 0
					if move[0] == 1:
						score += 1

					for el in even_n1 if move[3] % 2 == 0 else odd_n1:
						try: 
							if simulated_grid[move[4] + el[1]][move[3] + el[0]]["status"] == abs(current_player - 3) and (0 <= (move[4] + el[1]) <= 8) and (0 <= (move[3] + el[0]) <= 8):
								score += 1
						except IndexError: # if the tile is out of bounds
							pass
					move.append(score)
				

				moves.sort(key=lambda x: int(x[5]), reverse=True)
				best_moves = [el for el in moves if el == moves[0]]
				"""
				move = random.choice(moves)
				moves_played +=1
				

				# Apply the chosen move to the current grid
				simulated_grid = apply_move(simulated_grid, move, current_player)
				# Switch to the other player's turn
				current_player = abs(current_player - 3)

		# Update the wins count of the nodes along the path
		#print(moves_played)
		node.wins += 1 if winner == node.player else 0
		return winner

	root_node = Node(cleaned_grid, 2, [])  # Start from the root state
	available_moves = get_untried_moves(root_node.grid, 2, root_node.explored_moves)
	for move in available_moves:
		add_child(root_node, move)

	for _ in range(num_iterations):
		
		# Selection: Choose the best child node until we reach a leaf node
		node = root_node
		while node.children:
			best_child = None
			best_score = float("-inf")
			for child in node.children:
				score = child.ucb_score(exploration_constant)
				if score > best_score:
					best_score = score
					best_child = child
			node = best_child

		# Expansion: If the leaf node is not fully expanded, expand it by adding a child node
		untried_moves = get_untried_moves(node.grid, 2, node.explored_moves)
		if untried_moves:
			move = random.choice(untried_moves)
			add_child(node, move)
			node.explored_moves.append(move)
			node = node.children[-1]
			

		# Simulation: Simulate a random game from the leaf node
		result = simulate(node)

		# Backpropagation: Update the visits and wins count from the leaf node up to the root node
		while node is not None:
			node.visits += 1
			if node.player == result:
				node.wins += 1
			node = node.parent

	# Choose the best move from the root node
	best_move = None
	best_score = float("-inf")
	for child in root_node.children:
		score = child.wins / child.visits
		if score > best_score:
			best_score = score
			best_move = child.move

	#print("--- %s seconds ---" % (time.time() - start_time)) - for debbugging
	return best_move