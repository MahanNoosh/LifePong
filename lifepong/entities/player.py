"""Player entity."""

from dataclasses import dataclass
from typing import Tuple


@dataclass
class Player:
    """Player state and zone information."""
    
    id: int
    color: Tuple[int, int, int]
    cells_remaining: int
    zone_start: int  # Grid X start
    zone_end: int    # Grid X end
    score: int = 0
    
    def can_place(self) -> bool:
        """Check if player can place more cells."""
        return self.cells_remaining > 0
    
    def is_in_zone(self, grid_x: int) -> bool:
        """Check if grid position is in player's zone."""
        return self.zone_start <= grid_x < self.zone_end
    
    def place_cell(self) -> bool:
        """Attempt to place a cell. Returns True if successful."""
        if self.cells_remaining > 0:
            self.cells_remaining -= 1
            return True
        return False
    
    def remove_cell(self) -> None:
        """Return a cell to the player."""
        self.cells_remaining += 1
