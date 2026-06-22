*This project has been created as part of the 42 curriculum by joasampa, mromao-s.*

# A-Maze-ing

## Description

A-Maze-ing is a configurable maze generator written in Python. It reads a
plain-text configuration file, generates a maze (optionally a *perfect* maze
with a single path between entry and exit), writes the result to an output file
using a hexadecimal wall encoding, and displays the maze in the terminal with an
interactive menu.

Every generated maze embeds a visible **"42"** pattern drawn with fully closed
cells, has closed external borders, contains no open area wider than 2 cells,
and is fully connected.

## Instructions

Requirements: **Python 3.10+**. No third-party runtime dependencies (standard
library only). Development tooling (`flake8`, `mypy`) is installed via `make
install`.

```bash
make install        # install dev tools (flake8, mypy)
make run            # generate a maze from config.txt and open the visualizer
make run CONFIG=my_config.txt   # use a different config file
make debug          # run under the pdb debugger
make lint           # flake8 + mypy (mandatory flags)
make clean          # remove caches and temporary files
```

Or run it directly:

```bash
python3 a_maze_ing.py config.txt
```

The program never crashes on bad input: invalid configuration, missing file,
bad syntax, out-of-bounds entry/exit, or impossible parameters all produce a
clear error message.

### Visualizer interactions

Once the maze is displayed, an interactive menu offers:

1. Re-generate a new maze
2. Show / hide the shortest path from entry to exit
3. Rotate the wall colour
4. Quit

## Configuration file format

One `KEY=VALUE` pair per line. Lines starting with `#` are comments and are
ignored. Blank lines are ignored.

| Key           | Required | Description                          | Example                 |
|---------------|----------|--------------------------------------|-------------------------|
| `WIDTH`       | yes      | Maze width in cells (> 0)            | `WIDTH=20`              |
| `HEIGHT`      | yes      | Maze height in cells (> 0)           | `HEIGHT=15`             |
| `ENTRY`       | yes      | Entry coordinates `x,y`              | `ENTRY=0,0`             |
| `EXIT`        | yes      | Exit coordinates `x,y` (≠ entry)     | `EXIT=19,14`            |
| `OUTPUT_FILE` | yes      | Output filename                      | `OUTPUT_FILE=maze.txt`  |
| `PERFECT`     | yes      | `True` for a perfect maze, else `False` | `PERFECT=True`       |
| `SEED`        | no       | Integer seed for reproducible output | `SEED=42`               |

Coordinates are `0`-indexed; `ENTRY` and `EXIT` must be inside the maze bounds,
must differ, and must not fall on the "42" pattern.

Example `config.txt`:

```
# A-Maze-ing default configuration
WIDTH=20
HEIGHT=15
ENTRY=0,0
EXIT=19,14
OUTPUT_FILE=maze.txt
PERFECT=True
SEED=42
```

### Output file format

Each cell is written as one hexadecimal digit encoding its **closed** walls
(bit set to `1` = wall closed, `0` = open):

| Bit | Direction |
|-----|-----------|
| 0 (LSB) | North |
| 1   | East  |
| 2   | South |
| 3   | West  |

Cells are stored row by row, one row per line. After an empty line, three more
lines follow: the entry coordinates, the exit coordinates, and the shortest
valid path from entry to exit (a string of the letters `N`, `E`, `S`, `W`). All
lines end with `\n`.

## Maze generation algorithm

The generator uses an **iterative depth-first search (recursive backtracker)**:

1. The cells forming the "42" glyph are reserved and kept fully walled before
   carving, so they remain isolated and visible.
2. Starting from the entry, DFS carves passages by repeatedly moving to a random
   unvisited neighbour and removing the wall between the two cells, backtracking
   when stuck. This produces a **perfect maze** — a spanning tree with exactly
   one path between any two cells.
