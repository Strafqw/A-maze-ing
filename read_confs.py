# what is a non perfect maze? Do i have to develop one?

import json
import random
from collections import deque
from vars import *


class Confs:
    def __init__(self, confs_file: str = "config.txt"):
        self.confs_file = confs_file
        self.config = self.read_confs()
        self.validate_config()

    def read_confs(self):
        try:
            config = {}

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

            # print(json.dumps(config, indent=2))
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
        self.entry = [int(_) for _ in self.config.get('ENTRY').split(',')]
        self.exit = [int(_) for _ in self.config.get('EXIT').split(',')]
        self.ft_grid = None
        self.grid    = self.dfs(self.width, self.height)
        self.make_imperfect()
        print(f"is perfect? {self.is_perfect_maze()}")

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
        stack = [(self.entry[1], self.entry[0])]
        visited[self.entry[0]][self.entry[1]] = True
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

    def make_imperfect(self) -> None:
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
                                self.grid[y][x] &= ~direction
                                self.grid[ny][nx] &= ~OPPOSITE[direction]


    def is_perfect_maze(self, blocked = None) -> bool:

        """
        Returns True iff the maze is perfect (connected + no cycles),
        exploring from start_xy.

        - grid[y][x] is your wall-bitmask cell.
        - start_xy = (x, y) e.g. (self.entry[1], self.entry[0])
        - blocked: optional 2D bool (True = ignore cell), e.g. maze.ft_grid
        """
        h, w = len(self.grid), len(self.grid[0])
        sx, sy = self.entry

        if blocked is None:
            blocked = [[False] * w for _ in range(h)]

        if not (0 <= sx < w and 0 <= sy < h) or blocked[sy][sx]:
            return False

        visited = set()
        stack = [(sx, sy, None)]  # (x, y, parent_xy)

        while stack:
            x, y, parent = stack.pop()

            if (x, y) in visited:
                # revisited through another route => cycle
                return False

            visited.add((x, y))
            cell = self.grid[y][x]

            for direction, dx, dy in DIRECTIONS:
                if (cell & direction) == 0:  # passage is open
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h and not blocked[ny][nx]:
                        if parent is not None and (nx, ny) == parent:
                            continue  # ignore the edge back to parent
                        stack.append((nx, ny, (x, y)))

        return True



    def bfs_path(self, blocked=None) -> list:
        """
        Shortest path BFS from start_xy to goal_xy.
        Returns: list[(x,y), ...] or None if unreachable.

        - grid[y][x] = wall-bitmask
        - DIRECTIONS = [(WALLBIT, dx, dy), ...]
        - A passage is OPEN if (cell & WALLBIT) == 0
        - blocked: optional 2D bool, True means 'do not step on that cell'
        """

        w, h = self.width, self.height

        sx, sy = self.entry
        gx, gy = self.exit

        if blocked is None:
            blocked = [[False] * w for _ in range(h)]

        # bounds / blocked checks
        def ok(x, y):
            return 0 <= x < w and 0 <= y < h and not blocked[y][x]

        if not ok(sx, sy) or not ok(gx, gy):
            return None

        q = deque([(sx, sy)])
        parent = {(sx, sy): None}   # child -> parent

        while q:
            x, y = q.popleft()
            if (x, y) == (gx, gy):
                break

            cell = self.grid[y][x]
            for wall_bit, dx, dy in DIRECTIONS:
                # Only move if that wall is open
                if (cell & wall_bit) == 0:
                    nx, ny = x + dx, y + dy
                    if ok(nx, ny) and (nx, ny) not in parent:
                        parent[(nx, ny)] = (x, y)
                        q.append((nx, ny))

        # reconstruct path
        if (gx, gy) not in parent:
            return None

        path = []
        cur = (gx, gy)
        while cur is not None:
            path.append(cur)
            cur = parent[cur]
        path.reverse()
        return path


def build_state(config: dict) -> dict:
    """Generate a maze and bundle everything the visualizer needs."""
    maze = MazeGenerator(config)
    return {
        "grid": maze.grid,
        "entry": (maze.entry[0], maze.entry[1]),
        "exit": (maze.exit[0], maze.exit[1]),
        "path": maze.bfs_path(),
        "ft_grid": maze.ft_grid,
    }


def main():
    from visualizer import run

    config = Confs().config
    state = build_state(config)
    run(state, regenerate=lambda: build_state(config))


if __name__ == '__main__':
    main()
