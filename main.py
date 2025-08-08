#!/usr/bin/env python3
"""
Tetris Game - Complete Implementation
A single-file Tetris-style game using Python and Pygame
"""

import pygame
import random
import time

# Game Setup & Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 700
GRID_WIDTH = 10
GRID_HEIGHT = 20
CELL_SIZE = 30
GRID_OFFSET_X = (SCREEN_WIDTH - GRID_WIDTH * CELL_SIZE) // 2
GRID_OFFSET_Y = (SCREEN_HEIGHT - GRID_HEIGHT * CELL_SIZE) // 2

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)

# Tetromino colors
COLORS = [BLACK, CYAN, YELLOW, MAGENTA, GREEN, RED, BLUE, ORANGE]

# Tetromino shapes (I, O, T, S, Z, J, L)
SHAPES = [
    # I piece
    [[1, 1, 1, 1]],
    # O piece
    [[1, 1],
     [1, 1]],
    # T piece
    [[0, 1, 0],
     [1, 1, 1]],
    # S piece
    [[0, 1, 1],
     [1, 1, 0]],
    # Z piece
    [[1, 1, 0],
     [0, 1, 1]],
    # J piece
    [[1, 0, 0],
     [1, 1, 1]],
    # L piece
    [[0, 0, 1],
     [1, 1, 1]]
]

class Piece:
    """Class to manage the current falling piece"""
    
    def __init__(self, shape_idx, color_idx):
        self.shape_idx = shape_idx
        self.color_idx = color_idx
        self.shape = SHAPES[shape_idx]
        self.x = GRID_WIDTH // 2 - len(self.shape[0]) // 2
        self.y = 0
        self.rotation = 0
    
    def get_rotated_shape(self):
        """Get the current shape with rotation applied"""
        shape = self.shape
        for _ in range(self.rotation):
            # Rotate 90 degrees clockwise
            shape = list(zip(*shape[::-1]))
            shape = [list(row) for row in shape]
        return shape
    
    def get_cells(self):
        """Get the current cells occupied by this piece"""
        rotated_shape = self.get_rotated_shape()
        cells = []
        for y, row in enumerate(rotated_shape):
            for x, cell in enumerate(row):
                if cell:
                    cells.append((self.x + x, self.y + y))
        return cells

