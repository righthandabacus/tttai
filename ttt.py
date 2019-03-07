"""https://www.geeksforgeeks.org/minimax-algorithm-in-game-theory-set-3-tic-tac-toe-ai-finding-optimal-move/"""

import copy
import random
import sys
from typing import List, Optional

PLAYERS = ["X", "O"]  # maximizer == "X"

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
    def __repr__(self):
        return str(self)
    def spaces(self):
        """tell how many empty spots on the board"""
        return sum(1 for i in range(3) for j in range(3) if self[i][j] == ' ')
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

def simple_evaluate(board) -> Optional[float]:
    """simple evaluator: +10, -10 for someone won, 0 for tie"""
    winner = board.won()
    if winner == "X":
        return 10
    elif winner == "O":
        return -10
    if not board.spaces():
        return 0

def heuristic_evaluate(board) -> float:
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

evaluate = heuristic_evaluate

def minimax(board, who) -> float:
    """player `who` moved one step on the board, find the minimax score"""
    assert who in PLAYERS
    opponent = PLAYERS[who == "X"]
    value = evaluate(board)
    if value is not None:
        return value  # exact score of the board
    # possible opponent moves
    candscores = [minimax(b, opponent) for b in [board.place(r, c, opponent) for r in range(3) for c in range(3)] if b]
    if not candscores:
        return 0 # should caught by above
    # evaluate the worse case score
    if who == "X":
        return min(candscores)
    else:
        return max(candscores)

def play():
    "auto play tic-tac-toe"
    minimizer = True
    game = Board()
    # loop until the game is done
    while not game.won():
        player = PLAYERS[minimizer]
        candidates = [(b, minimax(b, player)) for b in [game.place(r, c, player) for r in range(3) for c in range(3)] if b]
        if not candidates:
            break
        random.shuffle(candidates)
        # find best move
        if player == "X":
            game = max(candidates, key=lambda pair: pair[1])[0]
        else:
            game = min(candidates, key=lambda pair: pair[1])[0]
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
    random.seed(int(sys.argv[1]))
    play()
