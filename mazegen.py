"""Reusable maze generator.

Public API:
    MazeGenerator -- generate, solve, and export a maze.
    MazeError     -- raised on invalid parameters.

Wall encoding (per cell, 4-bit mask, 1 = closed):
    NORTH = 0b0001
    EAST  = 0b0010
    SOUTH = 0b0100
    WEST  = 0b1000

Example:
    >>> from mazegen import MazeGenerator
    >>> maze = MazeGenerator(width=20, height=15, entry=(0, 0),
    ...                      exit=(19, 14), perfect=True, seed=42)
    >>> maze.solve()                # populates maze.solution
    >>> maze.export("maze.txt")     # subject-format hex file
"""

import random
from typing import Optional

# --------------------------------------------------------------------- #
# Constants
# --------------------------------------------------------------------- #

NORTH = 0b0001
EAST = 0b0010
SOUTH = 0b0100
WEST = 0b1000

DIRECTIONS: list[tuple[int, int, int]] = [
    (EAST, 1, 0),
    (NORTH, 0, -1),
    (WEST, -1, 0),
    (SOUTH, 0, 1),
]

OPPOSITE: dict[int, int] = {
    EAST: WEST,
    WEST: EAST,
    NORTH: SOUTH,
    SOUTH: NORTH,
}

# Cells, in glyph-local coordinates, that draw the "42" pattern.
# The generator centres them inside the maze.
GLYPH_42: list[tuple[int, int]] = [
    # "4"
    (0, 0),
    (0, 1),
    (0, 2), (1, 2), (2, 2),
    (2, 3),
    (2, 4),
    # "2"
    (4, 0), (5, 0), (6, 0),
    (6, 1),
    (4, 2), (5, 2), (6, 2),
    (4, 3),
    (4, 4), (5, 4), (6, 4),
]

_GLYPH_MIN_WIDTH = 9
_GLYPH_MIN_HEIGHT = 7


# --------------------------------------------------------------------- #
# Exceptions
# --------------------------------------------------------------------- #


class MazeError(Exception):
    """Raised when a maze cannot be generated for the given parameters."""


# --------------------------------------------------------------------- #
# Generator
# --------------------------------------------------------------------- #


