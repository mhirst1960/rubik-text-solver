import random
import time
import subprocess
from pathlib import Path
from shutil import copyfile

from rubik import solve
from rubik.cube import Cube
from rubik.solve import Solver
from rubik.optimize import optimize_moves
from rubik.CubeOrder import CubeOrder
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
643 344 444 446
665 566 661 166
    566
    646
    661
"""

# pieces labeled with any character.  "-" means no label or None
CLOCK_CUBE_LABELS = """
    904
    215
    213
-11 0-- 526 8-7
-2P A-- 402 53-
96M M-- 48- -79
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
    
    saveMovesToFile = False  # Useful to import data into a simple viewer program
    doForever = False


    successes = 0
    failures = 0
    
    avg_opt_moves = 0.0
    avg_moves = 0.0
    avg_time = 0.0

    co = CubeOrder()

    #C = Cube(TEST_CUBE_STR)
    #C = random_cube(CUBE_COLORS)        

    # rotate cube so we will solve the white side
    #C.orientToFront()

    #actualCube = random_cube(TMW_CUBE_LABELS, TMW_CUBE_LABELS, TMW_CUBE_GROUPS)
    cube = Cube(CUBE_COLORS, CLOCK_CUBE_LABELS, CLOCK_CUBE_GROUPS, CLOCK_CUBE_GROUPS)
    clockSolver = Solver(cube)
    
    print("starting cube:")
    print(cube)
    
    movesFile = "rubik-clock-moves.py"
    #copyfile(movesFile, movesFile+".bak")

    if saveMovesToFile:
        f = open(movesFile, "w")
        f.write("RUBICK_CLOCK_MOVES = {\n")
        f.close()
        
    hours = 0
    minutes = 0
    totalMinutes = 0

    while doForever or totalMinutes < 1440:
        totalMinutes += 1
        currentTime = getTime()
        

        print ("------------------------------------------------------")
        if DEBUG > 0: print("Solving for: ", currentTime)
        
        timeString = f"{hours}{minutes}"
        clockCube = clockSolver.generateCubeForMessage(currentTime)
        verifierCube1 = Cube(cube) # save for the end to verify moves are correct
        verifierCube2 = Cube(cube) # save for the end to verify moves are correct
        clockSolver = Solver(clockCube, groups=CLOCK_CUBE_GROUPS)
        print (f"{timeString} unsolved cube = ", clockCube)
        unsolvedCubeState = clockCube.getDestinationColorString()
        myState = clockCube.getDestinationString()
        kociembaState = co.convert(myState, co.SLICE_UNFOLD_BACK, co.KOCIEMBA_ORDER)
        
        start = time.time()

        clockSolver.solveFront()
        duration = time.time() - start

        moves = clockSolver.getMovesString()                
        optimizedMoves = optimize_moves(clockSolver.moves)
        rm = RobotMoves()
        robotMoves = rm.convert(optimizedMoves)
        optimizedRobotMoves = rm.optimize(optimizedMoves)
        

        doKociembaOptimization = True
        if doKociembaOptimization:
            # this does not seem to work reliably I get this error:
            #Error: Wrong edge and corner parity

            #kociemba requires server to be running
            # cd .../RubiksCube-TwophaseSolver
            # python3 start_server.py 8080 20 2
            #
            
            # if it is not running then stdout returns ''
            #output = subprocess.run(["python3",
            #    "/Users/michaelhirst/TMW/rubik/hkociemba/RubiksCube-TwophaseSolver/main.py",
            #    kociembaInput], stdout=subprocess.PIPE).stdout.decode('utf-8')
            #print ("kociemba output: ", output)
            proc1 = subprocess.Popen(['echo', kociembaState], stdout=subprocess.PIPE)
            proc2 = subprocess.Popen(['nc', 'localhost', '8080'], stdin=proc1.stdout,
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            proc1.stdout.close() # Allow proc1 to receive a SIGPIPE if proc2 exits.
            out, err = proc2.communicate()
            print('kociemba output: {0}'.format(out))
            print('stderr: {0}'.format(err))
            kMoves = out.decode('utf-8').split('(')[0]
            print(f"{timeString} kociembe moves: {kMoves}")
        
            if "Error" in kMoves:
                print ("Error from kociemba: ", kMoves)
            elif kMoves == '':
                print ("kocieba server not running.  Do this:")
                print ("python3 RubiksCube-TwophaseSolver/start_server.py 8080 20 2")
            else:
                verifierCube2.sequence(kMoves)
                #print (f"{timeString} verifier2 solved cube = ", verifierCube2)
                if not verifierCube2.is_solved(currentTime):
                    print ("kocieba failed to solve the cube correctly.")
                else:                    
                    kMovesList = kMoves.split(' ')
                    optimizedRobotMoves = rm.optimize(kMovesList)
                    #print(f"{person} k robot moves: {' '.join(optimizedRobotMoves)}")

        verifierCube1.sequence(optimizedRobotMoves)
        print (f"{timeString} verifier solved cube = ", verifierCube1)
                
        print(f"{timeString} robot moves:   {' '.join(optimizedRobotMoves)}\n")
        
        moveString = ' '.join(optimizedRobotMoves)
        dictEntry = f'"{currentTime}":"{moveString}", '
        
        if saveMovesToFile:
            f = open(movesFile, "a")
            f.write(dictEntry + "\n")
            f.close()
       
    if saveMovesToFile:     
        f = open(movesFile, "a")
        f.write("}\n")
        f.close()

if __name__ == '__main__':
    DEBUG = 1
    hours = 23
    minutes = 56
    run()
