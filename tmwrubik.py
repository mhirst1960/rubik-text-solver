#! /bin/python3
"""
Solve the front of a rubik cube so a person's initialz are displayed
on the front side of the cube.

Example:
    python3 tmwrubik.py --person DJH


Arguments:

    --person <person>
    
"""

import random
import time
import re
import argparse
import subprocess

from rubik import solve
from rubik.cube import Cube
from rubik.CubeOrder import CubeOrder
from rubik.solve import Solver
from rubik.optimize import optimize_moves
from rubik.RobotMoves import RobotMoves
from TmwSolvedCubes import tmwCubes


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

CUBE_COLOR_STRING = "OOOOOOOOOGGGWWWBBBYYYGGGWWWBBBYYYGGGWWWBBBYYYRRRRRRRRR"

# pieces labeled with any character.  "-" means no label or None
TMW_CUBE_LABELS_XRAY = """
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


TMW_PEOPLE = [
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

def getColorString(destinationsString):
    # if string is cube state not colors, convert to colors
    allowed = set('UDFBLR')
    if set(destinationsString) <= allowed:
        tbl = {'U':'O','D':'R','F':'W','B':'Y','L':'G','R':'B'}
        l = list(destinationsString)
        for i,d in enumerate(l):
            l[i] = tbl[l[i]]
        destinationsString = ''.join(l)
    return destinationsString
        
def run():
    
    global inputColors
    
    if DEBUG > 0:
        print ("tmwrubik")
        print ("verbose:     ", DEBUG)
        print ("Person:      ", person)
        print ("Input order: ", inputOrder)
        print ("Index:       ", "          11111111112222222222333333333344444444445555")
        print ("Index:       ", "012345678901234567890123456789012345678901234567890123")
        if inputColors is not None:
            print ("Input:       ", inputColors)
        print ("Output type: ", outputStyle)
        print ("Will output: ", outputDataType)

    if inputFile != None:
        f = open(inputFile, "r")
        inputColors = f.read()
        f.close()
        inputColors = inputColors.rstrip()
        assert len(inputColors) == 54
    
    referenceCube = Cube(CUBE_COLORS, TMW_CUBE_LABELS_XRAY, TMW_CUBE_GROUPS)
    if DEBUG > 1: print (f"Initial reference cube: \n", referenceCube)

    co = CubeOrder()
    if inputOrder == 'xray':
        xrayColors = inputColors
    elif inputOrder == 'unfold':
        xrayColors = co.convert(inputColors, co.SLICE_UNFOLD_BACK, co.SLICE_XRAYBACK)
    elif inputOrder == 'kociemba':
        #xrayColors = co.convert(inputColors, co.COLOR_RESOLVER_ORDER, co.SLICE_XRAYBACK)
        xrayColors = co.convert(inputColors, co.KOCIEMBA_ORDER, co.SLICE_XRAYBACK)
    else:
        xrayColors = None

    unfoldColors = co.convert(xrayColors, co.SLICE_XRAYBACK, co.SLICE_UNFOLD_BACK)
    kociembaColors = co.convert(xrayColors, co.SLICE_XRAYBACK, co.KOCIEMBA_ORDER)
    if DEBUG > 1: print ("xray input:      ", xrayColors)
    if DEBUG > 1: print ("fold input:      ", unfoldColors)
    if DEBUG > 1: print ("kociemba input:  ", kociembaColors)

    # if string is cube state not colors, convert to colors
    xrayColors = getColorString(xrayColors)
            
    #cube.setDestinationsToColors(xrayColors)
    cCube = Cube(xrayColors)

    cCube.assignSecondaryAttributes(referenceCube)
    cubeSolver = Solver(cCube)
    personCube = cubeSolver.generateCubeForMessage(person)
    xDestinations = personCube.getDestinationString()
    kDestinations = co.convert(xDestinations, co.SLICE_XRAYBACK, co.KOCIEMBA_ORDER)
    xColors = personCube.colorString()
    kColors = co.convert(xColors, co.SLICE_XRAYBACK, co.KOCIEMBA_ORDER)
    aColors = co.convert(xColors, co.SLICE_XRAYBACK, co.SLICE_ANIMJS3)

    if DEBUG > 1:
        print (f"{person} personCube before solve: \n", personCube)
        print (f"xray colors:     {xColors}")
        print (f"Kociemba colors: {kColors}")
        print (f"Anim colors:     {aColors}")
        
    if outputDataType == 'colors' or outputDataType == 'frontstring' or outputDataType == 'moves':
        if DEBUG > 1: print (f"cube before solve: \n", cCube)
        solver = Solver(cCube)
        #personCube = solver.generateCubeForMessage(person)
        solver.solveFrontString(person)
        moves = solver.moves
        if moveNotation == "singmaster":
            for i, move in enumerate(moves):
                move = move.replace("i", "'")
                moves[i] = move
        elif moveNotation == "programmer":
            for i, move in enumerate(moves):
                move = move.replace("'", "i")
                moves[i] = move
        if DEBUG > 1: print (f"Solved Cube: \n", cCube)
        if DEBUG > 1: print (f"Solved Moves: \n", moves)
    
    destinations = personCube.getDestinationString()
    kociembaDestinations = co.convert(destinations, co.SLICE_XRAYBACK, co.KOCIEMBA_ORDER)
    xrayColors = getColorString(destinations)
    kociembaColors = getColorString(kociembaDestinations)

    if DEBUG > 0:
        print (f"-----------Debug----------------------")
        print (f"tmwrubik output:")
        print (f"xray Destinations:     {destinations}")
        print (f"Xray Colors:           {xrayColors}")
        print (f"Kociemba Destinations: {kociembaDestinations}")
        print (f"Kociemba Colors:       {kociembaColors}")
        print (f"Message:               {cCube.getFrontString()}")
        print (f"Moves:                 {solver.getMovesString()}")
        print ("---------------------------------------")

    if outputDataType == "destinations":
        print (f"{kociembaDestinations}")
    elif outputDataType == "colors":
        print (f"{cCube.colorString()}")
    elif outputDataType == 'frontstring':
        print (f"{cCube.getFrontString()}")
    elif outputDataType == 'moves':
        print (f"{solver.getMovesString()}")
        
    subprocess.run(["python3",
                    "/Users/michaelhirst/TMW/rubik/hkociemba/RubiksCube-TwophaseSolver/main.py",
                    kDestinations])

if __name__ == '__main__':
    DEBUG = 0
    
    parser = argparse.ArgumentParser()
    
    parser.add_argument('--verbose', '-v', action='count', default=0, \
        help="show debug messages -v, -vv, -vvv for more and more debug")
    parser.add_argument("--person", default='TMW', help="initials for person to solve for")
    parser.add_argument("--inputorder", default='xray', help="Color input from camera or color string order: back=front, onfolded paper cube, or orbital kociemba", \
                            choices=['xray', 'unfold', 'kociemba', 'camera'])
    parser.add_argument("--infile", \
        help="File contains one line list of colors: OGYWBR and order depends on --inputorder: back=front, onfolded paper cube, or orbital kociemba")
    parser.add_argument("--input", default='OOOOOOOOOGGGWWWBBBYYYGGGWWWBBBYYYGGGWWWBBBYYYRRRRRRRRR', \
        help='values for input are: "camera", "file", or list of colors: OGYWBR and order depends on --inputorder: back=front, onfolded paper cube, or orbital kociemba')
    parser.add_argument("--output", default='moves', help="robot solve, or print planned moves, or print destination order: back=front, onfolded paper cube, or orbital kociemba", \
                            choices=['xray', 'unfold', 'kociemba', 'robot', 'moves'])
    parser.add_argument("--outputdatatype", default='destinations', help="how should we print output (No output = None)", \
                            choices=['destinations', 'colors', 'frontstring', 'moves', 'None'])
    parser.add_argument("--movenotation", default='singmaster', help="primmaster uses prime like X', programmer uses i like Xi", \
                            choices=['singmaster', 'programmer'])
    
    parser.add_argument('--robot', dest='robot', action='store_true', help="Allow robot to move (default: --no-robot)")
    parser.add_argument('--no-robot', dest='robot', action='store_false', help="Do not allow robot to move (default: --no-robot)")
    parser.set_defaults(robot=False)

    parser.add_argument('--camera', dest='camera', action='store_true', help="Use the camera (default: --no-camera)")
    parser.add_argument('--no-camera', dest='camera', action='store_false', help="Do not use the camera (default: --no-camera)")
    parser.set_defaults(camera=False)

    
    args = parser.parse_args()
    
    if args.verbose:
        DEBUG=args.verbose
    
    person = args.person
    useRobot = args.robot
    useCamera = args.camera
    inputOrder = args.inputorder
    outputDataType = args.outputdatatype
    moveNotation = args.movenotation

    inputFile = None
    inputColors = None

    if args.input == 'camera':
        if useCamera == False:
            print ("ERROR: must enable camera with --camera")
            parser.print_help()
            exit(-1)
        if useRobot == False:
            print ("ERROR: must enable robot with --robot")
            parser.print_help()
            exit(-1)
        getInputFromCamera = True
        inputColors = None
    elif args.input == 'file':
        if not args.infile:
            print ("ERROR: input file not specified")
            parser.print_help()
            exit(-1)
        inputColors=None
        inputFile=args.infile
    else:
        getInputFromCamera = False
        inputColors = args.input
        
    if args.output == 'robot':
        if useRobot == False:
            print ("ERROR: must enable robot with --robot")
            parser.print_help()
            exit(-1)
        solveWithRobot = True
    else:
        solveWithRobot = False

    outputStyle = args.output
    
    
    run()
