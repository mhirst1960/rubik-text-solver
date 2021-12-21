#! /usr/bin/python3

import subprocess
import argparse
import psutil
import os
from threading import Thread
from pathlib import Path

import bottle
from bottle import route, run, template
from bottle import route, request
from bottle import run
from bottle import static_file

from CubeWebpage import CubeWebpage

simulation=False  # use --simulation to disable using camera and robot

cubeState = ''
getCubeStatePid = None
process_getcubestate = None

abs_app_dir_path = os.path.dirname(os.path.realpath(__file__))
abs_views_path = os.path.join(abs_app_dir_path, 'views')
bottle.TEMPLATE_PATH.insert(0, abs_views_path )

    
cubepage = CubeWebpage()

home = str(Path.home())
cubeStateFile = home + '/cubestate.txt'

personDecoder = {
    "TMW":"TMW",  # The Mad Wrapper
    
    "kind ramanujan":       "DEH",  # Don
    "quirky banach":        "LMH",  # Linnea
    "dazzling panini":      "EVH",  # Eric
    "competent ardinghelli":"JZH",  # Julie Howe
    "objective mirzakhani": "CAM",  # Caroline

    "relaxed kepler":       "C-M",  # Chris
    "zen neumann":          "SJG",  # Sandy
    "elated hawking":       "DAG",  # David
    "pedantic wright":      "MNH",  # Mike
    "hungry benz":          "DJH",  # Diane
    "optimistic saha":      "SJS",  # Steven
    "objective sammet":     "KLH",  # Kristin
    "dazzling nobel":       "DVG",  # Dan
    "eloquent joliot":      "BNG",  # Briana
    "eager hermann":        "LEG",  # Lily
    
    "amazing hypatia":      "SMT", # Steph
    "wizardly shockley":    "MAL", # Michelle
}

def decodeCodeName(codeName):
    if codeName in personDecoder:
        return personDecoder[codeName]
    else:
        return ""

@route('/static/<filename>')
def server_static(filename):
    dirPath = os.path.dirname(os.path.realpath(__file__))
    return static_file(filename, root=dirPath + '/static')

@route('/cube')
def cube():
        
    cubepage.loadCubeState(cubeStateFile)
        
    return cubepage.renderPage()


@route('/cube', method='POST')
def do_cube():
    global process_getcubestate

    def do_getcubestate():
        global getCubeStatePid
        global process_getcubestate
        
        if simulation:
            process_getcubestate = subprocess.Popen(["sleep","30"], stdout = subprocess.PIPE)
        else:
            try:
                process_getcubestate = subprocess.Popen(["getcubestate.py",], stdout = subprocess.PIPE)
            except:
                cubepage.setMessage("Error attempting to access camera or robot")
                return cubepage.renderPage()
        getCubeStatePid = process_getcubestate.pid
        out, err = process_getcubestate.communicate()
        getCubeStatePid = None
        process_getcubestate = None
        print ("Done getting cube state.")
    
    def do_solveit(person):
        global solveitPid
        global process_solveit
        
        if simulation:
            process_solveit = subprocess.Popen(["sleep","10"], stdout = subprocess.PIPE)
        else:
            try:
                process_solveit = subprocess.Popen(["tmwrubik.py","--person", person, "-vv", "--simulation", "--input", "file", "--infile", "~/cubestate.txt"], stdout = subprocess.PIPE)
            except:
                cubepage.setMessage("Error attempting to access camera or robot")
                return cubepage.renderPage()
        getCubeStatePid = process_solveit.pid
        out, err = process_solveit.communicate()
        solveitPid = None
        process_solveit = None
        print ("Done solving the cube.")
    
    editAction = request.forms.get('cube-TMW')

    if editAction != None:
        print ("process color: ", editAction)
        result = cubepage.processEditAction(editAction)
        cubepage.setMessage(result)
        return cubepage.renderPage()

    action = request.forms.get('robotaction')
    
    if action == 'stop':
        if process_getcubestate != None:
            process_getcubestate.kill()
        cubepage.setMessage("Stop")
        return cubepage.renderPage()
    elif action == 'open':
        if simulation:
            output = subprocess.run(["sleep","10"], stdout=subprocess.PIPE).stdout.decode('utf-8')
        else:
            try:
                output = subprocess.run(["opengrippers.py",], stdout=subprocess.PIPE).stdout.decode('utf-8')
            except:
                cubepage.setMessage("Error attempting to open grippers")
                return cubepage.renderPage()
            
        cubepage.setMessage("Open")
        return cubepage.renderPage()
    elif action == 'cradle':
        if simulation:
            output = subprocess.run(["sleep","10"], stdout=subprocess.PIPE).stdout.decode('utf-8')
        else:
            try:
                output = subprocess.run(["cradle.py",], stdout=subprocess.PIPE).stdout.decode('utf-8')
            except:
                cubepage.setMessage("Error attempting to cradle grippers")
                return cubepage.renderPage()
        cubepage.setMessage("Cradle")
        return cubepage.renderPage()
    elif action == 'camera':
        
        thread = Thread(target=do_getcubestate)
        thread.start()
        cubepage.setMessage("Inspecting Cube")
        return cubepage.renderPage()

        return "<p>Inspecting Cube now.</p>"
    elif action == 'solve':
        cubepage.saveCubeState()
        codeName = request.forms.get('solve')
        if codeName != "":
            person = decodeCodeName(codeName)
        else:
            person = ""
        #person = request.forms.get('solve')
        if person != "":
            thread = Thread(target=do_solveit)
            thread.start()
            cubepage.setMessage(f"Solving cube for {person}")
        else:
            cubepage.setMessage("Nope. Thats not a good name: " + codeName)
    elif action == 'reloadcubestate':
        cubepage.loadCubeState(cubeStateFile)
        cubepage.setMessage(f"refreshed the cube")

    elif action == 'savecubestate':
        cubepage.saveCubeState(cubeStateFile)
        cubepage.setMessage(f"saved the cube")

    return cubepage.renderPage()

def parseArgs():
    
    global simulation
    
    parser = argparse.ArgumentParser()
    
    parser.add_argument('--simulation', dest='simulation', action='store_true', help="do not use the camera or robot. Generate webpage and update state file when done.")

    args = parser.parse_args()
    
    if args.simulation:
        simulation = True
    
parseArgs()

run(host='localhost', port=18080,
#    reloader=True  #debugging: to refresh when source changes
    )
