"""Visual effects systems."""

import random
from typing import Tuple


class ScreenShake:
    """Screen shake effect manager."""
    
    def __init__(self, decay: float = 0.9):
        self.amount = 0.0
        self.decay = decay
        
    def add_shake(self, amount: float) -> None:
        """Add shake intensity."""
        self.amount = amount
        
    def get_offset(self) -> Tuple[int, int]:
        """Get current shake offset and decay."""
        if self.amount > 0.5:
            offset_x = random.uniform(-self.amount, self.amount)
            offset_y = random.uniform(-self.amount, self.amount)
            self.amount *= self.decay
            return int(offset_x), int(offset_y)
        return 0, 0
