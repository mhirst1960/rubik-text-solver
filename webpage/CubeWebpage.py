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


class CubeWebpage:
#TODO these should be moved to template files
    HTML_HEADER = '''
    <!DOCTYPE html>
<html>
<title>Cube</title>
    <head>
        <link rel="icon" href="static/favicon.ico" type="image/x-icon">
        <link rel="stylesheet" href="https://www.w3schools.com/w3css/4/w3.css">
        <link rel="stylesheet" href="https://www.w3schools.com/lib/w3-theme-black.css">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.3.0/css/font-awesome.min.css">
        <link rel="stylesheet" href="static/cubestyle.css">
        <!-- <script src="AnimCube3.js"></script> -->
    </head>
    
    <body>
    '''

    HTML_CONTROL_BUTTONS = '''
        <form action="/cube" method="post">
        <div>
        Robot Commands: 
            <input name="robotaction" value="open" type="submit" />
            <input name="robotaction" value="cradle" type="submit" />
            <button name="robotaction" value="camera" type="submit"> Inspect Cube </button>
            <input name="robotaction" value="stop" type="submit" /> <br>
        </div>
        <div>
            Enter TMW Solver Code here: <input name="solve" value="" type="text" /> <br>
        </div>
        <div>
            <button name="robotaction" value="reloadcubestate" type="submit"> Reload Cube </button>
            <button name="robotaction" value="savecubestate" type="submit"> Save Cube </button>
            <button name="robotaction" value="solve" type="submit"> Solve The Cube! </button>
        <div>
        </form> 
    '''
    
    HTML_CUBESTATE = '''
    <BR>
        Cube state: {cubeState} <br>

</div>
    '''
    
    HTML_STATUS = '''
        Status: {lastCommand}
    '''
    
    HTML_SUFFIX = '''

</body>
</html>
        '''
    
    def __init__(self):
        self.cubeSate = "X"*54
        self.lastCommand = ""
        self.cubeStateFile = None
    
    rubikColors = {'green':'#008000', 'red':'#FF0000', 'blue':'#0000FF', 'orange':'#ff7900', 'white':'#FFFFFF', 'yellow':'#FFFF00', 'grey':'#a9a9a9',
                    'G':'#008000', 'R':'#FF0000', 'B':'#0000FF', 'O':'#ff7900', 'W':'#FFFFFF', 'Y':'#FFFF00', 'X':'#a9a9a9'}
    rubikWarningColors = {'green':'#558055', 'red':'#ff5555', 'blue':'#8888FF', 'orange':'#FFA588', 'white':'#ffffe0', 'yellow':'#ffff80', 'grey':'#a9a9a9',
                    'G':'#558055', 'R':'#ff5555', 'B':'#8888FF', 'O':'#FFA588', 'W':'#ffffe0', 'Y':'#ffff80', 'X':'#a9a9a9'}
    rubikSpectrum = [rubikColors['green'], rubikColors['red'], rubikColors['blue'], rubikColors['orange'], rubikColors['white'], rubikColors['yellow']]
    editColorDropdownStateLookup  = {0:'L', 1:'D', 2:'R', 3:'U', 4:'F', 5:'B'}
    editColorDropdownColorLookup  = {0:'G', 1:'R', 2:'B', 3:'O', 4:'W', 5:'Y'}

    def isColorBad(self, color):
        # if too many or too few if this color in cubeState then color is bad
        #TODO check:
        #       only four corners same color
        #       only four edges same color
        #       only one face same color
        cubeColors = self.getCubeStateColors()
        count = cubeColors.count(color)
        if cubeColors.count(color) != 9:
            return True # wrong number of stickers this color: yes, it's bad
        else:
            return False

  
    def convertToRubikColors(self, colors):
        # Convert a list of colors to the list of values to display on the webpage
        rubikColors = list()
        for i,htmlColor in enumerate(colors):
            if htmlColor not in self.rubikColors:
                rubikColors += [self.rubikColors['X']]
            else:
                if self.isColorBad(htmlColor):
                    rubikColors += [self.rubikWarningColors[htmlColor]]
                else:
                    rubikColors += [self.rubikColors[htmlColor]]
            
        return rubikColors
    
    def getCubeStateColors(self):
        
        if self.cubeSate == None:
            return "X" * 54
        
        # if string is cube state not colors, convert to colors
        allowed = set('UDFBLR')
        if set(self.cubeSate) <= allowed:
            tbl = {'U':'O','D':'R','F':'W','B':'Y','L':'G','R':'B'}
            l = list(self.cubeSate)
            for i,d in enumerate(l):
                l[i] = tbl[l[i]]
            colors = ''.join(l)
        else:
            colors = self.cubeSate
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

        
    def generateCubeHTML(self):

        upColors    = self.getCubeFaceColors('up')
        leftColors  = self.getCubeFaceColors('left')
        frontColors = self.getCubeFaceColors('front')
        rightColors = self.getCubeFaceColors('right')
        backColors  = self.getCubeFaceColors('back')
        downColors  = self.getCubeFaceColors('down')
        
        return template('flatcube', name='TMW', rubikspectrum=self.rubikSpectrum,
                                                upcolors=upColors,
                        leftcolors=leftColors, frontcolors=frontColors, rightcolors=rightColors, backcolors=backColors,
                                                downcolors=downColors)
        
    def renderPage(self):

        cubeHTML = self.generateCubeHTML()
        
        page = (self.HTML_HEADER + self.HTML_CONTROL_BUTTONS +
                cubeHTML +
                self.HTML_STATUS.format(lastCommand=self.lastCommand) +
                self.HTML_SUFFIX
                )
        
        return page
    
    def loadCubeState(self, file=None):
        
        if file == None:
            file = self.cubeStateFile
        else:
            self.cubeStateFile = file
                        
        if file != None:
            f = open(file, "r")
            inputColors = f.read()
            f.close()
            inputColors = inputColors.rstrip()
            if len(inputColors) == 54:
                cubeState = inputColors
        
        self.setCubeState(cubeState)
        
        return self.cubeSate
        
    def saveCubeState(self, file=None):
        
        if file == None:
            file = self.cubeStateFile
        else:
            self.cubeStateFile = file
        
        if file != None:
            f = open(file, "w")
            f.write(self.cubeSate)
            f.close()
                
        return self.cubeSate
        
        
    def setCubeState(self, cubeState):
        self.cubeSate = cubeState
        
    def setMessage(self, lastCommand):
        self.lastCommand = lastCommand
    
    def getCubeFaceColors(self, face=None):
        rubicColors = self.convertToRubikColors(self.getCubeStateColors())
        cs = list(rubicColors)
        
        if len(cs) < 54:
            return list('X'*54)
        
        cubeColors = list()
        if face == None:
            cubeColors = cs
        elif face == 'up':
            cubeColors = cs[:9]
        elif face == 'left':
            cubeColors = cs[36:45]
        elif face == 'front':
            cubeColors = cs[18:27]
        elif face == 'right':
            cubeColors = cs[9:18]
        elif face == 'back':
            cubeColors = cs[45:54]
        elif face == 'down':
            cubeColors = cs[27:36]
        else:
            assert False # unsupported face name
        
        return cubeColors
    
    def setStickerState(self, face, stickerIndex, colorIndex):
        
        cs = list(self.getCubeStateColors())
        #cs = list(self.cubeSate)
        
        newColor = self.editColorDropdownColorLookup[colorIndex]
        #newColor = self.editColorDropdownStateLookup[colorIndex]
        
        if face == 'up':
            faceColors = cs[:9]
            faceColors[stickerIndex] = newColor
            cs[:9] = faceColors
        elif face == 'left':
            faceColors = cs[36:45]
            faceColors[stickerIndex] = newColor
            cs[36:45] = faceColors
        elif face == 'front':
            faceColors = cs[18:27]
            faceColors[stickerIndex] = newColor
            cs[18:27] = faceColors
        elif face == 'right':
            faceColors = cs[9:18]
            faceColors[stickerIndex] = newColor
            cs[9:18] = faceColors
        elif face == 'back':
            faceColors = cs[45:54]
            faceColors[stickerIndex] = newColor
            cs[45:54] = faceColors
        elif face == 'down':
            faceColors = cs[27:36]
            faceColors[stickerIndex] = newColor
            cs[27:36] = faceColors
        else:
            return 'X'
            
        self.setCubeState(''.join(cs))
        #self.cubeSate = ''.join(cs)
        
        return newColor

    def processEditAction(self, cubeAction):
        keyValue = cubeAction.split('=')
        if len(keyValue) != 2:
            return "error: " + cubeAction
        
        stickerIndex = keyValue[0][-1:]
        if not stickerIndex.isdigit():
            return "error: sticker out of bounds!"
        
        i = int(stickerIndex)
        
        face = keyValue[0][:-1]
        
        if keyValue[1].isdigit():
            value = int(keyValue[1])
        else:
            return "error: color value not integer. " + cubeAction
        
        self.setStickerState(face, i, value)

        return f"face: {face}, sticker: {stickerIndex}, new value: {keyValue[1]}"
    