3. If `PERFECT=False`, extra walls are removed afterwards to introduce loops,
   turning the maze imperfect while preserving the no-wide-corridor and
   border constraints.
4. The shortest path between entry and exit is found with **breadth-first
   search (BFS)**.

### Why this algorithm

The recursive backtracker is simple, memory-friendly, and *guarantees* a perfect
maze (full connectivity, no cycles) without any post-processing — which directly
satisfies the perfect-maze requirement. It produces long, winding corridors that
look good when rendered, and reserving the "42" cells beforehand keeps the glyph
intact. BFS is the natural choice for the *shortest* solution path because every
step has equal cost.

## Reusable module

The maze generation logic lives in a standalone, importable module
(`mazegen`) so it can be reused in other projects. It exposes the
maze structure independently of the output-file format.

```python
from mazegen import MazeGenerator

# Instantiate with custom parameters (size, entry/exit, perfect, seed)
maze = MazeGenerator(
    width=20,
    height=15,
    entry=(0, 0),
    exit=(19, 14),
    perfect=True,
    seed=42,          # omit or None for a random maze
)

# Access the generated structure: grid[y][x] is the wall bitmask of a cell
# (bit0=North, bit1=East, bit2=South, bit3=West; 1 = closed wall).
grid = maze.grid

# Access a solution: list of (x, y) cells from entry to exit (shortest path)
path = maze.solve()

# ...or the same path as a direction string ("NESW")
directions = maze.path_to_dirs()

# Cells belonging to the "42" pattern (2D bool grid, True = glyph cell)
glyph = maze.ft_grid
```

| Member | Description |
|--------|-------------|
| `MazeGenerator(width, height, entry, exit, perfect=True, seed=None)` | Build and carve a maze |
| `.grid` | `list[list[int]]` — wall bitmask per cell |
| `.solve()` | Compute and return the shortest path as `list[(x, y)]` (or `None`) |
| `.solution` | The last computed path |
| `.path_to_dirs()` | The solution as a `NESW` string |
| `.is_perfect_maze()` | `True` if the maze is connected and acyclic |
| `.ft_grid` | 2D bool grid marking the "42" glyph cells |

## Team and project management

- **Roles:** mromao-s: maze generation & algorithms, joasampa: parser, visualizer & packaging
- **Planning and how it evolved:** *Planned to freeze at the same time so both could work on their part of the project independently, asked other peers how they had divided their work and discussed what seemed like the best approach, did weekly meetings to show our progress and started doing mock evaluations with other peers*
- **What worked well / what could be improved:** *Splitting the work by component (generation vs. parser/visualizer) let us progress in parallel without stepping on each other, and the weekly meetings plus mock evaluations caught misunderstandings about the subject early — especially around the output format and the "42" pattern. The clean separation also made the generator easy to expose as a reusable module. What we'd improve: we underestimated the polish work (linting, type hints, packaging) and left it for the end, so it piled up; next time we'd run `make lint` from day one. The interface between the two parts also drifted a couple of times, which a shared data-structure agreed on earlier would have avoided.*
- **Tools used:** Git, flake8, mypy, venv. See the Resources section for AI usage.

## Resources

- Jamis Buck, *Maze Generation: Recursive Backtracking* —
  <https://weblog.jamisbuck.org/2010/12/27/maze-generation-recursive-backtracking>
- *Maze generation algorithm* (Wikipedia) —
  <https://en.wikipedia.org/wiki/Maze_generation_algorithm>
- *Spanning tree* and perfect mazes (Wikipedia) —
  <https://en.wikipedia.org/wiki/Spanning_tree>
- Breadth-first search —
  <https://en.wikipedia.org/wiki/Breadth-first_search>

### How AI was used

*(Adjust to match what you actually did.)* AI was used as an assistant for:
reviewing the project against the subject requirements, drafting documentation
(this README and the Makefile), and discussing algorithm and edge-case ideas.
All generated content was reviewed, tested, and is fully understood by the team.
