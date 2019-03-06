"""https://www.geeksforgeeks.org/minimax-algorithm-in-game-theory-set-3-tic-tac-toe-ai-finding-optimal-move/"""

import copy
import random
from typing import List, Optional

class Board:
    """simple tic-tac-toe board"""
    def __init__(self, board=None):
        if board:
            self.board = copy.deepcopy(board)
        else:
            self.board = [[' '] * 3 for _ in range(3)]
    def place(self, row, col, what):
        """produce a new board with row and col set to a symbol. Return None if
        some symbol already set."""
        if self.board[row][col] == ' ':
            newboard = Board(self.board)
            newboard[row][col] = what
            return newboard
    def __getitem__(self, key):
        return self.board[key]
    def __str__(self):
        separator = "\n---+---+---\n"
        return separator.join([" " + " | ".join(row) for row in self.board])
    def won(self) -> Optional[str]:
        """check winner. Return the winner's symbol or None"""
        # check rows
        for row in self.board:
            if row[0] != ' ' and all(c==row[0] for c in row):
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

def evaluate(board) -> float:
    """simple evaluator: +10, -10 for someone won, 0 for all other cases"""
    winner = board.won()
    if not winner:
        return 0
    elif winner == "X":
        return 10
    else:
        return -10

def minimax(board, who) -> float:
    """player `who` move any one step on the board, find the minimax score"""
    assert who in ["X", "O"]
    opponent = ["O", "X"][who == "X"]
    value = evaluate(board)
    if value:
        return value
    # possible opponent moves
    candidates = [b for b in [board.place(r, c, opponent) for r in range(3) for c in range(3)] if b]
    if not candidates:
        return 0
    # evaluate my minimax score
    elif who == "X":
        return max(minimax(b, who) for b in candidates)
    else:
        return min(minimax(b, who) for b in candidates)

def play():
    "auto play tic-tac-toe"
    players = ["X", "O"]
    minimizer = True
    game = Board()
    # loop until the game is done
    while not game.won():
        player = players[minimizer]
        candidates = [b for b in [game.place(r, c, player) for r in range(3) for c in range(3)] if b]
        if not candidates:
            break
        random.shuffle(candidates)
        # find best move
        if player == "O":
            game = min(candidates, key=lambda b: minimax(b, players[not minimizer]))
        else:
            game = max(candidates, key=lambda b: minimax(b, players[not minimizer]))
        # print board and switch
        minimizer = not minimizer
        print()
        print("%s move:" % player)
        print(game)
    winner = game.won()
    print()
    if not winner:
        print("Tied")
    else:
        print("%s has won" % winner)

if __name__ == "__main__":
    random.seed(3)
    play()
