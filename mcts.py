#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tic-tac-toe using monte carlo tree search
"""

import random
import sys
import itertools

import gmpy

PLAYERS = [1, -1]  # maximizer == 1
COORDS = [(r, c) for r in range(3) for c in range(3)]

def symbol(code):
    """Return the symbol of player"""
    assert code in PLAYERS
    return "X" if code == 1 else "O"

def grouper(iterable, n, fillvalue=None):
    # function copied from Python doc, itertools module
    args = [iter(iterable)] * n
    return itertools.zip_longest(*args, fillvalue=fillvalue)

class Board:
    """bit-vector based tic-tac-toe board"""
    def __init__(self, board=0):
        self.board = board
    def mask(self, row, col, player):
        """Produce the bitmask for row and col
        The 18-bit vector is row-major, with matrix cell (0,0) the MSB. And the
        higher 9-bit is for 1 (X) and lower 9-bit is for -1 (O)

        Args:
            row, col: integers from 0 to 2 inclusive
        """
        offset = 3*(2-row) + (2-col)
        if player == 1:
            offset += 9
        return 1 << offset
    def place(self, row, col, player):
        """produce a new board with row and col set to a symbol. Return None if
        some symbol already set.

        Args:
            what: either +1 or -1
        """
        assert player in PLAYERS
        mask = self.mask(row, col, player)
        othermask = self.mask(row, col, -player)
        if (mask | othermask) & self.board:
            return None  # something already on this position
        return Board(self.board | mask)
    def __repr__(self):
        def emit():
            omask = 1 << 8
            xmask = omask << 9
            while omask: # until the mask becomes zero
                yield "O" if self.board & omask else "X" if self.board & xmask else " "
                omask >>= 1
                xmask >>= 1
        separator = "\n---+---+---\n "
        return " " + separator.join(" | ".join(g) for g in grouper(emit(), 3))
    def spaces(self):
        """tell how many empty spots on the board"""
        # alternative if no gmpy: bit(self.board).count("1")
        return 9 - gmpy.popcount(self.board)

    masks = (0b000000111, 0b000111000, 0b111000000, # rows
             0b001001001, 0b010010010, 0b100100100, # cols
             0b100010001, 0b001010100               # diags
            )
    def won(self):
        """check winner. Return the winner (+1 or -1) or None"""
        shifted = self.board >> 9
        for mask in self.masks:
            if self.board & mask == mask:
                return -1
            if shifted & mask == mask:
                return 1

def simple_evaluate(board):
    """simple evaluator: +10, -10 for someone won, 0 for tie. None otherwise"""
    winner = board.won()
    if winner == 1:
        return 10
    elif winner == -1:
        return -10
    if not board.spaces():
        return 0

evaluate = simple_evaluate

def mcts(board, player):
    """monte carlo tree serach

    Returns:
        the fraction of tree search that the player wins
    """
    assert player in PLAYERS
    N = 500  # number of rounds to search
    count = 0  # count the number of wins
    for _ in range(N):
        step = Board(board.board)
        who = player
        while step.spaces():
            r, c = random.choice(COORDS)
            nextstep = step.place(r, c, who)
            if nextstep is not None:
                who = -who  # next player's turn
                step = nextstep
                if step.won():  # someone won
                    break
        if step.won() == player:
            count += 1
    return count / N

def play():
    "auto play tic-tac-toe"
    minimizer = True
    game = Board()
    # loop until the game is done
    while not game.won():
        player = PLAYERS[minimizer]
        opponent = PLAYERS[not minimizer]
        candidates = [(b, mcts(b, opponent)) for b in [game.place(r, c, player) for r, c in COORDS] if b]
        if not candidates:
            break
        random.shuffle(candidates)
        # find best move: min opponent's score
        game, score = min(candidates, key=lambda pair: pair[1])
        # print board and switch
        minimizer = not minimizer
        print("\n%s move on score %f:" % (symbol(player), score))
        print(game)
    winner = game.won()
    if not winner:
        print("\nTied")
    else:
        print("\n%s has won" % symbol(winner))

if __name__ == "__main__":
    random.seed(int(sys.argv[1]))
    play()
