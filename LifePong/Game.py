"""
A "creative" game by combination of two games named Pong and Conway's Game Of Life.
One of them is multiplayer and the other zero player game which make me think, Is this game Zero, One or Multiplayer?

Mahan "Noosh" Nourhosseinalipour
December 2024
"""

import pygame
import pickle  # For saving and loading the grid
# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 1200, 600
CELL_SIZE = 10
GRID_WIDTH = SCREEN_WIDTH // CELL_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // CELL_SIZE
FPS = 30
PLACING_WIDTH = 40  # Columns designated for player placement

# Colors
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)

# Ball Settings
BALL_SIZE = 15
BALL_SPEED = [5, 5]

# Initialize Screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("LifePong")

# Fonts
font = pygame.font.SysFont(None, 60)


# Save grid to a file
def save_grid(grid, filename="saved_grid.pkl"):
    """
    Saves the current Game of Life grid to a file.

    Parameters:
        grid (list of lists): The current grid state.
        filename (str): The file name to save the grid.
    """
    with open(filename, "wb") as f:
        pickle.dump(grid, f)
    print("Grid saved successfully!")


# Load grid from a file
def load_grid(filename="saved_grid.pkl"):
    """
    Loads a previously saved grid from a file.

     Parameters:
        filename (str): The file name from which to load the grid.

    Returns:
        list of lists: The loaded grid state or a new empty grid if not found.
    """
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        print("No saved grid found!")
        return create_empty_grid()


# Create Game of Life Grid
def create_empty_grid():
    """
    Creates an empty Game of Life grid.

    Returns:
        list of lists: A grid initialized with all cells set to 0.
    """
    return [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]


def update_grid(grid):
    """
    Updates the grid based on Conway's Game of Life rules.

    Parameters:
        grid (list of lists): The current grid state.

    Returns:
        list of lists: The updated grid state.
    """
    new_grid = [[0] * GRID_WIDTH for _ in range(GRID_HEIGHT)]
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            # Count live neighbors
            neighbors = sum(
                grid[(y + dy) % GRID_HEIGHT][(x + dx) % GRID_WIDTH]
                for dy in [-1, 0, 1]
                for dx in [-1, 0, 1]
                if (dx != 0 or dy != 0)
            )
            # Apply Conway's Game of Life rules
            if grid[y][x] == 1 and neighbors in [2, 3]:
                new_grid[y][x] = 1
            elif grid[y][x] == 0 and neighbors == 3:
                new_grid[y][x] = 1
    return new_grid


# Draw the grid
def draw_grid(grid, game_started):
    """
    Draws the grid and placement boundaries on the screen.

    Parameters:
        grid (list of lists): The current grid state.
        game_started (bool): Indicates if the game has started.
    """
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            color = WHITE if grid[y][x] == 1 else BLACK
            pygame.draw.rect(
                screen, color, pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            )

    # Draw placement boundaries
    if not game_started:
        pygame.draw.line(screen, GRAY, (10 * CELL_SIZE, 0), (10 * CELL_SIZE, SCREEN_HEIGHT), 2)
        pygame.draw.line(screen, GRAY, ((GRID_WIDTH - 10) * CELL_SIZE, 0), ((GRID_WIDTH - 10)
                                                                            * CELL_SIZE, SCREEN_HEIGHT), 2)
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                color = WHITE if grid[y][x] == 1 else BLACK
                pygame.draw.rect(screen, color, rect)
                # Draw border for each cell
                pygame.draw.rect(screen, (50, 50, 50), rect, 1)  # Gray border


# Ball Initialization
ball = pygame.Rect(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, BALL_SIZE, BALL_SIZE)
ball_speed = BALL_SPEED[:]
grid = create_empty_grid()
player1_cells = 40
player2_cells = 40
start_ticks = 0


# Reset Game
def reset_game():
    """
    Resets the game to its initial state.
    """
    global grid, ball, ball_speed, player1_cells, player2_cells, start_ticks
    grid = create_empty_grid()
    ball = pygame.Rect(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, BALL_SIZE, BALL_SIZE)
    ball_speed = BALL_SPEED[:]
    start_ticks = pygame.time.get_ticks()


