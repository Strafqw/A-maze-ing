import sys
from typing import Any

from mazegen.config_parser import Config, ConfigError, parse_config
from mazegen import MazeGenerator, MazeError
from mazegen.visualizer import run


def make_maze(cfg: Config) -> MazeGenerator:
    """Build a maze from a parsed config and solve it."""
    maze = MazeGenerator(
        width=cfg.width,
        height=cfg.height,
        entry=cfg.entry,
        exit=cfg.exit,
        perfect=cfg.perfect,
        seed=cfg.seed,
        output_file=cfg.output_file,
    )
    if not maze.perfect:
        for i in range(1000):
            if not maze.is_perfect_maze():
                break
            else:
                maze = MazeGenerator(
                    width=cfg.width,
                    height=cfg.height,
                    entry=cfg.entry,
                    exit=cfg.exit,
                    perfect=cfg.perfect,
                    seed=cfg.seed,
                    output_file=cfg.output_file,
                )
    maze.solve()
    if maze.small_size:
        print("cannot generate 42 symbol (small size)")
    return maze


def build_state(maze: MazeGenerator) -> dict[str, Any]:
    """Bundle everything the visualizer needs into a single dict."""
    return {
        "grid": maze.grid,
        "entry": maze.entry,
        "exit": maze.exit,
        "path": maze.solution,
        "ft_grid": maze.ft_grid,
    }


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv
    if len(argv) != 2:
        print(f"Usage: {argv[0]} <config_file>")
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

    run(
        build_state(maze),
        regenerate=lambda: build_state(make_maze(cfg)),
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
