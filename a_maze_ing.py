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


def make_maze(cfg: Config) -> MazeGenerator_new:
    """Build a maze from a parsed config and solve it."""
    maze = MazeGenerator_new(
        width=cfg.width,
        height=cfg.height,
        entry=cfg.entry,
        exit=cfg.exit,
        perfect=cfg.perfect,
        seed=cfg.seed,
    )
    if maze.perfect == False:
        for i in range(1000):
            if maze.is_perfect_maze() == False:
                break
            else:
                maze = MazeGenerator_new(
                    width=cfg.width,
                    height=cfg.height,
                    entry=cfg.entry,
                    exit=cfg.exit,
                    perfect=cfg.perfect,
                    seed=cfg.seed,
                )
    maze.solve()
    if maze.small_size:
        print("cannot generate 42 symbol (small size)")
    try:
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
