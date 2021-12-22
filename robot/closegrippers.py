#! /bin/python3

from time import sleep
from CubeMover import CubeMover

# close both grippers as-is.

mover = CubeMover()

mover.left.close()
mover.right.close()


exit()
