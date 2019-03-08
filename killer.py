#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tic-tac-toe using minimax algorithm with alpha-beta pruning, and use killer
heuristics
"""

import copy
import random
import sys
from collections import deque
from itertools import zip_longest
from typing import List, Optional

from gmpy import popcount

PLAYERS = [1, -1]  # maximizer == 1
POSITIONS = [(r,c) for r in range(3) for c in range(3)]
COUNT = 0

def symbol(code) -> str:
    """Return the symbol of player"""
    assert code in PLAYERS
    return "X" if code == 1 else "O"

def grouper(iterable, n, fillvalue=None):
    # https://stackoverflow.com/questions/434287/what-is-the-most-pythonic-way-to-iterate-over-a-list-in-chunks
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)

class Board:
    """bit-vector based tic-tac-toe board"""
    def __init__(self, board=0):
        self.board = board
    def mask(self, row, col, who) -> int:
        """Produce the bitmask for row and col
        The 18-bit vector is row-major, with matrix cell (0,0) the MSB. And the
        higher 9-bit is for 1 (X) and lower 9-bit is for -1 (O)

        Args:
            row, col: integers from 0 to 2 inclusive
        """
        offset = 3*(2-row) + (2-col)
        if who == 1:
            offset += 9
        return 1 << offset
    def check(self, row, col, player):
        """check if a row and col is empty

        Returns:
            bitmask for player on such row and col, None otherwise
        """
        assert player in PLAYERS
        mask = self.mask(row, col, player)
        othermask = self.mask(row, col, -player)
        if (mask | othermask) & self.board:
            return None  # something already on this position
        return mask
    def place(self, *args):
        """produce a new board with row and col set to a symbol. Return None if
        some symbol already set.

        Args (first form):
            row, col, player: player is either +1 or -1
        Args (second form):
            mask: The bit mask to set, this mode will skip the check
        """
        if len(args) == 1:
            return Board(self.board | args[0])
        mask = self.check(*args)
        if not mask:
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
        return 9 - popcount(self.board)

    masks = (0b000000111, 0b000111000, 0b111000000, # rows
             0b001001001, 0b010010010, 0b100100100, # cols
             0b100010001, 0b001010100               # diags
            )
    def won(self) -> Optional[int]:
        """check winner. Return the winner's symbol or None"""
        shifted = self.board >> 9
        for mask in self.masks:
            if self.board & mask == mask:
                return -1
            if shifted & mask == mask:
                return 1

def simple_evaluate(board) -> Optional[float]:
    """simple evaluator: +10, -10 for someone won, 0 for tie"""
    winner = board.won()
    if winner == 1:
        return 10
    elif winner == -1:
        return -10
    if not board.spaces():
        return 0

def heuristic_evaluate(board) -> float:
    """heuristic evaluation <http://www.ntu.edu.sg/home/ehchua/programming/java/javagame_tictactoe_ai.html>"""
    score = 0
    for mask in Board.masks:
        # 3-in-a-row == score 100
        # 2-in-a-row == score 10
        # 1-in-a-row == score 1
        # 0-in-a-row, or mixed entries == score 0 (no chase for either to win)
        # X == positive, O == negative
        oboard = board.board
        xboard = oboard >> 9
        countx = popcount(xboard & mask)
        counto = popcount(oboard & mask)
        if countx == 0:
            score -= int(10**(counto-1))
        elif counto == 0:
            score += int(10**(countx-1))
    return score

evaluate = simple_evaluate

CACHE = {}

def simple_minimax(board, player) -> float:
    """player to move one step on the board, find the minimax (best of the worse case) score"""
    # check cache for quick return
    if (board.board, player) in CACHE:
        return CACHE[(board.board, player)]
    global COUNT
    COUNT += 1
    assert player in PLAYERS
    opponent = -player
    value = evaluate(board)
    if value is not None:
        return value  # exact score of the board
    # possible opponent moves: The worse case scores in different options
    candscores = [simple_minimax(b, opponent) for b in [board.place(r, c, player) for r, c in POSITIONS] if b]
    # evaluate the best of worse case scores
    if player == 1:
        value = max(candscores)
    else:
        value = min(candscores)
    # save into cache
    CACHE[(board.board, player)] = value
    return value

KILLERS = deque()

def alphabeta(board, player, alpha=-float("inf"), beta=float("inf")) -> float:
    """minimax with alpha-beta pruning. It implies that we expect the score
    should between lowerbound alpha and upperbound beta to be useful
    """
    if "Use cache" == False:
        # make alpha-beta with memory: interferes with killer heuristics
        if (board.board, player) in CACHE:
            return CACHE[(board.board, player)]
    global COUNT
    COUNT += 1
    assert player in PLAYERS
    opponent = -player
    value = evaluate(board)
    if value is not None:
        return value  # exact score of the board (terminal nodes)
    # minimax search with alpha-beta pruning
    masks = filter(None, [board.check(r, c, player) for r,c in POSITIONS])
    children = [(mask, board.place(mask)) for mask in masks]
    if "Heuristic improvement" == False:
        # sort by a heuristic function to hint for earlier cut-off
        children = sorted(children, key=heuristic_evaluate, reverse=True)
    if "Killer heuristic":
        # remember the move that caused the last (last 2) beta cut-off and check those first
        # <https://en.wikipedia.org/wiki/Killer_heuristic>
        children = sorted(children, key=lambda x: x[0] not in KILLERS)
    if player == 1:   # player is maximizer
        value = -float("inf")
        for mask, child in children:
            value = max(value, alphabeta(child, opponent, alpha, beta))
            alpha = max(alpha, value)
            if alpha >= beta:
                KILLERS.append(mask)
                if len(KILLERS) > 4:
                    KILLERS.popleft()
                break   # beta cut-off
    else:               # player is minimizer
        value = float("inf")
        for _, child in children:
            value = min(value, alphabeta(child, opponent, alpha, beta))
            beta = min(beta, value)
            if alpha >= beta:
                break   # alpha cut-off
    # save into cache
    if "Use cache" == False:
        CACHE[(board.board, player)] = value
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
        candidates = [(b, minimax(b, opponent)) for b in [game.place(r, c, player) for r, c in POSITIONS] if b]
        if not candidates:
            break
        random.shuffle(candidates)
        # find best move: optimizing the worse case score
        if player == 1:
            game = max(candidates, key=lambda pair: pair[1])[0]
        else:
            game = min(candidates, key=lambda pair: pair[1])[0]
        # print board and switch
        minimizer = not minimizer
        print()
        print("%s move after %d search steps:" % (symbol(player), COUNT))
        print(game)
    winner = game.won()
    print()
    if not winner:
        print("Tied")
    else:
        print("%s has won" % symbol(winner))

if __name__ == "__main__":
    random.seed(int(sys.argv[1]))
    play()
