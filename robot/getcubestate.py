#! /bin/python3

from warnings import simplefilter
from numpy.lib import index_tricks
from picamera.array import PiRGBArray
from picamera import PiCamera
import picamera.array
import subprocess

import cv2
import numpy as np

from PIL import Image
from PIL import ImageDraw

from fractions import Fraction

from time import sleep
from CubeMover import CubeMover
from Lighting import Lighting

HOME = "/home/pi/"
#OUTFILE = HOME + "cameracubestate.txt"
OUTFILE = HOME + "cubestate.txt"
HTMLDIR = HOME + "/cameraviewer/"

hiRes = False

if hiRes:
    resolution = (1280, 720)
    stickerSize=100
    stickerSize2= int(stickerSize * 0.5)
    stickerSpace=190

    #Sticker centers
    stickerX1 = 410
    stickerY1 = 120
    
    #areas for white balance (white rubber bands)
    wbX1 = 240
    wbY1 = 650
    wbX2 = 1050
    wbY2 = 580
    wbWidth1 = 30
    wbHeight1 = 30

else:
    resolution = (640, 480)
    stickerSize=65
    stickerSize2= int(stickerSize * 0.5)
    stickerSpace=90

    #Sticker centers
    stickerX1 = 190
    stickerY1 = 95   

    #areas for white balance (white rubber bands)
    wbX1 = 120
    wbY1 = 360
    wbX2 = 530
    wbY2 = 350
    wbWidth1 = 15
    wbHeight1 = 15
    
stickerX2 = stickerX1+stickerSize2+stickerSpace
stickerY2 = stickerY1+stickerSize2+stickerSpace

stickerX3 = stickerX2+stickerSize2+stickerSpace
stickerY3 = stickerY2+stickerSize2+stickerSpace



wbRec1 = [(wbX1-wbWidth1,wbY1-wbHeight1), (wbX1+wbWidth1,wbY1+wbHeight1)]
wbRec2 = [(wbX2-wbWidth1,wbY2-wbHeight1), (wbX2+wbWidth1,wbY2+wbHeight1)]

sticker1 = [(stickerX1-stickerSize2, stickerY1-stickerSize2), (stickerX1+stickerSize2, stickerY1+stickerSize2)]
sticker2 = [(stickerX2-stickerSize2, stickerY1-stickerSize2), (stickerX2+stickerSize2, stickerY1+stickerSize2)]
sticker3 = [(stickerX3-stickerSize2, stickerY1-stickerSize2), (stickerX3+stickerSize2, stickerY1+stickerSize2)]
sticker4 = [(stickerX1-stickerSize2, stickerY2-stickerSize2), (stickerX1+stickerSize2, stickerY2+stickerSize2)]
sticker5 = [(stickerX2-stickerSize2, stickerY2-stickerSize2), (stickerX2+stickerSize2, stickerY2+stickerSize2)]
sticker6 = [(stickerX3-stickerSize2, stickerY2-stickerSize2), (stickerX3+stickerSize2, stickerY2+stickerSize2)]
sticker7 = [(stickerX1-stickerSize2, stickerY3-stickerSize2), (stickerX1+stickerSize2, stickerY3+stickerSize2)]
sticker8 = [(stickerX2-stickerSize2, stickerY3-stickerSize2), (stickerX2+stickerSize2, stickerY3+stickerSize2)]
sticker9 = [(stickerX3-stickerSize2, stickerY3-stickerSize2), (stickerX3+stickerSize2, stickerY3+stickerSize2)]

stickers = [sticker1, sticker2, sticker3, sticker4, sticker5, sticker6, sticker7, sticker8, sticker9]
stickerCenters = [(stickerX1,stickerY1),
                  (stickerX2,stickerY1),
                  (stickerX3,stickerY1),
                  
                  (stickerX1,stickerY2),
                  (stickerX2,stickerY2),
                  (stickerX3,stickerY2),
                  
                  (stickerX1,stickerY3),
                  (stickerX2,stickerY3),
                  (stickerX3,stickerY3)
                  ]
lowLight = False

