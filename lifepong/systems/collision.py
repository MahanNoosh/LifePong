"""Collision detection and response system."""

import math
import random
from typing import Optional, Tuple

from ..config import CONFIG, GameConfig
from ..entities import Ball, GameOfLifeGrid


class CollisionSystem:
    """Handles all collision detection and response."""
    
    def __init__(self, config: GameConfig = CONFIG):
        self.config = config
        
    def calculate_damage(self, ball: Ball) -> int:
        """Calculate damage based on ball speed."""
        damage = self.config.BALL_DAMAGE_BASE
        if self.config.BALL_DAMAGE_SPEED_BONUS:
            speed_ratio = ball.speed / self.config.BALL_MAX_SPEED
            if speed_ratio > 0.7:
                damage += 1
            if speed_ratio > 0.9:
                damage += 1
        return damage
        
    def check_wall_collision(self, ball: Ball) -> Optional[str]:
        """
        Check ball collision with walls.
        
        Returns:
            'top', 'bottom', 'left', 'right', or None
        """
        radius = self.config.BALL_RADIUS
        
        if ball.y - radius <= 0:
            return 'top'
        elif ball.y + radius >= self.config.SCREEN_HEIGHT:
            return 'bottom'
        elif ball.x - radius <= 0:
            return 'left'
        elif ball.x + radius >= self.config.SCREEN_WIDTH:
            return 'right'
        return None
    
    def handle_wall_collision(self, ball: Ball, wall: str) -> None:
        """Apply wall collision response to ball."""
        radius = self.config.BALL_RADIUS
        
        if wall == 'top':
            ball.y = radius
            ball.vy = abs(ball.vy)
        elif wall == 'bottom':
            ball.y = self.config.SCREEN_HEIGHT - radius
            ball.vy = -abs(ball.vy)
            
    def check_grid_collision(self, ball: Ball, grid: GameOfLifeGrid) -> Optional[Tuple[int, int, int, int]]:
        """
        Check ball collision with grid cells.
        
        Returns:
            Tuple of (normal_x, normal_y, cell_x, cell_y) or None
        """
        if not ball.can_collide():
            return None
            
        cell_size = self.config.CELL_SIZE
        
        for px, py in ball.get_collision_points():
            grid_x = int(px // cell_size)
            grid_y = int(py // cell_size)
            
            if grid.is_alive(grid_x, grid_y):
                # Calculate collision normal
                cell_center_x = grid_x * cell_size + cell_size // 2
                cell_center_y = grid_y * cell_size + cell_size // 2
                
                dx = ball.x - cell_center_x
                dy = ball.y - cell_center_y
                
                # Determine primary collision axis
                if abs(dx) > abs(dy):
                    normal_x = 1 if dx > 0 else -1
                    normal_y = 0
                else:
                    normal_x = 0
                    normal_y = 1 if dy > 0 else -1
                    
                return (normal_x, normal_y, grid_x, grid_y)
                
        return None
    
    def handle_grid_collision(self, ball: Ball, grid: GameOfLifeGrid, 
                              collision: Tuple[int, int, int, int]) -> Tuple[bool, int, int]:
        """
        Apply grid collision response to ball and damage cell.
        
        Returns:
            Tuple of (cell_destroyed, cell_x, cell_y)
        """
        nx, ny, cx, cy = collision
        cell_size = self.config.CELL_SIZE
        radius = self.config.BALL_RADIUS
        
        # Calculate and apply damage
        damage = self.calculate_damage(ball)
        _, destroyed = grid.damage_cell(cx, cy, damage)
        
        # Reflect velocity
        if nx != 0:
            ball.vx = -ball.vx
            # Push ball out of cell
            if nx > 0:
                ball.x = (cx + 1) * cell_size + radius + 1
            else:
                ball.x = cx * cell_size - radius - 1
                
        if ny != 0:
            ball.vy = -ball.vy
            if ny > 0:
                ball.y = (cy + 1) * cell_size + radius + 1
            else:
                ball.y = cy * cell_size - radius - 1
        
        # Prevent 90-degree trap: ensure minimum angle
        self._ensure_minimum_angle(ball)
        
        # Add slight randomness for variety
        ball.vx += random.uniform(-0.2, 0.2)
        ball.vy += random.uniform(-0.2, 0.2)
        ball.normalize_velocity()
        
        # Set cooldown
        ball.set_collision_cooldown()
        
        return destroyed, cx, cy
    
    def _ensure_minimum_angle(self, ball: Ball) -> None:
        """Ensure ball has minimum angle to prevent 90-degree traps."""
        min_angle = self.config.MIN_BOUNCE_ANGLE
        
        # Calculate current angle
        current_angle = math.atan2(abs(ball.vy), abs(ball.vx))
        
        # If angle is too steep (close to 90 degrees vertical)
        if current_angle > (math.pi / 2 - min_angle):
            # Add horizontal velocity
            adjustment = min_angle * random.choice([-1, 1])
            ball.vx += math.cos(adjustment) * ball.speed * 0.3
            
        # If angle is too shallow (close to 0 degrees horizontal)
        elif current_angle < min_angle:
            # Add vertical velocity
            adjustment = min_angle * random.choice([-1, 1])
            ball.vy += math.sin(min_angle) * ball.speed * 0.3 * random.choice([-1, 1])