class MazeGenerator:
    """Random maze with a wall-bitmask grid, BFS solver, and exporter.

    Attributes:
        width:    Maze width in cells.
        height:   Maze height in cells.
        entry:    (x, y) of the entry cell.
        exit:     (x, y) of the exit cell.
        perfect:  Whether the maze is perfect (single path entry->exit).
        grid:     2D list, ``grid[y][x]`` is the cell's wall bitmask.
        ft_grid:  2D bool list, True where the "42" glyph closes cells.
        solution: List of (x, y) from entry to exit, set by :meth:`solve`.
    """

    def __init__(
        self,
        width: int,
        height: int,
        entry: tuple[int, int],
        exit: tuple[int, int],
        perfect: bool = True,
        seed: Optional[int] = None,
    ) -> None:
        self.width = width
        self.height = height
        self.entry = entry
        self.exit = exit
        self.perfect = perfect
        if seed is not None:
            random.seed(seed)
        self.ft_grid: list[list[bool]] = [
            [False] * width for _ in range(height)
        ]
        self.solution: Optional[list[tuple[int, int]]] = None
        self.grid: list[list[int]] = self._carve()
        if not perfect:
            self._punch_loops()

    # ----- construction ----- #

    def _close_glyph(self, visited: list[list[bool]]) -> None:
        """Pre-mark glyph cells as visited so DFS cannot enter them."""
        if (self.width >= _GLYPH_MIN_WIDTH
                and self.height >= _GLYPH_MIN_HEIGHT):
            ox = self.width // 2 - 3
            oy = self.height // 2 - 2
            for gx, gy in GLYPH_42:
                visited[gy + oy][gx + ox] = True
            self.ft_grid = [row[:] for row in visited]
            ex, ey = self.entry
            if self.ft_grid[ey][ex]:
                raise MazeError("ENTRY collides with the '42' glyph cells")
            xx, xy = self.exit
            if self.ft_grid[xy][xx]:
                raise MazeError("EXIT collides with the '42' glyph cells")
        else:
            print("Maze too small to render the '42' glyph - skipping it")

    def _carve(self) -> list[list[int]]:
        """Randomised DFS carving. Returns the wall-bitmask grid."""
        grid = [[0b1111] * self.width for _ in range(self.height)]
        visited = [[False] * self.width for _ in range(self.height)]
        self._close_glyph(visited)
        stack: list[tuple[int, int]] = [self.entry]
        while stack:
            x, y = stack[-1]
            dirs = DIRECTIONS[:]
            random.shuffle(dirs)
            for direction, dx, dy in dirs:
                nx, ny = x + dx, y + dy
                in_bounds = 0 <= nx < self.width and 0 <= ny < self.height
                if in_bounds and not visited[ny][nx]:
                    grid[y][x] &= ~direction
                    grid[ny][nx] &= ~OPPOSITE[direction]
                    visited[ny][nx] = True
                    stack.append((nx, ny))
                    break
            else:
                stack.pop()
        return grid

    def _punch_loops(self) -> None:
        """Open one extra passage per row to add cycles (imperfect maze)."""
        for y in range(self.height):
            opened = False
            for x in range(self.width):
                if opened:
                    break
                if not (0 < x < self.width - 1 and 0 < y < self.height - 1):
                    continue
                if self.ft_grid[y][x]:
                    continue
                for direction, dx, dy in DIRECTIONS:
                    nx, ny = x + dx, y + dy
                    if not (0 <= nx < self.width and 0 <= ny < self.height):
                        continue
                    if self.ft_grid[ny][nx]:
                        continue
                    self.grid[y][x] &= ~direction
                    self.grid[ny][nx] &= ~OPPOSITE[direction]
                    opened = True
                    break

    # ----- solving ----- #

    def solve(self) -> Optional[list[tuple[int, int]]]:
        """BFS shortest path entry->exit. Caches and returns it."""
        w, h = self.width, self.height
        sx, sy = self.entry
        gx, gy = self.exit
        if not (0 <= sx < w and 0 <= sy < h):
            return None
        if not (0 <= gx < w and 0 <= gy < h):
            return None

        queue: list[tuple[int, int]] = [(sx, sy)]
        head = 0
        parent: dict[tuple[int, int], Optional[tuple[int, int]]] = {
            (sx, sy): None,
        }
        while head < len(queue):
            x, y = queue[head]
            head += 1
            if (x, y) == (gx, gy):
                break
            cell = self.grid[y][x]
            for wall, dx, dy in DIRECTIONS:
                if cell & wall:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in parent:
                    parent[(nx, ny)] = (x, y)
                    queue.append((nx, ny))

        if (gx, gy) not in parent:
            return None
        path: list[tuple[int, int]] = []
        cur: Optional[tuple[int, int]] = (gx, gy)
        while cur is not None:
            path.append(cur)
            cur = parent[cur]
        path.reverse()
        self.solution = path
        return path

    def solution_directions(self) -> str:
        """Return :attr:`solution` as a string of N/E/S/W letters."""
        path = self.solution
        if not path or len(path) < 2:
            return ""
        out: list[str] = []
        for (x1, y1), (x2, y2) in zip(path, path[1:]):
            step = (x2 - x1, y2 - y1)
            if step == (0, -1):
                out.append("N")
            elif step == (1, 0):
                out.append("E")
            elif step == (0, 1):
                out.append("S")
            elif step == (-1, 0):
                out.append("W")
            else:
                raise ValueError(
                    f"Invalid step: {(x1, y1)} -> {(x2, y2)}"
                )
        return "".join(out)

    # ----- output ----- #

    def export(self, out_file: str) -> None:
        """Write the maze to ``out_file`` in the subject's hex format."""
        with open(out_file, "w", encoding="utf-8") as f:
            for y in range(self.height):
                row = "".join(
                    format(self.grid[y][x] & 0xF, "X")
                    for x in range(self.width)
                )
                f.write(row + "\n")
            f.write("\n")
            f.write(f"{self.entry[0]},{self.entry[1]}\n")
            f.write(f"{self.exit[0]},{self.exit[1]}\n")
            f.write(self.solution_directions() + "\n")
