"""A-Maze-ing entry point.

Usage:
    python3 a_maze_ing.py config.txt

Reads the config file, generates a maze, writes the hex output file,
then launches the interactive ASCII visualizer.
"""

import sys
from typing import Any

from config_parser import Config, ConfigError, parse_config
# from mazegen import MazeError, MazeGenerator
from MazeGenerator_new import MazeGenerator_new, MazeError


# just to visualize and know if it is working
def draw_ascii(grid):
    EAST  = 0b1000
    NORTH = 0b0100
    WEST  = 0b0010
    SOUTH = 0b0001
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



def make_maze(cfg: Config) -> MazeGenerator_new:
    print(f"cfg is {cfg}")
    """Build a maze from a parsed config and solve it."""
    maze = MazeGenerator_new(
        width=cfg.width,
        height=cfg.height,
        entry=cfg.entry,
        exit=cfg.exit,
        perfect=cfg.perfect,
        seed=cfg.seed,
    )
    maze.solve()
    try:
        print(f"exporting to {cfg.output_file}")
        maze.export(cfg.output_file)
    except OSError as e:
        print(f"Cannot write output file {cfg.output_file}: {e}")
        return 1
    return maze


def build_state(maze: MazeGenerator_new) -> dict[str, Any]:
    """Bundle everything the visualizer needs into a single dict."""
    return {
        "grid": maze.grid,
        "entry": maze.entry,
        "exit": maze.exit,
        "path": maze.solution,
        "ft_grid": maze.ft_grid,
    }


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(f"Usage: python3 {argv[0]} <config_file>")
        return 1
    try:
        cfg = parse_config(argv[1])
    except ConfigError as e:
        print(f"Config error: {e}")
        return 1
    try:
        maze = make_maze(cfg)
    except MazeError as e:
        print(f"Maze error: {e}")
        return 1
    if maze.solution is None:
        print("Maze has no valid path from ENTRY to EXIT")
        return 1

    from visualizer import run

    run(
        build_state(maze),
        regenerate=lambda: build_state(make_maze(cfg)),
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
