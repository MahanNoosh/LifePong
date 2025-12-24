"""Ball entity with physics."""

import math
import random
from typing import List, Tuple

from ..config import CONFIG, GameConfig


class Ball:
    """
    Ball entity with realistic physics.
    
    Handles position, velocity, collision detection points,
    and speed management.
    """
    
    def __init__(self, x: float, y: float, config: GameConfig = CONFIG):
        self.config = config
        self.x = float(x)
        self.y = float(y)
        self.vx = 0.0
        self.vy = 0.0
        self.speed = config.BALL_BASE_SPEED
        self.collision_cooldown = 0
        
    def reset(self, x: float, y: float) -> None:
        """Reset ball to starting position with random direction."""
        self.x = float(x)
        self.y = float(y)
        self.speed = self.config.BALL_BASE_SPEED
        
        # Random initial direction with slight angle variation
        angle = random.uniform(-0.4, 0.4)
        direction = random.choice([-1, 1])
        self.vx = direction * self.speed * math.cos(angle)
        self.vy = self.speed * math.sin(angle) * random.choice([-1, 1])
        self.collision_cooldown = 0
        
    def get_collision_points(self) -> List[Tuple[float, float]]:
        """Get 8 points around the ball perimeter for collision detection."""
        points = []
        for angle_deg in range(0, 360, 45):
            rad = math.radians(angle_deg)
            px = self.x + math.cos(rad) * self.config.BALL_RADIUS
            py = self.y + math.sin(rad) * self.config.BALL_RADIUS
            points.append((px, py))
        return points
    
    def normalize_velocity(self) -> None:
        """Maintain consistent speed after direction changes."""
        current_speed = math.sqrt(self.vx ** 2 + self.vy ** 2)
        if current_speed > 0:
            self.vx = (self.vx / current_speed) * self.speed
            self.vy = (self.vy / current_speed) * self.speed
            
    def accelerate(self, amount: float = None) -> None:
        """Increase ball speed up to maximum."""
        if amount is None:
            amount = self.config.BALL_ACCELERATION
        self.speed = min(self.speed + amount, self.config.BALL_MAX_SPEED)
        self.normalize_velocity()
        
    def update(self) -> None:
        """Update ball position and cooldown timer."""
        self.x += self.vx
        self.y += self.vy
        if self.collision_cooldown > 0:
            self.collision_cooldown -= 1
            
    def can_collide(self) -> bool:
        """Check if ball can register a new collision."""
        return self.collision_cooldown == 0
    
    def set_collision_cooldown(self) -> None:
        """Set cooldown after a collision."""
        self.collision_cooldown = self.config.COLLISION_COOLDOWN
