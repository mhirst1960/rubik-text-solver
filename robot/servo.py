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


#bottomLED.bright()
#topLeftLED.bright()
#topRightLED.bright()

mover.cradleCube()

if False:
    mover.pinchTest()
    mover.rotateTest()
    #mover.rotateBottomTest() #close left and rithg, rotate right
    #mover.rotateFrontTest() #close left and right, rotate left

if False:
    # rotate whole cube around face facing the world
    mover.Zi()
    mover.Z()
    
if True:
    # view all sides

    #blink(1)
    #mover.Z()
    #blink(1)
    #mover.Z()
    #blink(1)
    #mover.Z()
    #blink(1)
    #mover.Z()
    mover.X()
    blink(1)
    mover.Z2()
    blink(1)
    mover.Z2()
    mover.Xi()
    
if False:
    mover.X()
    mover.Xi()
    mover.X2()
    mover.X2()
    mover.Y()
    mover.Yi()
    mover.Y2()
    mover.Y2()
    mover.Z()
    mover.Zi()
    mover.Z2()
    mover.Z2()
    
if False:
    mover.D()
    mover.Di()
    mover.D2()
    mover.D2()
    mover.U()
    mover.Ui()
    mover.U2()
    mover.U2()
    
if False:
    mover.B()
    mover.Bi()
    mover.B2()
    mover.B2()
    mover.F()
    mover.Fi()
    mover.F2()
    mover.F2()
    
if False:
    mover.M()
    mover.Mi()
    mover.M2()
    mover.M2()
    mover.E()
    mover.Ei()
    mover.E2()
    mover.E2()
    mover.S()
    mover.Si()
    mover.S2()
    mover.S2()
    
if False:
    for x in range(1):
        mover.Y()
        mover.Yi()
        mover.Y2()
        mover.Y2()
        mover.Z()
        mover.Zi()
        mover.Z2()
        mover.Z2()
        mover.D()
        mover.Di()
        mover.B()
        mover.Bi()
        mover.D2()
        mover.D2()
        mover.B2()
        mover.B2()

    
if False:
    # rotate "Down" layer wich is the layer facing away from the people
    mover.D()
    sleep(1)
    mover.Di()


mover.cradleCube()

#mover.left.front()
#sleep(1)
#mover.left.back()

#mover.cradleCube()

print("moves completed: ", mover.history)

for percent in range (100, 0, -1):
    bottomLED.percent(percent)
    topLeftLED.percent(percent)
    topRightLED.percent(percent)
    sleep(0.02)
    
#sleep(1)

#bottomLED.medium()
#topLeftLED.medium()
#topRightLED.medium()

#sleep(1)
#bottomLED.dim()
#topLeftLED.dim()
#topRightLED.dim()

#sleep(1)
bottomLED.off()
topLeftLED.off()
topRightLED.off()

#sleep(1)


exit()

