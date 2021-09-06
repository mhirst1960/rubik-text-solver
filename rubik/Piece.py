import string
import textwrap

from rubik.Sticker import Sticker
import rubik.Rotations

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

        #TODO kind of redundent to save solved faces and solvedPos both.  Should remove solved faces.
        # Face directions for this piece in solved position
        if solvedFaces == None:
            #self.solvedFaces = list()
            self.solvedPos = pos
            self.solvedFaces = self._getSolvedFacesFromPostions()

        else:
            self.solvedFaces = list(solvedFaces)
            self.solvedPos = self._getSolvedPosFromFaces()
            
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


        stickers = zip(colors, self.labels, groups, self.solvedFaces)

        # each sticker has a color, a label, and a group
        # each piece is initialized with an array of three stickers
        # But center pieces will have two "stickers" with color=None and Label=None
        # And edge pieces with have one such phantom "sticker"
        #stickers = list(stickers)

        
        for c,l,g,f in stickers:
            if c is not None and l is not None:
                sticker = Sticker(c, l, g, f)
            else:
                sticker = None

            if not self.stickers:
                self.stickers = [sticker]
            else:
                self.stickers = self.stickers + [sticker]

        self._set_piece_type()

    def _getSolvedFacesFromPostions(self, pos=None):
        
        if pos == None:
            pos = self.solvedPos
            
        x = {-1:'L', 0:None, 1:'R'}
        y = {-1:'D', 0:None, 1:'U'}
        z = {-1:'B', 0:None, 1:'F'}

        solvedFaces = list()
        solvedFaces += [x[pos.x]]
        solvedFaces += [y[pos.y]]
        solvedFaces += [z[pos.z]]
        
        return solvedFaces
    

    def _getSolvedPosFromFaces(self):
        x = {'L':-1, None:0, 'R':1}
        y = {'D':-1, None:0, 'U':1}
        z = {'B':-1, None:0, 'F':1}

        solvedPos.x = [x[self.solvedFaces[0]]]
        solvedPos.y = [y[self.solvedFaces[1]]]
        solvedPos.z = [z[self.solvedFaces[2]]]
        
        return solvedPos


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

    def getColor(self, index):
        if index < 0 or index > 2:
            return None
        
        if self.stickers[index] == None:
            return None
        
        return self.stickers[index].color
    
    def getLabels(self):
        labels = list()
        for i, v in enumerate(self.stickers):
            if (v == None):
                labels += [None]
            else:
                labels += v.label

        return labels

    def getLabel(self, index):
        if index < 0 or index > 2:
            return None
        
        if self.stickers[index] == None:
            return None
        
        return self.stickers[index].label
    
    def getDestinations(self):
        destinations = list()
        for i, v in enumerate(self.stickers):
            if v == None:
                destinations += [None]
            else:
                destinations += [v.destination]

        return destinations
  
    def clearDestinations(self):
        for s in self.stickers:
            if s != None:
                s.destination = None

    
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

        # TODO someday remove colors and labels
        i, j = (i for i, x in enumerate(rot) if x != 0)
        self.colors[i], self.colors[j] = self.colors[j], self.colors[i]
        # TODO colors and labels are same object self.labels[i], self.labels[j] = self.labels[j], self.labels[i]
        self.stickers[i], self.stickers[j] = self.stickers[j], self.stickers[i]


    def assignDestinationToFront(self, labelChar, solvedPosition):
        """
        Rotate destinations so label destination is to the front.
        Other stickers are oriented based on solved position
        """
        
        # 1 - make a cophy if self
        # 2 - rotate copy
        
        rotated = False
        
        copyPiece = Piece(self.pos, self.getColors(), self.getLabels(), self.group)
        
        rewind = list()
        
        for rot in range(4):
            if copyPiece.getLabel(2) == labelChar:
                rotated = True
                break
            copyPiece.rotate(rubik.Rotations.ROT_XZ_CW)
            rewind += [rubik.Rotations.ROT_XZ_CC]

        if not rotated:
            for rot in range(4):
                if copyPiece.getLabel(2) == labelChar:
                    rotated = True
                    break
                copyPiece.rotate(rubik.Rotations.ROT_YZ_CW)
                rewind += [rubik.Rotations.ROT_YZ_CC]

        # now rotate keeping front label in place until position is correct
        
        if copyPiece.pos[2] == -1:
            copyPiece.rotate(rubik.Rotations.ROT_YZ_CW)
            copyPiece.rotate(rubik.Rotations.ROT_YZ_CW)
            rewind += [rubik.Rotations.ROT_YZ_CC]
            rewind += [rubik.Rotations.ROT_YZ_CC]

        
        if rotated:
            for rot in range (4):
                if copyPiece.pos == solvedPosition:
                    break
                copyPiece.rotate(rubik.Rotations.ROT_XY_CW)
                rewind += [rubik.Rotations.ROT_XY_CC]
                
        assert copyPiece.pos == solvedPosition
         
        copyPiece.solvedFaces = copyPiece._getSolvedFacesFromPostions(solvedPosition)
        copyPiece.solvedPos = solvedPosition
        for i, sticker in enumerate(copyPiece.stickers):
            if sticker != None:
                sticker.destination = copyPiece.solvedFaces[i]
        
        #rotate the copy back to where it was when we started so it aligns with piece it was cloned from
        for m in reversed(rewind):
            copyPiece.rotate(m)
            
        # 3 - assign self destinations based on final position of copy
        for i, sticker in enumerate(copyPiece.stickers):
            if sticker != None:
                self.stickers[i].destination = sticker.destination
            

                
                
            