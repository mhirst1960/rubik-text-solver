import string
import textwrap

import rubik.Rotations as rot
from rubik.maths import Point, Matrix
from rubik.Piece import Piece

RIGHT = X_AXIS = Point(1, 0, 0)
LEFT           = Point(-1, 0, 0)
UP    = Y_AXIS = Point(0, 1, 0)
DOWN           = Point(0, -1, 0)
FRONT = Z_AXIS = Point(0, 0, 1)
BACK           = Point(0, 0, -1)


FACE = 'face'
EDGE = 'edge'
CORNER = 'corner'


def get_rot_from_face(face):
    """
    :param face: One of FRONT, BACK, LEFT, RIGHT, UP, DOWN
    :return: A pair (CW, CC) given the clockwise and counterclockwise rotations for that face
    """
    if face == RIGHT:   return "R", "Ri"
    elif face == LEFT:  return "L", "Li"
    elif face == UP:    return "U", "Ui"
    elif face == DOWN:  return "D", "Di"
    elif face == FRONT: return "F", "Fi"
    elif face == BACK:  return "B", "Bi"
    return None



class Cube:
    """Stores Pieces which are addressed through an x-y-z coordinate system:
        -x is the LEFT direction, +x is the RIGHT direction
        -y is the DOWN direction, +y is the UP direction
        -z is the BACK direction, +z is the FRONT direction
    """

    def _from_cube(self, c):
        
        self.faces = list()
        self.edges = list()
        self.corners = list()

        for p in c.faces:
            pos, colors, labels, group, solvedFaces = p.getAttributes()
            self.faces.append(Piece(pos=pos, colors=colors, labels=labels, group=group, solvedFaces=solvedFaces))

        for p in c.edges:
            pos, colors, labels, group, solvedFaces = p.getAttributes()
            self.edges.append(Piece(pos=pos, colors=colors, labels=labels, group=group, solvedFaces=solvedFaces))

        for p in c.corners:
            pos, colors, labels, group, solvedFaces = p.getAttributes()
            self.corners.append(Piece(pos=pos, colors=colors, labels=labels, group=group, solvedFaces=solvedFaces))

        self.pieces = self.faces + self.edges + self.corners

    def _assert_data(self):
        assert len(self.pieces) == 26
        assert all(p.type == FACE for p in self.faces)
        assert all(p.type == EDGE for p in self.edges)
        assert all(p.type == CORNER for p in self.corners)

    def _newPiece(self, pos, x, y, z):
        # create a new piece
        if x == None:
            cx = None
            lx = None
            gx = None
        else:
            cx = self.color_str[x]
            lx = self.labels_str[x]
            gx = self.groups_str[x]
            
        if y == None:
            cy = None
            ly = None
            gy = None
        else:
            cy = self.color_str[y]
            ly = self.labels_str[y]
            gy = self.groups_str[y]
            
        if z == None:
            cz = None
            lz = None
            gz = None
        else:
            cz = self.color_str[z]
            lz = self.labels_str[z]
            gz = self.groups_str[z]
            
        if gx != None:
            g = gx
        else:
            if gy != None:
                g = gy
            else:
                g = gz

        p = Piece(pos, colors=(cx, cy, cz), labels=(lx, ly, lz), group=g)
        return p

        
    def __init__(self, colors, labels=None, groups=None):
        """
        cube_str looks like:
                UUU                        0  1  2
                UUU                        3  4  5
                UUU                        6  7  8
            LLL FFF RRR BBB      9 10 11  12 13 14  15 16 17  18 19 20
            LLL FFF RRR BBB     21 22 23  24 25 26  27 28 29  30 31 32
            LLL FFF RRR BBB     33 34 35  36 37 38  39 40 41  42 43 44
                DDD                       45 46 47
                DDD                       48 49 50
                DDD                       51 52 53
        Note that the back side is mirrored in the horizontal axis during unfolding.
        So 18 (on the back) is directly under 12 (on the front)
        Each 'sticker' must be a single character.
        """
        
        # True: print Back stickers in same order as Front order. 1st stick is under 1st sticker
        # False: print rotated 180 degrees, 1st sticker is under 3rd front sticker 
        self.backViewIsXray = True
                
        if isinstance(colors, Cube):
            self._from_cube(colors)
            return

        cube_str = "".join(x for x in colors if x not in string.whitespace)
        
        if labels == None:
            labels_str = cube_str
        else:
            labels_str = "".join(x for x in labels if x not in string.whitespace)
            
        if groups == None:
            groups_str = "0" * 54  # everything is group "0"
        else:
            groups_str = "".join(x for x in groups if x not in string.whitespace)


        assert len(cube_str) == 54
        assert len(labels_str) == 54
        assert len(groups_str) == 54
        
        self.color_str = cube_str
        self.labels_str = labels_str
        self.groups_str = groups_str
        
        self.faces = (
            self._newPiece(RIGHT, 28, None, None),
            self._newPiece(LEFT, 22, None, None),
            self._newPiece(UP,  None, 4, None),
            self._newPiece(DOWN, None, 49, None),
            self._newPiece(FRONT, None, None, 25),
            self._newPiece(BACK, None, None, 31),
            )
        self.edges = (
            self._newPiece(RIGHT + UP,    16, 5, None),
            self._newPiece(RIGHT + DOWN,  40, 50, None),
            self._newPiece(RIGHT + FRONT, 27, None, 26),
            self._newPiece(RIGHT + BACK,  29, None, 30),
            self._newPiece(LEFT + UP,     10, 3, None),
            self._newPiece(LEFT + DOWN,   34, 48, None),
            self._newPiece(LEFT + FRONT,  23, None, 24),
            self._newPiece(LEFT + BACK,   21, None, 32),
            self._newPiece(UP + FRONT,    None, 7, 13),
            self._newPiece(UP + BACK,     None, 1, 19),
            self._newPiece(DOWN + FRONT,  None, 46, 37),
            self._newPiece(DOWN + BACK,   None, 52, 43),
        )
        self.corners = (
            self._newPiece(RIGHT + UP + FRONT,   15, 8, 14),
            self._newPiece(RIGHT + UP + BACK,    17, 2, 18),
            self._newPiece(RIGHT + DOWN + FRONT, 39, 47, 38),
            self._newPiece(RIGHT + DOWN + BACK,  41, 53, 42),
            self._newPiece(LEFT + UP + FRONT,    11, 6, 12),
            self._newPiece(LEFT + UP + BACK,     9, 0, 20),
            self._newPiece(LEFT + DOWN + FRONT,  35, 45, 36),
            self._newPiece(LEFT + DOWN + BACK,   33, 51, 44),
        )

        self.pieces = self.faces + self.edges + self.corners

        self._assert_data()
        
        self.orientToFront()

    def is_solved(self, message=None):
        def check(destinations):
            assert len(destinations) == 9
            return all(c == destinations[0] for c in destinations)
        
        if message == None:
            return (check([piece.getDestinations()[2] for piece in self._face(FRONT)]) and
                    check([piece.getDestinations()[2] for piece in self._face(BACK)]) and
                    check([piece.getDestinations()[1] for piece in self._face(UP)]) and
                    check([piece.getDestinations()[1] for piece in self._face(DOWN)]) and
                    check([piece.getDestinations()[0] for piece in self._face(LEFT)]) and
                    check([piece.getDestinations()[0] for piece in self._face(RIGHT)]))
        else:
            # TODO: should check actual string on front face
            solvedMessage = ""
            front = ''.join([p.getLabels()[2] for p in sorted(self._face(FRONT), key=lambda p: (-p.pos.y, p.pos.x))])
            solvedMessage = front.replace("-", "")
            return message.replace("-", "") == solvedMessage

    def _face(self, axis):
        """
        :param axis: One of LEFT, RIGHT, UP, DOWN, FRONT, BACK
        :return: A list of Pieces on the given face
        """
        assert axis.count(0) == 2
        return [p for p in self.pieces if p.pos.dot(axis) > 0]

    def _slice(self, plane):
        """
        :param plane: A sum of any two of X_AXIS, Y_AXIS, Z_AXIS (e.g. X_AXIS + Y_AXIS)
        :return: A list of Pieces in the given plane
        """
        assert plane.count(0) == 1
        i = next((i for i, x in enumerate(plane) if x == 0))
        return [p for p in self.pieces if p.pos[i] == 0]

    def _rotate_face(self, face, matrix):
        self._rotate_pieces(self._face(face), matrix)

    def _rotate_slice(self, plane, matrix):
        self._rotate_pieces(self._slice(plane), matrix)

    def _rotate_pieces(self, pieces, matrix):
        for piece in pieces:
            piece.rotate(matrix)

    # Rubik's Cube Notation: http://ruwix.com/the-rubiks-cube/notation/
    def L(self):  self._rotate_face(LEFT, rot.ROT_YZ_CC)
    def Li(self): self._rotate_face(LEFT, rot.ROT_YZ_CW)
    def R(self):  self._rotate_face(RIGHT, rot.ROT_YZ_CW)
    def Ri(self): self._rotate_face(RIGHT, rot.ROT_YZ_CC)
    def U(self):  self._rotate_face(UP, rot.ROT_XZ_CW)
    def Ui(self): self._rotate_face(UP, rot.ROT_XZ_CC)
    def D(self):  self._rotate_face(DOWN, rot.ROT_XZ_CC)
    def Di(self): self._rotate_face(DOWN, rot.ROT_XZ_CW)
    def F(self):  self._rotate_face(FRONT, rot.ROT_XY_CW)
    def Fi(self): self._rotate_face(FRONT, rot.ROT_XY_CC)
    def B(self):  self._rotate_face(BACK, rot.ROT_XY_CC)
    def Bi(self): self._rotate_face(BACK, rot.ROT_XY_CW)
    def M(self):  self._rotate_slice(Y_AXIS + Z_AXIS, rot.ROT_YZ_CC)
    def Mi(self): self._rotate_slice(Y_AXIS + Z_AXIS, rot.ROT_YZ_CW)
    def E(self):  self._rotate_slice(X_AXIS + Z_AXIS, rot.ROT_XZ_CC)
    def Ei(self): self._rotate_slice(X_AXIS + Z_AXIS, rot.ROT_XZ_CW)
    def S(self):  self._rotate_slice(X_AXIS + Y_AXIS, rot.ROT_XY_CW)
    def Si(self): self._rotate_slice(X_AXIS + Y_AXIS, rot.ROT_XY_CC)
    def X(self):  self._rotate_pieces(self.pieces, rot.ROT_YZ_CW)
    def Xi(self): self._rotate_pieces(self.pieces, rot.ROT_YZ_CC)
    def Y(self):  self._rotate_pieces(self.pieces, rot.ROT_XZ_CW)
    def Yi(self): self._rotate_pieces(self.pieces, rot.ROT_XZ_CC)
    def Z(self):  self._rotate_pieces(self.pieces, rot.ROT_XY_CW)
    def Zi(self): self._rotate_pieces(self.pieces, rot.ROT_XY_CC)
    def X2(self): self.X(); self.X()
    def Y2(self): self.Y(); self.Y()
    def Z2(self): self.Z(); self.Z()
    def D2(self): self.D(); self.D()
    def U2(self): self.U(); self.U()
    def L2(self): self.L(); self.L()
    def R2(self): self.R(); self.R()
    def F2(self): self.F(); self.F()
    def B2(self): self.B(); self.B()
    def M2(self): self.M(); self.M()
    def E2(self): self.E(); self.E()
    def S2(self): self.S(); self.S()
    
    def sequence(self, move_str):
        """
        :param moves: A string containing notated moves separated by spaces: "L Ri U M Ui B M"
        """
        moves = [getattr(self, name) for name in move_str.split()]
        for move in moves:
            move()

    def findPieceByColors(self, *colors):
        if None in colors:
            return
        for p in self.pieces:
            if p.colors.count(None) == 3 - len(colors) \
                and all(c in p.colors for c in colors):
                return p

    # find a piece based on the intended solved orientation directions
    def findPieceByDestinations(self, *destinations):
        if None in destinations:
            return
        for p in self.pieces:
            if p.stickers.count(None) == 3 - len(destinations):
                pieceDestinations = p.getDestinations()
                if all(d in pieceDestinations for d in destinations):
                    return p

    # find a piece based on the intended solved orientation directions
    def findPieceByLabelAndGroupWithNoDestination(self, label, group, type=None):
        for p in self.pieces:
            if p.group != group:
                continue
            if type!=p.type and type != None:
                continue
            destinations = p.getDestinations()
            if all(d is None for d in destinations):
                labels = p.getLabels()
                for l in labels:
                    if l == label:
                        return p
        return None
    
    def clearAllDestinations(self):
        # for every non-center piece in the cube if a destination was previously assigned, clear it.ArithmeticError
        for p in self.pieces:
            p.clearDestinations()
            
    def assignDefaultFaceDestinations(self):
        for face in self.faces:
            face.assignDefaultDestinations()
        
    def assignClearedDestinations(self):
        """
        find all pieces with no destination and assign a good default value
        based on destinations already assigned
        """
        
        for p in self.pieces:
            if p.getDestinations() != [None, None, None]:
                continue
            
            
        assert false #TODO implement
            
    def getFrontPieces(self):
        front = [p for p in sorted(self._face(FRONT), key=lambda p: (-p.pos.y, p.pos.x))]
        return front
        
    def get_piece(self, x, y, z):
        """
        :return: the Piece at the given Point
        """
        point = Point(x, y, z)
        for p in self.pieces:
            if p.pos == point:
                return p

    def __getitem__(self, *args):
        if len(args) == 1:
            return self.get_piece(*args[0])
        return self.get_piece(*args)

    def __eq__(self, other):
        return isinstance(other, Cube) and self.flat_str() == other.flat_str()
        #return isinstance(other, Cube) and self.colors()() == other.colors()

    def __ne__(self, other):
        return not (self == other)

    def colors(self):
        """
        :return: A set containing the colors of all stickers on the cube
        """
        #for piece in self.pieces:
        #    print ("colors: ", piece.getColors())

        return set(c for piece in self.pieces for c in piece.getColors() if c is not None)


    def stickers(self):
        """
        :return: A set containing all stickers on the cube
        """
        return set(s for piece in self.pieces for s in piece.stickers if s is not None)

    def left_color(self): return self[LEFT].colors[0]
    def right_color(self): return self[RIGHT].colors[0]
    def up_color(self): return self[UP].colors[1]
    def down_color(self): return self[DOWN].colors[1]
    def front_color(self): return self[FRONT].colors[2]
    def back_color(self): return self[BACK].colors[2]

    def leftSticker(self): return self[LEFT].stickers[0]
    def rightSticker(self): return self[RIGHT].stickers[0]
    def upSticker(self): return self[UP].stickers[1]
    def downSticker(self): return self[DOWN].stickers[1]
    def frontSticker(self): return self[FRONT].stickers[2]
    def backSticker(self): return self[BACK].stickers[2]
    
    def leftDestination(self): return self.leftSticker().destination
    def rightDestination(self): return self.rightSticker().destination
    def upDestination(self): return self.upSticker().destination
    def downDestination(self): return self.downSticker().destination
    def frontDestination(self): return self.frontSticker().destination
    def backDestination(self): return self.backSticker().destination

    #orient entire cube so front destination is in front and up is up
    def orientToFront(self):
        face = self.findPieceByDestinations('F')
        move = ""
        moves = ""

        if face.pos[1] == 1:
            move = "Xi"
        elif face.pos[1] == -1:
            move = "X"
        elif face.pos[2] == 1:
            move = ""
        elif face.pos[2] == -1:
            move = "X X"
        elif face.pos[0] == -1:
            move = "Yi"
        elif face.pos[0] == 1:
            move = "Y"
        else:
            print("ERROR: illegal color ", frontColor)
            
        moves = move
        self.sequence(move)
        #print("front color should be ", color, ". It is: ", self.front_color())

        up    = self.findPieceByDestinations('U')
        down  = self.findPieceByDestinations('D')
        left  = self.findPieceByDestinations('L')
        right = self.findPieceByDestinations('R')
        back  = self.findPieceByDestinations('B')
        
        if up == None or down == None or left == None or right == None or back == None:
            # at least one face destination is unassigned.  Simply assign based on current position and return.
            self.upSticker().destination = 'U'
            self.downSticker().destination = 'D'
            self.leftSticker().destination = 'L'
            self.rightSticker().destination = 'R'
            self.backSticker().destination = 'B'
            return moves
        
        move = ""

        if up.pos[0] == 1:
            move = "Zi"
        elif up.pos[0] == -1:
            move = "Z"
        elif up.pos[2] == 1:
            move = "X"
        elif up.pos[2] == -1:
            move = "Xi"
        elif up.pos[1] == -1:
            move = "Z Z"
        elif up.pos[1] == 1:
            move = ""

        moves += " " + move
        self.sequence(move)
        
        return moves

    def orientToUp(self):
        self.orientToFront()
        self.sequence("X")
        
    def orient(self, direction="F"):
        self.orientToFront()
        
        if direction == "F":
            return
        elif direction == "B":
            self.sequence("Y2")
        elif direction == "U":
            self.sequence("X")
        elif direction == "D":
            self.sequence("Xi")
        elif direction == "L":
            self.sequence("Yi")
        elif direction == "R":
            self.sequence("Y")
        
    def orientToCube(self, cube):
        
        labels = cube.getLabels()
        colors = cube.getColors()
        
        assert labels != None
        
        sortedLabelsUp = sorted(labels[:9])
        sortedColorsUp = sorted(colors[:9])
        foundUp = False
        
        for z in range(2):
            for x in range(4):
                if (sorted(self.getLabels()[:9]) == sortedLabelsUp
                    and sorted(self.getColors()[:9]) == sortedColorsUp):
                    foundUp = True
                    break
                self.sequence("X")
            if foundUp:
                break
            self.sequence("Z")
            
        done = False

        if foundUp:
            labelsUp = labels[:9]
            colorsUp = colors[:9]

            for y in range(4):
                if (self.getLabels() == labels):
                    done = True
                    break
                self.sequence("Y")
            
        assert done
            
        
    def colorList(self):
        right = [p.getColor(0) for p in sorted(self._face(RIGHT), key=lambda p: (-p.pos.y, -p.pos.z))]
        left  = [p.getColor(0) for p in sorted(self._face(LEFT),  key=lambda p: (-p.pos.y, p.pos.z))]
        up    = [p.getColor(1) for p in sorted(self._face(UP),    key=lambda p: (p.pos.z, p.pos.x))]
        down  = [p.getColor(1) for p in sorted(self._face(DOWN),  key=lambda p: (-p.pos.z, p.pos.x))]
        front = [p.getColor(2) for p in sorted(self._face(FRONT), key=lambda p: (-p.pos.y, p.pos.x))]
        if self.backViewIsXray:
            back  = [p.getColor(2) for p in sorted(self._face(BACK),  key=lambda p: (-p.pos.y, p.pos.x))]
        else:
            back  = [p.getColor(2) for p in sorted(self._face(BACK),  key=lambda p: (-p.pos.y, -p.pos.x))]

        return (up + left[0:3] + front[0:3] + right[0:3] + back[0:3]
                   + left[3:6] + front[3:6] + right[3:6] + back[3:6]
                   + left[6:9] + front[6:9] + right[6:9] + back[6:9] + down)

    def getColors(self):
        return self.colorList()
    
    def colorString(self):
        return "".join(x for x in self.colorList() if x not in string.whitespace)

    def _sticker_list(self):
        right = [p.stickers[0] for p in sorted(self._face(RIGHT), key=lambda p: (-p.pos.y, -p.pos.z))]
        left  = [p.stickers[0] for p in sorted(self._face(LEFT),  key=lambda p: (-p.pos.y, p.pos.z))]
        up    = [p.stickers[1] for p in sorted(self._face(UP),    key=lambda p: (p.pos.z, p.pos.x))]
        down  = [p.stickers[1] for p in sorted(self._face(DOWN),  key=lambda p: (-p.pos.z, p.pos.x))]
        front = [p.stickers[2] for p in sorted(self._face(FRONT), key=lambda p: (-p.pos.y, p.pos.x))]
        if self.backViewIsXray:
            back  = [p.stickers[2] for p in sorted(self._face(BACK),  key=lambda p: (-p.pos.y, p.pos.x))]
        else:
            back  = [p.stickers[2] for p in sorted(self._face(BACK),  key=lambda p: (-p.pos.y, -p.pos.x))]

        return (up + left[0:3] + front[0:3] + right[0:3] + back[0:3]
                   + left[3:6] + front[3:6] + right[3:6] + back[3:6]
                   + left[6:9] + front[6:9] + right[6:9] + back[6:9] + down)

    def getLabels (self, face=None):
        # get all stickers for the cube or a face
        if face == None:
            return self._label_list()
        elif face == 'R':
            return [p.getLabels()[0] for p in sorted(self._face(RIGHT), key=lambda p: (-p.pos.y, -p.pos.z))]
        elif face == 'L':
            return [p.getLabels()[0] for p in sorted(self._face(LEFT),  key=lambda p: (-p.pos.y, p.pos.z))]
        elif face == 'U':
            return [p.getLabels()[1] for p in sorted(self._face(UP),    key=lambda p: (p.pos.z, p.pos.x))]
        elif face == 'D':
            return [p.getLabels()[1] for p in sorted(self._face(DOWN),  key=lambda p: (-p.pos.z, p.pos.x))]
        elif face == 'F':
            return [p.getLabels()[2] for p in sorted(self._face(FRONT), key=lambda p: (-p.pos.y, p.pos.x))]
        elif face == 'B':
            return [p.getLabels()[2] for p in sorted(self._face(BACK),  key=lambda p: (-p.pos.y, p.pos.x))]
        else:
            return ''

    def _label_list(self):
        right = [p.getLabels()[0] for p in sorted(self._face(RIGHT), key=lambda p: (-p.pos.y, -p.pos.z))]
        left  = [p.getLabels()[0] for p in sorted(self._face(LEFT),  key=lambda p: (-p.pos.y, p.pos.z))]
        up    = [p.getLabels()[1] for p in sorted(self._face(UP),    key=lambda p: (p.pos.z, p.pos.x))]
        down  = [p.getLabels()[1] for p in sorted(self._face(DOWN),  key=lambda p: (-p.pos.z, p.pos.x))]
        front = [p.getLabels()[2] for p in sorted(self._face(FRONT), key=lambda p: (-p.pos.y, p.pos.x))]
        if self.backViewIsXray:
            back  = [p.getLabels()[2] for p in sorted(self._face(BACK),  key=lambda p: (-p.pos.y, p.pos.x))]
        else:
            back  = [p.getLabels()[2] for p in sorted(self._face(BACK),  key=lambda p: (-p.pos.y, -p.pos.x))]

        return (up + left[0:3] + front[0:3] + right[0:3] + back[0:3]
                   + left[3:6] + front[3:6] + right[3:6] + back[3:6]
                   + left[6:9] + front[6:9] + right[6:9] + back[6:9] + down)
        
    def flat_str(self):
        return ''.join(self._label_list())
        #return "".join(x for x in str(self) if x not in string.whitespace)

    def __str__(self):

        template = ("       {}{}{}\n"
                    "       {}{}{}\n"
                    "       {}{}{}\n"
                    "\n"
                    "{}{}{} {}{}{} {}{}{} {}{}{}\n"
                    "{}{}{} {}{}{} {}{}{} {}{}{}\n"
                    "{}{}{} {}{}{} {}{}{} {}{}{}\n"
                    "\n"
                    "       {}{}{}\n"
                    "       {}{}{}\n"
                    "       {}{}{}")

        return                ''.join(self._label_list()) + "\n       " + template.format(*self._sticker_list()).strip()
        #return                template.format(*self._sticker_list()).strip()


if __name__ == '__main__':
    cube = Cube("    DLU\n"
                "    RRD\n"
                "    FFU\n"
                "BBL DDR BRB LDL\n"
                "RBF RUU LFB DDU\n"
                "FBR BBR FUD FLU\n"
                "    DLU\n"
                "    ULF\n"
                "    LFR")
    print(cube)
