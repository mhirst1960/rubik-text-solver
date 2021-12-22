
from time import sleep
from adafruit_servokit import ServoKit


class Lighting:
    """
    We have extra pins on the PC9685 so might as well use them to control lighting
    100% converts to 180 degrees which is fed into the ServoKit library for full power
    """
    def __init__(self, PWMPin, kit=None):
        if kit == None:
            self.kit = ServoKit(channels=16)
        else:
            self.kit = kit
            
            
        self.PWMPin=PWMPin

    def off(self):
        self.kit.servo[self.PWMPin]._pwm.duty_cycle = 0
        
    def dim(self):
        self.kit.servo[self.PWMPin]._pwm.duty_cycle = 0x3fff
        
    def medium(self):
        self.kit.servo[self.PWMPin]._pwm.duty_cycle = 0x7fff
        
    def bright(self):
        self.kit.servo[self.PWMPin]._pwm.duty_cycle = 0xffff
        
    def percent(self, percent):
        value = int(percent * 0xffff / 100)
        if value > 0xffff:
            value = 0xffff
        if value < 0:
            value = 0
        self.kit.servo[self.PWMPin]._pwm.duty_cycle = value
        
