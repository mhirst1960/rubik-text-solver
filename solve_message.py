#! /bin/python3

import random
import time
import re
import subprocess

from rubik import solve
from rubik.cube import Cube
from rubik.CubeOrder import CubeOrder
from rubik.solve import Solver
from rubik.optimize import optimize_moves
from rubik.RobotMoves import RobotMoves
from TmwSolvedCubes import tmwCubes
from rubik.CubeWebpage import CubeWebpage


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
TMW_CUBE_LABELS_UNFOLD = """
    CEK
    B-L
    D-S
J-L -T- --M ---
ANJ -M- NVL Z--
--T -W- HS- ---
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


TMW_PEOPLE = [
    #"TMW",  # The Mad Wrapper
    
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
        
        'X3 X1',
        'Y3 Y1',
        'Z3 Z1',
        'U3 U1',
        'D3 D1',
        'R3 R1',
        'L3 L1',
        'F3 F1',
        'B3 B1',
        

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

def random_cube(solvedString=CUBE_COLORS, labels=TMW_CUBE_LABELS_UNFOLD, groups=TMW_CUBE_GROUPS):
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

def easy_cube(solvedString=CUBE_COLORS, labels=TMW_CUBE_LABELS_UNFOLD, groups=TMW_CUBE_GROUPS, moves="B"):
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
        a = Cube(CUBE_COLORS, TMW_CUBE_LABELS_UNFOLD, TMW_CUBE_GROUPS)
        print ("Initial cube: ", a)
        for move in ALL_MOVES:
            print ("################### Move: ", move)
            a = Cube(CUBE_COLORS, TMW_CUBE_LABELS_UNFOLD, TMW_CUBE_GROUPS)
            a.orientToFront()
            b = Cube(CUBE_COLORS, TMW_CUBE_LABELS_UNFOLD, TMW_CUBE_GROUPS)
            b.orientToFront()
            c = Cube(CUBE_COLORS, TMW_CUBE_LABELS_UNFOLD, TMW_CUBE_GROUPS)
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
        a = Cube(CUBE_COLORS, TMW_CUBE_LABELS_UNFOLD, TMW_CUBE_GROUPS)
        b = Cube(CUBE_COLORS, TMW_CUBE_LABELS_UNFOLD, TMW_CUBE_GROUPS)
        initialCube = Cube(CUBE_COLORS, TMW_CUBE_LABELS_UNFOLD, TMW_CUBE_GROUPS)
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

    if False:
        # convert to various cube notations
        co = CubeOrder()
        unwrapState = re.sub(r'\s+', '', TMW_CUBE_LABELS_UNFOLD)
        #xray = ''.join(TMW_CUBE_LABELS_UNFOLD.strip())
        unfoldBack = co.convert(unwrapState, co.SLICE_XRAYBACK, co.SLICE_UNFOLD_BACK)
        kociembaState = co.convert(unwrapState, co.SLICE_XRAYBACK, co.KOCIEMBA_ORDER)
        print (f"xray        = \"\"\"\n{unwrapState}\n\"\"\"")
        print (f"unfold back = \"\"\"\n{unfoldBack}\n\"\"\"")
        print (f"kociemba    = \"\"\"\n{kociembaState}\n\"\"\"")
        

    # test all combos of solving from any person to different person
    # including kociemba optimization
    if False:
        co = CubeOrder()
        for fromName, fromParams in tmwCubes.items():
            for toName, toParams in tmwCubes.items():
                print ("-----------------------------------")
                print (f"Solving from {fromName} to {toName}")
                cube = Cube(colors=fromParams["colors"], labels=fromParams["labels"], groups=fromParams["groups"])
                print ("From: \n", cube)
                # reverse solve to generate color pattern of unsolved cube
                cube.setDestinationsToColors(toParams["colors"])
                print (f"{toName} To before solve: \n", cube)
                solver = Solver(cube)
                solver.solve()
                print (f"{toName} To after solved: \n", cube)
                #cube.alignToColors(toParams["colors"])
                unwrapState = cube.flat_str()
                kociembaState = co.convert(unwrapState, co.SLICE_XRAYBACK, co.KOCIEMBA_ORDER)
                print (f"{toName} xray     = \"\"\"\n{unwrapState}\n\"\"\"")
                print (f"{toName} kociemba = \"\"\"\n{kociembaState}\n\"\"\"")
        
        
    # test align to colors
    if False:
        for i in range(100):
            randomCube = random_cube(CUBE_COLORS, TMW_CUBE_LABELS_UNFOLD, TMW_CUBE_GROUPS)
            colors = randomCube.getColors()
            print ("colors: ", ''.join(colors))
            cube = Cube(colors)
            cube.assignSecondaryAttributes(randomCube)
            print ("aligned cube: ", cube)


    # generate some python output for a solved cube customized for each person
    if False:        
        analysisCube = Cube(CUBE_COLORS, TMW_CUBE_LABELS_UNFOLD, TMW_CUBE_GROUPS)
        
        print ("\"\"\"")
        print ("TmwSolved Cubes\n\n")
        
        if analysisCube.backViewIsXray:
            print ("Back View is XRay.")
            print ("So the back stickers are printed in the same left-to-right order as the front stickers")
            print ("   LBR")
            print ("   LBR")
            print ("   LBR")
        else:
            print ("Back View is unfolded as if viewed from bottom")
            print ("So the back stickers are printed right-to-left in the opposite left-to-right order as the front stickers")
            print ("   RBL")
            print ("   RBL")
            print ("   RBL")
        print ("\"\"\"")
        
        print (f"CUBE_LABELS_COLOR_SOLVED = \"\"\"\n{TMW_CUBE_LABELS_UNFOLD}\n\"\"\"")
        print (f"CUBE_GROUPS_COLOR_SOLVED = \"\"\"\n{TMW_CUBE_GROUPS}\n\"\"\"")
        print (f"CUBE_COLORS_COLOR_SOLVED = \"\"\"\n{CUBE_COLORS}\n\"\"\"")


        print ("tmwCubes = {\n")
        showCubeAsComment = False

        for person in TMW_PEOPLE:
            analysisCube.orientToFront()
            peopleSolver = Solver(analysisCube, groups=TMW_CUBE_GROUPS)
            personCube = peopleSolver.generateCubeForMessage(person)
            pSolver = Solver(personCube, groups=TMW_CUBE_GROUPS)

            pSolver.cross()
            pSolver.cross_corners()
            pSolver.alignToMessageOrder()
            
            if showCubeAsComment:
                print ("\"\"\"")
                print ("------------------------------------")
                print (f"Cube for {person}:\n", personCube)
                print ("\"\"\"")
                print()

            personVariableSuffix = person.replace('-', '_')
            print (f"        \"{person}\" : {{\"colors\" : \"{''.join(personCube.getColors())}\",")
            print (f"                 \"labels\" : \"{''.join(personCube.getLabels())}\",")
            print (f"                 \"groups\" : \"{''.join(personCube.getGroups())}\"}},")
            print()
            personVariableSuffix = person.replace('-', '_')
            #print (f"CUBE_COLORS_{personVariableSuffix} = \"{''.join(personCube.getColors())}\"")
            #print (f"CUBE_LABELS_{personVariableSuffix} = \"{''.join(personCube.getLabels())}\"")
            #print (f"CUBE_GROUPS_{personVariableSuffix} = \"{''.join(personCube.getGroups())}\"")
            #print()
        print ("}")


    if False:
        #testing moves generated by kociemba
        inputColors = "WWGRBBOOYRYWBBGOYWGROOYBWOYGWOGRWBOBYBBRGRYRYRRWYGWOGG"
        noviceMoves = "X X Z Z L L R R Z B L L B R R Zi B D Bi Di Z B D Bi Di Z D B Di B B B Bi Ri B R Z B B B D Bi Di Z"
        kociembaMoves = "U2 F3 R2 B3 D2 F2 D2 R2 F1 R2 U1 L1 B1 U2 L3 F2 U3 L1 B2 D1"
        person = "DJH"
        
        referenceCube = Cube(CUBE_COLORS, TMW_CUBE_LABELS_UNFOLD, TMW_CUBE_GROUPS)
        cCube = Cube(inputColors)
        cCube.assignSecondaryAttributes(referenceCube)
        print(f"{person} starting cube:", cCube)
        solver = Solver(cCube)
        solver.move(noviceMoves)
        print("Novice moves: ", solver.getMovesString())
        print(f"{person} Novice {noviceMoves}\nsolved cube:", cCube)

        cCube = Cube(inputColors)
        cCube.assignSecondaryAttributes(referenceCube)
        #cCube.sequence(kociembaMoves)
        solver = Solver(cCube)
        solver.move(kociembaMoves)
        print("Kociemba moves: ", solver.getMovesString())
        print(f"{person} kociemba {kociembaMoves}\nsolved cube:", cCube)
        
    if True:
        # generate kociemba orientations for cubes based on a person
        people = TMW_PEOPLE
        co = CubeOrder()

        for t in range(1):
            if DEBUG: print ("=============== test loop ", t, " =====================")
            #random.shuffle(people)
            for person in people:


                print ("------------------------------------------------------")
                if DEBUG > 0: print("Solving for: ", person)

                
                cube = Cube(CUBE_COLORS, TMW_CUBE_LABELS_UNFOLD, TMW_CUBE_GROUPS)
                cubeSolver = Solver(cube)
                personCube = cubeSolver.generateCubeForMessage(person)
                print (f"{person} unsolved cube = ", personCube)
                
                unsolvedCubeString = personCube.colorString()
                unsolvedCubeState = personCube.getDestinationColorString()
                
                unwrapState = personCube.getDestinationString()
                kociembaState = co.convert(unwrapState, co.SLICE_UNFOLD_BACK, co.KOCIEMBA_ORDER)
                print (f"{person} state    = \"{unwrapState}\"")
                print (f"{person} kociemba = \"{kociembaState}\"")
                peopleSolver = Solver(personCube)
                peopleSolver.solveFront()
                
                moves = peopleSolver.getMovesString()                
                optimizedMoves = optimize_moves(peopleSolver.moves)
                rm = RobotMoves()
                robotMoves = rm.convert(optimizedMoves)
                optimizedRobotMoves = rm.optimize(optimizedMoves)
                                
                print ("moves: ", peopleSolver.getMovesString())
                print (f"{person} solved cube = ", personCube)
                
                if doKociembaOptimization:
                    #kociemba requires server to be running
                    # cd .../RubiksCube-TwophaseSolver
                    # python3 start_server.py 8080 20 2
                    #
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
                    print(f"{person} kociembe moves: {kMoves}")
                    kMovesList = kMoves.split(' ')
                    kRobotMoves = rm.optimize(kMovesList)
                    print(f"{person} k robot moves: {' '.join(kRobotMoves)}")

                print(f"{person} robot moves:   {' '.join(robotMoves)}\n")
                #TODO kociemba uses fewer moves but is not quite working.  someday use this
                subtitle = f"Cube for {person}"
                html = CubeWebpage("/Users/michaelhirst/TMW/rubik/cubeviewer",
                                   cubeColors=unsolvedCubeState,
                                   cubeMoves=robotMoves,
                                   subTitle=subtitle)
                html.generateHTML()
                
                print("------------------------------------")
        
    if False:

        analysisCube = Cube(CUBE_COLORS, TMW_CUBE_LABELS_UNFOLD, TMW_CUBE_GROUPS)
        realCube = Cube(CUBE_COLORS, TMW_CUBE_LABELS_UNFOLD, TMW_CUBE_GROUPS)
        realCubeOpt = Cube(CUBE_COLORS, TMW_CUBE_LABELS_UNFOLD, TMW_CUBE_GROUPS)
        robotCube = Cube(CUBE_COLORS, TMW_CUBE_LABELS_UNFOLD, TMW_CUBE_GROUPS)
        robotCubeOpt = Cube(CUBE_COLORS, TMW_CUBE_LABELS_UNFOLD, TMW_CUBE_GROUPS)


        people = TMW_PEOPLE

        for t in range(1):
            if DEBUG: print ("=============== test loop ", t, " =====================")
            #random.shuffle(people)
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
