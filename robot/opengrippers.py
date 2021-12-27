#! /bin/python3

from time import sleep
from CubeMover import CubeMover

# Run this if cube is stuck in a weird position between grippers
# simply open both grippers as-is. Done.

mover = CubeMover()

mover.left.open()
mover.right.open()


exit()

