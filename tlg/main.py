#!/bin/python

import pygame
import random
import asyncio
import sys

# Define the size of the game window and the size of each block
WINDOW_WIDTH = 200
WINDOW_HEIGHT = 600
BLOCK_SIZE = 20

BACKGROUND_COLOR = (255, 255, 255)

OUTLINE_WIDTH = 1
OUTLINE_COLOR = (0, 0, 0)

FPS = 20

# Define the colors for the shapes
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

PINK = (255, 128, 171)
MINT = (0, 255, 127)
PERIWINKLE = (0, 191, 255)
PEACH = (235, 235, 20)
ORANGE =  (255, 165, 0)
PURPLE = (153, 50, 204)
CREAM = (20, 235, 235)

BLOCK_COLORS = [
    PINK,
    MINT,
    PERIWINKLE,
    PEACH,
    ORANGE,
    PURPLE,
    CREAM
]

# Define the shapes as a list of lists of blocks
SHAPES = [
    [[1, 1, 1],
     [0, 1, 0]],
    [[2, 2],
     [2, 2]],
    [[0, 3, 3],
     [3, 3, 0]],
    [[4, 4, 0],
     [0, 4, 4]],
    [[5, 0, 0],
     [5, 5, 5]],
    [[0, 0, 6],
     [6, 6, 6]],
    [[7, 7, 7, 7]]
]

GRID_WIDTH = WINDOW_WIDTH // BLOCK_SIZE
GRID_HEIGHT = WINDOW_HEIGHT // BLOCK_SIZE

SCORE_WIDTH = 150

# Create the game window
screen = pygame.display.set_mode((WINDOW_WIDTH + SCORE_WIDTH, WINDOW_HEIGHT))

running = True
# Define the initial piece speed in grid moves per second
piece_speed = 5
fall_delay = 1000 // piece_speed

score = 0

game_over = False 

# Initialize the grid to all zeros
grid = []
for i in range(GRID_HEIGHT):
    row = [0] * GRID_WIDTH
    grid.append(row)

# Define a function to check for collisions between a piece and the grid
def check_collision(piece, grid):
    shape = piece["shape"]
    x = piece["x"]
    y = piece["y"]
    for i in range(len(shape)):
        for j in range(len(shape[i])):
            if shape[i][j] != 0:
                pos_x = x + j
                pos_y = y + i
                if pos_y >= GRID_HEIGHT or grid[pos_y][pos_x] != 0:
                    return True
    return False

# Define a function to add a piece to the grid
def add_piece_to_grid(piece, grid):
    shape = piece["shape"]
    x = piece["x"]
    y = piece["y"]
    color = BLOCK_COLORS.index(piece["color"]) + 1
    for i in range(len(shape)):
        for j in range(len(shape[i])):
            if shape[i][j] != 0:
                pos_x = x + j
                pos_y = y + i
                grid[pos_y][pos_x] = color

# Define a function to generate a new piece
def new_piece():
    shape = random.choice(SHAPES)
    color = random.choice(BLOCK_COLORS)
    x = random.randint(0, GRID_WIDTH - len(shape[0]))
    y = 0
    piece = {
        "shape": shape,
        "color": color,
        "x": x,
        "y": y,
    }
    return piece

# Define a function to draw a piece on the screen
def draw_piece_at(piece, x, y):
    shape = piece["shape"]
    color = piece["color"]
    for i in range(len(shape)):
        for j in range(len(shape[i])):
            if shape[i][j] != 0:
                pos_x = (x + j) * BLOCK_SIZE
                pos_y = (y + i) * BLOCK_SIZE
                rect = pygame.Rect(pos_x, pos_y, BLOCK_SIZE, BLOCK_SIZE)
                pygame.draw.rect(screen, color, rect)
                pygame.draw.rect(screen, OUTLINE_COLOR, rect, OUTLINE_WIDTH)

def draw_piece(piece):
    draw_piece_at(piece, piece["x"], piece["y"])

# Define a function to draw the grid on the screen
def draw_grid(grid):
    for i in range(GRID_HEIGHT):
        for j in range(GRID_WIDTH):
            color = BLOCK_COLORS[grid[i][j] - 1] if grid[i][j] != 0 else BACKGROUND_COLOR
            pos_x = j * BLOCK_SIZE
            pos_y = i * BLOCK_SIZE
            rect = pygame.Rect(pos_x, pos_y, BLOCK_SIZE, BLOCK_SIZE)
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, OUTLINE_COLOR, rect, OUTLINE_WIDTH)

def get_left_edge(piece):
    shape = piece["shape"]
    left_edge = len(shape[0])
    for row in shape:
        # Find the index of the first non-zero element in the row
        row_edge = next((i for i, x in enumerate(row) if x != 0), len(row))
        # Update the left edge if necessary
        if row_edge < left_edge:
            left_edge = row_edge
    return left_edge

def get_right_edge(piece):
    shape = piece["shape"]
    right_edge = 0
    for row in shape:
        # Find the index of the last non-zero element in the row
        row_edge = next((i for i, x in reversed(list(enumerate(row))) if x != 0), -1)
        # Update the right edge if necessary
        if row_edge > right_edge:
            right_edge = row_edge
    return right_edge

def move_shape_right(current_piece):
    current_piece["x"] += 1
    if get_right_edge(current_piece) + current_piece["x"] >= GRID_WIDTH:
        current_piece["x"] -= 1
    if check_collision(current_piece, grid):
        current_piece["x"] -= 1
   
