"""Game state definitions."""

from enum import Enum, auto


class GameState(Enum):
    """Possible states of the game."""
    
    PLACEMENT = auto()  # Players placing cells
    PLAYING = auto()    # Game in progress
    PAUSED = auto()     # Game paused
