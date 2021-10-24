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
    a.sequence(scramble_moves)
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
    avg_robot_moves = 0.0
    avg_moves = 0.0
    avg_time = 0.0

    # testing robot moves    
    if False:
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
            opt_robot_moves = robotMoves.optimize([move])
            solverA.move(move)
            solverB.move(" ".join(rm))
            solverC.move(" ".join(opt_robot_moves))
            print ("a: ", a)
            print ("b: ", b)
            print ("c: ", c)
            print (f"move:           ({move})")
            print (f"robot move:     ({rm})")
            print (f"optimize robot: ({opt_robot_moves})")
            assert a == b
            assert a == c
            
    if False:
        # testing moves that return back to origional configuration
        a = Cube(CUBE_COLORS, TMW_CUBE_LABELS, TMW_CUBE_GROUPS)
        b = Cube(CUBE_COLORS, TMW_CUBE_LABELS, TMW_CUBE_GROUPS)
        initialCube = Cube(CUBE_COLORS, TMW_CUBE_LABELS, TMW_CUBE_GROUPS)
        print ("Initial cube: ", a)
        for move in NULL_MOVES:
            print ("################### Move: ", move)
            solverB = Solver(b, groups=TMW_CUBE_GROUPS)
            a.sequence(move)
            solverB.move(move)
            print ("a: ", a)
            print ("b: ", b)
            assert a == initialCube
            assert b == initialCube


    if True:

        analysisCube = Cube(CUBE_COLORS, TMW_CUBE_LABELS, TMW_CUBE_GROUPS)
        realCube = Cube(CUBE_COLORS, TMW_CUBE_LABELS, TMW_CUBE_GROUPS)
        realCubeOpt = Cube(CUBE_COLORS, TMW_CUBE_LABELS, TMW_CUBE_GROUPS)
        robotCube = Cube(CUBE_COLORS, TMW_CUBE_LABELS, TMW_CUBE_GROUPS)
        robotCubeOpt = Cube(CUBE_COLORS, TMW_CUBE_LABELS, TMW_CUBE_GROUPS)


        people = TMW1_PEOPLE

        for t in range(100):
            if DEBUG: print ("=============== test loop ", t, " =====================")
            random.shuffle(people)
            for person in people:


                print ("------------------------------------------------------")
                if DEBUG > 0: print("Solving for: ", person)
                
                #print ("analysisCube before orient:\n", analysisCube)
                #print ("realCube before orient:\n", realCube)
                
                analysisCube.orientToFront()
                realCube.orientToCube(analysisCube)
                realCubeOpt.orientToCube(analysisCube)
                robotCube.orientToCube(analysisCube)
                robotCubeOpt.orientToCube(analysisCube)
                
                #print ("Starting Cube: \n", testCube1)
                peopleSolver = Solver(analysisCube, groups=TMW_CUBE_GROUPS)
                
                #print (f"realCube:      {realCube.flat_str()}")
                #print (f"analysisCube:  {analysisCube.flat_str()}")
                assert realCube == analysisCube
                
                start = time.time()
                peopleSolver.solveFrontString(person)
                duration = time.time() - start
                moves = peopleSolver.moves

                realCube.sequence(" ".join(moves))
                
                #print (f"realCube:      {realCube.flat_str()}")
                #print (f"analysisCube:  {analysisCube.flat_str()}")
                assert realCube == analysisCube

                opt_moves = optimize_moves(peopleSolver.moves)
                
                realCubeOpt.sequence(" ".join(opt_moves))
                assert realCubeOpt == analysisCube

                robotMoves = RobotMoves()
                rm = robotMoves.convert(opt_moves)

                robotCube.sequence(" ".join(rm))
                assert robotCube == analysisCube
                
                robotMoves = RobotMoves()
                opt_robot_moves = robotMoves.optimize(opt_moves)
                    
                robotCubeOpt.sequence(" ".join(opt_robot_moves))
                assert robotCubeOpt == analysisCube
                
                if analysisCube.is_solved(person):

                    if DEBUG > 0:
                        print (f"({person}) Solved analysis Cube:   \n", analysisCube)
                        print (f"Analysis  number of moves: ({len(opt_moves)})")
                        print (f"Robot     number of moves: ({len(rm)})")
                        print (f"Robot opt number of moves: ({len(opt_robot_moves)})")

                        
                    print(f"{person}:  {len(opt_moves)} moves: {' '.join(opt_moves)}")
                    print(f"{person}:  {len(rm)}     robot moves: {' '.join(rm)}")
                    print()
                    print(f"{person}:  {len(opt_robot_moves)} robot opt moves: {' '.join(opt_robot_moves)}")
                            
                    if DEBUG > 0: time.sleep(1)
                
                    successes += 1
                    avg_moves = (avg_moves * (successes - 1) + len(peopleSolver.moves)) / float(successes)
                    avg_time = (avg_time * (successes - 1) + duration) / float(successes)
                    avg_opt_moves = (avg_opt_moves * (successes - 1) + len(opt_moves)) / float(successes)
                    avg_robot_moves = (avg_robot_moves * (successes - 1) + len(opt_robot_moves)) / float(successes)
                else:
                    failures += 1
                    print(f"Failed ({successes + failures}): {analysisCube.flat_str()}")
                    
            total = successes + failures
            pass_percentage = 100 * successes / total

            avg_moves = (avg_moves * (successes - 1) +
                         len(peopleSolver.moves)) / float(successes)
            avg_time = (avg_time * (successes - 1) +
                        duration) / float(successes)
            avg_opt_moves = (avg_opt_moves * (successes - 1) +
                             len(opt_moves)) / float(successes)
            avg_robot_moves = (avg_robot_moves * (successes - 1) +
                             len(opt_robot_moves)) / float(successes)

            print ("====================================")
            print(f"{total}: {successes} successes ({pass_percentage:0.3f}% passing)"
                  f" avg_moves={avg_moves:0.3f} avg_opt_moves={avg_opt_moves:0.3f}"
                  f" avg_robot_moves={avg_robot_moves:0.3f}"
                  f" avg_time={avg_time:0.3f}s")

            #print(f"{len(opt_moves)} moves: {' '.join(opt_moves)}")
            print ("====================================")


if __name__ == '__main__':
    DEBUG = 1
    run()
