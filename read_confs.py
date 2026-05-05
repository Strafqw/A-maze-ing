# what is a non perfect maze? Do i have to develop one?

import json
import random
from vars import *


class Confs:
    def __init__(self, confs_file: str = "config.txt"):
        self.confs_file = confs_file
        self.config = self.read_confs()
        self.validate_config()

    def read_confs(self):
        try:
            config = {}

            coords = ["ENTRY", "EXIT"]
            int_measures = ["WIDTH", "HEIGHT"]
            with open(self.confs_file) as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    key, value = line.split("=", 1)
                    if key in int_measures:
                        config[key.strip()] = int(value.strip())
                    else:
                        config[key.strip()] = value.strip()

            print(json.dumps(config, indent=2))
            return config

        except Exception as e:
            raise type(e) (f"Error on read_confs | {e}")

    def validate_config(self):
        if self.config.get("WIDTH") < 9 or self.config.get("HEIGHT") < 7:
            raise (f"{self.config.get('WIDTH')} is less than 9. No 42")


class MazeGenerator:
    def __init__(self, config: dict):
        self.config  = config
        self.width   = self.config.get('WIDTH')
        self.height  = self.config.get('HEIGHT')
        self.ft_grid = None
        self.grid    = self.dfs(self.width, self.height)
        self.make_imperfect()

    def close_ft(self, visited: list, glip: list):
        for _ in glip:
            x, y = _
            visited[y + int(self.height / 2)  - 2][x + int(self.width / 2) - 3] = True
        self.ft_grid = [row[:] for row in visited]
        return visited

    def dfs(self, width, height):
        # creates all cells with 4 walls
        grid = [[0b1111 for _ in range(width)] for _ in range(height)]
        visited = [[False]*width for _ in range(height)]
        ft_closed = self.close_ft(visited, GLYPH_42)
        stack = [(ENTRY[1], ENTRY[0])]
        visited[ENTRY[0]][ENTRY[1]] = True
        if self.config.get("SEED") == '1':
            random.seed(10)

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

    def between_four_nodes(self, x: int, y: int) -> bool:
        if 0 < x < self.width - 1 and 0 < y < self.height - 1:
            return True
        return False

    def make_imperfect(self):
        if self.config.get('PERFECT') == 'True':
            return None
        dirs = DIRECTIONS[:]

        for y in range(self.height):
            next = True
            for x in range(self.width):
                for direction, dx, dy in dirs:
                    nx = x + dx
                    ny = y + dy

                    if 0 <= nx < self.width and 0 <= ny < self.height and next == True:
                        if not self.ft_grid[ny][nx] and not self.ft_grid[y][x] and next == True:
                            if self.between_four_nodes(x, y):
                                next = False
                                print(f"coords are {(x, y)}")
                                self.grid[y][x] &= ~direction
                                self.grid[ny][nx] &= ~OPPOSITE[direction]


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


config = Confs()
print(f"config = {config.config}")
maze = MazeGenerator(config.config)
# for _ in maze.grid:
#     print(_)
draw_ascii(maze.grid)
print(maze.grid[0][0])
