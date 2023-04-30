#!/bin/python

import pygame
import random
import asyncio
import sys
import time

# Define the size of the game window and the size of each block
WINDOW_WIDTH = 200
WINDOW_HEIGHT = 600
BLOCK_SIZE = 20

BACKGROUND_COLOR = (255, 255, 255)

OUTLINE_WIDTH = 1
OUTLINE_COLOR = (0, 0, 0)

FPS = 30

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
BASE_SPEED = 5


# Create the game window
screen = pygame.display.set_mode((WINDOW_WIDTH + SCORE_WIDTH, WINDOW_HEIGHT))

running = True
# Define the initial piece speed in grid moves per second
piece_speed = BASE_SPEED
fall_delay = 1000 // piece_speed

piece_speed_boost = False

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

def top_control_rect_height(screen_height):
    return int(screen_height / 3)

def bottom_control_rect_height(screen_height):
    return int(3 * screen_height / 4)

def left_right_control_rect_width(screen_width):
    return screen_width / 2

def check_line_completion(grid):
    global score
    row_idx = 0
    while row_idx < len(grid):
        # If the row has no zeros, remove it and add an empty row at the top
        if not any(cell == 0 for cell in grid[row_idx]):
            grid.pop(row_idx)
            grid.insert(0, [0] * len(grid[0]))
            score += 10
        else:
            row_idx += 1

def handle_piece_collided():
    global running, piece_speed, score, game_over, current_piece, next_piece, piece_speed_boost
    add_piece_to_grid(current_piece, grid)
    check_line_completion(grid)
    current_piece = next_piece
    next_piece = new_piece()
    if check_collision(current_piece, grid):
        game_over = True

    piece_speed_boost = False
    score += 1

def handle_shape_rotate(current_piece):
    current_piece["shape"] = rotate_clockwise(current_piece["shape"])
    right_edge = get_right_edge(current_piece)
        # Check if the rotated shape is out of bounds
    if right_edge + current_piece["x"] >= GRID_WIDTH:
        # If so, and move the shape off the right edge
        current_piece["x"] = GRID_WIDTH - (right_edge +1)
    if get_left_edge(current_piece) + current_piece["x"] < 0:
        # If so, move the shape shape off the left edge
        current_piece["x"] = 0

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

def render_control_areas():
    global smallFont
    screen_width, screen_height = screen.get_size()
    top_height = top_control_rect_height(screen_height)
    bottom_height = bottom_control_rect_height(screen_height)

    # Draw control rectangle outlines
    colors = [PINK, MINT, PERIWINKLE, ORANGE]
    rects = [pygame.Rect(0, 0, screen_width, top_height),
             pygame.Rect(0, top_height, screen_width // 2, bottom_height - top_height),
             pygame.Rect(left_right_control_rect_width(screen_width), top_height, left_right_control_rect_width(screen_width), bottom_height - top_height),
             pygame.Rect(0, bottom_height, screen_width, screen_height - bottom_height)]

    for color, rect in zip(colors, rects):
        pygame.draw.rect(screen, color, rect, 2)

    # Render lables
    text_labels = [('rotate', colors[0]),
                   ('left', colors[1]),
                   ('right', colors[2]),
                   ('down', colors[3])]
    
    for i, (label, color) in enumerate(text_labels):
        text = smallFont.render(label, True, color)
        text_rect = text.get_rect(center=rects[i].center)
        screen.blit(text, text_rect)

def set_speed(new_speed):
    global speed, fall_delay
    speed = new_speed
    fall_delay = 1000 // speed

def update_speed_for_score():
    global speed, score
    score_speed_penalty = score // 50
    new_speed = BASE_SPEED + score_speed_penalty
    set_speed(new_speed) 

# Define the main function
async def main():
    global running, piece_speed, fall_delay, score, game_over, current_piece, next_piece, smallFont, piece_speed_boost

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

    click_counter = 0
    start_time = 0

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
                    piece_speed_boost = True
                elif event.key == pygame.K_UP:
                    handle_shape_rotate(current_piece) 
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
            elif event.type == pygame.MOUSEBUTTONDOWN and not moved:
                x, y = event.pos
                screen_width, screen_height = screen.get_size()
                
                if click_counter == 0:
                    start_time = time.time()

                click_counter += 1

                # Check if the click is on the top or bottom 1/3 of the screen
                if y < top_control_rect_height(screen_height):
                    handle_shape_rotate(current_piece)
                elif y > bottom_control_rect_height(screen_height):
                    piece_speed_boost = True
                # Check if the click is on the left or right half of the screen
                elif x < left_right_control_rect_width(screen_width):
                    move_shape_left(current_piece)
                    moved = True
                else:
                    move_shape_right(current_piece) 
                    moved = True

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
            # Move the current piece down at normal speed, or 4x speed if speed boost is active 
            if fall_counter >= fall_delay or (piece_speed_boost and fall_counter >= (fall_delay//4)):
                # Move the current piece down
                current_piece["y"] += 1
                if check_collision(current_piece, grid):
                    current_piece["y"] -= 1
                    handle_piece_collided()
                fall_counter = 0

            update_speed_for_score()

            # Clear the screen
            screen.fill((255, 255, 255))

            # Draw the pieces and the grid
            # for piece in current_pieces:
            draw_grid(grid)
            draw_piece(current_piece)

            render_score(screen, score)
            render_next(screen, next_piece)

            # Draw control areas outlines if clicked less than 10 times and within 10 seconds of first click
            if click_counter > 0 and click_counter < 10 and time.time() - start_time < 10 :
                render_control_areas()

        # Update the screen
        pygame.display.flip()

        # Tick the clock
        clock.tick(FPS)
        await asyncio.sleep(0)
        
    pygame.quit()

if __name__ == '__main__':
    if sys.platform != "emscripten":
        asyncio.run(main())

if sys.platform == "emscripten":
    asyncio.run(main())
