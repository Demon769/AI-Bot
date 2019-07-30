import sys
import random
import signal
import time
import copy
from random import randint

class Player58:
	def __init__(self):
		self.pos_weight = ((3,2,3),(2,4,2),(3,2,3)) # weight of winning position[i][j]
		self.infinity = 99999999
		self.ninfinity = -99999999
		self.next_move = (0, 0)
		self.symbol = 'x'
		self.value = [1 , 10 , 100 , 1000]
		self.blockHeuriStore = {} 
		self.boardHeuriStore = {}
		self.blockPoints = 30
		patterns = []
		# diagonal patterns
		# for i in xrange(1,3):
		patterns.append(((0,0) , (1,1) , (2,2)))
		patterns.append(((0,2) , (1,1) , (2,0)))

		#straight line patterns
		for i in xrange(3):
			row_array = [] # i'th row
			col_array = [] # i'th column
			for j in xrange(3):
				row_array.append((i,j))
				col_array.append((j,i))
			patterns.append(tuple(row_array))
			patterns.append(tuple(col_array))
		# for i in xrange(3):
		# 	row_array = [] # i'th row
		# 	for j in xrange(3):
		# 		row_array.append((i,j))
		# 	patterns.append(tuple(row_array))
		# for j in xrange(3):
		# 	col_array = [] # i'th column
		# 	for i in xrange(3):
		# 		col_array.append((i,j))
		# patterns.append(tuple(row_array))

		self.patterns = patterns
		print self.patterns

	def board_heuristic(self, blockHeurs):
		boardHeur = 0
		for i in xrange(3):
			for j in xrange(3):
				if blockHeurs[i][j] > 0:
					boardHeur += 0.02 * self.pos_weight[i][j] * blockHeurs[i][j]
		return boardHeur

	def board_pattern_checker(self, pos_arr, blockHeurs):
		playerCount = 0
		patternHeur = 0

		for pos in pos_arr:
			val = blockHeurs[pos[0]][pos[1]]
			patternHeur += val
			if val < 0:
				return 0
			elif val == self.blockPoints:
				playerCount+=1
			multiplier=1
		# if playerCount == 1:	
		# 	multiplier = 1.1
		if playerCount == 2:
			multiplier = 4
		elif playerCount == 3:
			multiplier = 50
		# elif playerCount == 4:
			# multiplier = 50

		return multiplier * patternHeur

	def block_heuristic(self, flag, block):
		# Not just the places of flags, but also their relative position contributes to heuristic
		blockHeur = 0

		for pos_arr in self.patterns:
			blockHeur += self.pattern_checker(flag,block,pos_arr)

		# Finally, contribution of place (for settling tie-breakers, etc)
		for i in xrange(3):
			for j in xrange(3):
				if block[i][j] == flag:
					blockHeur += 0.1 * self.pos_weight[i][j]
		return blockHeur


	def pattern_checker(self, flag, block, pos_array):
		playerCount = 0
		for pos in pos_array:
			if block[pos[0]][pos[1]] == flag:
				playerCount += 1
			elif block[pos[0]][pos[1]] == self.oppFlag(flag):
				return 0
		# if playerCount == 1:
		# 	return 3
		if playerCount == 2:
			# 2/4 of pattern complete. 3 points awarded for this
			return 8
		# elif playerCount == 3:
			# 3/4 of pattern complete. 3 points awarded for this
			# return 11
		return 0
	
	def oppFlag(self, flag):
		# NOT operation on flag
		return 'o' if flag == 'x' else 'x'

	def heuristic(self, flag, board):

		total = 0
		for k in range(2):
			blocks = board.small_boards_status[k]
			b = board.big_boards_status[k]
			blockHeurs = [[0,0,0],[0,0,0],[0,0,0]]

			for i in xrange(3):
				for j in xrange(3):
					if blocks[i][j]==flag:
						blockHeurs[i][j] = self.blockPoints
					elif blocks[i][j]==self.oppFlag(flag) or blocks[i][j]=='d':
						blockHeurs[i][j] = -1
					else:
						  block = tuple([tuple(b[3*i + x][3*j:3*(j+1)]) for x in xrange(3)])
						# if (self.blockHash[i][j],flag) in self.blockHeuriStore:
						# 	blockHeurs[i][j] = self.blockHeuriStore[(self.blockHash[i][j],flag)]
						# else:
						  blockHeurs[i][j] = self.block_heuristic(flag,block)
						# self.blockHeuriStore[(self.blockHash[i][j],flag)] = blockHeurs[i][j]

			for pos_arr in self.patterns:
				total += self.board_pattern_checker(pos_arr,blockHeurs)

			total += self.board_heuristic(blockHeurs)

		return total
	
	def move(self, board, old_move, flag):
		self.symbol = flag
		utility = self.minimax_search(board, old_move, 0, self.ninfinity, self.infinity, True, flag)
		return (self.next_move[0], self.next_move[1], self.next_move[2])

	def minimax_search(self, board, old_move, depth, alpha, beta, max_player, flag):
		status = board.find_terminal_state();
		if depth == 3 or status[0] != 'CONTINUE':
			return ( self.heuristic(flag,board) - self.heuristic(self.oppFlag(flag),board) )

		if max_player:
			value = self.ninfinity
			valid_moves = board.find_valid_move_cells(old_move)
			random.shuffle(valid_moves)
			for move in valid_moves:
				board.update(old_move, move, flag)
				if flag == 'x':
					next_flag = 'o'
				else:
					next_flag = 'x'
				child_value = self.minimax_search(board, move, depth + 1, alpha, beta, False, next_flag)
				
				board.big_boards_status[move[0]][move[1]][move[2]] = '-';
				board.small_boards_status[move[0]][move[1] / 3][move[2] / 3] = '-'

				if child_value > value:
					value = child_value
					if depth == 0:
						self.next_move = copy.deepcopy(move)
				alpha = max(alpha, value)				
				if beta <= alpha:
					break
			return value
		else:
			value = self.infinity
			valid_moves = board.find_valid_move_cells(old_move)
			random.shuffle(valid_moves)
			for move in valid_moves:
				board.update(old_move, move, flag)
				if flag == 'x':
					next_flag = 'o'
				else:
					next_flag = 'x'
				child_value = self.minimax_search(board, move, depth + 1, alpha, beta, True, next_flag)
				
				board.big_boards_status[move[0]][move[1]][move[2]] = '-';
				board.small_boards_status[move[0]][move[1] / 3][move[2] / 3] = '-'
				
				if child_value < value:
					value = child_value
					if depth == 0:
						self.next_move = copy.deepcopy(move)
				beta = min(beta, value)				
				if beta <= alpha:
					break
			return value