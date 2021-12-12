#!/bin/python3

"""
class CubeWebpage

This class generates a webpage using animCube3 for showing cube state and colors and moves.
To view the webpage open a web browser like Chrome or Firefox or Chromium or Safari.  The URL, entered
as a webite would be "file:<path to your html file>".  For example:

   python3 CubeWebpage.py --htmldir /home/pi/cubeviewer

generates, by default index.html in the directory /home/pi/cubeshower . So in you browser enter
this URL to view the cube:

    file:/home/pi/cubeviewer/index.html


The assumption is this is running on Linux like on a Raspberry Pi or Ubuntu or MAC commandline.

Before you start, this requires 3x3x3 AnimCubeJS simulator, which is simple free javascript package.
You can download the 3x3x3 zip file from here:
 
https://cubing.github.io/AnimCubeJS/animcubejs.html#download

Please unzip it to the local directory where you would like to generate your webpage.
The parameter htmlDir (--htmldir <directory>) should point to the same place that
3x3x3-AnimCubeJS.zip is unzipped to.

Installation example:
    cd /home/pi/cubeviewer
    unzip 3x3x3-AnimCubeJS.zip
    
"""

import argparse
import os
from shutil import copyfile
import string

#from CubeOrder import CubeOrder
from rubik.CubeOrder import CubeOrder


CUBE_COLORS_DEFAULT = \
"""
    OOO
    OOO
    OOO
GGG WWW BBB YYY
GGG WWW BBB YYY
GGG WWW BBB YYY
    RRR
    RRR
    RRR
"""

class CubeWebpage:
    
    config = """
    bgcolor=ffffff
    butbgcolor=99eebb
    """

    HTML_CUBE_TEMPLATE = """
        <div style="width:400px; height:400px; float: left">
        <div> {info} </div>
        <script>AnimCube3("config=AnimCube3.cfg&"
            +"edit=0&yz=1&hint=10&scale=3&"
            +"facelets={colors}&hint=10&scale=3"
            +"movetext=1&"
            +"move={moves}&")
            </script>
        </div>
        """

    HTML_PAGE_PREFIX_TEMPLATE = """
        
    <!DOCTYPE html>
    <html>
        <head>
        <link rel="icon" href="favicon.ico" type="image/x-icon">
        <script src="AnimCube3.js"></script>
        </head>
        <body>
        <div> <H1> {title} </H1> </div>
        <div> <H3> {subtitle} </H3> </div>
        <div> Moves: {moves} </div>

    """

    HTML_PAGE_SUFFIX_TEMPLATE = """
        </body>
    </html>
    """

    HTML_ERROR_TEMPLATE = """
        <div style="width:400px; height:400px; float: left">
         ERROR: file not found: {animjsFile} <br>
please download 3x3x3-AnimCubeJS.zip from <a href="https://cubing.github.io/AnimCubeJS/animcubejs.html#download">cubing.github.io/AnimCubeJS</a>  <br>
and install like this: <br>
    cd {htmlDir}<br>
    unzip 3x3x3-AnimCubeJS.zip<br>
        </div>
            """
            
    def __init__(self, htmlDir, htmlFile='index.html', cubeColors=None, cubeState=None, cubeMoves='', title='Cube Viewer', subTitle=''):
        

        self.htmlDir = htmlDir
        self.htmlFile = htmlFile
        
        self.animjsFile = htmlDir + "/AnimCube3.js"
        if not os.path.exists(self.animjsFile):
            errorText = f"""
<br> <br>
ERROR: file not found: {self.animjsFile} <br>
please download 3x3x3-AnimCubeJS.zip from https://cubing.github.io/AnimCubeJS/animcubejs.html#download <br>
and install like this:
    cd {htmlDir}
    unzip 3x3x3-AnimCubeJS.zip
            """
            print (errorText)
            self.animjsInstalled = False
        else:
            self.animjsInstalled = True

        if isinstance(cubeMoves, list):
            self.cubeMoves = ''.join(cubeMoves)
        else:
            self.cubeMoves = cubeMoves
        
        self.title = title
        self.subTitle = subTitle
        
        if cubeColors == None:
            self.cubeColors = CUBE_COLORS_DEFAULT
        else:
            self.cubeColors = cubeColors
        self.compactColors = "".join(x for x in self.cubeColors if x not in string.whitespace)
        
        self.cubeState = cubeState
        if self.cubeState == None:
            self.compactState = None
        else:
            self.compactState = "".join(x for x in self.cubeState if x not in string.whitespace)
            self.compactState = self.getDimColorString(self.compactState)
 

        
        self.cubeOrder = CubeOrder()


    def getDimColorString(self, colorString):
        # convert to anim dim colors
        tbl = {'W':'4', 'Y':'5', 'O':'6', 'R':'7', 'G':'8', 'B':'9',
                'w':'4', 'y':'5', 'o':'6', 'r':'7', 'g':'8', 'b':'9'}
        l = list(colorString)
        for i,d in enumerate(l):
            l[i] = tbl[l[i]]
        dimString = ''.join(l)
        return dimString


    def generateHTML(self):
        
        
        
        indexHtml = self.htmlDir + "/" + self.htmlFile
        configFile = self.htmlDir + "/AnimCube3.cfg"
        pythonScriptDir = os.path.dirname(os.path.realpath(__file__))

        co = self.cubeOrder
        
        animColors = co.convert(self.compactColors, co.SLICE_UNFOLD_BACK, co.SLICE_ANIMJS3)
        animMoves = self.cubeMoves.replace('i', "'")
        if self.compactState != None:
            animStateColors = co.convert(self.compactState, co.SLICE_UNFOLD_BACK, co.SLICE_ANIMJS3)
        else:
            animStateColors = None

        # little icon in the browser tab
        copyfile(pythonScriptDir + "/favicon.ico", self.htmlDir + '/favicon.ico')
        
        f = open(configFile, "w")
        f.write(self.config)
        f.close()
        if not self.animjsInstalled:
            print ("ERROR CubeWebpage is not installed")
            html = self.HTML_PAGE_PREFIX_TEMPLATE.format(title=self.title, subtitle=self.subTitle, moves=animMoves)
            html += self.HTML_ERROR_TEMPLATE.format(animjsFile=self.animjsFile, htmlDir=self.htmlDir)
        else:  
            html = self.HTML_PAGE_PREFIX_TEMPLATE.format(title=self.title, subtitle=self.subTitle, moves=animMoves)
            html += self.HTML_CUBE_TEMPLATE.format(info="Cube Colors", colors=animColors, moves=animMoves)
            
            if animStateColors != None:
                html += self.HTML_CUBE_TEMPLATE.format(info="Cube State", colors=animStateColors, moves=animMoves)
                                                   
        html += self.HTML_PAGE_SUFFIX_TEMPLATE
        
        f = open(indexHtml, "w")
        f.write(html)
        f.close()

