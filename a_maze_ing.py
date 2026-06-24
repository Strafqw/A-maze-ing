"""A-Maze-ing entry point.

Usage:
    python3 a_maze_ing.py config.txt
"""
import sys
from mazegen.__main__ import main

if __name__ == "__main__":
    sys.exit(main(sys.argv))
