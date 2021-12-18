#!/bin/python3

"""
loop forever listening for events ont he RFID
perform a task based on the known RFID values

open grippers
cradle grippers
read Rubik cube state using robot and camera
solve cube normal
solve cube for person's name

"""
import subprocess
import argparse
import psutil

import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
from time import sleep
#led=40
GPIO.setwarnings(False)    # Ignore warning for now
GPIO.setmode(GPIO.BOARD)


personLookup = {
    385842869373:"TMW",  # 10 The Mad Wrapper
    
    521168090332:"DEH",  # 11 Don
    177554257028:"LMH",  # 12 Linnea
    385407120412:"EVH",  # 13 Eric
    588830864489:"JZH",  # 14 Julie Howe
    472513952470:"CAM",  # 15 Carolyn

    520228828320:"C-M",  # 16 Chris
    864631583843:"SJG",  # 17 Sandy
    246894032054:"DAG",  # 18 David
    451123147932:"MNH",  # 19 Mike
    313583531190:"DJH",  # 20 Diane
    936202859742:"SJS",  # 21 Steven
    316452434971:"KLH",  # 22 Kristin
    316469212186:"DVG",  # 23 Dan
    797572658422:"BNG",  # 24 Briana
    177520374913:"LEG",  # 25 Lily
    
    796062774301:"SMT", # 26 Steph
    248336806937:"MAL", # 27 Michelle
    

    # blue tags work better
        
    185921132020:"MNH"
}

def abortAll():
    
    global cubeStateProcess
    
    print ("abort all actions")

    #cubeStateProcess.terminate()
    
    #kill -9 pid
    #p = psutil.Process(pid)
    #p.terminate()  #or p.kill()
    # output = subprocess.run(["kill","-9",pid], stdout=subprocess.PIPE).stdout.decode('utf-8')

def opengrippers():
    print ("open grippers")
    output = subprocess.run(["opengrippers.py",], stdout=subprocess.PIPE).stdout.decode('utf-8')

def cradlegrippers():
    print ("cradle grippers")
    output = subprocess.run(["cradle.py",], stdout=subprocess.PIPE).stdout.decode('utf-8')
    
def getCubeState():
    global cubeStatePid
    
    print ("Using camera  to get current cube state")
    #output = subprocess.run(["getcubestate.py",], stdout=subprocess.PIPE).stdout.decode('utf-8')
    #process = subprocess.Popen(path + ' > /dev/null 2> /dev/null &', shell=True)
    cubeStateProcess = subprocess.Popen(["getcubestate.py",], stdout=subprocess.PIPE)
    #cubeStatePid = cubeStateProcess.pid

def solve(person=None):
    if DEBUG >0: print("solve")
    if person == None:
        print("solve normal cube")
    else:
        if DEBUG >1: print ("Solve for person: ", person)
        #solverStateProcess = subprocess.Popen(["tmwrubik.py","--person", person,
        #                                       "-vv", "--simulation",
        #                                       "--input", "file", "--infile", "~/cubestate.txt"],
        #                                      stdout=subprocess.PIPE)
    
functionLookup = {
    363899372860:opengrippers,
    544215487835:cradlegrippers,
    705177466212:getCubeState,
    267359237614:solve,
    280393831834:abortAll
}

def solvePerson(person):
    if DEBUG >1: print ("solving for person: ", person)

def readerLoop():
    
    reader = SimpleMFRC522()
    try:

        while True:

            handledId = False
            
            id, text = reader.read()
            if DEBUG >0: print("id: ", id)
            #print("id type: ", type(id))
            #print("text: ", text)
                
            if id in personLookup.keys():
                solvePerson(personLookup[id])
                handledId = True

            if id in functionLookup.keys():
                functionLookup[id]()
                handledId = True
                
            if not handledId:
                print("id: ", id)
                
            sleep(2)

    except KeyboardInterrupt:
        GPIO.cleanup()

def parseArgs():
    
    global DEBUG
    
    parser = argparse.ArgumentParser()
    
    parser.add_argument('--verbose', '-v', action='count', default=0, \
        help="show debug messages -v, -vv, -vvv for more and more debug")

    args = parser.parse_args()

    if args.verbose:
        DEBUG=args.verbose
        
    
if __name__ == '__main__':
    DEBUG = 0
    
    parseArgs()
    
    readerLoop()
    