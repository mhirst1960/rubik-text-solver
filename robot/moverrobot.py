#! /bin/python3

from time import sleep
import argparse

from CubeMover import CubeMover
from Lighting import Lighting

simulation = False


bottomLEDChannel   = 12
topLeftLEDChannel  = 13
topRightLEDChannel = 14

mover = CubeMover()

bottomLED = Lighting(bottomLEDChannel, mover.kit)
topLeftLED = Lighting(topLeftLEDChannel, mover.kit)
topRightLED = Lighting(topRightLEDChannel, mover.kit)

def blink(numBlinks):
    # blink three times to warn that servos are about to start
    for i in range (0, numBlinks):
        
        bottomLED.bright()
        topLeftLED.bright()
        topRightLED.bright()
        sleep (0.3)
        bottomLED.off()
        topLeftLED.off()
        topRightLED.off()
        sleep (0.3)
    
blink(3)
sleep(1)

#! /bin/python3

from time import sleep
from CubeMover import CubeMover
from Lighting import Lighting

bottomLEDChannel   = 12
topLeftLEDChannel  = 13
topRightLEDChannel = 14

mover = CubeMover()

bottomLED = Lighting(bottomLEDChannel, mover.kit)
topLeftLED = Lighting(topLeftLEDChannel, mover.kit)
topRightLED = Lighting(topRightLEDChannel, mover.kit)

def blink(numBlinks):
    # blink three times to warn that servos are about to start
    for i in range (0, numBlinks):
        
        if simulation:
            print("simulate lights on.")
            sleep (0.3)
            print("simulate lights off.")
            sleep (0.3)
        else:
            print ("blink now.  not a simulation!")
            bottomLED.bright()
            topLeftLED.bright()
            topRightLED.bright()
            sleep (0.3)
            bottomLED.off()
            topLeftLED.off()
            topRightLED.off()
            sleep (0.3)

def move(moves):
    if simulation:
        print ("simulating moves: ", moves)
    else:
        print ("executing these moves: ", moves)
        mover.move(moves)
        if cradleAfter:
            mover.cradleCube()

def parseArgs():
    
    global DEBUG
    global simulation
    global robotMoves
    global cradleAfter
    
    parser = argparse.ArgumentParser()
    
    parser.add_argument('--verbose', '-v', action='count', default=0, \
        help="show debug messages -v, -vv, -vvv for more and more debug")
    parser.add_argument("--moves", default='', help="list of moves for the robot to execute")
    parser.add_argument('--cradleafter', dest='cradleAfter', action='store_true',
                        help="After all moves are complete cradle the cube so users are able to easily remove the cube.")

    parser.add_argument('--simulation', dest='simulation', action='store_true', help="do not use the camera or robot. Generate webpage and update state file when done.")

    args = parser.parse_args()
    
    if args.verbose:
        DEBUG=args.verbose
    
    robotMoves = args.moves

    if args.cradleAfter:
        cradleAfter = True
        
    if args.simulation:
        simulation = True
    
def init():
    
    global bottomLEDChannel
    global topLeftLEDChannel
    global topRightLEDChannel
    global mover
    global bottomLED
    global topLeftLED
    global topRightLED
    
    if simulation:
        mover = None

        bottomLED = None
        topLeftLED = None
        topRightLED = None
                
    else:
    
        bottomLEDChannel   = 12
        topLeftLEDChannel  = 13
        topRightLEDChannel = 14

        mover = CubeMover()

        bottomLED = Lighting(bottomLEDChannel, mover.kit)
        topLeftLED = Lighting(topLeftLEDChannel, mover.kit)
        topRightLED = Lighting(topRightLEDChannel, mover.kit)

def run():
    
    global robotMoves
    
    blink(3)
    sleep(1)
    move(robotMoves)

if __name__ == '__main__':

    DEBUG = 0
    cradleAfter = False # default is to not cradle the cube when moves are complete

    parseArgs()
    init()
    run()
    