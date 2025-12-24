"""Particle system for visual effects."""

from typing import List, Tuple

from ..config import CONFIG, GameConfig
from ..entities import Particle


class ParticleSystem:
    """Manages all particles in the game."""
    
    def __init__(self, config: GameConfig = CONFIG):
        self.config = config
        self.particles: List[Particle] = []
        
    def spawn(self, x: float, y: float, color: Tuple[int, int, int], count: int = 10) -> None:
        """Spawn particles at position."""
        for _ in range(count):
            self.particles.append(Particle(x, y, color, self.config))
            
    def update(self) -> None:
        """Update all particles and remove dead ones."""
        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if p.is_alive()]
        
    def clear(self) -> None:
        """Remove all particles."""
        self.particles.clear()
