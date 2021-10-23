#! /bin/python3

import random
import time
from rubik import solve
from rubik.cube import Cube
from rubik.solve import Solver
from rubik.optimize import optimize_moves
from rubik.RobotMoves import RobotMoves


CUBE_COLORS = """
    OOO
    OOO
    OOO
GGG WWW BBB YYY
GGG WWW BBB YYY
GGG WWW BBB YYY
    RRR
    RRR
    RRR
"""

# pieces labeled with any character.  "-" means no label or None
TMW_CUBE_LABELS = """
    CEK
    B-L
    D-S
J-L -T- --M ---
ANJ -M- NVL Z--
--T -W- H-S ---
    LGG
    -E-
    --M
"""

# pieces labeled with any character.  "-" means no label or None
TMW_CUBE_GROUPS = """
    111
    121
    111
111 111 111 111
222 222 222 222
333 333 333 333
    333
    323
    333
"""


TMW1_PEOPLE = [
    "TMW",  # The Mad Wrapper
    
    "DEH",  # Don
    "LMH",  # Linnea
    "EVH",  # Eric
    "JZH",  # Julie Howe
    "CAM",  # Caroline

    "C-M",  # Chris
    "SJG",  # Sandy
    "DAG",  # David
    "MNH",  # Mike
    "DJH",  # Diane
    "SJS",  # Steven
    "KLH",  # Kristin
    "DVG",  # Dan
    "BNG",  # Briana
    "LEG",  # Lily
    
    "SMT", # Steph
    "MAL", # Steph's wife

]


ALT_CUBE_COLORS = """
    OOB
    OOO
    OOY
GGG WBO BWW OYY
GGG WWB WBB YYY
GGR YRB RBB YYW
    GWW
    RRR
    RRR
"""

ALT1_CUBE_COLORS = """
    OOO
    OOO
    WOW
GGO GWB OBB YYY
GGG WWW BBB YYY
GGG WRW BBB YYY
    RWR
    RRR
    RRR
"""

MOVES = ["L", "R", "U", "D", "F", "B", "M", "E", "S"]
ALL_MOVES = [
        'X',
        'Xi',
        'X2',
        'Y',
        'Yi',
        'Y2',
        'Z',
        'Zi',
        'Z2',

        'D',
        'Di',
        'D2',
        'U',
        'Ui',
        'U2',
        'B',
        'Bi',
        'B2',
        'F',
        'Fi',
        'F2',
        'L',
        'Li',
        'L2',
        'R',
        'Ri',
        'R2',
        
        'M',
        'Mi',
        'M2',
        'E',
        'Ei',
        'E2',
        'S',
        'Si',
        'S2'          
]

NULL_MOVES = [
        'X Xi',
        'X X X X',
        'X2 X2',
        'Y Yi',
        'Y Y Y Y',
        'Y2 Y2',
        'Z Zi',
        'Z Z Z Z',
        'Z2 Z2',

        'D Di',
        'D D D D',
        'D2 D2 ',
        'U Ui',
        'U U U U',
        'U2 U2',
        'B Bi',
        'B B B B',
        'B2 B2',
        'F Fi',
        'F F F F',
        'F2 F2',
        'L Li',
        'L L L L',
        'L2 L2 ',
        'R Ri',
        'R R R R',
        'R2 R2',
        
        'M Mi',
        'M M M M',
        'M2 M2',
        'E Ei',
        'E E E E',
        'E2 E2',
        'S Si',
        'S S S S',
        'S2 S2'          
]

def random_cube(solvedString=CUBE_COLORS, labels=TMW_CUBE_LABELS, groups=TMW_CUBE_GROUPS):
    """
    :return: A new scrambled Cube
    """
    scramble_moves = " ".join(random.choices(MOVES, k=200))
    #a = Cube(CUBE_COLORS)
    a = Cube(solvedString, labels=labels, groups=groups)

    #a = Cube(ALT_CUBE_COLORS)
    # a.sequence(scramble_moves)
    print("Scrambled Cube:")
    print(a)

    return a

