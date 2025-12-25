"""Game configuration settings."""

from dataclasses import dataclass


@dataclass(frozen=True)
class GameConfig:
    """Immutable game configuration settings."""
    
    # Screen
    SCREEN_WIDTH: int = 1200
    SCREEN_HEIGHT: int = 600
    FPS: int = 60
    TITLE: str = "LifePong"
    
    # Grid
    CELL_SIZE: int = 10
    PLACING_WIDTH: int = 40  # Columns for player placement
    
    # Ball Physics
    BALL_RADIUS: int = 9
    BALL_BASE_SPEED: float = 6.0
    BALL_MAX_SPEED: float = 12.0
    BALL_ACCELERATION: float = 0.3
    BALL_ACCEL_INTERVAL: int = 120  # Frames between acceleration
    COLLISION_COOLDOWN: int = 5
    
    # Game Rules
    STARTING_CELLS: int = 40
    RESTART_CELLS: int = 20  # Cells given after each round restart (set to 0 to disable)
    MAX_CELLS: int = 300  # Maximum cells a player can hold at any time
    LIFE_UPDATE_INTERVAL: int = 3  # Frames between Game of Life updates
    
    # Multiplayer Placement System
    PLACEMENT_TIME_SECONDS: float = 25.0  # Total placement window duration
    # Rate limiting cooldowns (in milliseconds)
    RAPID_BUILD_COOLDOWN_MS: int = 50  # First 15 seconds: max 1 edit every 100ms (~10 edits/sec)
    PRECISION_COOLDOWN_MS: int = 250  # Last 10 seconds: max 1 edit every 300ms (~3 edits/sec)
    RAPID_BUILD_DURATION: float = 15.0  # Duration of rapid build phase in seconds
    
    # Cell Health System
    CELL_MAX_HEALTH: int = 3  # Hits required to destroy a cell
    BALL_DAMAGE_BASE: int = 1  # Base damage per hit
    BALL_DAMAGE_SPEED_BONUS: bool = True  # Extra damage at high speed
    # Speed thresholds (as ratio of max speed) and their damage bonuses
    # Format: [(threshold_ratio, damage_bonus), ...]
    BALL_DAMAGE_THRESHOLDS: list = None  # Uses default [(0.7, 1), (0.9, 1)] if None
    
    # Bounce Angle Control
    ENFORCE_MIN_BOUNCE_ANGLE: bool = False  # Enable minimum angle enforcement to prevent 90-degree traps
    MIN_BOUNCE_ANGLE: float = 0.2  # Minimum angle in radians (0.2 ≈ 11.5°, 0.0 = disabled)
    BOUNCE_ANGLE_ADJUSTMENT: float = 0.3  # How strongly to adjust velocity (0.1-0.5 recommended)
    
    # Visual Effects
    TRAIL_LENGTH: int = 15
    PARTICLE_LIFETIME_MIN: int = 20
    PARTICLE_LIFETIME_MAX: int = 40
    
    @property
    def GRID_WIDTH(self) -> int:
        """Calculate grid width based on screen and cell size."""
        return self.SCREEN_WIDTH // self.CELL_SIZE
    
    @property
    def GRID_HEIGHT(self) -> int:
        """Calculate grid height based on screen and cell size."""
        return self.SCREEN_HEIGHT // self.CELL_SIZE


# Global configuration instance
CONFIG = GameConfig()