def parseArgs():
    
    global DEBUG
    global htmlDir
    global htmlFile
    global htmlTitle
    global htmlInfo
    global cubeColors
    global compactColors
    global cubeMoves
    
    parser = argparse.ArgumentParser()

    parser.add_argument('--verbose', '-v', action='count', default=0, \
    help="show debug messages -v, -vv, -vvv for more and more debug")

    parser.add_argument("--htmldir", default=".", help="Directory where to put the webpage (default is current directory)")
    parser.add_argument("--htmlfile", default='index.html', help="HTML file name (default=index.html)")
    parser.add_argument("--title", default='Cube Viewer', help="Title of the Webpage")
    parser.add_argument("--subtitle", default='', help="Some information about the cube you want to show")
    parser.add_argument("--cubecolors", default='', help="sequence of moves to show.  For example: ")
    parser.add_argument("--moves", default='', help="sequence of moves to show.  For example: ")
    
    args = parser.parse_args()
    
    if args.verbose:
        DEBUG=args.verbose
        
    if args.htmldir:
        htmlDir = args.htmldir
        print ("arg htmldir = ", htmlDir)

    if htmlDir == '.':
        htmlDir = os.getcwd()

    if args.htmlfile:
        htmlFile = args.htmlfile
    
    if args.cubecolors != '':
        cubeColors = args.cubecolors
        compactColors = "".join(x for x in cubeColors if x not in string.whitespace)

    cubeMoves = args.moves
    
        
                
def run():
    print ("Running CubeWebPage")
    if DEBUG == None:
        print("DEBUG = None")
    else:
        print("DEBUG = ", DEBUG)
        
    if DEBUG > 0:
        print (f"Saving to {htmlDir}/{htmlFile}")

    cubePage = CubeWebpage(htmlDir, htmlFile, compactColors, cubeMoves=cubeMoves)
    cubePage.generateHTML()

    print (f"Enter this URL in your browser\n   file:{htmlDir}/{htmlFile}")

    

if __name__ == '__main__':
    DEBUG = 0
    cubeColors= CUBE_COLORS_DEFAULT
    compactColors = "".join(x for x in cubeColors if x not in string.whitespace)

    parseArgs()
    run()
