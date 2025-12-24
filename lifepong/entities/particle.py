"""Particle entity for visual effects."""

import random
from typing import Tuple

from ..config import CONFIG, GameConfig


class Particle:
    """Visual particle effect entity."""
    
    def __init__(self, x: float, y: float, color: Tuple[int, int, int], 
                 config: GameConfig = CONFIG):
        self.x = x
        self.y = y
        self.color = color
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-3, 3)
        self.life = random.randint(config.PARTICLE_LIFETIME_MIN, config.PARTICLE_LIFETIME_MAX)
        self.max_life = self.life
        self.size = random.randint(2, 5)
        
    def update(self) -> None:
        """Update particle position and life."""
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        self.vx *= 0.95
        self.vy *= 0.95
        
    def is_alive(self) -> bool:
        """Check if particle should still exist."""
        return self.life > 0
    
    @property
    def alpha(self) -> int:
        """Current transparency based on remaining life."""
        return int(255 * (self.life / self.max_life))
    
    @property
    def current_size(self) -> int:
        """Current size based on remaining life."""
        return int(self.size * (self.life / self.max_life))
