"""Shared constants: wall bit flags, directions and the "42" glyph."""

GLYPH_42 = [
    # ---- "4" ----
    (0, 0),
    (0, 1),
    (0, 2), (1, 2), (2, 2),
    (2, 3),
    (2, 4),

    # ---- "2" ----
    (4, 0), (5, 0), (6, 0),
    (6, 1),
    (4, 2), (5, 2), (6, 2),
    (4, 3),
    (4, 4), (5, 4), (6, 4),
]


NORTH = 0b0001
EAST = 0b0010
SOUTH = 0b0100
WEST = 0b1000

DIRECTIONS = [
    (EAST, 1, 0),
    (NORTH, 0, -1),
    (WEST, -1, 0),
    (SOUTH, 0, 1),
]

OPPOSITE = {
    EAST: WEST,
    WEST: EAST,
    NORTH: SOUTH,
    SOUTH: NORTH,
}
