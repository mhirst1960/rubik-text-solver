import sys
import time
import string

import rubik.Rotations
from rubik import cube
from rubik.maths import Point
from rubik.Piece import Piece

DEBUG = False

FACE = 'face'
EDGE = 'edge'
CORNER = 'corner'

class Solver:

    def __init__(self, c, groups=None):
        
        self.origionalCubeLabels = c.getLabels()
        
        c.orientToFront()
        
        self.cube = c
        self.colors = c.colors()
        self.stickers = c.stickers()
        self.moves = []

        self.left_piece  = self.cube.findPieceByDestinations('L')
        self.right_piece = self.cube.findPieceByDestinations('R')
        self.up_piece    = self.cube.findPieceByDestinations('U')
        self.down_piece  = self.cube.findPieceByDestinations('D')
        
        if groups == None:
            groups_str = "0" * 54  # everything is group "0"
        else:
            groups_str = "".join(x for x in groups if x not in string.whitespace)
        
        frontGroups = list()
        for r in range(12, 15):
            frontGroups += [groups_str[r]]
        for r in range(24, 27):
            frontGroups += [groups_str[r]]
        for r in range(36, 39):
            frontGroups += [groups_str[r]]
        
            
        self.origionalFrontPieces = list()
        groupIndex = 0
        for y in range(-1,2):
            for x in range(-1,2):
                if x != 0 and y != 0:
                    type = CORNER
                    colors = ('W','W','W') # fake colors.  We don't care
                elif x == 0 and y == 0:
                    type = FACE
                    colors = ('W', None, None) # fake colors.  We don't care
                else:
                    type = EDGE
                    colors = ('W','W', None) # fake colors.  We don't care
                self.origionalFrontPieces += [Piece(pos=Point(x,y,1), colors=colors, group=frontGroups[groupIndex])]
                groupIndex += 1


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


    def generateCubeForMessage(self, message):
        self.solveFrontString(message)
        return cube.Cube(self.cube)
        
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
                        
        # start fresh.  Destinations are assigned based on front string
        self.cube.clearAllDestinations()
        #self.cube.assignDefaultFaceDestinations()
    
        # each character is in a different group. find pieces that have that group and character
        futureFrontPieces = list()
        group = 1
        groupch = chr(ord('0') + group)
        for labelChar in frontString:
            labeledPiece = self.cube.findPieceByLabelAndGroupWithNoDestination(labelChar, groupch)
            
            assert labeledPiece != None

            matched = False

            for p in self.origionalFrontPieces:
                if p.group != groupch:
                    continue
                
                rotated = False
                if not matched and p.type == labeledPiece.type:
                    futureFrontPieces += [labeledPiece]
                    labeledPiece.assignDestinationToFront(labelChar, p.pos)
                    matched = True
                else:
                    blankPiece = self.cube.findPieceByLabelAndGroupWithNoDestination(label='-', group=groupch, type=p.type)
                    
                    assert blankPiece != None
                    
                    futureFrontPieces += [blankPiece]
                    blankPiece.assignDestinationToFront('-', p.pos)
                                                             
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
        
        #print ("Cube before orient:\n", self.cube)
        
        # rotate the entire cube and, if needed, assign non-front destinations
        move_str = self.cube.orientToFront()
        if move_str != None and not move_str.isspace():
            self.moves.extend(move_str.split())

        # non-front destinations may have been newly assigned so reinitialize the face pieces
        self.left_piece  = self.cube.findPieceByDestinations('L')
        self.right_piece = self.cube.findPieceByDestinations('R')
        self.up_piece    = self.cube.findPieceByDestinations('U')
        self.down_piece  = self.cube.findPieceByDestinations('D')

        ##########################################
        # Setup complete. Now actually solve it!
        ##########################################

        #print ("Cube before cross:\n", self.cube)

        self.cross()
        self.cross_corners()
        #Done. Do not solve the middle slice and back layer.  There is no need.  Besides: destinations have not been assigned.
        self.alignToMessageOrder()
        #print ("after cross_corners: ", self.cube)
        # Solved.  Verify and assert we got what we wanted
        message = ""
        FRONT = Point(0, 0, 1)

        front = ''.join([p.getLabels()[2] for p in sorted(self.cube._face(FRONT), key=lambda p: (-p.pos.y, p.pos.x))])
        message = front.replace("-", "")
        assert message == frontString.replace("-", "")
        
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
        
    def move(self, move_str):
        self.moves.extend(move_str.split())
        self.cube.sequence(move_str)

    def cross(self):
        if DEBUG: print("cross..")
        # place the front-LEFT piece
        
        fl_piece = self.cube.findPieceByDestinations('F', 'L')
        fr_piece = self.cube.findPieceByDestinations('F', 'R')
        fu_piece = self.cube.findPieceByDestinations('F', 'U')
        fd_piece = self.cube.findPieceByDestinations('F', 'D')
                
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
        
        # rotate back layer until peice we want is aligned with its front destiny position
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
            self.move("B D Bi Di")
        elif corner_piece.getDestinations()[1] == front_destination:
            self.move("Bi Ri B R")
        else:
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
    c = cube.Cube("DLURRDFFUBBLDDRBRBLDLRBFRUULFBDDUFBRBBRFUDFLUDLUULFLFR")
    print("Solving:\n", c)
    orig = cube.Cube(c)
    solver = Solver(c)
    solver.solve()

    print(f"{len(solver.moves)} moves: {' '.join(solver.moves)}")

    check = cube.Cube(orig)
    check.sequence(" ".join(solver.moves))
    assert check.is_solved()
