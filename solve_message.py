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


USA_COLORS = """
    OOO
    OOO
    OOO
GGW BRR YBB YYY
GGG WWW BBB YYY
GGB RRR GBB YYY
    WRW
    RRR
    WWW
"""

# pieces labeled with any character.  "-" means no label or None
CLOCK_CUBE_LABELS = """
    924
    2-5
    213
-11 00- 5-6 7-8
--0 -AM --1 -PM
--3 --- 5-6 8-9
    402
    9-3
    714
"""

TMW1_PEOPLE = [
    "DEH",  # Don
    "LMH",  # Linnea
    "EVH",  # Eric
    "J-H",  # Julie Howe
    "C-S",  # Caroline

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
]

# pieces labeled with any character.  "-" means no label or None
TMW_CUBE_LABELS_TENTITIVE = """
    CEK
    B?L
    D-S
J?L -T- M?? ???
ANJ -M- NVL ?-?
??? -W- H?S ???
    ?GG
    ?E?
    ?-M
"""


# pieces labeled with any character.  "-" means no label or None
TMW_CUBE_LABELS = """
    CEK
    B-L
    D-S
J-L -T- M-- ---
ANJ -M- NVL ---
--- -W- H-S ---
    -GG
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

# pieces labeled with any character.  "-" means no label or None
ALPHABET_CUBE_LABELS = """
    ABC
    DEF
    GHI
JKL MNO PQR STU
VWX YZa bcd efg
hij klm nop qrs
    tuv
    wxy
    z12
"""

# group pieces based on the clock digit each piece-face is used for
# make sure all faces in a tuple are in the same group
# group 1: 1x:xx
# group 2: x1:xx
# group 3: xx:1x
# group 4: xx:x1
# group 5: AP- (in AM, PM or none)
# group 6: M-  (in AM/PM or none)

CLOCK_CUBE_GROUPS = """
    222
    353
    122
231 122 232 222
853 356 654 458
443 344 444 454
    344
    454
    454
"""

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

TEST_CUBE_STR = """
  ORB
  YYG
  RRY
GBG WWO BWG RYW
GRO GWO YOW OBR
OYB YBG OOW RRY
  RGB
  WGB
  WBY
        """
MOVES = ["L", "R", "U", "D", "F", "B", "M", "E", "S"]


def random_cube(solvedString=CUBE_COLORS, labels=CLOCK_CUBE_LABELS, groups=CLOCK_CUBE_GROUPS):
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


                if DEBUG > 0: print ("------------------------------------------------------")
                if DEBUG > 0: print("Solving for: ", person)
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
    DEBUG = 0
    run()
