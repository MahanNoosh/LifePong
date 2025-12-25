"""Player entity."""

import time
from dataclasses import dataclass, field
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
    # Rate limiting: timestamp (ms) of last edit for anti-spam cooldown
    last_edit_time_ms: float = field(default=0.0)
    # Track live cells on grid (for MAX_LIVE_CELLS enforcement)
    live_cells_count: int = field(default=0)
    
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
    
    # ==========================================================================
    # RATE LIMITING METHODS
    # Used to enforce anti-spam cooldowns during placement phase.
    # Cooldown depends on remaining placement time (rapid vs precision window).
    # ==========================================================================
    
    def is_on_cooldown(self, cooldown_ms: int) -> bool:
        """
        Check if player is currently on edit cooldown.
        
        Rate limiting is enforced per-player independently.
        If player attempts an edit before cooldown expires, input is ignored (not queued).
        
        Args:
            cooldown_ms: Current cooldown period in milliseconds
                        (100ms for rapid build, 300ms for precision window)
        
        Returns:
            True if player cannot edit yet (on cooldown), False if edit is allowed
        """
        current_time_ms = time.time() * 1000
        return (current_time_ms - self.last_edit_time_ms) < cooldown_ms
    
    def record_edit(self) -> None:
        """Record the timestamp of an edit action for rate limiting."""
        self.last_edit_time_ms = time.time() * 1000
    
    def reset_edit_cooldown(self) -> None:
        """Reset the edit cooldown (used when starting new placement phase)."""
        self.last_edit_time_ms = 0.0
