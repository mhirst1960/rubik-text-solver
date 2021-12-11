import sys
import time
import string

import rubik.Rotations
from rubik import cube
from rubik.cube import Cube
from rubik.maths import Point
from rubik.Piece import Piece

DEBUG = False

FACE = 'face'
EDGE = 'edge'
CORNER = 'corner'

RIGHT = X_AXIS = Point(1, 0, 0)
LEFT           = Point(-1, 0, 0)
UP    = Y_AXIS = Point(0, 1, 0)
DOWN           = Point(0, -1, 0)
FRONT = Z_AXIS = Point(0, 0, 1)
BACK           = Point(0, 0, -1)
class Solver:


    moveComplements = {
        'Y':'Yi',
        'Yi':'Y',
        'Y2':'Y2',
        'Z':'Zi',
        'Zi':'Z',
        'Z2':'Z2',
        'X':'Xi',
        'Xi':'X',
        'X2':'X2',

        'D':'Di',
        'Di':'D',
        'D2':'D2',
        'B':'Bi',
        'Bi':'B',
        'B2':'B2',
        'F':'Fi',
        'Fi':'F',
        'F2':'F2',
        'U':'Ui',
        'Ui':'U',
        'U2':'U2',
        'L':'Li',
        'Li':'L',
        'L2':'L2',
        'R':'Ri',
        'Ri':'R',
        'R2':'R2',
        
        'M':'Mi',
        'Mi':'M',
        'M2':'M2',
        'E':'Ei',
        'Ei':'E',
        'E2':'E2',
        'S':'Si',
        'Si':'S',
        'S2':'S2'    
    }
    
    def __init__(self, cube, groups=None):
        
        self.origionalCubeLabels = cube.getLabels()
        self.cube = cube

        self.initCube(cube)

        moves = cube.orientToFront()
        self.moves = moves.split()

        self.left_piece  = self.cube.findPieceByDestinations('L')
        self.right_piece = self.cube.findPieceByDestinations('R')
        self.up_piece    = self.cube.findPieceByDestinations('U')
        self.down_piece  = self.cube.findPieceByDestinations('D')
        
        if groups == None:
            groups = cube.getGroups()
            if groups == None:
                groups_str = "0" * 54  # everything is group "0"
            else:
                groups_str = "".join(x for x in groups if x not in string.whitespace)
        else:
            groups_str = "".join(x for x in groups if x not in string.whitespace)

    def initCube(self, cube):
        self.colors = cube.colors()
        self.stickers = cube.stickers()

    def solve(self):
        if DEBUG: print(self.cube)
        self.cross()
        if DEBUG: print('---\nCross done\n', self.cube)
        self.cross_corners()
        if DEBUG: print('---\nCorners done\n', self.cube)
        self.second_layer()
        if DEBUG: print('---\nSecond layer done\n', self.cube)
        self.back_face_edges()
        if DEBUG: print('---\nLast layer edges done\n', self.cube)
        self.last_layer_corners_position()
        if DEBUG: print('---\nLast layer corners -- position done\n', self.cube)
        self.last_layer_corners_orientation()
        if DEBUG: print('---\nLast layer corners -- orientation done\n', self.cube)
        self.last_layer_edges()
        if DEBUG: print('---\nSolved. Cube looks like this:\n', self.cube)

    def solveFront(self):

        self.cross()
        self.cross_corners()


    def generateCubeForMessage(self, frontString):
        # start fresh.  Destinations are assigned based on front string
        self.cube.clearAllDestinations()
        
        frontPiecesCopy = list()
        for p in sorted(self.cube._face(FRONT), key=lambda p: (-p.pos.y, p.pos.x)):
            frontPiecesCopy += [Piece(p.pos, p.getColors(), p.getLabels(), p.group, p.getDestinations())]
            
            
        #TODO need to assign front face: is either letter or '-'
        middleGroup = self.cube.frontFaceGroup()
        middleGroupIndex = int(middleGroup) - 1
        middleLetter = frontString[middleGroupIndex]
        middlePiece = self.cube.findPieceByLabelAndGroupWithNoDestination(middleLetter, middleGroup, FACE)
        if middlePiece == None:
            middlePiece = self.cube.findPieceByLabelAndGroupWithNoDestination('-', middleGroup, FACE)

        assert middlePiece is not None
        
        if middlePiece.pos[1] == 0:
            # rotate around Y until piece is in front
            for _ in range(4):
                if middlePiece.pos == FRONT:
                    break
                self.move('Y')
        else:
            #rotate around X until piece is in front
            for _ in range(4):
                if middlePiece.pos == FRONT:
                    break
                self.move('X')

        assert middlePiece.pos == FRONT
        #Set all the face desitnations based on current cube orientation
        #TODO not sure if we need to rotate around Y in the future for some cases.  I don't think so.
        self.cube.assignDefaultFaceDestinations()
        
        # each character is in a different group. find pieces that have that group and character
        futureFrontPieces = list()
        group = 1
        groupch = chr(ord('0') + group)
        count = 0
        for labelChar in frontString:
            labeledPiece = self.cube.findPieceByLabelAndGroupWithNoDestination(labelChar, groupch)

            matched = False

            if groupch == middleGroup and labeledPiece == None:
                labeledPiece = middlePiece
                #matched = True
                
            assert labeledPiece != None

            debugPieceList = list()
            
            #for p in sorted(self.cube._face(FRONT), key=lambda p: (-p.pos.y, p.pos.x)):
            #for p in self.cube.origionalFrontPieces:
            for p in frontPiecesCopy:
                if p.group != groupch:
                    continue
                
                rotated = False
                if not matched and p.type == labeledPiece.type:
                    futureFrontPieces += [labeledPiece]
                    print (f"rotate {labelChar} to front")
                    self.rotateLabelToFront(labelChar, labeledPiece, p.pos)
                    count += 1
                    #labeledPiece.assignDestinationToFront(labelChar, p.pos)
                    matched = True
                else:
                    blankPiece = self.cube.findPieceByLabelAndGroupWithNoDestination(label='-', group=groupch, type=p.type)
                    
                    if groupch == middleGroup and blankPiece == None:
                        blankPiece = middlePiece

                    assert blankPiece != None
                    
                    futureFrontPieces += [blankPiece]
                    print (f"rotate - to front")
                    self.rotateLabelToFront('-', blankPiece, p.pos)
                    count += 1
                    #blankPiece.assignDestinationToFront('-', p.pos)
                print(f"{frontString}: {labelChar} Cube so far:\n", self.cube)
                print(f"moves so far: {self.moves}")
                
            group+=1
            groupch = chr(ord('0') + group)
        
        # now verify and assert that the front stickers contain the requested string
        message = ""
        for ffp in futureFrontPieces:
            for s in ffp.stickers:
                if s != None and s.destination == 'F':
                    message += s.label
        m = message.replace("-", "")
        assert m == frontString.replace("-", "")
        
        # Now assign the rest of the destinations however they might fall after solved
        self.cube.assignDefaultDestinations()

        print ("========================================")
        print ("========================================")
        print (f"{frontString} Cube is configured.  Solved is this: \n", self.cube)
        self.undoAllMoves()

        print (f"{frontString} Cube is configured. Unsolved is this: \n", self.cube)
        print ("========================================")
        print ("========================================")

        if True:
            #Just verifying that cube can be solved
            tmpCube = Cube(self.cube)
            tSolver = Solver(tmpCube)
            tSolver.solve()
            tSolver.orientToFront()
            print (f" {frontString} Cube solved front not aligned:\n", tmpCube)
            tSolver.alignToMessageOrder()
            print (f" {frontString} Cube solved front:\n", tmpCube)
            tmpCube.assignDefaultDestinations()
            tSolver.undoAllMoves()
            print (f" {frontString} Cube origional orientation:\n", tmpCube)
            print (f" {frontString} should match origional cube:\n", self.cube)
        
                
        return self.cube
    
        """ 
        # rotate the entire cube and, if needed, assign non-front destinations
        move_str = self.cube.orientToFront()
        if move_str != None and not move_str.isspace():
            self.moves.extend(move_str.split())

        # non-front destinations may have been newly assigned so reinitialize the face pieces
        self.left_piece  = self.cube.findPieceByDestinations('L')
        self.right_piece = self.cube.findPieceByDestinations('R')
        self.up_piece    = self.cube.findPieceByDestinations('U')
        self.down_piece  = self.cube.findPieceByDestinations('D')
        #self.solveFrontString(message)
        return cube.Cube(self.cube)
        """
        
    def solveFrontString(self, frontString):
        """
        Solve the front layer such that the frontString string appears on that side of the cube.
        Only the front palyer is solved since we don't really care how the rest of the cube looks
        as long as the message shows up on the side we do care about.
        
        Keep the front string very short.  For instance 3 letters for a person's initials.
        "-" represents a blank.  "?" is unknown.  Otherwise, any ASCII character is good.
        
        Careful thought needs to be put into the placement of stickers on a cube such that all possoible
        strings can be solved without interfering with eachother.  If you hit a bad assert then you
        probably need to redesign the sticker arrangement on the cube.
        """
                        
        tmpCube = self.generateCubeForMessage(frontString)
        
        self.initCube(tmpCube)

        # assign the new destinations to our cube
        self.cube.setDestinations(tmpCube)

        ##########################################
        # Setup complete. Now actually solve it!
        ##########################################
        
        tSolver = Solver(self.cube)
        tSolver.solveFront()
        tSolver.alignToMessageOrder()
        self.moves = tSolver.moves
        
        # Solved.  Verify and assert we got what we wanted
        message = ""
        FRONT = Point(0, 0, 1)

        front = ''.join([p.getLabels()[2] for p in sorted(self.cube._face(FRONT), key=lambda p: (-p.pos.y, p.pos.x))])
        message = front.replace("-", "")
        assert message == frontString.replace("-", "")
        
    def orientToFront(self):
        moves = self.cube.orientToFront()
        self.moves += moves.split()
        
    def alignToMessageOrder(self):
        """
        rotate the cube so beginning of message is top-left and end if botto-left
        Simply rotate around Z until groups are in increasing numberical order
        """
        FRONT = Point(0, 0, 1)

        goodOrientation = False
        for i in range (4):
            frontGroups = [p.getGroups()[2] for p in sorted(self.cube._face(FRONT), key=lambda p: (-p.pos.y, p.pos.x))]
            if all(frontGroups[i] <= frontGroups[i+1] for i in range(len(frontGroups)-1)):
                goodOrientation = True
                break
            self.move("Z")
        
        assert goodOrientation
        
    def getMovesString(self):
        return  ' '.join(self.moves)

    def move(self, move_str):
        self.moves.extend(move_str.split())
        self.cube.sequence(move_str)
        #print (f"after move {move_str} cube looks like this: \n", self.cube)

    def undoLastMove(self):
        """
        perform complement most recent move.  Undo it.
        """
        lastMove = self.moves[-1]
        undoMove = self.moveComplements[lastMove]
        self.cube.sequence(undoMove)
        self.moves = self.moves[:-1]
    
    def undoAllMoves(self):
        """
        perform complement move for every item in self.moves.  In reverse order.
        """
        
        while len(self.moves) > 0:
            self.undoLastMove()

    def rotateLabelToFront(self, labelChar, piece, destinationPosition):
        """
        The piece has at least one sticker labelled with labelChar.
        Use legal cube moves to place the piece in the destinationPosition
        such that the sticker with labelChar faces front
        """
        
        labels = piece.getLabels()
        if piece.type == FACE:
            for i, label in enumerate(labels):
                if label == None:
                    continue
                elif label == labelChar:
                    piece.setDestination(i, 'F')

        elif piece.type == EDGE:
            
            if destinationPosition == LEFT + FRONT:
                self.move("Z2")
                self.placeFrEdgeLabel(piece, labelChar)
                self.move("Z2")
            elif destinationPosition == RIGHT + FRONT:
                self.placeFrEdgeLabel(piece, labelChar)
            elif destinationPosition == UP + FRONT:
                self.move("Z")
                self.placeFrEdgeLabel(piece, labelChar)
                self.move("Zi")
            elif destinationPosition == DOWN + FRONT:
                self.move("Zi")
                self.placeFrEdgeLabel(piece, labelChar)
                self.move("Z")
                        
        else:

            if destinationPosition == LEFT + UP + FRONT:
                self.move("Z2")
                self.placeFrdCornerLabel(piece, labelChar)
                self.move("Z2")
            elif destinationPosition == RIGHT + UP + FRONT:
                self.move("Z")
                self.placeFrdCornerLabel(piece, labelChar)
                self.move("Zi")
            elif destinationPosition == LEFT + DOWN + FRONT:
                self.move("Zi")
                self.placeFrdCornerLabel(piece, labelChar)
                self.move("Z")
            elif destinationPosition == RIGHT + DOWN + FRONT:
                self.placeFrdCornerLabel(piece, labelChar)

        piece.setDestinationsFromPos()

        destinations = piece.getDestinations()

        print (f"piece destinations: {''.join(piece.getDestinationsNotNone())}")

    def cross(self):
        if DEBUG: print("cross..")
        # place the front-LEFT piece
        
        fl_piece = self.cube.findPieceByDestinations('F', 'L')
        fr_piece = self.cube.findPieceByDestinations('F', 'R')
        fu_piece = self.cube.findPieceByDestinations('F', 'U')
        fd_piece = self.cube.findPieceByDestinations('F', 'D')
                
        # "E L Ei Li" move left-back (left face) edge to left-front (front face) Basically "E" without disturbing rest of front
        # "Ei R E Ri" move right-back (right face) edge to right-front (front face) Basically "Ei" without disturbing rest of front
        
        self._cross_left_or_right(fl_piece, self.left_piece, self.cube.leftDestination(), "L L", "E L Ei Li")
        self._cross_left_or_right(fr_piece, self.right_piece, self.cube.rightDestination(), "R R", "Ei R E Ri")

        self.move("Z")

        self._cross_left_or_right(fd_piece, self.down_piece, self.cube.leftDestination(), "L L", "E L Ei Li")
        self._cross_left_or_right(fu_piece, self.up_piece, self.cube.rightDestination(), "R R", "Ei R E Ri")
        self.move("Zi")

    def _cross_left_or_right(self, edge_piece, face_piece, face_destination, move_1, move_2):
        # don't do anything if piece is in correct place
        if (edge_piece.pos == (face_piece.pos.x, face_piece.pos.y, 1)
                and edge_piece.getDestinations()[2] == self.cube.frontDestination()):
            return

        # ensure piece is at z = -1
        undo_move = None
        if edge_piece.pos.z == 0:
            pos = Point(edge_piece.pos)
            pos.x = 0  # pick the UP or DOWN face
            cw, cc = cube.get_rot_from_face(pos)

            if edge_piece.pos in (cube.LEFT + cube.UP, cube.RIGHT + cube.DOWN):
                self.move(cw)
                undo_move = cc
            else:
                self.move(cc)
                undo_move = cw
        elif edge_piece.pos.z == 1:
            pos = Point(edge_piece.pos)
            pos.z = 0
            cw, cc = cube.get_rot_from_face(pos)
            self.move("{0} {0}".format(cc))
            # don't set the undo move if the piece starts out in the right position
            # (with wrong orientation) or we'll screw up the remainder of the algorithm
            if edge_piece.pos.x != face_piece.pos.x:
                undo_move = "{0} {0}".format(cw)

        assert edge_piece.pos.z == -1

        # piece is at z = -1, rotate to correct face (LEFT or RIGHT)
        
        # rotate back layer until piece we want is aligned with its front destiny position
        count = 0
        while (edge_piece.pos.x, edge_piece.pos.y) != (face_piece.pos.x, face_piece.pos.y):
            self.move("B")
            count += 1
            if count == 4: # back where we started
                print("ERROR: unsolvable cube? ", self.cube)
                raise Exception("Stuck in loop - unsolvable cube?\n")

        # if we moved a correctly-placed piece, restore it
        if undo_move:
            self.move(undo_move)

        # the piece is on the correct face on plane z = -1, but has two orientations
        if edge_piece.getDestinations()[0] == face_destination:
            self.move(move_1)
        else:
            self.move(move_2)

    def cross_corners(self):
        if DEBUG: print("cross_corners")

        fld_piece = self.cube.findPieceByDestinations('F','L','D')
        flu_piece = self.cube.findPieceByDestinations('F','L','U')
        frd_piece = self.cube.findPieceByDestinations('F','R','D')
        fru_piece = self.cube.findPieceByDestinations('F','R','U')
        
        self.place_frd_corner(frd_piece, self.right_piece, self.down_piece, self.cube.frontDestination())
        self.move("Z")
        self.place_frd_corner(fru_piece, self.up_piece, self.right_piece, self.cube.frontDestination())
        self.move("Z")
        self.place_frd_corner(flu_piece, self.left_piece, self.up_piece, self.cube.frontDestination())
        self.move("Z")
        self.place_frd_corner(fld_piece, self.down_piece, self.left_piece, self.cube.frontDestination())
        self.move("Z")

    def placeFrEdgeLabel(self, edgePiece, label):
        # move the corner piece that has this label into position front-right-down
        #  such that the label is oriented to the front
        
        if label == 'Z':
            print ("Z breakpoint here")

        if (edgePiece.pos == RIGHT + FRONT):
            if edgePiece.getLabel(2) == label:
                #already in place.  Nothing to do.
                return
            else:
                #swap orientation
                self.move("Ri S R2 S2 Ri")
                return

        if edgePiece.pos.z == 1:
            count = 0
            while (edgePiece.pos.x, 0, 0) != RIGHT:
                self.move("Z")
                count += 1
                assert count < 5
            
            # piece is in front: move to back-right
            self.move("S Di Si D")
            
        #if edgePiece z=0 move to left-down
        if edgePiece.pos.z == 0:
            count = 0
            while edgePiece.pos != Point(-1, -1, 0):
                self.move("S")
                count += 1
                assert count < 5
            if edgePiece.getLabel(1) == label:
                self.move("R S2 Ri")
            else:
                self.move("Ri Si R")
            assert edgePiece.getLabel(2) == label
            return
        
        count = 0
        while (edgePiece.pos.x, 0, 0) != RIGHT:
            self.move("B")
            count += 1
            assert count < 10

        if edgePiece.pos.z == 1:
            # if piece is already oriented correctly we are done!
            if edgePiece.getLabel(2) == label:
                return
            # 2) if piece is in front: move to back, to back-right
            self.move("S Di Si D")
            
        # z=-1 on right-bottom move to position front-right
        # two possible moves
        if edgePiece.getLabel(0) == label:
            # label is on right sticker
            self.move("B E Bi Ei")
        else:
            #label is on back sticker
            self.move("E B2 Ei")
            
            
    def placeFrdCornerLabel(self, cornerPiece, label):
        # move the corner piece that has this label into position front-right-down
        #  such that the label is oriented to the front
                
        if (cornerPiece.pos == LEFT + RIGHT + FRONT) and (cornerPiece.getLabel(2) == label):
            #already in place.  Nothing to do.
            return
        
        if cornerPiece.pos.z == 1:
            count = 0
            while (cornerPiece.pos.x, cornerPiece.pos.y, 0) != (RIGHT + DOWN):
                self.move("Z")
                count += 1
                assert count < 10
            
            # piece is in front: move to back-right-down
            self.move("Ri Bi R B")
            
            #rotate the cube back to where it was so we can solve FRD
            for _ in range(count):
                self.move("Zi")

        # rotate piece to be directly below its destination
        count = 0
        while (cornerPiece.pos.x, cornerPiece.pos.y, 0) != (RIGHT + DOWN):
            self.move("B")
            count += 1
            assert count < 10

        if cornerPiece.pos.z == 1:
            # if piece is already oriented correctly we are done!
            if cornerPiece.getLabel(2) == label:
                return
            # if piece is in front: move to back, to back-right-down
            self.move("Ri Bi R B")

        # move into position front-right-down
        # there are 3 possible moves:
            # move back-right-down (right sticker) to front-right-down (front sticker) Like "L" without disturbing rest of up
        if cornerPiece.getLabel(0) == label:
            # move back-right-down (right sticker) to front-right-down (front sticker) Like "L" without disturbing rest of up
            self.move("B D Bi Di")
        elif cornerPiece.getLabel(1) == label:
            # move back-right-down (down sticker) to front-right-down (front sticker) Like "R" without disturbing rest of front
            self.move("Bi Ri B R")
        else:
            # move back-right-down (back sticker) to front-right-down (front sticker) Like taking the back corner sticker and moving to the opposite side (front)
            self.move("Ri B B R Bi Bi D Bi Di")

        

    def place_frd_corner(self, corner_piece, right_piece, down_piece, front_destination):
        # rotate to z = -1
        if corner_piece.pos.z == 1:
            pos = Point(corner_piece.pos)
            pos.x = pos.z = 0
            cw, cc = cube.get_rot_from_face(pos)

            # be careful not to screw up other pieces on the front face
            count = 0
            undo_move = cc
            while corner_piece.pos.z != -1:
                self.move(cw)
                count += 1

            if count > 1:
                # go the other direction because I don't know which is which.
                # we need to do only one flip (net) or we'll move other
                # correctly-placed corners out of place.
                for _ in range(count):
                    self.move(cc)

                count = 0
                while corner_piece.pos.z != -1:
                    self.move(cc)
                    count += 1
                undo_move = cw
            self.move("B")
            for _ in range(count):
                self.move(undo_move)

        # rotate piece to be directly below its destination
        while (corner_piece.pos.x, corner_piece.pos.y) != (right_piece.pos.x, down_piece.pos.y):
            self.move("B")

        # there are three possible orientations for a corner
        if corner_piece.getDestinations()[0] == front_destination:
            # move back-right-down (right sticker) to front-right-down (front sticker) Like "L" without disturbing rest of up
            self.move("B D Bi Di")
        elif corner_piece.getDestinations()[1] == front_destination:
            # move back-right-down (down sticker) to front-right-down (front sticker) Like "R" without disturbing rest of front
            self.move("Bi Ri B R")
        else:
            # move back-right-down (back sticker) to front-right-down (front sticker) Like taking the back corner sticker and moving to the opposite side (front)
            self.move("Ri B B R Bi Bi D Bi Di")

    def second_layer(self):

        rd_piece = self.cube.findPieceByDestinations('R','D')
        ru_piece = self.cube.findPieceByDestinations('R','U')
        ld_piece = self.cube.findPieceByDestinations('L','D')
        lu_piece = self.cube.findPieceByDestinations('L','U')
                
        self.place_middle_layer_ld_edge(ld_piece, self.cube.leftDestination(), self.cube.downDestination())
        self.move("Z")
        self.place_middle_layer_ld_edge(rd_piece, self.cube.leftDestination(), self.cube.downDestination())
        self.move("Z")
        self.place_middle_layer_ld_edge(ru_piece, self.cube.leftDestination(), self.cube.downDestination())
        self.move("Z")
        self.place_middle_layer_ld_edge(lu_piece, self.cube.leftDestination(), self.cube.downDestination())
        self.move("Z")

    def place_middle_layer_ld_edge(self, ld_piece, left_destination, down_destination):
        # move to z == -1
        if ld_piece.pos.z == 0:
            count = 0
            while (ld_piece.pos.x, ld_piece.pos.y) != (-1, -1):
                self.move("Z")
                count += 1

            self.move("B L Bi Li Bi Di B D")
            for _ in range(count):
                self.move("Zi")

        assert ld_piece.pos.z == -1

        if ld_piece.getDestinations()[2] == left_destination:
            # left_color is on the back face, move piece to to down face
            while ld_piece.pos.y != -1:
                self.move("B")
            self.move("B L Bi Li Bi Di B D")
        elif ld_piece.getDestinations()[2] == down_destination:
            # down_color is on the back face, move to left face
            while ld_piece.pos.x != -1:
                self.move("B")
            self.move("Bi Di B D B L Bi Li")
        else:
            raise Exception("BUG!!")

    def back_face_edges(self):
        # rotate BACK to FRONT
        self.move("X X")

        # States:  1     2     3     4
        #         -B-   -B-   ---   ---
        #         BBB   BB-   BBB   -B-
        #         -B-   ---   ---   ---
        def state1():            
            return (self.cube[0, 1, 1].getDestinations()[2] == 'B' and
                    self.cube[-1, 0, 1].getDestinations()[2] == 'B' and
                    self.cube[0, -1, 1].getDestinations()[2] == 'B' and
                    self.cube[1, 0, 1].getDestinations()[2] == 'B')

        def state2():
            return (self.cube[0, 1, 1].getDestinations()[2] == 'B' and
                    self.cube[-1, 0, 1].getDestinations()[2] == 'B')
            
        def state3():
            return (self.cube[-1, 0, 1].getDestinations()[2] == 'B' and
                    self.cube[1, 0, 1].getDestinations()[2] == 'B')
            
        def state4():
            return (self.cube[0, 1, 1].getDestinations()[2] != 'B' and
                    self.cube[-1, 0, 1].getDestinations()[2] != 'B' and
                    self.cube[0, -1, 1].getDestinations()[2] != 'B' and
                    self.cube[1, 0, 1].getDestinations()[2] != 'B')
            
        count = 0
        while not state1():
            if state4() or state2():
                self.move("D F R Fi Ri Di")
            elif state3():
                self.move("D R F Ri Fi Di")
            else:
                self.move("F")
            count += 1
            if count == 10:
                raise Exception("Stuck in loop - unsolvable cube\n" + str(self.cube))

        self.move("Xi Xi")

    def last_layer_corners_position(self):
        self.move("X X")
        # UP face:
        #  4-3
        #  ---
        #  2-1
        move_1 = "Li Fi L D F Di Li F L F F "  # swaps 1 and 2
        move_2 = "F Li Fi L D F Di Li F L F "  # swaps 1 and 3

        c1 = self.cube.findPieceByDestinations('B','R','U')
        c2 = self.cube.findPieceByDestinations('B','L','U')
        c3 = self.cube.findPieceByDestinations('B','R','D')
        c4 = self.cube.findPieceByDestinations('B','L','D')
        
        # place corner 4
        if c4.pos == Point(1, -1, 1):
            self.move(move_1 + "Zi " + move_1 + " Z")
        elif c4.pos == Point(1, 1, 1):
            self.move("Z " + move_2 + " Zi")
        elif c4.pos == Point(-1, -1, 1):
            self.move("Zi " + move_1 + " Z")
        assert c4.pos == Point(-1, 1, 1)

        # place corner 2
        if c2.pos == Point(1, 1, 1):
            self.move(move_2 + move_1)
        elif c2.pos == Point(1, -1, 1):
            self.move(move_1)
        assert c2.pos == Point(-1, -1, 1)

        # place corner 3 and corner 1
        if c3.pos == Point(1, -1, 1):
            self.move(move_2)
        assert c3.pos == Point(1, 1, 1)
        assert c1.pos == Point(1, -1, 1)

        self.move("Xi Xi")

    def last_layer_corners_orientation(self):
        self.move("X X")

        # States:  1        2      3      4      5      6      7      8
        #           B      B             B      B        B
        #         BB-      -B-B   BBB    -BB    -BB   B-B-   B-B-B   BBB
        #         BBB      BBB    BBB    BBB    BBB    BBB    BBB    BBB
        #         -B-B     BB-    -B-    -BB    BB-B  B-B-   B-B-B   BBB
        #         B          B    B B    B               B
        def state1():           
            return (self.cube[ 1,  1, 1].getDestinations()[1] == 'B' and
                    self.cube[-1, -1, 1].getDestinations()[1] == 'B' and
                    self.cube[ 1, -1, 1].getDestinations()[0] == 'B')
            
        def state2():
            return (self.cube[-1,  1, 1].getDestinations()[1] == 'B' and
                    self.cube[ 1,  1, 1].getDestinations()[0] == 'B' and
                    self.cube[ 1, -1, 1].getDestinations()[1] == 'B')

        def state3():
            return (self.cube[-1, -1, 1].getDestinations()[1] == 'B' and
                    self.cube[ 1, -1, 1].getDestinations()[1] == 'B' and
                    self.cube[-1,  1, 1].getDestinations()[2] == 'B' and
                    self.cube[ 1,  1, 1].getDestinations()[2] == 'B')
            
        def state4():
            return (self.cube[-1,  1, 1].getDestinations()[1] == 'B' and
                    self.cube[-1, -1, 1].getDestinations()[1] == 'B' and
                    self.cube[ 1,  1, 1].getDestinations()[2] == 'B' and
                    self.cube[ 1, -1, 1].getDestinations()[2] == 'B')
            
        def state5():
            return (self.cube[-1,  1, 1].getDestinations()[1] == 'B' and
                    self.cube[ 1, -1, 1].getDestinations()[0] == 'B')
            
        def state6():
            return (self.cube[ 1,  1, 1].getDestinations()[1] == 'B' and
                    self.cube[ 1, -1, 1].getDestinations()[1] == 'B' and
                    self.cube[-1, -1, 1].getDestinations()[0] == 'B' and
                    self.cube[-1,  1, 1].getDestinations()[0] == 'B')
            
        def state7():
            return (self.cube[ 1,  1, 1].getDestinations()[0] == 'B' and
                    self.cube[ 1, -1, 1].getDestinations()[0] == 'B' and
                    self.cube[-1, -1, 1].getDestinations()[0] == 'B' and
                    self.cube[-1,  1, 1].getDestinations()[0] == 'B')
            
        def state8():
            return (self.cube[ 1,  1, 1].getDestinations()[2] == 'B' and
                    self.cube[ 1, -1, 1].getDestinations()[2] == 'B' and
                    self.cube[-1, -1, 1].getDestinations()[2] == 'B' and
                    self.cube[-1,  1, 1].getDestinations()[2] == 'B')
            
        move_1 = "Ri Fi R Fi Ri F F R F F "
        move_2 = "R F Ri F R F F Ri F F "

        count = 0
        while not state8():
            count += 1
            assert count < 10 # endless loop.  Possibly an impossible cube
            if state1(): self.move(move_1)
            elif state2(): self.move(move_2)
            elif state3(): self.move(move_2 + "F F " + move_1)
            elif state4(): self.move(move_2 + move_1)
            elif state5(): self.move(move_1 + "F " + move_2)
            elif state6(): self.move(move_1 + "Fi " + move_1)
            elif state7(): self.move(move_1 + "F F " + move_1)
            else:
                self.move("F")

        # rotate corners into correct locations (cube is inverted, so swap up and down colors)
        bru_corner = self.cube.findPieceByDestinations('B','R','D')
        
        while bru_corner.pos != Point(1, 1, 1):
            self.move("F")

        self.move("Xi Xi")

    def last_layer_edges(self):
        self.move("X X")

        br_edge = self.cube.findPieceByDestinations('B','R')
        bl_edge = self.cube.findPieceByDestinations('B','L')
        bu_edge = self.cube.findPieceByDestinations('B','U')
        bd_edge = self.cube.findPieceByDestinations('B','D')
        
        # States:
        #       1              2
        #      ---            ---
        #      ---            ---
        #      -B-            -a-
        #  --- B-B ---    aaa BBB ---
        #  --B -B- B--    aaB -B- B--
        #  --- B-B ---    aaa B-B ---
        #      -B-            -B-
        #      ---            ---
        #      ---            ---
        #              (aB edge on any FRONT)
        def state1():            
            return (bu_edge.getDestinations()[2] != 'B' and
                    bd_edge.getDestinations()[2] != 'B' and
                    bl_edge.getDestinations()[2] != 'B' and
                    br_edge.getDestinations()[2] != 'B')
               
        def state2():
            return (bu_edge.getDestinations()[2] == 'B' or
                    bd_edge.getDestinations()[2] == 'B' or
                    bl_edge.getDestinations()[2] == 'B' or
                    br_edge.getDestinations()[2] == 'B')

        cycle_move = "R R F D Ui R R Di U F R R"
        h_pattern_move = "Ri S Ri Ri S S Ri Fi Fi R Si Si Ri Ri Si R Fi Fi "
        fish_move = "Di Li " + h_pattern_move + " L D"

        if state1():
            # ideally, convert state1 into state2
            self._handle_last_layer_state1(br_edge, bl_edge, bu_edge, bd_edge, cycle_move, h_pattern_move)
        if state2():
            self._handle_last_layer_state2(br_edge, bl_edge, bu_edge, bd_edge, cycle_move)

        def h_pattern1():
            return (self.cube[-1,  0, 1].getDestinations()[0] != self.cube.leftDestination() and
                    self.cube[ 1,  0, 1].getDestinations()[0] != self.cube.rightDestination() and
                    self.cube[ 0, -1, 1].getDestinations()[1] == self.cube.downDestination() and
                    self.cube[ 0,  1, 1].getDestinations()[1] == self.cube.upDestination())
            
        def h_pattern2():
            return (self.cube[-1,  0, 1].getDestinations()[0] == self.cube.leftDestination() and
                    self.cube[ 1,  0, 1].getDestinations()[0] == self.cube.rightDestination() and
                    self.cube[ 0, -1, 1].getDestinations()[1] == self.cube.frontDestination() and
                    self.cube[ 0,  1, 1].getDestinations()[1] == self.cube.frontDestination())
            
        def fish_pattern():
            return (self.cube[cube.FRONT + cube.DOWN].getDestinations()[2] == self.cube.downDestination() and
                    self.cube[cube.FRONT + cube.RIGHT].getDestinations()[2] == self.cube.rightDestination() and
                    self.cube[cube.FRONT + cube.DOWN].getDestinations()[1] == self.cube.frontDestination() and
                    self.cube[cube.FRONT + cube.RIGHT].getDestinations()[0] == self.cube.frontDestination())

        count = 0
        while not self.cube.is_solved():
            for _ in range(4):
                if fish_pattern():
                    self.move(fish_move)
                    if self.cube.is_solved():
                        return
                else:
                    self.move("Z")

            if h_pattern1():
                self.move(h_pattern_move)
            elif h_pattern2():
                self.move("Z " + h_pattern_move + "Zi")
            else:
                self.move(cycle_move)
            count += 1
            if count == 10:
                raise Exception("Stuck in loop - unsolvable cube:\n" + str(self.cube))

        self.move("Xi Xi")


    def _handle_last_layer_state1(self, br_edge, bl_edge, bu_edge, bd_edge, cycle_move, h_move):
        if DEBUG: print("_handle_last_layer_state1")
        def check_edge_lr():
            return self.cube[cube.LEFT + cube.FRONT].getDestinations()[2] == self.cube.leftDestination()

        count = 0
        while not check_edge_lr():
            self.move("F")
            count += 1
            if count == 4:
                raise Exception("Bug: Failed to handle last layer state1")

        self.move(h_move)

        for _ in range(count):
            self.move("Fi")


    def _handle_last_layer_state2(self, br_edge, bl_edge, bu_edge, bd_edge, cycle_move):
        if DEBUG: print("_handle_last_layer_state2")
        def correct_edge():
            piece = self.cube[cube.LEFT + cube.FRONT]
            if piece.getDestinations()[2] == self.cube.frontDestination() and piece.getDestinations()[0] == self.cube.leftDestination():
                return piece
            piece = self.cube[cube.RIGHT + cube.FRONT]
            if piece.getDestinations()[2] == self.cube.frontDestination() and piece.getDestinations()[0] == self.cube.rightDestination():
                return piece
            piece = self.cube[cube.UP + cube.FRONT]
            if piece.getDestinations()[2] == self.cube.frontDestination() and piece.getDestinations()[1] == self.cube.upDestination():
                return piece
            piece = self.cube[cube.DOWN + cube.FRONT]
            if piece.getDestinations()[2] == self.cube.frontDestination() and piece.getDestinations()[1] == self.cube.downDestination():
                return piece

        count = 0
        while True:
            edge = correct_edge()
            if edge == None:
                self.move(cycle_move)
            else:
                break

            count += 1

            if count % 3 == 0:
                self.move("Z")

            if count == 12:
                raise Exception("Stuck in loop - unsolvable cube:\n" + str(self.cube))

        while edge.pos != Point(-1, 0, 1):
            self.move("Z")

        assert self.cube[cube.LEFT + cube.FRONT].getDestinations()[2] == self.cube.frontDestination() and \
               self.cube[cube.LEFT + cube.FRONT].getDestinations()[0] == self.cube.leftDestination()


if __name__ == '__main__':
    DEBUG = True
    cube = cube.Cube("DLURRDFFUBBLDDRBRBLDLRBFRUULFBDDUFBRBBRFUDFLUDLUULFLFR")
    print("Solving:\n", cube)
    orig = cube.Cube(cube)
    solver = Solver(cube)
    solver.solve()

    print(f"{len(solver.moves)} moves: {' '.join(solver.moves)}")

    check = cube.Cube(orig)
    check.sequence(" ".join(solver.moves))
    assert check.is_solved()
