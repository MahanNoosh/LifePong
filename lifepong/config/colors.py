"""Color palette definitions."""

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class Colors:
    """Color palette for the game."""
    
    # Neon colors
    NEON_PINK: Tuple[int, int, int] = (255, 16, 240)
    NEON_CYAN: Tuple[int, int, int] = (0, 255, 255)
    NEON_GREEN: Tuple[int, int, int] = (57, 255, 20)
    NEON_ORANGE: Tuple[int, int, int] = (255, 95, 31)
    NEON_PURPLE: Tuple[int, int, int] = (191, 64, 191)
    NEON_YELLOW: Tuple[int, int, int] = (255, 255, 0)
    
    # Base colors
    BLACK: Tuple[int, int, int] = (5, 5, 15)
    WHITE: Tuple[int, int, int] = (244, 245, 247)
    GRAY: Tuple[int, int, int] = (40, 45, 60)


# Global colors instance
COLORS = Colors()
