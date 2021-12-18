#! /bin/python3

import subprocess
import argparse
import psutil
import os
from threading import Thread

from bottle import route, run, template
from bottle import route, request
from bottle import run

cubeState = ''
inputFile = '/home/pi/cubestate.txt'
getCubeStatePid = None
process_getcubestate = None

class CubeWebpage:

    template = '''
<!DOCTYPE html>
<html>
<title>Cube</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="https://www.w3schools.com/w3css/4/w3.css">
<link rel="stylesheet" href="https://www.w3schools.com/lib/w3-theme-black.css">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.3.0/css/font-awesome.min.css">
<body>
        <form action="/cube" method="post">
        Robot Commands: 
            <input name="robotaction" value="open" type="submit" />
            <input name="robotaction" value="cradle" type="submit" />
            <button name="robotaction" value="camera" type="submit"> Inspect Cube </button>
            <input name="robotaction" value="stop" type="submit" /> <br>
            Enter TMW Solver Code here: <input name="solve" value="" type="text" />
            <button name="robotaction" value="solve" type="submit"> Solve Cube! </button> <br>
        </form> <BR>
        Cube state: {cubeState} <br>
        Status: {lastCommand}
        
</body>
</html>
        '''
    
    def __init__(self):
        self.cubeSate = ""
        self.lastCommand = ""
    
    def getColors(self):
        # if string is cube state not colors, convert to colors
        allowed = set('UDFBLR')
        if set(self.cubeSate) <= allowed:
            tbl = {'U':'O','D':'R','F':'W','B':'Y','L':'G','R':'B'}
            l = list(self.cubeSate)
            for i,d in enumerate(l):
                l[i] = tbl[l[i]]
            colors = ''.join(l)
        return colors
    
    def getFormattedCube(self, colors):
        if colors == '':
            return ''
        
        template = (
            #"<div style=\"white-space: pre-wrap;\">"
            "<pre style=white-space: pre-wrap;>"
            "    {}{}{}<br>"
            "    {}{}{}<br>"
            "    {}{}{}<br>"
            "<br>"
            "{}{}{} {}{}{} {}{}{} {}{}{}<br>"
            "{}{}{} {}{}{} {}{}{} {}{}{}<br>"
            "{}{}{} {}{}{} {}{}{} {}{}{}<br>"
            "<br>"
            "    {}{}{}<br>"
            "    {}{}{}<br>"
            "    {}{}{}</pre>"
            #"</div>"
            )
        return template.format(*colors)
                
    def renderPage(self):
        colors = self.getColors()
        formattedColors = self.getFormattedCube(colors)
        return self.template.format(cubeState=formattedColors, lastCommand=self.lastCommand)
    
    def setCubeState(self, cubeState):
        self.cubeSate = cubeState
        
    def setMessage(self, lastCommand):
        self.lastCommand = lastCommand
     
     
cubepage = CubeWebpage()


@route('/cube')
def cube():

    if inputFile != None:
        f = open(inputFile, "r")
        inputColors = f.read()
        f.close()
        inputColors = inputColors.rstrip()
        if len(inputColors) == 54:
            cubeState = inputColors
        
        cubepage.setCubeState(cubeState)
        
    return cubepage.renderPage()


@route('/cube', method='POST')
def do_cube():
    global process_getcubestate

    def do_getcubestate():
        global getCubeStatePid
        global process_getcubestate
        
        
        process_getcubestate = subprocess.Popen(["getcubestate.py",], stdout = subprocess.PIPE)
        #process_getcubestate = subprocess.Popen(["sleep","20"], stdout = subprocess.PIPE)
        getCubeStatePid = process_getcubestate.pid
        out, err = process_getcubestate.communicate()
        getCubeStatePid = None
        process_getcubestate = None
        print ("Done getting cube state.")
    
    action = request.forms.get('robotaction')
    if action == 'stop':
        if process_getcubestate != None:
            process_getcubestate.kill()
        cubepage.setMessage("Stop")
        return cubepage.renderPage()
    elif action == 'open':
        output = subprocess.run(["opengrippers.py",], stdout=subprocess.PIPE).stdout.decode('utf-8')
        cubepage.setMessage("Open")
        return cubepage.renderPage()
    elif action == 'cradle':
        output = subprocess.run(["cradle.py",], stdout=subprocess.PIPE).stdout.decode('utf-8')
        cubepage.setMessage("Cradle")
        return cubepage.renderPage()
    elif action == 'camera':
        
        thread = Thread(target=do_getcubestate)
        thread.start()
        #process_getcubestate = subprocess.Popen(["catgetcubestate.py",], stdout = subprocess.PIPE)
        
        #output = subprocess.run(["getcubestate.py",], stdout=subprocess.PIPE).stdout.decode('utf-8')
        cubepage.setMessage("Inspecting Cube")
        return cubepage.renderPage()

        return "<p>Inspecting Cube now.</p>"
    elif action == 'solve':
        person = request.forms.get('solve')
        if person != "":
            cubepage.setMessage(f"Solving cube for {person}")
        else:
            cubepage.setMessage("Error: unknown command")

    return cubepage.renderPage()


    
run(host='localhost', port=18080,
#    reloader=True  #debugging: to refresh when source changes
    )
