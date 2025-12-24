#!/usr/bin/env python3
"""
LifePong - Entry Point

A creative combination of Pong and Conway's Game of Life.
Run this file to start the game.
"""

from lifepong.core import LifePong


def main():
    """Entry point for the game."""
    game = LifePong()
    game.run()


if __name__ == "__main__":
    main()
