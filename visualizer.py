"""Interactive ASCII visualizer for the maze.

Renders the wall-bitmask grid with box-drawing characters and highlights:
    * the entry cell (magenta)
    * the exit cell (red)
    * the BFS solution path, if shown (cyan)
    * the "42" glyph cells (yellow)

The :func:`run` function drives an interactive menu loop matching the
subject's requirements (regenerate, show/hide path, change wall colours,
quit).
"""

from typing import Callable, Optional

from vars import NORTH, EAST, SOUTH, WEST


RESET = "\033[0m"

WALL_COLORS = [
    ("white",   "\033[37m"),
    ("cyan",    "\033[36m"),
    ("green",   "\033[32m"),
    ("yellow",  "\033[33m"),
    ("magenta", "\033[35m"),
]

ENTRY_COLOR = "\033[45m"   # magenta background
EXIT_COLOR  = "\033[41m"   # red background
PATH_COLOR  = "\033[46m"   # cyan background
FT_COLOR    = "\033[43m"   # yellow background


def _cell_marker(
    x: int,
    y: int,
    entry: tuple[int, int],
    exit_: tuple[int, int],
    path_set: Optional[set[tuple[int, int]]],
    ft_grid: Optional[list[list[bool]]],
) -> str:
    """Return the 3-character inner block for a cell, with colour codes."""
    if (x, y) == tuple(entry):
        return f"{ENTRY_COLOR}   {RESET}"
    if (x, y) == tuple(exit_):
        return f"{EXIT_COLOR}   {RESET}"
    if path_set is not None and (x, y) in path_set:
        return f"{PATH_COLOR}   {RESET}"
    if ft_grid is not None and ft_grid[y][x]:
        return f"{FT_COLOR}   {RESET}"
    return "   "


def render(
    grid: list[list[int]],
    entry: tuple[int, int],
    exit_: tuple[int, int],
    path: Optional[list[tuple[int, int]]] = None,
    ft_grid: Optional[list[list[bool]]] = None,
    wall_color: str = WALL_COLORS[0][1],
) -> str:
    """Build the ASCII rendering as a single string."""
    if not grid or not grid[0]:
        return ""

    h, w = len(grid), len(grid[0])
    path_set = set(path) if path else None

    lines: list[str] = []
    for y in range(h):
        top_chars: list[str] = []
        mid_chars: list[str] = []

        for x in range(w):
            cell = grid[y][x]
            top_chars.append(f"{wall_color}┼{RESET}")
            if cell & NORTH:
                top_chars.append(f"{wall_color}───{RESET}")
            else:
                top_chars.append(_cell_marker(x, y, entry, exit_, path_set, ft_grid))

            if cell & WEST:
                mid_chars.append(f"{wall_color}│{RESET}")
            else:
                mid_chars.append(" ")
            mid_chars.append(_cell_marker(x, y, entry, exit_, path_set, ft_grid))

            if x == w - 1:
                if cell & EAST:
                    mid_chars.append(f"{wall_color}│{RESET}")
                else:
                    mid_chars.append(" ")

        top_chars.append(f"{wall_color}┼{RESET}")
        lines.append("".join(top_chars))
        lines.append("".join(mid_chars))

    bottom = [f"{wall_color}┼{RESET}"]
    for _ in range(w):
        bottom.append(f"{wall_color}───┼{RESET}")
    lines.append("".join(bottom))

    return "\n".join(lines)


def run(
    initial_state: dict,
    regenerate: Callable[[], dict],
) -> None:
    """Drive the interactive menu loop.

    Args:
        initial_state: dict with keys ``grid``, ``entry``, ``exit``,
            ``path`` (optional), ``ft_grid`` (optional).
        regenerate: zero-argument callable returning a fresh state dict
            of the same shape, used when the user picks "re-generate".
    """
    state = dict(initial_state)
    show_path = True
    color_idx = 0

    while True:
        wall_color = WALL_COLORS[color_idx][1]
        path = state.get("path") if show_path else None
        print(render(
            grid=state["grid"],
            entry=state["entry"],
            exit_=state["exit"],
            path=path,
            ft_grid=state.get("ft_grid"),
            wall_color=wall_color,
        ))

        print()
        print("=== A-Maze-ing ===")
        print("1. Re-generate a new maze")
        print("2. Show/Hide path from entry to exit "
              f"(currently {'shown' if show_path else 'hidden'})")
        print(f"3. Rotate wall colour (currently {WALL_COLORS[color_idx][0]})")
        print("4. Quit")

        try:
            choice = input("Choice? (1-4): ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return

        if choice == "1":
            try:
                state = regenerate()
            except Exception as e:
                print(f"Failed to regenerate: {e}")
        elif choice == "2":
            show_path = not show_path
        elif choice == "3":
            color_idx = (color_idx + 1) % len(WALL_COLORS)
        elif choice == "4":
            return
        else:
            print(f"Unknown choice: {choice!r}")