camera = PiCamera()
if lowLight:
    camera.resolution = resolution
    # Set a framerate of 1/2fps, then set shutter
    # speed to 2s and ISO to 800
    camera.framerate = Fraction(1, 2)
    camera.shutter_speed = 2000000
    camera.exposure_mode = 'off'
    camera.iso = 800
else:
    camera.resolution = resolution
    # Set a framerate of 1/2fps, then set shutter
    # speed to 2s and ISO to 800
    camera.framerate = Fraction(1, 2)
    #camera.shutter_speed = 2000000
    #camera.exposure_mode = 'off'
    #camera.iso = 800    

camera.awb_mode = 'off'

animColorLookup = {'L':'G', 'R':'B', 'F':'W', 'B':'Y', 'U':'O', 'D':'R'}
rcrStateFaceReorderLookup = {'L':'U', 'R':'D', 'F':'B', 'B':'F', 'U':'L', 'D':'R'}

colorResolverLookup = [
                     1,  2,  3,
                     4,  5,  6,
                     7,  8,  9,
        37, 38, 39,  19, 20, 21,   10, 11, 12,   46, 47, 48,
        40, 41, 42,  22, 23, 24,   13, 14, 15,   49, 50, 51,
        43, 44, 45,  25, 26, 27,   16, 17, 18,   52, 53, 54,
                     28, 29, 30,
                     31, 32, 33,
                     34, 35, 36,
    ]

animOrderLookup = [7, 8, 9,
                   4, 5, 6,
                   1, 2, 3,
    39, 38, 37,   19, 22, 25,  46, 49, 52,  28, 31, 34,
    42, 41, 40,   20, 23, 26,  47, 50, 53,  29, 32, 35,
    45, 44, 43,   21, 24, 27,  48, 51, 54,  30, 33, 36,
                  10, 13, 16,
                  11, 14, 17,
                  12, 15, 18]

#
def convertRCRStateToMyState(rcrCubeState):
    """
    color resolver assigned corors differently that we do. E.g. orange should be up not left
    """
    assert len(rcrCubeState) == 54
    reorderedState = [None] * 54
    for i in range(54):
        #find i in colorResolverLookup
        s = rcrCubeState[i]
        color = rcrStateFaceReorderLookup[s]
        
        reorderedState[i] = color
        
    newState = "".join(reorderedState)
    return newState

def convertStateToAnimColors(state):
    """
    input side order is from color resolver
    output color order is for AnimCube3 viewer
    """
    assert len(state) == 54
    animState = [None] * 54
    for i in range(54):
        #find i in colorResolverLookup
        s = state[i]
        color = animColorLookup[s]
        
        sIndex = colorResolverLookup.index(i+1)
        aIndex = animOrderLookup[sIndex]-1
        
        animState[aIndex] = color
        
    colors = "".join(animState)
    return colors

    
def generateHTML(htmlDir, cubeState):
    indexHtml = htmlDir + "/index.html"
    configFile = htmlDir + "/AnimCube3.cfg"
    
    print ("cubeState = ", cubeState)
    animColors = convertStateToAnimColors(cubeState)
    
    config = """
bgcolor=ffffff
butbgcolor=99eebb
    """
    f = open(configFile, "w")
    f.write(config)
    f.close()
    
    html = """
    
   <!DOCTYPE html>
   <html>
    <head>
     <script src="AnimCube3.js"></script>
    </head>
    <body>
 
     <div style="width:400px; height:400px">
      <script>AnimCube3("config=AnimCube3.cfg&"
          +"edit=0&yz=1&hint=10&scale=3&"
          +"facelets={colors}&hint=10&scale=3"
          +"movetext=1&"
          +"move={moves}&")
        </script>
     </div>
 
    </body>
   </html>
    """.format(colors=animColors, moves="RUR'URU2R'U2")
    f = open(indexHtml, "w")
    f.write(html)
    f.close()

def pix_average(im, x,y):
    r,g,b = 0,0,0
    count = 0
    for i in range (0,20):
        for j in range (0,20):
            r1,g1,b1 = im.getpixel((x-10+i,y-10+j))
            if r1 < 10 and g1 < 10 and b1 < 10:
                # ignore black, which is typically lettering
                continue
            r += r1
            g += g1
            b += b1
            count += 1
    if count == 0:
        return 0, 0, 0
    
    r = r/count
    g = g/count
    b = b/count

    return r, g, b