def move_shape_left(current_piece):
    current_piece["x"] -= 1
    if check_collision(current_piece, grid):
        current_piece["x"] += 1
    if get_left_edge(current_piece) + current_piece["x"] < 0:
        current_piece["x"] += 1 # move back to previous position

def rotate_clockwise(shape):
    return [list(col) for col in zip(*shape[::-1])]

def check_line_completion(grid):
    # TODO maybe make top row zeros always
    global score
    grid_height = len(grid)
    grid_width = len(grid[0])

    completed_lines = []
    for row in range(grid_height):
        if all(grid[row][col] != 0 for col in range(grid_width)):
            completed_lines.append(row)

    for line in sorted(completed_lines, reverse=False):
        for row in range(line, 0, -1):
            for col in range(grid_width):
                grid[row][col] = grid[row-1][col]
        
    score += len(completed_lines) * 10

def handle_piece_collided():
    global running, piece_speed, fall_delay, score, game_over, current_piece, next_piece
    add_piece_to_grid(current_piece, grid)
    check_line_completion(grid)
    current_piece = next_piece
    next_piece = new_piece()
    if check_collision(current_piece, grid):
        game_over = True

    # Reset speed if it was made faster with down arrow
    if piece_speed != 5:
        piece_speed = 5
        fall_delay = 1000 // piece_speed
    score += 1

def render_score(screen, score):
    global smallFont
    text = smallFont.render("Score: " + str(score), True, BLACK)
    text_rect = text.get_rect()
    text_rect.right = WINDOW_WIDTH + (SCORE_WIDTH) - 5
    text_rect.top = 10
    screen.blit(text, text_rect)

def render_next(screen, next_piece):
    global smallFont
    text = smallFont.render("Next", True, BLACK)
    text_rect = text.get_rect()
    text_rect.left = WINDOW_WIDTH + 38
    text_rect.top = 65
    screen.blit(text, text_rect)

    draw_piece_at(next_piece, GRID_WIDTH + 2, 5)

# Define the main function
async def main():
    global running, piece_speed, fall_delay, score, game_over, current_piece, next_piece, smallFont

    # Initialize Pygame
    pygame.init()

    largeFont = pygame.font.SysFont("arial", 32)
    smallFont = pygame.font.SysFont("arial", 22)

    # Set the title of the game window
    pygame.display.set_caption("TLG")

    # Create a clock to control the frame rate
    clock = pygame.time.Clock()    

    current_piece = new_piece()
    next_piece = new_piece()

    # Define the initial fall delay and counter
    fall_counter = 0

    paused = False

    while running:
        moved = False
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    move_shape_left(current_piece)
                    moved = True
                elif event.key == pygame.K_RIGHT and not moved:
                    move_shape_right(current_piece) 
                    moved = True
                elif event.key == pygame.K_DOWN and not moved:
                    piece_speed = 20
                    fall_delay = 1000 // piece_speed
                elif event.key == pygame.K_UP:
                    current_piece["shape"] = rotate_clockwise(current_piece["shape"])
                    right_edge = get_right_edge(current_piece)
                    # Check if the rotated shape is out of bounds
                    if right_edge + current_piece["x"] >= GRID_WIDTH:
                        # If so, and move the shape off the right edge
                        current_piece["x"] = GRID_WIDTH - (right_edge +1)
                    if get_left_edge(current_piece) + current_piece["x"] < 0:
                        # If so, move the shape shape off the left edge
                        current_piece["x"] = 0 
                elif event.key == pygame.K_SPACE and not moved:
                    # Move the current piece down, checking for collisions
                    while True:
                        current_piece["y"] += 1
                        if check_collision(current_piece, grid):
                            current_piece["y"] -= 1
                            handle_piece_collided()
                            break
                elif event.key == pygame.K_p or event.key == pygame.K_PAUSE:
                    paused = not paused
                elif event.key == pygame.K_ESCAPE:
                    running = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and not moved:
            move_shape_left(current_piece)
            moved = True
        if keys[pygame.K_RIGHT] and not moved:
            move_shape_right(current_piece)
            moved = True
        
        if game_over:
            game_over_text = largeFont.render("GAME OVER", True, RED)
            screen.blit(game_over_text, (20, WINDOW_HEIGHT // 2))
            moved = True
        elif paused:
            paused_text = largeFont.render("PAUSED", True, GREEN)
            screen.blit(paused_text, (20, WINDOW_HEIGHT // 2))
            moved = True
        else:
            # Move the current piece down
            fall_counter += clock.tick(FPS)
            if fall_counter >= fall_delay:
                # Move the current piece down
                current_piece["y"] += 1
                if check_collision(current_piece, grid):
                    current_piece["y"] -= 1
                    handle_piece_collided()

                fall_counter = 0

            # Clear the screen
            screen.fill((255, 255, 255))

            # Draw the pieces and the grid
            # for piece in current_pieces:
            draw_grid(grid)
            draw_piece(current_piece)

            render_score(screen, score)
            render_next(screen, next_piece)

        # Update the screen
        pygame.display.flip()

        # Tick the clock
        clock.tick(FPS)
        await asyncio.sleep(0)  # Very important, and keep it 0

    pygame.quit()

if __name__ == '__main__':
    if sys.platform != "emscripten":
        asyncio.run(main())

if sys.platform == "emscripten":
    asyncio.run(main())
