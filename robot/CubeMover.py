
from time import sleep
from adafruit_servokit import ServoKit
from Gripper import Gripper, Orientation


"""
CubeMover uses two grippers (4 servos) to move layers of the cube


^
 \
  up

        \
         |
     \___/

Notation:

"up" faces the camera
"down" is held by the left gripper
"back" hidden in the jaws of the right gripper
"front" empty space (not toward the camera).  This is layer 1 solved for cross and corners.
"right" faces the front of the robot (touching the left jaw of the right gripper)
"left"  is at the back of the robot

Whole Cube:     X X' Y Y' Z Z'
Face clockwise: U L F R B D
Face cc:        U' L' F' R' B' D'
180 degrees:    U2 L2 F2 R2 B2 D2
center Left:    M M' M2
center down:    E E' E2
center front:   S S' S2

Note: because there are only two grippers
actual movement is restricted to "down" and "front":
Y Y' Y2
Z Z' Z2
D D' D2
F F' F2

Other movements require whole-cube movment for gripper contact:
X X' X2
U U' U2
L L' L2
R R' R2
M M' M2
E E' E2
S S' S2
"""
class CubeMover:
    
    GrippersYZ = {
        '':[],
        
        'Y':['Y'],
        'Yi':['Yi'],
        'Y2':['Y2'],
        'Z':['Z'],
        'Zi':['Zi'],
        'Z2':['Z2'],
        'X':['Y', 'Z', 'Yi'],
        'Xi':['Y', 'Zi', 'Yi'],
        'X2':['Y', 'Z2', 'Yi'],

        'D':['D'],
        'Di':['Di'],
        'D2':['D2'],
        'B':['B'],
        'Bi':['Bi'],
        'B2':['B2'],
        'F':['Y2', 'B', 'Y2'],
        'Fi':['Y2', 'Bi', 'Y2'],
        'F2':['Y2', 'B2', 'Y2'],
        'U':['Z2', 'D', 'Z2'],
        'Ui':['Z2', 'Di', 'Z2'],
        'U2':['Z2', 'D2', 'Z2'],
        'L':['Y', 'B', 'Yi'],
        'Li':['Y', 'Bi', 'Yi'],
        'L2':['Y', 'B2', 'Yi'],
        'R':['Yi', 'B', 'Y'],
        'Ri':['Yi', 'Bi', 'Y'],
        'R2':['Yi', 'B2', 'Y'],
        
        'M':['Y', 'Bi', 'Y2', 'B', 'Z', 'Y'],
        'Mi':['Y', 'B', 'Y2', 'Bi', 'Zi', 'Y'],
        'M2':['Y', 'B2', 'Y2', 'B2', 'Yi', 'Z2'],
        'E':['Di', 'Z2', 'D', 'Z2', 'Yi'],
        'Ei':['D', 'Z2', 'Di', 'Z2', 'Y'],
        'E2':['D2', 'Z2', 'D2', 'Y2', 'Z2'],
        'S':['B', 'Y2', 'Bi', 'Y2', 'Z'],
        'Si':['Bi', 'Y2', 'B', 'Y2', 'Zi'],
        'S2':['B2', 'Y2', 'B2', 'Y2', 'Z2']          
    }
 
    def isMoveLegal(self, move):
        return move in self.GrippersYZ
    
    def move(self, moves):
        moveList = moves.split()
        
        # before doing anything with the robot, validate these are legal moves
        for i,move in enumerate(moveList):
            if not self.isMoveLegal(move):
                print (f"ERROR illgeal move at {i}: {move}")
                return False
             
        moves = [getattr(self, name) for name in moveList]
        for move in moves:
            move()
            
        return True

    def __init__ (self, kit=None,
                  rightPinchChannel=None, rightWristChannel=None,
                  leftPinchChannel=None, leftWristChannel=None):
        self.rightPinch = 0
        self.rightWrist = 1
        self.leftPinch  = 2
        self.leftWrist  = 3

        self.doRight = True
        self.doLeft  = False
        
        self.history = ""

        if kit == None:
            self.kit = ServoKit(channels=16)
        else:
            self.kit = kit
            
        # adjust range for full 180 degrees
