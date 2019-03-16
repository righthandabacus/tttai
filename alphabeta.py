#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tic-tac-toe using minimax algorithm with alpha-beta pruning
"""

import copy
import random
import sys

PLAYERS = ["X", "O"]  # maximizer == "X"
COUNT = 0

class Board:
    """simple tic-tac-toe board"""
    def __init__(self, board=None):
        if board:
            self.board = copy.deepcopy(board)
        else:
            self.board = [[' '] * 3 for _ in range(3)]
    def place(self, row, col, player):
        """produce a new board with row and col set to a symbol. Return None if
        some symbol already set."""
        if self.board[row][col] == ' ':
            newboard = Board(self.board)
            newboard[row][col] = player
            return newboard
    def __getitem__(self, key):
        return self.board[key]
    def __repr__(self):
        separator = "\n---+---+---\n "
        return " " + separator.join([" | ".join(row) for row in self.board])
    def spaces(self):
        """tell how many empty spots on the board"""
        return sum(1 for i in range(3) for j in range(3) if self[i][j] == ' ')
    def won(self):
        """check winner. Return the winner's symbol or None"""
        # check rows
        for row in self.board:
            if row[0] != ' ' and all(c == row[0] for c in row):
                return row[0]
        # check cols
        for n in range(3):
            if self.board[0][n] != ' ' and all(self.board[i][n] == self.board[0][n] for i in range(3)):
                return self.board[0][n]
        # check diag
        if self.board[0][0] != ' ' and all(self.board[n][n] == self.board[0][0] for n in range(3)):
            return self.board[0][0]
        if self.board[0][2] != ' ' and all(self.board[n][2-n] == self.board[0][2] for n in range(3)):
            return self.board[0][2]

def simple_evaluate(board):
    """simple evaluator: +10, -10 for someone won, 0 for tie. None otherwise."""
    winner = board.won()
    if winner == "X":
        return 10
    elif winner == "O":
        return -10
    if not board.spaces():
        return 0

def heuristic_evaluate(board):
    """heuristic evaluation <http://www.ntu.edu.sg/home/ehchua/programming/java/javagame_tictactoe_ai.html>"""
    score = 0
    rows = [# two diagonals
        [board.board[i][i] for i in range(3)],
        [board.board[i][2-i] for i in range(3)]
    ] + [   # horizontals
        [board.board[n][i] for i in range(3)] for n in range(3)
    ] + [   # verticals
        [board.board[i][n] for i in range(3)] for n in range(3)
    ]
    for row in rows:
        # 3-in-a-row == score 100
        # 2-in-a-row == score 10
        # 1-in-a-row == score 1
        # 0-in-a-row, or mixed entries == score 0 (no chase for either to win)
        # X == positive, O == negative
        countx = sum(1 for c in row if c == 'X')
        counto = sum(1 for c in row if c == 'O')
        if countx == 0:
            score -= int(10**(counto-1))
        elif counto == 0:
            score += int(10**(countx-1))
    return score

evaluate = simple_evaluate

def simple_minimax(board, player):
    """player to move one step on the board, find the minimax (best of the worse case) score"""
    global COUNT
    COUNT += 1
    assert player in PLAYERS
    opponent = "O" if player == "X" else "X"
    value = evaluate(board)
    if value is not None:
        return value  # exact score of the board
    # possible opponent moves: The worse case scores in different options
    candscores = [simple_minimax(b, opponent) for b in [board.place(r, c, player) for r in range(3) for c in range(3)] if b]
    # evaluate the best of worse case scores
    if player == "X":
        return max(candscores)
    else:
        return min(candscores)

def alphabeta(board, player, alpha=-float("inf"), beta=float("inf")):
    """minimax with alpha-beta pruning. It implies that we expect the score
    should between lowerbound alpha and upperbound beta to be useful
    """
    global COUNT
    COUNT += 1
    assert player in PLAYERS
    opponent = "O" if player == "X" else "X"
    value = evaluate(board)
    if value is not None:
        return value  # exact score of the board (terminal nodes)
    # minimax search with alpha-beta pruning
    children = filter(None, [board.place(r, c, player) for r in range(3) for c in range(3)])
    if "Heuristic improvement" == False:
        # sort by a heuristic function to hint for earlier cut-off
        children = sorted(children, key=heuristic_evaluate, reverse=True)
    if player == "X":   # player is maximizer
        value = -float("inf")
        for child in children:
            value = max(value, alphabeta(child, opponent, alpha, beta))
            alpha = max(alpha, value)
            if alpha >= beta:
                break   # beta cut-off
    else:               # player is minimizer
        value = float("inf")
        for child in children:
            value = min(value, alphabeta(child, opponent, alpha, beta))
            beta = min(beta, value)
            if alpha >= beta:
                break   # alpha cut-off
    return value

minimax = alphabeta

def play():
    "auto play tic-tac-toe"
    global COUNT
    minimizer = True
    game = Board()
    # loop until the game is done
    while not game.won():
        player = PLAYERS[minimizer]
        opponent = PLAYERS[not minimizer]
        COUNT = 0
        candidates = [(b, minimax(b, opponent)) for b in [game.place(r, c, player) for r in range(3) for c in range(3)] if b]
        if not candidates:
            break
        random.shuffle(candidates)
        # find best move: optimizing the worse case score
        if player == "X":
            game = max(candidates, key=lambda pair: pair[1])[0]
        else:
            game = min(candidates, key=lambda pair: pair[1])[0]
        # print board and switch
        minimizer = not minimizer
        print("\n%s move after %d search steps:" % (player, COUNT))
        print(game)
    # show result
    winner = game.won()
    if not winner:
        print("\nTied")
    else:
        print("\n%s has won" % winner)

if __name__ == "__main__":
    random.seed(int(sys.argv[1]))
    play()