def easy_cube(solvedString=CUBE_COLORS, labels=TMW_CUBE_LABELS, groups=TMW_CUBE_GROUPS, moves="B"):
    """
    :return: A new Cube that has been moved using moves
    """
    #a = Cube(CUBE_COLORS)
    a = Cube(solvedString, labels=labels, groups=groups)

    #a = Cube(ALT_CUBE_COLORS)
    a.sequence(moves)
    #print("Simple Cube:")
    #print(a)

    a.orientToFront()

    return a


def run():
    successes = 0
    failures = 0

    avg_opt_moves = 0.0
    avg_moves = 0.0
    avg_time = 0.0

    testRobotMoves = False
    
    if testRobotMoves:
        robotMoves = RobotMoves()
        a = Cube(CUBE_COLORS, TMW_CUBE_LABELS, TMW_CUBE_GROUPS)
        print ("Initial cube: ", a)
        for move in ALL_MOVES:
            print ("################### Move: ", move)
            a = Cube(CUBE_COLORS, TMW_CUBE_LABELS, TMW_CUBE_GROUPS)
            a.orientToFront()
            b = Cube(CUBE_COLORS, TMW_CUBE_LABELS, TMW_CUBE_GROUPS)
            b.orientToFront()
            c = Cube(CUBE_COLORS, TMW_CUBE_LABELS, TMW_CUBE_GROUPS)
            c.orientToFront()
            solverA = Solver(a, groups=TMW_CUBE_GROUPS)
            solverB = Solver(b, groups=TMW_CUBE_GROUPS)
            solverC = Solver(c, groups=TMW_CUBE_GROUPS)
            if move == 'F':
                print ('F')
            rm = robotMoves.convert([move])
            rmo = robotMoves.optimize([move])
            solverA.move(move)
            solverB.move(" ".join(rm))
            solverC.move(" ".join(rmo))
            print ("a: ", a)
            print ("b: ", b)
            #print ("c: ", c)
            assert a.flat_str() == b.flat_str()
            assert a.flat_str() == c.flat_str()
            
    if False:
        # testing moves that return back to origional configuration
        a = Cube(CUBE_COLORS, TMW_CUBE_LABELS, TMW_CUBE_GROUPS)
        b = Cube(CUBE_COLORS, TMW_CUBE_LABELS, TMW_CUBE_GROUPS)
        initialCube = Cube(CUBE_COLORS, TMW_CUBE_LABELS, TMW_CUBE_GROUPS)
        print ("Initial cube: ", a)
        for move in NULL_MOVES:
            print ("################### Move: ", move)
            #a = Cube(CUBE_COLORS, TMW_CUBE_LABELS, TMW_CUBE_GROUPS)
            #a.orientToFront()
            #b = Cube(CUBE_COLORS, TMW_CUBE_LABELS, TMW_CUBE_GROUPS)
            #b.orientToFront()
            #solverA = Solver(a, groups=TMW_CUBE_GROUPS)
            solverB = Solver(b, groups=TMW_CUBE_GROUPS)
            a.sequence(move)
            solverB.move(move)
            print ("a: ", a)
            print ("b: ", b)
            #print ("c: ", c)
            #assert a == initialCube
            #assert b == initialCube
            assert a.flat_str() == initialCube.flat_str()
            assert b.flat_str() == initialCube.flat_str()
            
    if False:
        #people = TMW1_PEOPLE
        people = ["DEH"]
        #people = ["MNH"]
        #people = ["TMW"]

        for person in people:
            for move in ALL_MOVES:
                print (f"----------- {person} -----------------")
                print (f"-----------  {move} ------------------")
                C = easy_cube(CUBE_COLORS, TMW_CUBE_LABELS, TMW_CUBE_GROUPS, move)
                print ("Starting Cube C: ", C)
                C1 = easy_cube(CUBE_COLORS, TMW_CUBE_LABELS, TMW_CUBE_GROUPS, move)
                peopleSolver = Solver(C, groups=TMW_CUBE_GROUPS)
                peopleSolver.solveFrontString(person)
                moves = peopleSolver.moves
                opt_moves = optimize_moves(peopleSolver.moves)
                print ("cube moves: ", moves)
                print ("opt  moves: ", opt_moves)
                C1.orientToFront()
                C1.sequence(" ".join(moves))
                CString = C1.flat_str()
                C1String = C.flat_str()
                print ("C:  ", C)
                print ("C1: ", C1)
                assert CString == C1String

    if True:
        #C = Cube(TEST_CUBE_STR)
        C = random_cube(CUBE_COLORS)        

        # rotate cube so we will solve the white side
        C.orientToFront()

        #actualCube = random_cube(TMW_CUBE_LABELS, TMW_CUBE_LABELS, TMW_CUBE_GROUPS)
        tmwCube = Cube(CUBE_COLORS, TMW_CUBE_LABELS, TMW_CUBE_GROUPS)
        realCube = Cube(CUBE_COLORS, TMW_CUBE_LABELS, TMW_CUBE_GROUPS)
        testCube1 = Cube(CUBE_COLORS, TMW_CUBE_LABELS, TMW_CUBE_GROUPS)
        testCube2 = Cube(CUBE_COLORS, TMW_CUBE_LABELS, TMW_CUBE_GROUPS)
        testCube3 = Cube(CUBE_COLORS, TMW_CUBE_LABELS, TMW_CUBE_GROUPS)
        testCube4 = Cube(CUBE_COLORS, TMW_CUBE_LABELS, TMW_CUBE_GROUPS)
        testCube5 = Cube(CUBE_COLORS, TMW_CUBE_LABELS, TMW_CUBE_GROUPS)
        testCube6 = Cube(CUBE_COLORS, TMW_CUBE_LABELS, TMW_CUBE_GROUPS)
        #print("starting cube:")
        #print(tmwCube)


        people = TMW1_PEOPLE
        #people = ["LEG", "TMW", "EVH", "MNH"]
        #people = ["LEG"]
        #people = ["SJG"]
        #people = ["BNG"]

        for t in range(100):
            if DEBUG: print ("=============== test loop ", t, " =====================")
            random.shuffle(people)
            for person in people:


                print ("------------------------------------------------------")
                if DEBUG > 0: print("Solving for: ", person)
                
                #print ("tmwCube before orient:\n", tmwCube)
                #print ("realCube before orient:\n", realCube)
                
                tmwCube.orientToFront()
                realCube.orientToCube(tmwCube)
                
                #print ("Starting Cube: \n", testCube1)
                peopleSolver = Solver(tmwCube, groups=TMW_CUBE_GROUPS)

                #fs = testCube1.flat_str()
                #fs1 = testCube2.flat_str()
                #assert fs == fs1
                
                #print ("tmwCube before moves:\n", tmwCube)
                #print ("realCube before moves:\n", realCube)
                print (f"realCube: {realCube.flat_str()}")
                print (f"tmwCube:  {tmwCube.flat_str()}")
                assert realCube == tmwCube
                
                #peopleSolver = Solver(actualCube, solvedCubes[person].labels_cube, TMW_CUBE_GROUPS)
                start = time.time()
                peopleSolver.solveFrontString(person)
                duration = time.time() - start
                moves = peopleSolver.moves

                realCube.sequence(" ".join(moves))
                
                #print ("tmwCube after moves:\n", tmwCube)
                #print ("realCube after moves:\n", realCube)
                
                assert realCube == tmwCube

                opt_moves = optimize_moves(peopleSolver.moves)
                successes += 1
                
                if DEBUG > 0: print(tmwCube)
                if DEBUG > 0: time.sleep(1)


                if tmwCube.is_solved(person):
                    #moves = optimize_moves(peopleSolver.moves)
                    moves = peopleSolver.moves
                    print(f"{person}:  {len(opt_moves)} moves: {' '.join(moves)}")
                    print (f"({person}) Solved tmw Cube:   \n", tmwCube)
                    robotMoves = RobotMoves()
                    rm = robotMoves.optimize(moves)
                    print(f"{person}:  {len(rm)} robot moves: {' '.join(rm)}")
                    if False:
                        testCube1.orient("F")
                        testCube2.orient("B")
                        testCube3.orient("L")
                        testCube4.orient("R")
                        testCube5.orient("U")
                        testCube6.orient("D")
                        #print(f"({person}) testCube1 normal before: ", testCube1)
                        print("================== moving: ", " ".join(moves), "====================")
                        print(f"({person}) testCube1 before moving moves \n{' '.join(moves)}\n", testCube1)
                        testCube1.sequence(" ".join(moves))
                        print(f"({person}) testCube1 after moving moves \n{' '.join(moves)}\n", testCube1)
                        print(f"({person}) testCube2 before moving moves \n{' '.join(moves)}\n", testCube2)
                        testCube2.sequence(" ".join(moves))
                        print(f"({person}) testCube2 after moving moves \n{' '.join(moves)}\n", testCube2)
                        print(f"({person}) testCube3 before moving moves \n{' '.join(moves)}\n", testCube3)
                        testCube3.sequence(" ".join(moves))
                        print(f"({person}) testCube3 after moving moves \n{' '.join(moves)}\n", testCube3)
                        print(f"({person}) testCube4 before moving moves \n{' '.join(moves)}\n", testCube4)
                        testCube4.sequence(" ".join(moves))
                        print(f"({person}) testCube4 after moving moves \n{' '.join(moves)}\n", testCube4)
                        print(f"({person}) testCube5 before moving moves \n{' '.join(moves)}\n", testCube5)
                        testCube5.sequence(" ".join(moves))
                        print(f"({person}) testCube5 after moving moves \n{' '.join(moves)}\n", testCube5)
                        print(f"({person}) testCube6 before moving moves \n{' '.join(moves)}\n", testCube6)
                        testCube6.sequence(" ".join(moves))
                        print(f"({person}) testCube6 after moving moves \n{' '.join(moves)}\n", testCube6)

                        twmc = tmwCube.flat_str()
                        tc1 = testCube1.flat_str()
                        #tc2 = testCube2.flat_str()
                        assert tc1 == twmc
                    #assert tc1 == tc2
                    #print (f"{person}:  Robot moves normal: {len(rm)} moves: {' '.join(rm)}")
                    #print ("Robot Cube:    ", testCube2.flat_str())
                    #rmo = robotMoves.optimize(opt_moves)
                    #testCube3.orientToUp()
                    #testCube3.sequence(" ".join(rmo))
                    #tc3 = testCube3.flat_str()
                    #assert tc1 == tc3
                    #print (f"{person}:  Robot moves opt   : {len(rmo)} moves: {' '.join(rmo)}")
                    #print ("Robot Opt :    ", testCube3.flat_str())
                    successes += 1
                    avg_moves = (avg_moves * (successes - 1) + len(peopleSolver.moves)) / float(successes)
                    avg_time = (avg_time * (successes - 1) + duration) / float(successes)
                    avg_opt_moves = (avg_opt_moves * (successes - 1) + len(opt_moves)) / float(successes)
                else:
                    failures += 1
                    print(f"Failed ({successes + failures}): {tmwCube.flat_str()}")

                if False:
                    scrambleMoves = " ".join(random.choices(MOVES, k=200))
                    tmwCube.sequence(scrambleMoves)
                    testCube1.sequence(scrambleMoves)
                    testCube2.sequence(scrambleMoves)
                    testCube3.sequence(scrambleMoves)
                    twmc = tmwCube.flat_str()
                    tc1 = testCube1.flat_str()
                    tc2 = testCube2.flat_str()
                    tc3 = testCube3.flat_str()
                    #TODO assert tc1 == twmc
                    #TODO assert tc2 == twmc
                    #TODO assert tc3 == twmc
                    
            total = successes + failures
            pass_percentage = 100 * successes / total

            avg_moves = (avg_moves * (successes - 1) +
                         len(peopleSolver.moves)) / float(successes)
            avg_time = (avg_time * (successes - 1) +
                        duration) / float(successes)
            avg_opt_moves = (avg_opt_moves * (successes - 1) +
                             len(opt_moves)) / float(successes)

            print ("====================================")
            print(f"{total}: {successes} successes ({pass_percentage:0.3f}% passing)"
                  f" avg_moves={avg_moves:0.3f} avg_opt_moves={avg_opt_moves:0.3f}"
                  f" avg_time={avg_time:0.3f}s")

            #print(f"{len(opt_moves)} moves: {' '.join(opt_moves)}")
            print ("====================================")


if __name__ == '__main__':
    DEBUG = 1
    run()
