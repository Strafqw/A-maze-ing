import json


def read_confs(confs_file: str = "config.txt"):
    try:
        config = {}

        int_measures = ["WIDTH", "HEIGHT", "ENTRY", "EXIT"]
        with open(confs_file) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                key, value = line.split("=", 1)
                config[key.strip()] = value.strip()

    except Exception as e:
        raise type(e) (f"Error on read_confs | {e}")

    print(json.dumps(config, indent=2))

import random
# DFS   depth first 
# BFS   

EAST  = 0b1000
NORTH = 0b0100
WEST  = 0b0010
SOUTH = 0b0001

DIRECTIONS = [
    (EAST,  1,  0),
    (NORTH, 0, -1),
    (WEST, -1,  0),
    (SOUTH, 0,  1),
]
OPPOSITE = {
    EAST: WEST,
    WEST: EAST,
    NORTH: SOUTH,
    SOUTH: NORTH
}

ENTRY = 0, 0
SEED = 0

class Maze:
    def __init__(self, width, height):
        self.grid = self.generate_maze(width, height)


    def generate_maze(self, width, height):
        # creates all cells with 4 walls
        grid = [[0b1111 for _ in range(width)] for _ in range(height)]
        visited = [[False]*width for _ in range(height)]
        stack = [(ENTRY[1], ENTRY[0])]
        print(f"stack is {stack}")
        visited[ENTRY[1]][ENTRY[0]] = True

        while stack:
            x, y = stack[-1]            # Last visited cell
            found = False

            dirs = DIRECTIONS[:]
            random.shuffle(dirs)    # if I don't shuffle them, I will get always the same maze

            for direction, dx, dy in dirs:
                nx, ny = x + dx, y + dy

                if 0 <= nx < width and 0 <= ny < height and not visited[ny][nx]:
                    grid[y][x] &= ~direction
                    grid[ny][nx] &= ~OPPOSITE[direction]

                    visited[ny][nx] = True
                    stack.append((nx, ny))  # go deeper
                    found = True
                    break

            if not found:
                stack.pop()  # backtrack
        return grid


    # print(DIRECTIONS)
    # print()
    # dirs = DIRECTIONS[:]
    # random.shuffle(dirs)
    # print(dirs)
    # print()

    # for _ in visited:
    #     print(_)



# just to visualize and know if it is working
def draw_ascii(grid):
    h = len(grid)
    w = len(grid[0])

    for y in range(h):
        # top walls
        top = ""
        mid = ""

        for x in range(w):
            cell = grid[y][x]

            top += "┼───" if cell & NORTH else "┼   "

            mid += "│   " if cell & WEST else "    "

            if x == w - 1:
                mid += "│" if cell & EAST else " "

        print(top + "┼")
        print(mid)

    print("┼" + "───┼" * w)


maze = Maze(10,10)
for _ in maze.grid:
    print(_)
draw_ascii(maze.grid)
