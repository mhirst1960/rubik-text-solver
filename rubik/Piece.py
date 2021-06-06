import string
import textwrap

from rubik.Sticker import Sticker

FACE = 'face'
EDGE = 'edge'
CORNER = 'corner'

class Piece:

    def __init__(self, pos, colors, labels=None, group='0', solvedFaces=None):
        """
        :param pos: A tuple of integers (x, y, z) each ranging from -1 to 1
        :param colors: A tuple of length three (x, y, z) where each component gives the color
            of the side of the piece on that axis (if it exists), or None.
        """
        assert all(type(x) == int and x in (-1, 0, 1) for x in pos)
        assert len(colors) == 3

        self.pos = pos
        self.group = group

        self.colors = list(colors)
        self.inSolvedPosition = False
        self.stickers = list()

        # Face directions for this piece in solved position
        if solvedFaces == None:
            self.solvedFaces = list()
        else:
            self.solvedFaces = list(solvedFaces)
            
        if not labels == None:
          assert len(labels) == 3
          self.labels = list(labels)
          #print("-------")
          #print("New Piece. pos   = ", self.pos)
          #print("New Piece. colors= ", self.colors)
          #print("New Piece. labels= ", self.labels)
          #print("New Piece. group = ", self.group)



        else:
          self.labels=self.colors

        groups = list()

        for l in self.labels:
            if l == None:
                groups = groups + [None]
            else:
                groups = groups + [self.group]


        stickers = zip(colors, self.labels, groups)

        # each sticker has a color, a label, and a group
        # each piece is initialized with an array of three stickers
        # But center pieces will have two "stickers" with color=None and Label=None
        # And edge pieces with have one such phantom "sticker"
        #stickers = list(stickers)

        
        for c,l,g in stickers:
            if c is not None and l is not None:
                sticker = Sticker(c, l, g)
            else:
                sticker = None

            if not self.stickers:
                self.stickers = [sticker]
            else:
                self.stickers = self.stickers + [sticker]

        self._set_piece_type()

#    def __str__(self):
#        colors = "".join(c for c in self.colors if c is not None)
#        return f"({self.type}, {colors}, {self.pos})"

    def __str__(self):
        #stickers = "".join(s.color for s in self.stickers if s is not None)
        stickers = "".join(str(s) for s in self.stickers if s is not None)
        #stickers = str(s) (stickerStr = for s in stickers str(s))
        return f"({stickers})"
        #return f"({self.type}, {stickers}, {self.pos})"

    def labels_str(self):
        labels = "".join(s.label for s in self.stickers if s is not None)
        return f"({self.type}, {labels}, {self.pos})"
      
    def labelsDotNone(self, xyz):
      if self.labels[xyz] == None:
        return '.'
      else:
        return self.labels[xyz]

    def stickersDotNone(self, xyz):
      if self.stickers[xyz] == None:
        return '.'
      else:
        return self.stickers[xyz]

    def _set_piece_type(self):
        count = 0
        for s in self.stickers:
            if s != None:
                count += 1
        if count == 1:
            self.type = FACE
        elif count == 2:
            self.type = EDGE
        elif count == 3:
            self.type = CORNER
        else:
            raise ValueError(f"Must have 1, 2, or 3 colors - given colors={self.colors}")

    def getColors(self):
        colors = list()
        for i, v in enumerate(self.stickers):
            if (v == None):
                colors += [None]
            else:
                colors += v.color

        return colors

    def getLabels(self):
        labels = list()
        for i, v in enumerate(self.stickers):
            if (v == None):
                labels += [None]
            else:
                labels += v.label

        return labels
    
    def rotate(self, matrix):
        """Apply the given rotation matrix to this piece."""
        before = self.pos
        self.pos = matrix * self.pos

        # we need to swap the positions of two things in self.colors so colors appear
        # on the correct faces. rot gives us the axes to swap between.
        rot = self.pos - before
        if not any(rot):
            return  # no change occurred
        if rot.count(0) == 2:
            rot += matrix * rot

        assert rot.count(0) == 1, (
            f"There is a bug in the Piece.rotate() method!"
            f"\nbefore: {before}"
            f"\nself.pos: {self.pos}"
            f"\nrot: {rot}"
        )

        #print("swap:")
        #print("  old colors", self.colors)
        #print("  old labels", self.labels)
        #print("  old stickers", self.stickers)

        # TODO someday remove colors and labels
        i, j = (i for i, x in enumerate(rot) if x != 0)
        self.colors[i], self.colors[j] = self.colors[j], self.colors[i]
        # TODO colors and labels are same object self.labels[i], self.labels[j] = self.labels[j], self.labels[i]
        self.stickers[i], self.stickers[j] = self.stickers[j], self.stickers[i]

        #print("  new colors", self.colors)
        #print("  new labels", self.labels)
        #print("  new stickers", self.stickers)
