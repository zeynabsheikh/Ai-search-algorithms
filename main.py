import pygame
import random
import math
import time
from queue import PriorityQueue

# CONFIGURATION

ROWS = 25
COLS = 25
WIDTH = 800
GRID_WIDTH = 600
CELL_SIZE = GRID_WIDTH // COLS

OBSTACLE_DENSITY = 0.30
DYNAMIC_PROBABILITY = 0.03

# COLORS

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)

# NODE CLASS

class Node:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.is_wall = False
        self.g = float("inf")
        self.h = 0
        self.f = float("inf")
        self.parent = None

    def position(self):
        return (self.row, self.col)


# HEURISTICS


def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def euclidean(a, b):
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)


# GRID FUNCTIONS


def create_grid():
    return [[Node(r, c) for c in range(COLS)] for r in range(ROWS)]

def randomize_walls(grid):
    for row in grid:
        for node in row:
            if random.random() < OBSTACLE_DENSITY:
                node.is_wall = True

def draw_grid(screen, grid, start, goal, frontier, visited, path):
    screen.fill(WHITE)

    for row in grid:
        for node in row:
            color = WHITE
            if node.is_wall:
                color = BLACK
            if node.position() in frontier:
                color = YELLOW
            if node.position() in visited:
                color = BLUE
            if node.position() in path:
                color = GREEN

            rect = pygame.Rect(node.col * CELL_SIZE,
                               node.row * CELL_SIZE,
                               CELL_SIZE,
                               CELL_SIZE)
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, GRAY, rect, 1)

    # Start & Goal
    pygame.draw.rect(screen, PURPLE,
                     (start.col * CELL_SIZE,
                      start.row * CELL_SIZE,
                      CELL_SIZE, CELL_SIZE))

    pygame.draw.rect(screen, RED,
                     (goal.col * CELL_SIZE,
                      goal.row * CELL_SIZE,
                      CELL_SIZE, CELL_SIZE))

# NEIGHBORS


def get_neighbors(grid, node):
    neighbors = []
    directions = [(1,0), (-1,0), (0,1), (0,-1)]
    for d in directions:
        r = node.row + d[0]
        c = node.col + d[1]
        if 0 <= r < ROWS and 0 <= c < COLS:
            if not grid[r][c].is_wall:
                neighbors.append(grid[r][c])
    return neighbors

# SEARCH ALGORITHMS


def reconstruct_path(end_node):
    path = []
    current = end_node
    while current.parent:
        path.append(current.position())
        current = current.parent
    return path

def search(grid, start, goal, heuristic_func, algorithm):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    start.g = 0
    start.h = heuristic_func(start.position(), goal.position())
    start.f = start.h

    frontier = set()
    visited = set()

    nodes_visited = 0
    start_time = time.time()

    while not open_set.empty():
        current = open_set.get()[2]
        nodes_visited += 1

        if current == goal:
            end_time = time.time()
            return reconstruct_path(current), frontier, visited, nodes_visited, (end_time - start_time)*1000

        visited.add(current.position())

        for neighbor in get_neighbors(grid, current):
            temp_g = current.g + 1

            if temp_g < neighbor.g:
                neighbor.parent = current
                neighbor.g = temp_g
                neighbor.h = heuristic_func(neighbor.position(), goal.position())

                if algorithm == "A*":
                    neighbor.f = neighbor.g + neighbor.h
                else:  # GBFS
                    neighbor.f = neighbor.h

                count += 1
                open_set.put((neighbor.f, count, neighbor))
                frontier.add(neighbor.position())

    return [], frontier, visited, nodes_visited, 0

# MAIN PROGRAM


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, GRID_WIDTH))
    pygame.display.set_caption("Dynamic Pathfinding Agent")

    grid = create_grid()
    randomize_walls(grid)

    start = grid[0][0]
    goal = grid[ROWS-1][COLS-1]
    start.is_wall = False
    goal.is_wall = False

    heuristic_func = manhattan
    algorithm = "A*"
    dynamic_mode = False

    running = True
    path = []
    frontier = set()
    visited = set()
    nodes = 0
    exec_time = 0

    font = pygame.font.SysFont(None, 24)

    while running:
        draw_grid(screen, grid, start, goal, frontier, visited, path)

        # Metrics Display
        info1 = font.render(f"Algorithm: {algorithm}", True, BLACK)
        info2 = font.render(f"Nodes Visited: {nodes}", True, BLACK)
        info3 = font.render(f"Path Cost: {len(path)}", True, BLACK)
        info4 = font.render(f"Execution Time: {round(exec_time,2)} ms", True, BLACK)
        info5 = font.render("Press SPACE to Search", True, BLACK)
        info6 = font.render("Press H to Toggle Heuristic", True, BLACK)
        info7 = font.render("Press G to Toggle Algorithm", True, BLACK)
        info8 = font.render("Press D for Dynamic Mode", True, BLACK)

        screen.blit(info1, (620, 20))
        screen.blit(info2, (620, 50))
        screen.blit(info3, (620, 80))
        screen.blit(info4, (620, 110))
        screen.blit(info5, (620, 160))
        screen.blit(info6, (620, 190))
        screen.blit(info7, (620, 220))
        screen.blit(info8, (620, 250))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if pygame.mouse.get_pressed()[0]:
                x, y = pygame.mouse.get_pos()
                if x < GRID_WIDTH:
                    row = y // CELL_SIZE
                    col = x // CELL_SIZE
                    grid[row][col].is_wall = not grid[row][col].is_wall

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_SPACE:
                    path, frontier, visited, nodes, exec_time = search(
                        grid, start, goal, heuristic_func, algorithm)

                if event.key == pygame.K_h:
                    heuristic_func = euclidean if heuristic_func == manhattan else manhattan

                if event.key == pygame.K_g:
                    algorithm = "GBFS" if algorithm == "A*" else "A*"

                if event.key == pygame.K_d:
                    dynamic_mode = not dynamic_mode

        # Dynamic Obstacles
        if dynamic_mode and path:
            if random.random() < DYNAMIC_PROBABILITY:
                r = random.randint(0, ROWS-1)
                c = random.randint(0, COLS-1)
                if (r, c) not in path and (r,c) != start.position() and (r,c) != goal.position():
                    grid[r][c].is_wall = True

    pygame.quit()

if __name__ == "__main__":
    main()