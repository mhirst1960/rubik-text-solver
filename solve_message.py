#! /bin/python3

import random
import time
from rubik import solve
from rubik.cube import Cube
from rubik.solve import Solver
from rubik.optimize import optimize_moves


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


def run():
    successes = 0
    failures = 0

    avg_opt_moves = 0.0
    avg_moves = 0.0
    avg_time = 0.0

    if True:
        #C = Cube(TEST_CUBE_STR)
        C = random_cube(CUBE_COLORS)        

        # rotate cube so we will solve the white side
        C.orientToFront()

        #actualCube = random_cube(TMW_CUBE_LABELS, TMW_CUBE_LABELS, TMW_CUBE_GROUPS)
        tmwCube = Cube(CUBE_COLORS, TMW_CUBE_LABELS, TMW_CUBE_GROUPS)
        #print("starting cube:")
        #print(tmwCube)
        

        people = TMW1_PEOPLE


        for t in range(100):
            if DEBUG: print ("=============== test loop ", t, " =====================")
            random.shuffle(people)
            for person in people:


                print ("------------------------------------------------------")
                if DEBUG > 0: print("Solving for: ", person)
                print ("Starting Cube: ", tmwCube.flat_str())
                peopleSolver = Solver(tmwCube, groups=TMW_CUBE_GROUPS)
                
                #peopleSolver = Solver(actualCube, solvedCubes[person].labels_cube, TMW_CUBE_GROUPS)
                start = time.time()
                peopleSolver.solveFrontString(person)
                duration = time.time() - start
                

                opt_moves = optimize_moves(peopleSolver.moves)
                successes += 1
                
                if DEBUG > 0: print(tmwCube)
                if DEBUG > 0: time.sleep(1)


                if tmwCube.is_solved(person):
                    opt_moves = optimize_moves(peopleSolver.moves)
                    print(f"{person}:  {len(opt_moves)} moves: {' '.join(opt_moves)}")
                    print ("Ending Cube:   ", tmwCube.flat_str())
                    successes += 1
                    avg_moves = (avg_moves * (successes - 1) + len(peopleSolver.moves)) / float(successes)
                    avg_time = (avg_time * (successes - 1) + duration) / float(successes)
                    avg_opt_moves = (avg_opt_moves * (successes - 1) + len(opt_moves)) / float(successes)
                else:
                    failures += 1
                    print(f"Failed ({successes + failures}): {tmwCube.flat_str()}")

                scrambleMoves = " ".join(random.choices(MOVES, k=200))
                tmwCube.sequence(scrambleMoves)

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
