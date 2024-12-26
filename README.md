# LifePong
A creative game by combination of two games named Pong and Conway's Game Of Life. Game of Pong/ Pong of Life/ Life as a Pong? Pong in real life? Help me with the name HAHAHA
# Rules:
at the beginning of each round players have 40 cells to place/remove (make alive/kill) on their side of board using mouse (you can also drag for quick input). These and their future generations will work as paddles of original pong game.
At each step in time, the following transitions occur:

- Any live cell with fewer than two live neighbours dies, as if by underpopulation.
- Any live cell with two or three live neighbours lives on to the next generation.
- Any live cell with more than three live neighbours dies, as if by overpopulation.
- Any dead cell with exactly three live neighbours becomes a live cell, as if by reproduction.

After placing cells you can press space to start the game. It runs at 30 fps which means 30 generations happens each second. It also saves each rounds input using pickle and .pkl file. Have fun I guess :D
