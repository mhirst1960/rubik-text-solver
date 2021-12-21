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

simulation=True

cubeState = ''
getCubeStatePid = None
process_getcubestate = None

abs_app_dir_path = os.path.dirname(os.path.realpath(__file__))
abs_views_path = os.path.join(abs_app_dir_path, 'views')
bottle.TEMPLATE_PATH.insert(0, abs_views_path )

    
cubepage = CubeWebpage()

home = str(Path.home())
cubeStateFile = home + '/cubestate.txt'


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
            process_getcubestate = subprocess.Popen(["getcubestate.py",], stdout = subprocess.PIPE)
        getCubeStatePid = process_getcubestate.pid
        out, err = process_getcubestate.communicate()
        getCubeStatePid = None
        process_getcubestate = None
        print ("Done getting cube state.")
    
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
            output = subprocess.run(["opengrippers.py",], stdout=subprocess.PIPE).stdout.decode('utf-8')
        cubepage.setMessage("Open")
        return cubepage.renderPage()
    elif action == 'cradle':
        if simulation:
            output = subprocess.run(["sleep","10"], stdout=subprocess.PIPE).stdout.decode('utf-8')
        else:
            output = subprocess.run(["cradle.py",], stdout=subprocess.PIPE).stdout.decode('utf-8')
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
        person = request.forms.get('solve')
        if person != "":
            if simulation:
                output = subprocess.run(["sleep","30"], stdout=subprocess.PIPE).stdout.decode('utf-8')
            else:
                output = subprocess.run(["sleep","30"], stdout=subprocess.PIPE).stdout.decode('utf-8')

            cubepage.setMessage(f"Solving cube for {person}")
        else:
            cubepage.setMessage("Error: unknown command")
    elif action == 'reloadcubestate':
        cubepage.loadCubeState(cubeStateFile)
        cubepage.setMessage(f"refreshed the cube")

    elif action == 'savecubestate':
        cubepage.saveCubeState(cubeStateFile)
        cubepage.setMessage(f"saved the cube")

    return cubepage.renderPage()


    
run(host='localhost', port=18080,
#    reloader=True  #debugging: to refresh when source changes
    )