def setWhiteBalance(face="up"):
    
    print("white balance " + face)
    left = wbRec1[0][0]
    top = wbRec1[0][1]
    right = wbRec1[1][0]
    bottom = wbRec1[1][1]
    zoomX = left/resolution[0]
    zoomY = top/resolution[1]
    zoomW = (right-left)/resolution[0]
    zoomH = (bottom-top)/resolution[1]
    
    rg, bg = (1.2, 1.2)
    camera.awb_gains = (rg, bg)
    
    zoomSave = camera.zoom
    camera.zoom=(zoomX, zoomY, zoomW, zoomH)
    # Allow 30 attempts to fix AWB
    for i in range(10):
        # Capture a tiny resized image in RGB format, and extract the
        # average R, G, and B values
        #camera.capture(img, format='rgb', resize=(128, 72), use_video_port=True)
        fname = HOME + "/cubeimages/white-balance-" + face + str(i) + ".jpg"
        camera.capture(fname, format='jpeg')
        img = Image.open(fname)

        #wbImage = img.crop((left, top, right, bottom))
        #r, g, b = (np.mean(img.array[..., i]) for i in range(3))
        #r, g, b = pix_average(img,(right-left)/2, (bottom-top)/2)
        r, g, b = pix_average(img,3, 3)
        print('R:%5.2f, B:%5.2f = (%5.2f, %5.2f, %5.2f)' % (
            rg, bg, r, g, b))
        # Adjust R and B relative to G, but only if they're significantly
        # different (delta +/- 2)
        if abs(r - g) > 2:
            if r > g:
                rg -= 0.1
            else:
                rg += 0.1
        if abs(b - g) > 1:
            if b > g:
                bg -= 0.1
            else:
                bg += 0.1
        camera.awb_gains = (rg, bg)
        #img.seek(0)
        #img.truncate()
    camera.zoom = zoomSave

