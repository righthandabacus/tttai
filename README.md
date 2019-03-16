# tttai

tic-tac-toe game programmed in old-school AI. See
<https://www.adrian.idv.hk/2019-03-15-tictactoe/>

Requires Python 3 (or `s/zip_longest/izip_longest/`)

To run:

    python3 mcts 10

where the number is any integer as random seed.

- `human.py`: Two human players required. For testing out the data structure.
- `minimax.py`: Minimax game tree search
- `alphabeta.py`: Alpha beta search
- `bitalphabeta.py`: New data structure, use bitboard instead of 2D array to hold the position
- `killer.py`: Alpha-beta search with killer heuristics
- `negascout.py`: Principal variation search
- `mcts.py`: Monte-Carlo tree search