#        self.kit.servo[self.rightWrist].set_pulse_width_range(500, 2500)
#        self.kit.servo[self.leftWrist].set_pulse_width_range(500, 2500)
        self.kit.servo[self.rightWrist].set_pulse_width_range(400, 2600)
        self.kit.servo[self.leftWrist].set_pulse_width_range(400, 2600)

        hasRubberband = False
        
        if hasRubberband:
            #pinch:smaller=tighter
            self.left = Gripper(self.kit, self.leftPinch,  self.leftWrist,
                                86, 103, 140, #close, cradle, open
                                18, 98, 171)  #back, up, front
            self.right= Gripper(self.kit, self.rightPinch, self.rightWrist,
                                83, 95, 140, #close, cradle, open
                                170, 93, 15)  #back, up, front
        else:
            #pinch:smaller=tighter
            self.left = Gripper(self.kit, self.leftPinch,  self.leftWrist,
                                86-5, 93, 150, #close, cradle, open
                                18, 98, 171)  #back, up, front
            self.right= Gripper(self.kit, self.rightPinch, self.rightWrist,
                                83-5, 90, 150, #close, cradle, open
                                170, 93, 15)  #back, up, front
            
    def Y(self, direction="1"):
        " rotate whole cube around face looking at camera "
        
        self.history += "Y"
        
        self.cradleCube()
        #TODO maybe: sleep(0.2)
        
        if direction == "2":
            # rotate 180 degrees
            self.history += "2"
            self.right.close()
            self.left.open()
            self.left.back()
            self.left.close()
            self.right.open()
            self.left.front()
        else:
            self.left.close()
            self.right.open()
            
            if direction == "1":
                self.left.back()
            else:
                self.history += "i"
                self.left.front()

        #sleep(0.2)
        #self.cradleCube()
        
    def Yi(self):
        self.Y("i")
    
    def Y2(self):
        self.Y("2")
    
    def Z(self, direction="1"):
        " rotate entire cube around face looking into space "
        
        self.cradleCube()
        self.history += "Z"
        
        if direction == "2":
            # rotate 180 degrees
            self.history += "2"
            self.left.close()
            self.right.open()
            self.right.back()
            self.right.close()
            self.left.open()
            self.right.front()
        else:
            self.right.close()
            self.left.open()
    
            #sleep(0.2)
            if direction == "1":
                # clockwise
                self.right.front()
            else:
                # counter clockwise
                self.history += "i"
                self.right.back()


    def Zi (self):
        self.Z("i")
        
    def Z2(self):
        self.Z("2")
        
    def X(self, direction="1"):
        #rotate left layer clockwise ("i" = counter clockwise)
        # note there is no convienent gripper so need requires extra moves
        
        self.Y()
        self.Z(direction)
        self.Yi()
        
    def Xi(self):
        self.X("i")
        
    def X2(self):
        self.X("2")
    
    def B(self, direction="1"):
        #rotate down layer counterclockwise
        # both grippers close and right gripper rotates

        self.cradleCube()
        
        self.history += "B"
        
        self.left.close()
        self.right.open()
        
        if direction == "2":
            # rotate 180 degrees
            self.history += "2"
            self.right.back()
            self.right.close()
            self.right.front()
            return
 
 
        self.right.up()            
        self.right.close()
        if direction == "1":
            self.right.back()
        else:
            self.history += "i"
            self.right.front()

    def Bi(self):
        #rotate back layer clockwise  (aka B')        
        self.B("i")
        
    def B2(self):
        #rotate back layer 180 degrees  (aka B2)        
        self.B("2")
        
    def F(self, direction="1"):
        self.Z2()
        self.B(direction)
        self.Z2()
        
    def Fi(self):
        self.F("i")
        
    def F2(self):
        self.F("2")
        
    def D(self, direction="1"):
        #rotate botton (down) layer counterclockwise
        # both grippers close and left gripper rotates
        
        self.cradleCube()
        
        self.right.close()
        self.left.open()
        
        if direction == "2":
            # rotate 180 degrees
            self.history += "2"
            self.left.back()
            self.left.close()
            self.left.front()
            return
        
        self.left.up()            
        self.left.close()
        if direction == "1":
            self.left.front()
        else:
            self.history += "i"
            self.left.back()

    def Di(self):
        #rotate up layer counter clockwise  (aka U')        
        self.D("i")

    def D2(self):
        #rotate up layer 180 degrees  (aka B2)        
        self.D("2")

    def U(self, direction="1"):
        #rotate up layer clockwise  (aka U)        
        
        self.Z2()
        self.D(direction)
        self.Z2()
        
    def Ui(self):
        #rotate up layer counter clockwise  (aka U')        
        self.U("i")

    def U2(self):
        #rotate up layer 180 degrees  (aka B2)        
        self.U("2")

    def F(self, direction="1"):
        self.Y2()
        self.B(direction)
        self.Y2()
        
    def Fi(self):
        self.F("i")
        
    def F2(self):
        self.F("2")
        
    def L(self, direction="1"):
        self.Z()
        self.B(direction)
        self.Zi()
        
    def Li(self):
        self.L("i")
        
    def L2(self):
        self.L("2")
        
    def R(self, direction="1"):
        self.Zi()
        self.B(direction)
        self.Z()
        
    def Ri(self):
        self.R("i")
        
    def R2(self):
        self.R("2")
        
    def M(self, direction="1"):
        # center slice rotates like L
        # actually we will move the left and right slices instead
        self.Y()
        if direction == "1":
            self.Bi()
            self.Y2()
            self.B()
            self.Z()
            self.Y()
        elif direction == "i":
            self.B()
            self.Y2()
            self.Bi()
            self.Zi()
            self.Y()
        elif direction == "2":
            self.B2()
            self.Y2()
            self.B2()
            self.Yi()
            self.Z2()
        else:
            print ("ERROR unknown direction ", direction)
            self.Yi()
        
    def Mi(self):
        self.M("i")
        
    def M2(self):
        self.M("2")
        
    def E(self, direction="1"):
        # center slice rotates like D
        # actually we will move the up and down slices instead
        if direction == "1":
            self.Di()
            self.Z2()
            self.D()
            self.Z2()
            self.Yi()
        elif direction == "i":
            self.D()
            self.Z2()
            self.Di()
            self.Z2()
            self.Y()
        elif direction == "2":
            self.D2()
            self.Z2()
            self.D2()
            self.Y2()
            self.Z2()
        else:
            print ("ERROR unknown direction ", direction)
                     
        
    def Ei(self):
        self.E("i")
        
    def E2(self):
        self.E("2")
        
    def S(self, direction="1"):
        # center slice rotates like F
        # actually we will move the front and back slices instead
        if direction == "1":
            self.B()
            self.Y2()
            self.Bi()
            self.Y2()
            self.Z()            
            
        elif direction == "i":
            self.Bi()
            self.Y2()
            self.B()
            self.Y2()
            self.Zi()            
            
        elif direction == "2":
            self.B2()
            self.Y2()
            self.B2()
            self.Y2()
            self.Z2()            
            
        else:
            print ("ERROR unknown direction ", direction)
                     

        
    def Si(self):
        self.S("i")
        
    def S2(self):
        self.S("2")
    
    def cradleIfConvienent(self):
        # only cradle cube if both wrists are already in up position
        
        leftOrientation = self.left.orientation()
        rightOrientation = self.right.orientation()
        
        if leftOrientation == None or rightOrientation == None:
            print("unknown orientation")
            return False
        
        if (leftOrientation, rightOrientation) == (Orientation.UP, Orientation.UP):
            self.left.close()
            self.right.close()
            self.left.cradle()
            self.right.cradle()
            return True
        
        return False
            
    def cradleCube(self):
        # move wrists to horizontal then open slightly to release grip but still
        # hold the cube.  Good for resetting to a known position or
        # to present a solved cube to the user.
        
        if not self.cradleIfConvienent():
            # wrists were not in good position, move to up then cradle
            self.right.close()
            self.left.open()
            self.left.up()
            sleep(0.1)
            self.left.close()
            self.right.open()
            self.right.up()
            sleep(0.1)

            self.right.close()
            self.left.close()
            self.left.cradle()
            self.right.cradle()


    def pinchTest(self):
        self.right.close()
        self.left.open()
        sleep(1)
        self.left.close()
        self.right.open()
        sleep(1)
        self.right.close()
        self.left.open()
        sleep(1)
        #right.open()
        #left.open()
        #sleep(2)
        self.right.close()
        self.left.close()
        sleep(1)

    def rotateBottomTest(self):
                
        self.left.close()
            
        self.right.close()
        self.right.front()
        sleep(1)
        self.right.back()
        sleep(1)
        self.right.front()
        sleep(1)
        self.right.up()
        
    def rotateFrontTest(self):
                
        self.left.close()
            
        self.right.close()
        self.left.front()
        sleep(1)
        self.left.back()
        sleep(1)
        self.left.front()
        sleep(1)
        self.left.up()
        


    def rotateTest(self):
                
        self.left.up()
        self.left.open()
            
        self.right.close()
        self.left.open()
        self.right.front()
        sleep(1)
        self.right.back()
        sleep(1)
        self.right.up()
        
        self.left.up()
        self.left.close()
        self.right.open()
        self.left.front()
        sleep(1)
        self.left.back()
        sleep(1)
        self.left.up()

    def pinchTest(self):
        self.right.close()
        self.left.open()
        sleep(1)
        self.left.close()
        self.right.open()
        sleep(1)
        self.right.close()
        self.left.open()
        sleep(1)
        #self.right.open()
        #self.left.open()
        #self.sleep(2)
        self.right.close()
        self.left.close()
        sleep(1)