def takePicture(face="up") :
    rawCapture = PiRGBArray(camera)

    mover.cradleCube()
    mover.right.close()
    mover.left.close()
    bottomLED.bright()
    topLeftLED.bright()
    topRightLED.bright()
    sleep (0.2)
    
    setWhiteBalance(face)

    fname = HOME + "/cubeimages/face-" + face + "-raw.jpg"
    camera.capture(fname, format='jpeg')
    #camera.capture(rawCapture, format="bgr")
    
    bottomLED.off()
    #topLeftLED.off()
    #topRightLED.off()
    
    stickerNumber = 0

    img = Image.open(fname)

    
    # get whiteness of extra white sticker for white balance
    left = wbRec1[0][0]
    top = wbRec1[0][1]
    right = wbRec1[1][0]
    bottom = wbRec1[1][1]
    wbImage = img.crop((left, top, right, bottom))
    wbr, wbg, wbb = pix_average(wbImage,(right-left)/2, (bottom-top)/2)
    whiteCorrectionR = 0 #255 - wbr
    whiteCorrectionG = 0 #255 - wbg
    whiteCorrectionB = 0 #255 - wbb
    
    stickerRGBValues = []
    
    for s in stickers:
        left = s[0][0]
        top = s[0][1]
        right = s[1][0]
        bottom = s[1][1]
        stickerImage = img.crop((left, top, right, bottom))
        r, g, b = pix_average(stickerImage,(right-left)/2, (bottom-top)/2)
        red = int(r+whiteCorrectionR)
        green = int(g+whiteCorrectionG)
        blue  = int(b+whiteCorrectionB)
        if red > 255:
            red = 255
        if green > 255:
            green = 255
        if blue > 255:
            blue = 255
            
        stickerRGBValues.append([red,green,blue])
        fname = HOME + "/cubeimages/sticker-" + face + str(stickerNumber) + "-raw.jpg"
        stickerImage.save(fname)
        stickerNumber += 1


    # display rectangle area of each sticker
    draw = ImageDraw.Draw(img)
    left = wbRec1[0][0]
    top = wbRec1[0][1]
    right = wbRec1[1][0]
    bottom = wbRec1[1][1]
    draw.rectangle((left, top, right, bottom), width=3, outline="red")
    del draw

    for s in stickers:
        draw = ImageDraw.Draw(img)
        left = s[0][0]
        top = s[0][1]
        right = s[1][0]
        bottom = s[1][1]
        draw.rectangle((left, top, right, bottom), width=3, outline="green")
        del draw
    
    #img = cv2.rectangle(img, s[0], s[1], (0, 255, 0), 2)
    fname = HOME + "/cubeimages/face-" + face + ".jpg"
    img.save(fname)
    
    if False:

        img = cv2.rectangle(img, wbRec1[0], wbRec1[1], (255, 0, 0), 2)
        img = cv2.rectangle(img, wbRec2[0], wbRec2[1], (255, 0, 0), 2)

        img = cv2.resize(img, (0, 0), fx=0.4, fy=0.4)
        
        # Create the resizeable window
        #cv2.namedWindow('image', cv2.WINDOW_NORMAL)
        cv2.imshow('image', img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        
    return(stickerRGBValues)

class StickerValue:
    
    #Note: botton layer of color-resolver is right to left
    #      our convension is left to right
    colorResolverTranslation = [
                     1,  2,  3,
                     4,  5,  6,
                     7,  8,  9,
        10, 11, 12,  19, 20, 21,   28, 29, 30,   39, 38, 37,
        13, 14, 15,  22, 23, 24,   31, 32, 33,   42, 41, 40,
        16, 17, 18,  25, 26, 27,   34, 35, 36,   45, 44, 43,
                     46, 47, 48,
                     49, 50, 51,
                     52, 53, 54
    ]

    def getColorResolverLabel(self, index):
        """convert cube index to color-resolver label"""
        if index < 0 or index >= len(self.colorResolverTranslation):
            return None
        else:
            return str(self.colorResolverTranslation[index])
        
    def __init__(self, index):
        self.index = index
        self.cubeSolverLabel = self.getColorResolverLabel(index)
        self.rgb = None
        self.color = None

    def cubeSolverJsonInputString(self):
        """
        rubicks-color-resolver takes a JSON string like this:
        {"15": [20, 118, 121], "20": [191, 33, 6], "2": [133, 126, 10],...}
        so we will return this part:
         "15": [20, 118, 121]
        """
        return f'"{self.cubeSolverLabel}": [{self.rgb[0]}, {self.rgb[1]}, {self.rgb[2]}]'
        
        
########Start of execution#######

#generateHTML(HTMLDIR, "LLBUUBUUBUUURRRRRRFFLFFUFFUDDFDDFRRFDLLDLLDLLRBBDBBDBB")
#generateHTML(HTMLDIR, "UUUUUUUUULLLFFFRRRBBBLLLFFFRRRBBBLLLFFFRRRBBBDDDDDDDDD")
#exit()

stickerValues = []

for i in range(0,54):
    stickerValues.append(StickerValue(i))


     
bottomLEDChannel   = 12
topLeftLEDChannel  = 13
topRightLEDChannel = 14

mover = CubeMover()

bottomLED = Lighting(bottomLEDChannel, mover.kit)
topLeftLED = Lighting(topLeftLEDChannel, mover.kit)
topRightLED = Lighting(topRightLEDChannel, mover.kit)

# blink three times to warn that servos are about to start
for i in range (0, 3):
    
    bottomLED.bright()
    topLeftLED.bright()
    topRightLED.bright()
    sleep (0.3)
    bottomLED.off()
    topLeftLED.off()
    topRightLED.off()
    sleep (0.3)
    
sleep(1)


#bottomLED.bright()
#topLeftLED.bright()
#topRightLED.bright()

mover.cradleCube()
mover.left.close()
mover.right.close()

rgbValues = takePicture("up") #Orange up sticker numbers as viewed from camera upperleft=9:
                # color-resolver: 9,8,7,  6,5,4,  3,2,1
                # cube index:     8,7,6,  5,4,3,  2,1,0
stickerIndexes = [8,7,6,  5,4,3,  2,1,0]
for rgbIndex, stickerIndex in enumerate(stickerIndexes):
    stickerValues[stickerIndex].rgb = rgbValues[rgbIndex]

mover.Z()

rgbValues = takePicture("left") #green left:
                # color-resolver: 10, 13, 16,   11, 14, 17,   12, 15, 18
                # cube index:     35, 34, 33,   23, 22, 21,   11, 10,  9
                # cube index:     11, 23, 25,   10, 22, 34,    9, 21, 33
stickerIndexes = [11, 23, 35,   10, 22, 34,    9, 21, 33]
for rgbIndex, stickerIndex in enumerate(stickerIndexes):
    stickerValues[stickerIndex].rgb = rgbValues[rgbIndex]

mover.Z()

rgbValues = takePicture("down") #red down:
                # color-resolver: 46, 47, 48,   49, 50, 51,   52, 53, 54
                # cube index:     45, 46, 47,   48, 49, 50,   51, 52, 53
stickerIndexes = [45, 46, 47,   48, 49, 50,   51, 52, 53]
for rgbIndex, stickerIndex in enumerate(stickerIndexes):
    stickerValues[stickerIndex].rgb = rgbValues[rgbIndex]
    
mover.Z()

rgbValues = takePicture("right") #blue right:
                # color-resolver: 34, 31, 28,   35, 32, 29,   36, 33, 30
                # cube index:     39, 27, 15,   40, 28, 16,   41, 29, 17
stickerIndexes = [39, 27, 15,   40, 28, 16,   41, 29, 17]
for rgbIndex, stickerIndex in enumerate(stickerIndexes):
    stickerValues[stickerIndex].rgb = rgbValues[rgbIndex]

mover.Z()
mover.X()
mover.Y2()

rgbValues = takePicture("front") #white front:
                # color-resolver: 25, 22, 19,   26, 23, 20,   27, 24, 21
                # cube index:     36, 24, 12,   37, 25, 13,   38, 26, 14
                # cube index:     12, 13, 14,   24, 25, 26,   36, 37, 38
stickerIndexes = [12, 13, 14,   24, 25, 26,   36, 37, 38]
for rgbIndex, stickerIndex in enumerate(stickerIndexes):
    stickerValues[stickerIndex].rgb = rgbValues[rgbIndex]

mover.Z2()

rgbValues = takePicture("back") #yellow back:
                # color-resolver: 37, 38, 39,   40, 41, 42,   43, 44, 45
                # cube index:     18, 19, 20,   30, 31, 32,   42, 43, 44
                # cube index:     20, 19, 18,   32, 31, 30,   44, 43, 42
stickerIndexes = [20, 19, 18,   32, 31, 30,   44, 43, 42]
for rgbIndex, stickerIndex in enumerate(stickerIndexes):
    stickerValues[stickerIndex].rgb = rgbValues[rgbIndex]

mover.Z2()
mover.Xi()
mover.Z2()
#cube should now be back where it started

mover.cradleCube()

#sleep(1)
bottomLED.off()
topLeftLED.off()
topRightLED.off()

jsonString = "{"
for count, stickerValue in enumerate(stickerValues):
    jsonString += stickerValue.cubeSolverJsonInputString()
    if count < len(stickerValues)-1:
        jsonString += ", "
jsonString += "}"

print (jsonString)

fname = HOME + "/rubik/colors.json"
jsonFile = open(fname, "w")
jsonFile.write(jsonString)
jsonFile.close()

#rubiks-color-resolver to assign colors to stickers: RWBGYO
result = subprocess.run(["rubiks-color-resolver.py",
                "--filename",
                fname], stdout=subprocess.PIPE)

rcrCubeState = result.stdout.decode('utf-8')
print ("rubiks-color-resolver cubeState = ", rcrCubeState)
rcrCubeState = rcrCubeState.rstrip()

#color resolver assigned corors differently that we do. E.g. orange should be up not left
cubeState = convertRCRStateToMyState(rcrCubeState)
print ("cubeState = ", cubeState)

f = open(OUTFILE, "w")
f.write(cubeState)
f.close()


generateHTML(HTMLDIR, cubeState)

exit()

