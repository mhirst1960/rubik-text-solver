
"""
Different ways of printing a cube.  Some ar useful for debugging
"""

from enum import Enum

class CubePrintStyles(Enum):
    Uncolored               = 0  # plain string
    Colored                 = 1  # sticker color background with no labels
    LabelColor              = 2  # show labels on sticker color background
    DestinationColored      = 3  # show labels on color background. Colors represent the destination face, not the sticker color
    DestinationGroupColored = 4  # labels and group character on destination background (for debugging)
