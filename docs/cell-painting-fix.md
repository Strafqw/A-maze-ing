# Fix: colored cells painting "1.5 cells"

## The symptom

When the maze was printed with the path / entry / exit / "42" cells highlighted
via ANSI background colors, some colored cells looked taller (or wider) than
their uncolored neighbors. A single path cell could appear to fill ~1.5 cell
rows, and a horizontal run of path cells looked like a row of separated blocks
with gaps between them instead of one continuous strip.

## Why it was happening

The renderer in `visualizer.py` emits two text lines per maze row:

1. A **top boundary** line:
   `┼` + (`───` if there is a NORTH wall, else the cell's 3-char inner block)
2. A **mid** line:
   (`│` if there is a WEST wall, else ` `) + the cell's 3-char inner block

So each cell visually occupies a 4×2 character area: a 1-char left edge and a
3-char body, stacked above a 1×3 top edge plus the body.

The "inner block" was always the same 3 spaces, painted with the cell's own
background color when that cell was entry / exit / path / FT.

That logic had two asymmetries:

### 1. Top boundary used only the *lower* cell's color (vertical 1.5× issue)

When there was no NORTH wall, the old code did:

```python
top_chars.append(marker)   # marker = color of cell (x, y)
```

The boundary between cell `(x, y-1)` and cell `(x, y)` was painted with the
color of the cell **below** it, regardless of what was above. So a path cell
with no NORTH wall would paint its color into the boundary row above it, even
if the cell directly above was uncolored (or a different color). Visually that
meant the colored block spanned `boundary row + own mid row` — about 1.5 row
heights — while a cell that *did* have a NORTH wall only spanned its own mid
row, ~1 row height. Hence "some cells paint 1.5 cells".

### 2. Horizontal gap was never painted (broken-run issue)

When there was no WEST wall, the old code did:

```python
mid_chars.append(" ")      # always uncolored
```

So even when two path cells sat side-by-side with no wall between them, the
1-char gap separating their 3-char bodies was left uncolored. The result was
`███ ███ ███` — three painted blocks with white gaps — instead of one
continuous painted strip.

## The fix

Boundaries between cells now reflect *both* sides, not just one. The renderer
asks: *is this opening between two cells of the same color?* If yes, paint the
opening with that shared color. Otherwise, leave it uncolored.

Concretely:

- New helper `_cell_bg(x, y, …)` returns the background ANSI code for a cell,
  or `None` if the cell is plain.
- New helper `_block(bg, width)` returns `width` spaces, optionally wrapped in
  an ANSI background color.
- In the render loop:
  - **Top boundary, no NORTH wall:** look up `bg(x, y)` and `bg(x, y-1)`. If
    they match and are non-`None`, paint the 3-char boundary with that color.
    Otherwise paint 3 plain spaces.
  - **Mid row, no WEST wall:** look up `bg(x, y)` and `bg(x-1, y)`. If they
    match and are non-`None`, paint the 1-char gap with that color. Otherwise
    paint a plain space.
  - The cell's own 3-char body is still always painted in its own color (or
    plain) — unchanged.

### Why this works

- **Vertical continuity preserved:** consecutive path cells stacked vertically
  share PATH_COLOR, so the boundary between them is now painted PATH_COLOR.
  Together they read as one tall continuous bar — but each *individual* cell
  is still only ~1 row tall in the sense that its color no longer leaks into a
  *non-path* neighbor above.
- **Horizontal continuity preserved:** consecutive path cells in the same row
  with no wall between them now have a PATH_COLOR-painted 1-char gap, so
  `█████████` instead of `███ ███ ███`.
- **Color boundaries stay clean:** where entry (magenta) meets path (cyan)
  through an open wall, the colors differ, so the boundary stays uncolored —
  neither cell bleeds into the other.
- **Layout is unchanged:** the row width is still `4·w + 1` characters and
  every row still produces exactly one top line and one mid line. Only the
  *coloring* of already-existing characters changed; no characters were added
  or removed.

## Files touched

- `visualizer.py` — replaced `_cell_marker` with `_cell_bg` + `_block`, and
  updated the `render` loop to apply the shared-color rule on open boundaries.
