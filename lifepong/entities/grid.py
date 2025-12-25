"""Game of Life grid entity."""

import pickle
from typing import List, Tuple

from ..config import CONFIG


class GameOfLifeGrid:
    """
    Conway's Game of Life grid manager.
    
    Handles grid state, updates, cell health, and placement rules.
    Cells store health value: 0 = dead, 1+ = alive with that health.
    """
    
    def __init__(self, width: int, height: int, max_health: int = None):
        self.width = width
        self.height = height
        self.max_health = max_health or CONFIG.CELL_MAX_HEALTH
        self.cells = self._create_empty()
        
    def _create_empty(self) -> List[List[int]]:
        """Create an empty grid."""
        return [[0 for _ in range(self.width)] for _ in range(self.height)]
    
    def reset(self) -> None:
        """Reset grid to empty state."""
        self.cells = self._create_empty()
        
    def get_cell(self, x: int, y: int) -> int:
        """Get cell health at position (with bounds checking). 0 = dead, 1+ = alive."""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.cells[y][x]
        return 0
    
    def is_alive(self, x: int, y: int) -> bool:
        """Check if cell is alive (has health > 0)."""
        return self.get_cell(x, y) > 0
    
    def get_health_ratio(self, x: int, y: int) -> float:
        """Get cell health as ratio (0.0 to 1.0) for visual effects."""
        health = self.get_cell(x, y)
        if health <= 0:
            return 0.0
        return health / self.max_health
    
    def set_cell(self, x: int, y: int, value: int) -> bool:
        """Set cell value at position. Returns True if successful."""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.cells[y][x] = value
            return True
        return False
    
    def place_cell(self, x: int, y: int) -> bool:
        """Place a new cell at full health. Returns True if successful."""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.cells[y][x] = self.max_health
            return True
        return False
    
    def damage_cell(self, x: int, y: int, damage: int = 1) -> Tuple[bool, bool]:
        """
        Damage a cell. Returns (was_hit, was_destroyed).
        """
        if not (0 <= x < self.width and 0 <= y < self.height):
            return False, False
            
        if self.cells[y][x] <= 0:
            return False, False
            
        self.cells[y][x] -= damage
        destroyed = self.cells[y][x] <= 0
        if destroyed:
            self.cells[y][x] = 0
        return True, destroyed
    
    def count_neighbors(self, x: int, y: int) -> int:
        """Count live neighbors for a cell (with wrapping)."""
        count = 0
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx = (x + dx) % self.width
                ny = (y + dy) % self.height
                # Count as alive if health > 0
                if self.cells[ny][nx] > 0:
                    count += 1
        return count
    
    def update(self) -> None:
        """Apply Conway's Game of Life rules (preserves health for surviving cells)."""
        new_cells = self._create_empty()
        
        for y in range(self.height):
            for x in range(self.width):
                neighbors = self.count_neighbors(x, y)
                current = self.cells[y][x]
                
                # Conway's rules (health > 0 means alive)
                if current > 0 and neighbors in [2, 3]:
                    # Survives - keep current health
                    new_cells[y][x] = current
                elif current == 0 and neighbors == 3:
                    # Born - full health
                    new_cells[y][x] = self.max_health
                    
        self.cells = new_cells
        
    def save(self, filename: str = "saved_grid.pkl") -> bool:
        """Save grid to file."""
        try:
            with open(filename, "wb") as f:
                pickle.dump(self.cells, f)
            return True
        except Exception as e:
            print(f"Error saving grid: {e}")
            return False
            
    def load(self, filename: str = "saved_grid.pkl") -> bool:
        """Load grid from file."""
        try:
            with open(filename, "rb") as f:
                self.cells = pickle.load(f)
            return True
        except FileNotFoundError:
            print("No saved grid found!")
            return False
        except Exception as e:
            print(f"Error loading grid: {e}")
            return False
