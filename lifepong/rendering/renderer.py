"""Game renderer for all visual output."""

import math
import pygame
from typing import List, Tuple, Optional

from ..config import CONFIG, COLORS, GameConfig, Colors
from ..entities import Ball, Particle, Player, GameOfLifeGrid


class Renderer:
    """
    Handles all visual rendering for the game.
    
    Separates drawing logic from game logic for cleaner architecture.
    """
    
    def __init__(self, screen: pygame.Surface, config: GameConfig = CONFIG, 
                 colors: Colors = COLORS):
        self.screen = screen
        self.config = config
        self.colors = colors
        
        # Create surfaces
        self.glow_surface = pygame.Surface(
            (config.SCREEN_WIDTH, config.SCREEN_HEIGHT), 
            pygame.SRCALPHA
        )
        self.background = self._create_background()
        
        # Fonts
        self._init_fonts()
        
    def _init_fonts(self) -> None:
        """Initialize fonts with fallbacks."""
        pygame.font.init()
        try:
            self.title_font = pygame.font.SysFont("Arial Black", 72)
            self.font = pygame.font.SysFont("Arial", 28)
            self.score_font = pygame.font.SysFont("Arial Black", 48)
            self.zone_font = pygame.font.SysFont("Arial", 20, bold=True)
        except:
            self.title_font = pygame.font.SysFont(None, 72)
            self.font = pygame.font.SysFont(None, 28)
            self.score_font = pygame.font.SysFont(None, 48)
            self.zone_font = pygame.font.SysFont(None, 20)
            
    def _create_background(self) -> pygame.Surface:
        """Create gradient background with grid lines."""
        surface = pygame.Surface((self.config.SCREEN_WIDTH, self.config.SCREEN_HEIGHT))
        
        # Gradient
        for y in range(self.config.SCREEN_HEIGHT):
            ratio = y / self.config.SCREEN_HEIGHT
            r = int(5 + ratio * 15)
            g = int(5 + ratio * 10)
            b = int(15 + ratio * 25)
            pygame.draw.line(surface, (r, g, b), (0, y), (self.config.SCREEN_WIDTH, y))
        
        # Grid lines
        for x in range(0, self.config.SCREEN_WIDTH, 50):
            pygame.draw.line(surface, (30, 30, 50), (x, 0), (x, self.config.SCREEN_HEIGHT), 1)
        for y in range(0, self.config.SCREEN_HEIGHT, 50):
            pygame.draw.line(surface, (30, 30, 50), (0, y), (self.config.SCREEN_WIDTH, y), 1)
            
        return surface
    
    def clear(self, shake_offset: Tuple[int, int] = (0, 0)) -> None:
        """Clear screen with background."""
        self.screen.blit(self.background, shake_offset)
        self.glow_surface.fill((0, 0, 0, 0))
        
    def get_cell_color(self, x: int, time: int) -> Tuple[int, int, int]:
        """Get color for cell based on position."""
        ratio = x / self.config.GRID_WIDTH
        if ratio < 0.33:
            return self.colors.NEON_CYAN
        elif ratio < 0.66:
            return self.colors.NEON_GREEN
        else:
            return self.colors.NEON_PINK
            
    def draw_glow_circle(self, color: Tuple[int, int, int], pos: Tuple[int, int], 
                         radius: int, intensity: int = 3) -> None:
        """Draw a glowing circle."""
        for i in range(intensity, 0, -1):
            alpha = int(60 / i)
            glow_radius = radius + i * 4
            glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*color, alpha), (glow_radius, glow_radius), glow_radius)
            self.screen.blit(glow_surf, (pos[0] - glow_radius, pos[1] - glow_radius))
        pygame.draw.circle(self.screen, color, pos, radius)
        
    def draw_glow_rect(self, surface: pygame.Surface, color: Tuple[int, int, int], 
                       rect: pygame.Rect, intensity: int = 2) -> None:
        """Draw a glowing rectangle."""
        for i in range(intensity, 0, -1):
            alpha = int(80 / i)
            glow_rect = rect.inflate(i * 3, i * 3)
            glow_surf = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (*color, alpha), glow_surf.get_rect(), border_radius=2)
            surface.blit(glow_surf, glow_rect.topleft)
            
    def draw_grid(self, grid: GameOfLifeGrid, time: int) -> None:
        """Draw the Game of Life grid during gameplay with health visualization."""
        cell_size = self.config.CELL_SIZE
        
        for y in range(grid.height):
            for x in range(grid.width):
                if grid.is_alive(x, y):
                    health_ratio = grid.get_health_ratio(x, y)
                    base_color = self.get_cell_color(x, time)
                    
                    # Damaged cells pulse faster and appear dimmer
                    pulse_speed = 0.1 + (1 - health_ratio) * 0.2
                    pulse = math.sin(time * pulse_speed + x * 0.1 + y * 0.1) * 0.3 + 0.7
                    
                    # Color dims as health decreases
                    brightness = 0.4 + health_ratio * 0.6
                    animated_color = tuple(int(c * pulse * brightness) for c in base_color)
                    
                    rect = pygame.Rect(x * cell_size, y * cell_size, cell_size - 1, cell_size - 1)
                    
                    # Glow intensity based on health
                    glow_intensity = 1 + int(health_ratio * 2)
                    self.draw_glow_rect(self.glow_surface, base_color, rect, intensity=glow_intensity)
                    pygame.draw.rect(self.screen, animated_color, rect, border_radius=2)
                    
                    # Draw damage cracks for damaged cells
                    if health_ratio < 1.0:
                        self._draw_cell_damage(x, y, health_ratio, base_color)
                    
        self.screen.blit(self.glow_surface, (0, 0), special_flags=pygame.BLEND_ADD)
    
    def _draw_cell_damage(self, x: int, y: int, health_ratio: float, color: Tuple[int, int, int]) -> None:
        """Draw damage indicator on cell."""
        cell_size = self.config.CELL_SIZE
        cx = x * cell_size + cell_size // 2
        cy = y * cell_size + cell_size // 2
        
        # More cracks as health decreases
        crack_alpha = int(200 * (1 - health_ratio))
        crack_color = (255, 100, 50, crack_alpha)
        
        crack_surf = pygame.Surface((cell_size, cell_size), pygame.SRCALPHA)
        
        if health_ratio <= 0.66:
            # First crack
            pygame.draw.line(crack_surf, crack_color, (2, 2), (cell_size-2, cell_size-2), 1)
        if health_ratio <= 0.33:
            # Second crack
            pygame.draw.line(crack_surf, crack_color, (cell_size-2, 2), (2, cell_size-2), 1)
            
        self.screen.blit(crack_surf, (x * cell_size, y * cell_size))
        
    def draw_placement_zones(self, grid: GameOfLifeGrid, players: List[Player], 
                             time: int, hover_pos: Optional[Tuple[int, int]]) -> None:
        """Draw placement zones during placement phase."""
        cell_size = self.config.CELL_SIZE
        placing_width = self.config.PLACING_WIDTH
        
        # Player zones
        for player in players:
            is_p1 = player.id == 1
            zone_surf = pygame.Surface(
                (placing_width * cell_size, self.config.SCREEN_HEIGHT), 
                pygame.SRCALPHA
            )
            
            for x in range(placing_width):
                fade = (1 - x / placing_width * 0.8) if is_p1 else (x / placing_width * 0.8 + 0.2)
                base_alpha = int(30 + math.sin(time * 0.03 + x * 0.1) * 10)
                
                if is_p1:
                    zone_color = (0, 180, 220, int(base_alpha * fade))
                    grid_color = (0, 150, 180, int(60 * fade))
                else:
                    zone_color = (220, 0, 180, int(base_alpha * fade))
                    grid_color = (180, 0, 150, int(60 * fade))
                    
                for y in range(grid.height):
                    rect = pygame.Rect(x * cell_size, y * cell_size, cell_size, cell_size)
                    pygame.draw.rect(zone_surf, zone_color, rect)
                    pygame.draw.rect(zone_surf, grid_color, rect, 1)
                    
            zone_x = 0 if is_p1 else (self.config.GRID_WIDTH - placing_width) * cell_size
            self.screen.blit(zone_surf, (zone_x, 0))
            
        # Hover preview
        if hover_pos:
            self._draw_hover_preview(grid, players, hover_pos, time)
            
        # Draw placed cells
        self._draw_placed_cells(grid, time)
        
        # Boundary lines
        self._draw_boundary_lines(time)
        
        # Zone labels
        self._draw_zone_labels()
        
    def _draw_hover_preview(self, grid: GameOfLifeGrid, players: List[Player], 
                           hover_pos: Tuple[int, int], time: int) -> None:
        """Draw cell placement preview at hover position."""
        hx, hy = hover_pos
        cell_size = self.config.CELL_SIZE
        
        if not (0 <= hx < grid.width and 0 <= hy < grid.height):
            return
            
        for player in players:
            if player.is_in_zone(hx):
                hover_rect = pygame.Rect(hx * cell_size, hy * cell_size, cell_size, cell_size)
                hover_pulse = abs(math.sin(time * 0.15)) * 0.5 + 0.5
                
                if not grid.is_alive(hx, hy) and player.can_place():
                    # Placement preview (only if player has cells remaining)
                    preview_color = (*player.color, int(150 * hover_pulse))
                    hover_surf = pygame.Surface((cell_size, cell_size), pygame.SRCALPHA)
                    pygame.draw.rect(hover_surf, preview_color, hover_surf.get_rect(), border_radius=2)
                    pygame.draw.rect(hover_surf, (*player.color, 200), hover_surf.get_rect(), 2, border_radius=2)
                    self.screen.blit(hover_surf, hover_rect.topleft)
                elif grid.is_alive(hx, hy):
                    # Removal preview (always available for existing cells)
                    remove_surf = pygame.Surface((cell_size, cell_size), pygame.SRCALPHA)
                    pygame.draw.rect(remove_surf, (255, 50, 50, int(100 * hover_pulse)), remove_surf.get_rect())
                    pygame.draw.line(remove_surf, (255, 100, 100, 200), (2, 2), (cell_size-2, cell_size-2), 2)
                    pygame.draw.line(remove_surf, (255, 100, 100, 200), (cell_size-2, 2), (2, cell_size-2), 2)
                    self.screen.blit(remove_surf, hover_rect.topleft)
                break
                
    def _draw_placed_cells(self, grid: GameOfLifeGrid, time: int) -> None:
        """Draw cells that have been placed."""
        cell_size = self.config.CELL_SIZE
        
        for y in range(grid.height):
            for x in range(grid.width):
                if grid.is_alive(x, y):
                    rect = pygame.Rect(x * cell_size, y * cell_size, cell_size - 1, cell_size - 1)
                    color = self.get_cell_color(x, time)
                    pulse = math.sin(time * 0.1 + x * 0.1 + y * 0.1) * 0.3 + 0.7
                    animated_color = tuple(int(c * pulse) for c in color)
                    
                    self.draw_glow_rect(self.screen, color, rect, intensity=4)
                    pygame.draw.rect(self.screen, animated_color, rect, border_radius=2)
                    pygame.draw.rect(self.screen, tuple(min(255, int(c * 1.3)) for c in color), 
                                   rect, 1, border_radius=2)
                    
    def _draw_boundary_lines(self, time: int) -> None:
        """Draw animated boundary lines between zones."""
        glow_intensity = abs(math.sin(time * 0.05)) * 0.5 + 0.5
        wave_offset = math.sin(time * 0.02) * 3
        cell_size = self.config.CELL_SIZE
        placing_width = self.config.PLACING_WIDTH
        
        # Left boundary
        left_x = placing_width * cell_size
        left_color = tuple(int(c * glow_intensity) for c in self.colors.NEON_CYAN)
        
        for i in range(10):
            alpha = int(255 / (i + 1))
            pygame.draw.line(self.screen, (*left_color, alpha),
                           (left_x - i + wave_offset, 0),
                           (left_x - i - wave_offset, self.config.SCREEN_HEIGHT), 2)
            pygame.draw.line(self.screen, (*left_color, alpha),
                           (left_x + i + wave_offset, 0),
                           (left_x + i - wave_offset, self.config.SCREEN_HEIGHT), 2)
                           
        # Right boundary
        right_x = (self.config.GRID_WIDTH - placing_width) * cell_size
        right_color = tuple(int(c * glow_intensity) for c in self.colors.NEON_PINK)
        
        for i in range(10):
            alpha = int(255 / (i + 1))
            pygame.draw.line(self.screen, (*right_color, alpha),
                           (right_x - i - wave_offset, 0),
                           (right_x - i + wave_offset, self.config.SCREEN_HEIGHT), 2)
            pygame.draw.line(self.screen, (*right_color, alpha),
                           (right_x + i - wave_offset, 0),
                           (right_x + i + wave_offset, self.config.SCREEN_HEIGHT), 2)
                           
    def _draw_zone_labels(self) -> None:
        """Draw zone label text."""
        cell_size = self.config.CELL_SIZE
        placing_width = self.config.PLACING_WIDTH
        
        # P1 label
        p1_text = self.zone_font.render("P1 ZONE", True, self.colors.NEON_CYAN)
        p1_bg = pygame.Surface((p1_text.get_width() + 20, p1_text.get_height() + 10), pygame.SRCALPHA)
        pygame.draw.rect(p1_bg, (0, 40, 50, 180), p1_bg.get_rect(), border_radius=5)
        pygame.draw.rect(p1_bg, self.colors.NEON_CYAN, p1_bg.get_rect(), 1, border_radius=5)
        p1_bg.blit(p1_text, (10, 5))
        self.screen.blit(p1_bg, (placing_width * cell_size // 2 - p1_bg.get_width() // 2, 70))
        
        # P2 label
        p2_text = self.zone_font.render("P2 ZONE", True, self.colors.NEON_PINK)
        p2_bg = pygame.Surface((p2_text.get_width() + 20, p2_text.get_height() + 10), pygame.SRCALPHA)
        pygame.draw.rect(p2_bg, (50, 0, 40, 180), p2_bg.get_rect(), border_radius=5)
        pygame.draw.rect(p2_bg, self.colors.NEON_PINK, p2_bg.get_rect(), 1, border_radius=5)
        p2_bg.blit(p2_text, (10, 5))
        p2_x = (self.config.GRID_WIDTH - placing_width // 2) * cell_size - p2_bg.get_width() // 2
        self.screen.blit(p2_bg, (p2_x, 70))
        
    def draw_ball(self, ball: Ball, trail: List[Tuple[int, int]], time: int) -> None:
        """Draw ball with trail and glow effects."""
        # Trail
        speed_ratio = ball.speed / self.config.BALL_MAX_SPEED
        for i, pos in enumerate(trail):
            alpha = int(255 * (i / len(trail)) * 0.5 * (0.5 + speed_ratio * 0.5))
            size = int(self.config.BALL_RADIUS * 0.6 * (i / len(trail)))
            if size > 0:
                trail_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                pygame.draw.circle(trail_surf, (*self.colors.NEON_GREEN, alpha), (size, size), size)
                self.screen.blit(trail_surf, (pos[0] - size, pos[1] - size))
                
        # Ball with glow
        glow_intensity = int(3 + speed_ratio * 4)
        self.draw_glow_circle(self.colors.NEON_GREEN, (int(ball.x), int(ball.y)), 
                             self.config.BALL_RADIUS, glow_intensity)
        
        # Core
        core_pulse = abs(math.sin(time * 0.2 + ball.speed * 0.1)) * 0.3 + 0.7
        core_size = int(self.config.BALL_RADIUS * 0.4 * core_pulse)
        pygame.draw.circle(self.screen, self.colors.WHITE, (int(ball.x), int(ball.y)), core_size)
        
    def draw_particles(self, particles: List[Particle]) -> None:
        """Draw all active particles."""
        for p in particles:
            size = p.current_size
            if size > 0:
                glow_surf = pygame.Surface((size * 4, size * 4), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (*p.color, p.alpha // 3), (size * 2, size * 2), size * 2)
                pygame.draw.circle(glow_surf, (*p.color, p.alpha), (size * 2, size * 2), size)
                self.screen.blit(glow_surf, (int(p.x - size * 2), int(p.y - size * 2)))
                
    def draw_scores(self, players: List[Player], time: int) -> None:
        """Draw score display (semi-transparent)."""
        # Semi-transparent background
        score_width, score_height = 240, 80
        score_surf = pygame.Surface((score_width, score_height), pygame.SRCALPHA)
        pygame.draw.rect(score_surf, (20, 20, 40, 140), score_surf.get_rect(), border_radius=10)
        pygame.draw.rect(score_surf, (*self.colors.NEON_PURPLE, 180), score_surf.get_rect(), 2, border_radius=10)
        
        # Scores
        for player in players:
            score_text = self.score_font.render(str(player.score), True, player.color)
            x_offset = 40 if player.id == 1 else 160
            score_surf.blit(score_text, (x_offset, 5))
            
        # Separator
        sep_pulse = abs(math.sin(time * 0.1)) * 0.5 + 0.5
        sep_color = tuple(int(c * sep_pulse) for c in self.colors.NEON_PURPLE)
        sep_text = self.score_font.render(":", True, sep_color)
        score_surf.blit(sep_text, (110, 2))
        
        self.screen.blit(score_surf, (self.config.SCREEN_WIDTH // 2 - score_width // 2, 10))
        
    def draw_placement_ui(self, players: List[Player], time: int) -> None:
        """Draw placement phase UI elements."""
        pulse = abs(math.sin(time * 0.05)) * 0.4 + 0.6
        
        # Title
        title = self.title_font.render("LIFEPONG", True, self.colors.NEON_GREEN)
        shadow = self.title_font.render("LIFEPONG", True, (0, 50, 0))
        self.screen.blit(shadow, (self.config.SCREEN_WIDTH // 2 - shadow.get_width() // 2 + 3,
                                  self.config.SCREEN_HEIGHT // 2 - 100 + 3))
        self.screen.blit(title, (self.config.SCREEN_WIDTH // 2 - title.get_width() // 2,
                                 self.config.SCREEN_HEIGHT // 2 - 100))
        
        # Start prompt
        start_color = tuple(int(c * pulse) for c in self.colors.WHITE)
        start_text = self.font.render("[ Press SPACE to Start ]", True, start_color)
        self.screen.blit(start_text, (self.config.SCREEN_WIDTH // 2 - start_text.get_width() // 2,
                                      self.config.SCREEN_HEIGHT // 2 + 10))
        
        # Player info boxes (semi-transparent)
        for player in players:
            is_p1 = player.id == 1
            x = 15 if is_p1 else self.config.SCREEN_WIDTH - 195
            box_width, box_height = 180, 80
            box = pygame.Rect(x, self.config.SCREEN_HEIGHT // 2 - 50, box_width, box_height)
            
            # Create semi-transparent surface
            box_surf = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
            bg_color = (15, 25, 35, 140) if is_p1 else (25, 15, 25, 140)
            pygame.draw.rect(box_surf, bg_color, box_surf.get_rect(), border_radius=10)
            pygame.draw.rect(box_surf, (*player.color, 180), box_surf.get_rect(), 2, border_radius=10)
            
            label = self.font.render(f"PLAYER {player.id}", True, player.color)
            cells_text = self.font.render(f"Cells: {player.cells_remaining}", True, self.colors.WHITE)
            
            box_surf.blit(label, (10, 5))
            box_surf.blit(cells_text, (10, 40))
            self.screen.blit(box_surf, box.topleft)
            
    def draw_speed_indicator(self, ball: Ball) -> None:
        """Draw ball speed indicator bar."""
        speed_ratio = ball.speed / self.config.BALL_MAX_SPEED
        bar_width = int(100 * speed_ratio)
        
        bg_rect = pygame.Rect(self.config.SCREEN_WIDTH // 2 - 50, self.config.SCREEN_HEIGHT - 25, 100, 8)
        bar_rect = pygame.Rect(self.config.SCREEN_WIDTH // 2 - 50, self.config.SCREEN_HEIGHT - 25, bar_width, 8)
        
        pygame.draw.rect(self.screen, (30, 30, 50), bg_rect, border_radius=4)
        
        speed_color = (
            int(50 + speed_ratio * 205),
            int(255 - speed_ratio * 200),
            50
        )
        pygame.draw.rect(self.screen, speed_color, bar_rect, border_radius=4)
        
    def draw_scanlines(self) -> None:
        """Draw retro scanline effect."""
        for y in range(0, self.config.SCREEN_HEIGHT, 4):
            pygame.draw.line(self.screen, (0, 0, 0, 30), (0, y), (self.config.SCREEN_WIDTH, y), 1)
