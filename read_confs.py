# what is a non perfect maze? Do i have to develop one?


import random
from vars import *

class MazeError(Exception):
    def __init__(self, message):
        super().__init__(message)


class Confs:
    def __init__(self, confs_file: str = "config.txt"):
        self.confs_file = confs_file
        self.config = self.read_confs()

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
        self.solution = None

    def close_ft(self, visited: list, glip: list) -> list:
        if self.width >= 9 and self.height >= 7:
            for _ in glip:
                x, y = _
                visited[y + int(self.height / 2)  - 2][x + int(self.width / 2) - 3] = True
            self.ft_grid = [row[:] for row in visited]
            if self.ft_grid[self.entry[1]][self.entry[0]] == True:
                raise MazeError(f"entry is in 42 symbol")
            if self.ft_grid[self.exit[1]][self.exit[0]] == True:
                raise MazeError(f"exit is in 42 symbol")
        else:
            for _ in glip:
                x, y = _
                visited[y][x] = False
                self.ft_grid = [row[:] for row in visited]
        return visited


    def dfs(self, width, height):
        # creates all cells with 4 walls (1111 = N,E,S,W closed)
        grid = [[0b1111 for _ in range(width)] for _ in range(height)]
        visited = [[False] * width for _ in range(height)]
           

        entry_x, entry_y = self.entry  # entry is [x, y]
        stack = [(entry_x, entry_y)]
        ft_closed = self.close_ft(visited, GLYPH_42)

        if self.config.get("SEED") == '1':
            random.seed(10)

        while stack:
            x, y = stack[-1]
            found = False

            dirs = DIRECTIONS[:]
            random.shuffle(dirs)

            for direction, dx, dy in dirs:
                nx, ny = x + dx, y + dy

                if 0 <= nx < width and 0 <= ny < height and not visited[ny][nx]:
                    # open passage between (x,y) and (nx,ny)
                    grid[y][x] &= ~direction
                    grid[ny][nx] &= ~OPPOSITE[direction]

                    visited[ny][nx] = True
                    stack.append((nx, ny))
                    found = True
                    break

            if not found:
                stack.pop()

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


    def bfs_path(self, blocked=None):
        """
        Shortest path BFS from start_xy to goal_xy.
        No deque: uses list + head index.
        Returns: list of (x,y) or None if unreachable.
        """
        w, h = self.width, self.height
        sx, sy = self.entry
        gx, gy = self.exit

        if blocked is None:
            blocked = [[False] * w for _ in range(h)]

        def ok(x, y):
            return 0 <= x < w and 0 <= y < h and not blocked[y][x]

        if not ok(sx, sy) or not ok(gx, gy):
            return None

        queue = [(sx, sy)]
        head = 0
        parent = {(sx, sy): None}  # child -> parent

        while head < len(queue):
            x, y = queue[head]
            head += 1

            if (x, y) == (gx, gy):
                break

            cell = self.grid[y][x]
            for wall_bit, dx, dy in DIRECTIONS:
                # open if wall bit not set
                if (cell & wall_bit) == 0:
                    nx, ny = x + dx, y + dy
                    if ok(nx, ny) and (nx, ny) not in parent:
                        parent[(nx, ny)] = (x, y)
                        queue.append((nx, ny))

        if (gx, gy) not in parent:
            return None

        # reconstruct
        path = []
        cur = (gx, gy)
        while cur is not None:
            path.append(cur)
            cur = parent[cur]
        path.reverse()
        self.solution = path
        return path


    def path_to_dirs(self):
        """Convert list[(x,y)] path to 'NESW' string."""
        if not self.solution or len(self.solution) < 2:
            return ""

        out = []
        for (x1, y1), (x2, y2) in zip(self.solution, self.solution[1:]):
            dx, dy = x2 - x1, y2 - y1
            if dx == 0 and dy == -1:
                out.append("N")
            elif dx == 1 and dy == 0:
                out.append("E")
            elif dx == 0 and dy == 1:
                out.append("S")
            elif dx == -1 and dy == 0:
                out.append("W")
            else:
                raise ValueError(f"Invalid step: {(x1,y1)} -> {(x2,y2)}")
        return "".join(out)


    def export_maze_hex(self, out_file: str):
        """
        Export ONLY the maze grid:
        - one hex digit per cell (0-9A-F), encoding closed walls bits (N=1,E=2,S=4,W=8)
        - cells stored row by row, one row per line
        - every line ends with '\n'
        """
        with open(out_file, "w", encoding="utf-8") as f:
            for y in range(self.height):
                line = "".join(format(self.grid[y][x] & 0xF, "X") for x in range(self.width))
                f.write(line + "\n")

            f.write("\n")
            f.write((",").join([str(el) for el in self.entry]))
            f.write("\n")
            f.write((",").join([str(el) for el in self.exit]))
            f.write("\n")
            f.write(self.path_to_dirs())


def draw_ascii(grid):
    h = len(grid)
    w = len(grid[0])

    for y in range(h):
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
