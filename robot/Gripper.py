from enum import Enum

from time import sleep
from adafruit_servokit import ServoKit
class Orientation(Enum):
    UP = 0
    FRONT = 1
    BACK = 2
class Gripper:

    def __init__(self, kit, pwmPinchPin, pwmWristPin,
                 closeAngle=83, cradleAngle=120, openAngle=180,
                 backAngle=180, upAngle=120, frontAngle=0):
        self.kit             = kit
        self.pwmPinchPin     = pwmPinchPin
        self.pwmWristPin     = pwmWristPin
        self.closeAngle      = closeAngle
        self.openAngle       = openAngle
        self.cradleAngle     = cradleAngle
        self.upAngle         = upAngle
        self.frontAngle      = frontAngle
        self.backAngle       = backAngle
                        
        self.moveDelay = 0.5 #seconds

    def easeInEaseOut(self, pin, angle):
        startAngle = self.kit.servo[pin].angle
        
        if startAngle > 180 or startAngle < 0:
            # probably uninitialized values.  Just move and exit
            self.kit.servo[pin].angle = angle
            return

        endAngle = angle
        currentAngle = startAngle
        
        easeInAngle = 20
        easeOutAngle= 20
        
        if endAngle < startAngle + 2 and endAngle > startAngle - 2:
            return
        elif endAngle > startAngle:
            direction = 1
        else:
            direction = -1
            
        aStartAngle = abs(startAngle)
        aCurrentAngle = abs(currentAngle)
        aEndAngle = abs(endAngle)
        while aCurrentAngle * direction < aEndAngle * direction:
            distanceTravelled = abs(currentAngle - startAngle)
            distanceToGo = abs(endAngle - currentAngle)
            
            if (distanceTravelled == 0
                or distanceTravelled <= easeInAngle
                or distanceToGo <= easeOutAngle):
                #print("slow.  Angle = ", currentAngle)
                currentAngle += direction * 5
                if direction > 0 and currentAngle > endAngle:
                    currentAngle = endAngle
                elif direction < 0 and currentAngle < endAngle:
                    currentAngle = endAngle
                    
                aCurrentAngle = abs(currentAngle)
            else:
                #print("fast.  Angle = ", currentAngle)
                if direction > 0:
                    currentAngle = endAngle - easeOutAngle
                else:
                    currentAngle = endAngle + easeOutAngle
                aCurrentAngle = abs(currentAngle)
            assert currentAngle >= 0 and currentAngle <= 180
            self.kit.servo[pin].angle = currentAngle
            sleep(0.02)
        #print ("current angle = ", currentAngle)
                    
        
    def orientation(self):
        angle = self.kit.servo[self.pwmWristPin].angle
        
        if angle > self.upAngle-5 and angle < self.upAngle+5:
            return Orientation.UP
        elif angle > self.frontAngle-5 and angle < self.frontAngle+5:
            return Orientation.FRONT
        elif angle > self.backAngle-5 and angle < self.backAngle+5:
            return Orientation.BACK
        else:
            return None
        
    def open(self):
        self.kit.servo[self.pwmPinchPin].angle = self.openAngle
        sleep(self.moveDelay)

    def close(self):
        self.kit.servo[self.pwmPinchPin].angle = self.closeAngle
        sleep(self.moveDelay)

    def cradle(self):
        self.kit.servo[self.pwmPinchPin].angle = self.cradleAngle
        sleep(self.moveDelay)

    def up(self):
        self.easeInEaseOut(self.pwmWristPin, self.upAngle)
        #self.kit.servo[self.pwmWristPin].angle = self.upAngle
        sleep(self.moveDelay)

    def front(self):
        self.easeInEaseOut(self.pwmWristPin, self.frontAngle)
        #self.kit.servo[self.pwmWristPin].angle = self.frontAngle
        sleep(self.moveDelay)

    def back(self):
        self.easeInEaseOut(self.pwmWristPin, self.backAngle)
        #self.kit.servo[self.pwmWristPin].angle = self.backAngle
        sleep(self.moveDelay)