# Main Game Loop
def main():
    """
    Main game loop for LifePong.
    """
    global grid, ball, ball_speed, start_ticks, player1_cells, player2_cells
    clock = pygame.time.Clock()
    game_started = False  # Track whether the game has started
    player1_score = 0
    player2_score = 0

    # Dragging-related variables
    mouse_down = False
    placing_cells = True  # True = placing cells, False = removing cells

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not game_started:
                    save_grid(grid)
                    game_started = True

            if event.type == pygame.MOUSEBUTTONDOWN and not game_started:
                mouse_x, mouse_y = event.pos
                grid_x, grid_y = mouse_x // CELL_SIZE, mouse_y // CELL_SIZE
                mouse_down = True  # Start dragging

                # Determine placing or removing based on the initial cell state
                if 0 <= grid_y < GRID_HEIGHT:
                    if 0 <= grid_x < PLACING_WIDTH and player1_cells >= 0:
                        placing_cells = not grid[grid_y][grid_x]
                    elif GRID_WIDTH - PLACING_WIDTH <= grid_x < GRID_WIDTH and player2_cells >= 0:
                        placing_cells = not grid[grid_y][grid_x]

            if event.type == pygame.MOUSEBUTTONUP:
                mouse_down = False  # Stop dragging

        if mouse_down and not game_started:
            # Dragging logic: toggle cells as the mouse moves
            mouse_x, mouse_y = pygame.mouse.get_pos()
            grid_x, grid_y = mouse_x // CELL_SIZE, mouse_y // CELL_SIZE

            if 0 <= grid_y < GRID_HEIGHT:
                # Handling the first 50 columns for player 1
                if 0 <= grid_x < PLACING_WIDTH:
                    if player1_cells > 0 and placing_cells and grid[grid_y][grid_x] == 0:  # Placing cells
                        grid[grid_y][grid_x] = 1
                        player1_cells -= 1
                    elif not placing_cells and grid[grid_y][grid_x] == 1:  # Removing cells
                        grid[grid_y][grid_x] = 0
                        player1_cells += 1

                # Handling the last 50 columns for player 2
                elif GRID_WIDTH - PLACING_WIDTH <= grid_x < GRID_WIDTH:
                    if player2_cells > 0 and placing_cells and grid[grid_y][grid_x] == 0:  # Placing cells
                        grid[grid_y][grid_x] = 1
                        player2_cells -= 1
                    elif not placing_cells and grid[grid_y][grid_x] == 1:  # Removing cells
                        grid[grid_y][grid_x] = 0
                        player2_cells += 1

        if game_started:
            # Update ball position
            ball.x += ball_speed[0]
            ball.y += ball_speed[1]

            # Ball collision with walls
            if ball.top <= 0 or ball.bottom >= SCREEN_HEIGHT:
                ball_speed[1] = -ball_speed[1]

            # Ball collision with grid (bounces off "live" cells)
            next_x = (ball.left + ball_speed[0]) // CELL_SIZE
            next_y = (ball.top + ball_speed[1]) // CELL_SIZE

            if 0 <= next_x < GRID_WIDTH and 0 <= next_y < GRID_HEIGHT:
                if grid[next_y][ball.centerx // CELL_SIZE] == 1:  # Vertical collision
                    ball_speed[1] = -ball_speed[1]
                    ball.y += ball_speed[1]  # Adjust to prevent sticking

                if grid[ball.centery // CELL_SIZE][next_x] == 1:  # Horizontal collision
                    ball_speed[0] = -ball_speed[0]
                    ball.x += ball_speed[0]  # Adjust to prevent sticking

            # Update Game of Life grid
            grid = update_grid(grid)

            # Check for ball passing sides
            if ball.left <= 0:
                player2_score += 1
                reset_game()
                game_started = False  # Reset to placement mode
                grid = load_grid()  # Load grid here for placement mode
            elif ball.right >= SCREEN_WIDTH:
                player1_score += 1
                reset_game()
                game_started = False  # Reset to placement mode
                grid = load_grid()  # Load grid here for placement mode

        # Draw everything
        screen.fill(BLACK)
        draw_grid(grid, game_started)

        # Display game state
        font = pygame.font.SysFont("Arial", 24)
        if not game_started:
            start_text = font.render("Press SPACE to Start", True, WHITE)
            screen.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2, SCREEN_HEIGHT // 2
                                     - start_text.get_height()))
            # Draw vertical lines as boundaries
            pygame.draw.line(screen, GREEN, (PLACING_WIDTH * CELL_SIZE, 0), (PLACING_WIDTH
                                                                             * CELL_SIZE, SCREEN_HEIGHT), 2)
            pygame.draw.line(screen, GREEN, ((GRID_WIDTH - PLACING_WIDTH) * CELL_SIZE, 0),
                             ((GRID_WIDTH - PLACING_WIDTH) * CELL_SIZE, SCREEN_HEIGHT), 2)
            # Display player grids remaining
            p1_text = font.render(f"Remaining: {player1_cells}", True, RED)
            p2_text = font.render(f"Remaining: {player2_cells}", True, BLUE)
            screen.blit(p1_text, (20, SCREEN_HEIGHT // 2 - 20))
            screen.blit(p2_text, (SCREEN_WIDTH - p2_text.get_width() - 20, SCREEN_HEIGHT // 2 - 20))
        else:
            pygame.draw.ellipse(screen, GREEN, ball)

        # Display scores
        score_text = font.render(f"{player1_score}                       {player2_score}", True, WHITE)
        screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 20))
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
