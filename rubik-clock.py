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
    244
    122
221 122 242 222
643 344 444 644
665 566 661 661
    566
    646
    661
"""

# pieces labeled with any character.  "-" means no label or None
CLOCK_CUBE_LABELS = """
    904
    215
    213
-11 0-- 526 7-8
-2P A-- 402 -35
96M M-- 48- 97-
    M23
    531
    06-
"""



MOVES = ["L", "R", "U", "D", "F", "B", "M", "E", "S"]

hours = 0
minutes = 0


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



def getTime():
    global hours
    global minutes
    
    minutes += 1
    
    if minutes >= 60:
        minutes = 0
        hours += 1
    if hours >= 24:
        hours = 0
    
    if hours == 0:
        h = 12
        ap = "A"
    elif hours == 12:
        h = hours
        ap = "P"
    elif hours > 12:
        h = hours-12
        ap = "P"
    else:
        h = hours
        ap = "A"
        
    minutesStr = "{:02d}".format(minutes)

    if h < 10:
        hoursStr = "-{:d}".format(h)
    else:
        hoursStr = "{:d}".format(h)

    #return str(hours) + "  " + str(minutes)  # military time
    return hoursStr + ap + minutesStr[0] + "M" + minutesStr[1]  # AM/PM

def run():
    successes = 0
    failures = 0

    avg_opt_moves = 0.0
    avg_moves = 0.0
    avg_time = 0.0

    #C = Cube(TEST_CUBE_STR)
    C = random_cube(CUBE_COLORS)        

    # rotate cube so we will solve the white side
    C.orientToFront()

    #actualCube = random_cube(TMW_CUBE_LABELS, TMW_CUBE_LABELS, TMW_CUBE_GROUPS)
    clockCube = Cube(CUBE_COLORS, CLOCK_CUBE_LABELS, CLOCK_CUBE_GROUPS)
    print("starting cube:")
    print(clockCube)
    
    hours = 0
    minutes = 0

    while True:
        currentTime = getTime()
        

        print ("------------------------------------------------------")
        if DEBUG > 0: print("Solving for: ", currentTime)
        print ("Starting Cube: ", clockCube.flat_str())
        clockSolver = Solver(clockCube, groups=CLOCK_CUBE_GROUPS)
        
        start = time.time()
        clockSolver.solveFrontString(currentTime)
        duration = time.time() - start
        

        opt_moves = optimize_moves(clockSolver.moves)
        successes += 1
        
        if DEBUG > 0: print(clockCube)
        if DEBUG > 0: time.sleep(1)


        if clockCube.is_solved(currentTime):
            opt_moves = optimize_moves(clockSolver.moves)
            print(f"{currentTime}:  {len(opt_moves)} moves: {' '.join(opt_moves)}")
            print ("Ending Cube:   ", clockCube.flat_str())
            successes += 1
            avg_moves = (avg_moves * (successes - 1) + len(clockSolver.moves)) / float(successes)
            avg_time = (avg_time * (successes - 1) + duration) / float(successes)
            avg_opt_moves = (avg_opt_moves * (successes - 1) + len(opt_moves)) / float(successes)
        else:
            failures += 1
            print(f"Failed ({successes + failures}): {clockCube.flat_str()}")

        scrambleMoves = " ".join(random.choices(MOVES, k=200))
        clockCube.sequence(scrambleMoves)

    total = successes + failures
    pass_percentage = 100 * successes / total

    avg_moves = (avg_moves * (successes - 1) +
                    len(clockSolver.moves)) / float(successes)
    avg_time = (avg_time * (successes - 1) +
                duration) / float(successes)
    avg_opt_moves = (avg_opt_moves * (successes - 1) +
                        len(opt_moves)) / float(successes)


if __name__ == '__main__':
    DEBUG = 1
    hours = 23
    minutes = 56
    run()