def create_grid():
    """Create an empty game grid"""
    return [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

def get_random_piece():
    """Get a random tetromino piece"""
    shape_idx = random.randint(0, len(SHAPES) - 1)
    color_idx = shape_idx + 1  # Color index corresponds to shape index + 1
    return Piece(shape_idx, color_idx)

def is_valid_position(piece, grid):
    """Check if a piece's position is valid"""
    cells = piece.get_cells()
    for x, y in cells:
        # Check boundaries
        if x < 0 or x >= GRID_WIDTH or y >= GRID_HEIGHT:
            return False
        # Check collision with locked pieces (but allow y < 0 for spawning)
        if y >= 0 and grid[y][x] != 0:
            return False
    return True

def lock_piece(piece, grid):
    """Lock a piece into the grid"""
    cells = piece.get_cells()
    for x, y in cells:
        if 0 <= y < GRID_HEIGHT and 0 <= x < GRID_WIDTH:
            grid[y][x] = piece.color_idx

def clear_lines(grid):
    """Clear completed lines and return the number of lines cleared"""
    lines_cleared = 0
    y = GRID_HEIGHT - 1
    while y >= 0:
        if all(cell != 0 for cell in grid[y]):
            # Remove the completed line
            del grid[y]
            # Add a new empty line at the top
            grid.insert(0, [0 for _ in range(GRID_WIDTH)])
            lines_cleared += 1
        else:
            y -= 1
    return lines_cleared

def is_game_over(piece, grid):
    """Check if the game is over"""
    return not is_valid_position(piece, grid)

def draw_grid(screen):
    """Draw the grid lines"""
    for x in range(GRID_WIDTH + 1):
        pygame.draw.line(screen, GRAY,
                        (GRID_OFFSET_X + x * CELL_SIZE, GRID_OFFSET_Y),
                        (GRID_OFFSET_X + x * CELL_SIZE, GRID_OFFSET_Y + GRID_HEIGHT * CELL_SIZE))
    
    for y in range(GRID_HEIGHT + 1):
        pygame.draw.line(screen, GRAY,
                        (GRID_OFFSET_X, GRID_OFFSET_Y + y * CELL_SIZE),
                        (GRID_OFFSET_X + GRID_WIDTH * CELL_SIZE, GRID_OFFSET_Y + y * CELL_SIZE))

def draw_board(screen, grid):
    """Draw the locked pieces on the board"""
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if grid[y][x] != 0:
                color = COLORS[grid[y][x]]
                rect = pygame.Rect(GRID_OFFSET_X + x * CELL_SIZE + 1,
                                 GRID_OFFSET_Y + y * CELL_SIZE + 1,
                                 CELL_SIZE - 2, CELL_SIZE - 2)
                pygame.draw.rect(screen, color, rect)

def draw_piece(screen, piece):
    """Draw the current falling piece"""
    cells = piece.get_cells()
    color = COLORS[piece.color_idx]
    for x, y in cells:
        if 0 <= y < GRID_HEIGHT and 0 <= x < GRID_WIDTH:
            rect = pygame.Rect(GRID_OFFSET_X + x * CELL_SIZE + 1,
                             GRID_OFFSET_Y + y * CELL_SIZE + 1,
                             CELL_SIZE - 2, CELL_SIZE - 2)
            pygame.draw.rect(screen, color, rect)

def draw_window(screen, grid, piece, game_over=False):
    """Draw the complete game window"""
    screen.fill(BLACK)
    
    # Draw grid and board
    draw_grid(screen)
    draw_board(screen, grid)
    
    # Draw current piece if game is not over
    if not game_over:
        draw_piece(screen, piece)
    
    # Draw game over message
    if game_over:
        font = pygame.font.Font(None, 74)
        text = font.render('GAME OVER', True, RED)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(text, text_rect)
    
    pygame.display.flip()

def main():
    """Main game function"""
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Tetris")
    clock = pygame.time.Clock()
    
    # Game state
    grid = create_grid()
    current_piece = get_random_piece()
    next_piece = get_random_piece()
    
    # Timing
    fall_time = 0
    fall_speed = 0.5  # seconds per fall
    last_time = time.time()
    
    # Game loop
    running = True
    game_over = False
    
    while running:
        current_time = time.time()
        delta_time = current_time - last_time
        last_time = current_time
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if not game_over:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        current_piece.x -= 1
                        if not is_valid_position(current_piece, grid):
                            current_piece.x += 1
                    
                    elif event.key == pygame.K_RIGHT:
                        current_piece.x += 1
                        if not is_valid_position(current_piece, grid):
                            current_piece.x -= 1
                    
                    elif event.key == pygame.K_DOWN:
                        current_piece.y += 1
                        if not is_valid_position(current_piece, grid):
                            current_piece.y -= 1
                    
                    elif event.key == pygame.K_UP:
                        current_piece.rotation = (current_piece.rotation + 1) % 4
                        if not is_valid_position(current_piece, grid):
                            current_piece.rotation = (current_piece.rotation - 1) % 4
        
        if not game_over:
            # Handle automatic falling
            fall_time += delta_time
            if fall_time >= fall_speed:
                fall_time = 0
                current_piece.y += 1
                
                if not is_valid_position(current_piece, grid):
                    current_piece.y -= 1
                    lock_piece(current_piece, grid)
                    
                    # Clear completed lines
                    lines_cleared = clear_lines(grid)
                    
                    # Spawn new piece
                    current_piece = next_piece
                    next_piece = get_random_piece()
                    
                    # Check for game over
                    if is_game_over(current_piece, grid):
                        game_over = True
        
        # Draw everything
        draw_window(screen, grid, current_piece, game_over)
        
        # Cap the frame rate
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    main()
