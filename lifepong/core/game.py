"""Main game controller class."""

import pygame
from typing import List, Tuple, Optional

from ..config import CONFIG, COLORS, GameConfig, Colors
from ..entities import Ball, Player, GameOfLifeGrid
from ..systems import CollisionSystem, ParticleSystem, ScreenShake
from ..rendering import Renderer
from .states import GameState


class LifePong:
    """
    Main game controller class.
    
    Orchestrates all game systems and manages the main game loop.
    """
    
    def __init__(self, config: GameConfig = CONFIG, colors: Colors = COLORS):
        pygame.init()
        
        self.config = config
        self.colors = colors
        
        # Display
        self.screen = pygame.display.set_mode(
            (self.config.SCREEN_WIDTH, self.config.SCREEN_HEIGHT)
        )
        pygame.display.set_caption(self.config.TITLE)
        self.clock = pygame.time.Clock()
        
        # Systems
        self.renderer = Renderer(self.screen, self.config, self.colors)
        self.collision = CollisionSystem(self.config)
        self.particles = ParticleSystem(self.config)
        self.screen_shake = ScreenShake()
        
        # Game state
        self.state = GameState.PLACEMENT
        self.time = 0
        
        # Entities
        self.ball = Ball(
            self.config.SCREEN_WIDTH // 2,
            self.config.SCREEN_HEIGHT // 2,
            self.config
        )
        self.ball_trail: List[Tuple[int, int]] = []
        
        self.grid = GameOfLifeGrid(self.config.GRID_WIDTH, self.config.GRID_HEIGHT)
        
        # Players
        self.players = [
            Player(
                id=1,
                color=self.colors.NEON_CYAN,
                cells_remaining=self.config.STARTING_CELLS,
                zone_start=0,
                zone_end=self.config.PLACING_WIDTH
            ),
            Player(
                id=2,
                color=self.colors.NEON_PINK,
                cells_remaining=self.config.STARTING_CELLS,
                zone_start=self.config.GRID_WIDTH - self.config.PLACING_WIDTH,
                zone_end=self.config.GRID_WIDTH
            )
        ]
        
        # Input state
        self.mouse_down = False
        self.placing_cells = True
        self.hover_pos: Optional[Tuple[int, int]] = None
        
    def get_player_for_position(self, grid_x: int) -> Optional[Player]:
        """Get player whose zone contains grid_x."""
        for player in self.players:
            if player.is_in_zone(grid_x):
                return player
        return None
        
    def handle_events(self) -> bool:
        """Process input events. Returns False if game should quit."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and self.state == GameState.PLACEMENT:
                    self._start_game()
                elif event.key == pygame.K_ESCAPE:
                    return False
                    
            if event.type == pygame.MOUSEBUTTONDOWN and self.state == GameState.PLACEMENT:
                self._handle_mouse_down(event.pos)
                
            if event.type == pygame.MOUSEBUTTONUP:
                self.mouse_down = False
                
        # Update hover position
        mouse_pos = pygame.mouse.get_pos()
        self.hover_pos = (
            mouse_pos[0] // self.config.CELL_SIZE,
            mouse_pos[1] // self.config.CELL_SIZE
        )
        
        # Handle dragging
        if self.mouse_down and self.state == GameState.PLACEMENT:
            self._handle_cell_placement(mouse_pos)
            
        return True
        
    def _handle_mouse_down(self, pos: Tuple[int, int]) -> None:
        """Handle mouse button press."""
        grid_x = pos[0] // self.config.CELL_SIZE
        grid_y = pos[1] // self.config.CELL_SIZE
        self.mouse_down = True
        
        if 0 <= grid_x < self.config.GRID_WIDTH and 0 <= grid_y < self.config.GRID_HEIGHT:
            player = self.get_player_for_position(grid_x)
            if player:
                # Determine if placing or removing based on clicked cell
                cell_exists = self.grid.is_alive(grid_x, grid_y)
                # Can remove if cell exists, can place if cell empty AND has cells remaining
                if cell_exists:
                    self.placing_cells = False
                elif player.can_place():
                    self.placing_cells = True
                
    def _handle_cell_placement(self, mouse_pos: Tuple[int, int]) -> None:
        """Handle cell placement/removal during drag."""
        grid_x = mouse_pos[0] // self.config.CELL_SIZE
        grid_y = mouse_pos[1] // self.config.CELL_SIZE
        
        if not (0 <= grid_x < self.config.GRID_WIDTH and 0 <= grid_y < self.config.GRID_HEIGHT):
            return
            
        player = self.get_player_for_position(grid_x)
        if not player:
            return
            
        if self.placing_cells and not self.grid.is_alive(grid_x, grid_y):
            if player.place_cell():
                self.grid.place_cell(grid_x, grid_y)
                self.particles.spawn(mouse_pos[0], mouse_pos[1], player.color, 3)
        elif not self.placing_cells and self.grid.is_alive(grid_x, grid_y):
            self.grid.set_cell(grid_x, grid_y, 0)
            player.remove_cell()
            
    def _start_game(self) -> None:
        """Start the game from placement phase."""
        self.grid.save()
        self.state = GameState.PLAYING
        self.ball.reset(self.config.SCREEN_WIDTH // 2, self.config.SCREEN_HEIGHT // 2)
        self.particles.spawn(
            self.config.SCREEN_WIDTH // 2,
            self.config.SCREEN_HEIGHT // 2,
            self.colors.NEON_GREEN, 30
        )
        
    def _reset_round(self) -> None:
        """Reset for a new round after scoring."""
        self.grid.reset()
        self.grid.load()
        self.ball.reset(self.config.SCREEN_WIDTH // 2, self.config.SCREEN_HEIGHT // 2)
        self.ball_trail.clear()
        self.state = GameState.PLACEMENT
        self.screen_shake.add_shake(15)
        
        # Reset player cells (add restart cells to remaining, capped at MAX_CELLS)
        for player in self.players:
            player.cells_remaining = min(
                player.cells_remaining + self.config.RESTART_CELLS,
                self.config.MAX_CELLS
            )
            
    def update(self) -> None:
        """Update game state."""
        self.time += 1
        self.particles.update()
        
        if self.state != GameState.PLAYING:
            return
            
        # Update ball
        self.ball.update()
        
        # Update trail
        self.ball_trail.append((int(self.ball.x), int(self.ball.y)))
        if len(self.ball_trail) > self.config.TRAIL_LENGTH:
            self.ball_trail.pop(0)
            
        # Accelerate ball
        if self.time % self.config.BALL_ACCEL_INTERVAL == 0:
            self.ball.accelerate()
            
        # Wall collisions
        wall = self.collision.check_wall_collision(self.ball)
        if wall in ['top', 'bottom']:
            self.collision.handle_wall_collision(self.ball, wall)
            self.screen_shake.add_shake(5)
            self.particles.spawn(int(self.ball.x), int(self.ball.y), self.colors.NEON_YELLOW, 15)
        elif wall == 'left':
            self.players[1].score += 1
            self.screen_shake.add_shake(25)
            self.particles.spawn(int(self.ball.x), int(self.ball.y), self.colors.NEON_PINK, 60)
            self._reset_round()
            return
        elif wall == 'right':
            self.players[0].score += 1
            self.screen_shake.add_shake(25)
            self.particles.spawn(int(self.ball.x), int(self.ball.y), self.colors.NEON_CYAN, 60)
            self._reset_round()
            return
            
        # Grid collisions
        collision = self.collision.check_grid_collision(self.ball, self.grid)
        if collision:
            destroyed, cx, cy = self.collision.handle_grid_collision(self.ball, self.grid, collision)
            shake_amount = 6 + self.ball.speed * 0.5
            
            if destroyed:
                # Extra effects when cell is destroyed
                shake_amount += 4
                self.particles.spawn(
                    cx * self.config.CELL_SIZE + self.config.CELL_SIZE // 2,
                    cy * self.config.CELL_SIZE + self.config.CELL_SIZE // 2,
                    self.colors.NEON_YELLOW, 25
                )
            
            self.screen_shake.add_shake(shake_amount)
            particle_count = int(15 + self.ball.speed)
            self.particles.spawn(int(self.ball.x), int(self.ball.y), self.colors.NEON_ORANGE, particle_count)
            
        # Update Game of Life
        if self.time % self.config.LIFE_UPDATE_INTERVAL == 0:
            self.grid.update()
            
    def render(self) -> None:
        """Render the game."""
        shake_offset = self.screen_shake.get_offset()
        self.renderer.clear(shake_offset)
        
        if self.state == GameState.PLACEMENT:
            self.renderer.draw_placement_zones(
                self.grid, self.players, self.time, self.hover_pos
            )
            self.renderer.draw_placement_ui(self.players, self.time)
        else:
            self.renderer.draw_grid(self.grid, self.time)
            self.renderer.draw_ball(self.ball, self.ball_trail, self.time)
            self.renderer.draw_speed_indicator(self.ball)
            
        self.renderer.draw_particles(self.particles.particles)
        self.renderer.draw_scores(self.players, self.time)
        self.renderer.draw_scanlines()
        
        pygame.display.flip()
        
    def run(self) -> None:
        """Main game loop."""
        running = True
        
        while running:
            running = self.handle_events()
            self.update()
            self.render()
            self.clock.tick(self.config.FPS)
            
        pygame.quit()
