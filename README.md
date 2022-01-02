![PyPI](https://img.shields.io/pypi/v/rubik-cube)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/rubik-cube)

# Overview

Provide a short string and this program will find the letters and solve such that those letters end up on the front of the cube.
You can also use it to solve the full cube in the normal fashon based on the colors.

I implemented two examples:
1. a solver for the initials of everyone in my family
2. a rubik-clock which shows the time of day on the cube as a 12-hour clock with am/pm

Everything is written using Python 3.

There are pictures on my website: https://madwrapper.com/?te_announcements=rubik-robot

TODO: Some of the functionality needs to be customized to adapt to your robot configuration and your Raspberry Pi configuration.  I did not do
an especially good job at seperating the configuration from the code.  The instructions below describe the files that need to be modified.
When I get a chance I will update the project to make the customization more flexible.  Meanwhile, I appologize for the sub-standard installation
requirements.

# Run the Robot

## start the web server
Run this command after logging in:

starttmwwebpage.sh

That is a script found in ~/bin that simply runs the folowing command without arguments.  This is the entry point to the web server:

rubik-text-solver/webpage/cubesolverhttp.py

## Run in browser

Use this URL in your browser running on the Raspberry Pi that runs the robot.

http://localhost:18080/cube


![image](https://user-images.githubusercontent.com/6749076/147514398-1ee665a4-c671-44bc-a9c6-5711c7e9bb34.png)

Assuming the cube is correctly represented in the picture, type in the user's code name and press "Solve the cube!".  Ultimately this runs the command:

tmwrubik.py --person person --inputorder kociemba --output robot" --robot" --input file --infile /home/pi/cubestate.txt

Where "person" is a person's initials (E.g. "KLH") and cubestate.txt is a 54-character string representing the current colors of the cube.  E.g.

BWWYOGBWGORGGGOGGOOOWBYWBRYRBROROORYYGYRBYWYWRBRBWWGYB


# More Details

The main solver is based on "Python Rubik's cube solver" https://github.com/pglass/cube .  Where I used the math transforms as-is
and I used fundimantal solving algorithm design.  But I refactored the code fairly significantly allowing extra attributes
for a piece beyond just it's colors.  And added a bunch of extra functionality to manipulate the cube based on labels decorated
with letters.


It contains:

- A simple implementation of the cube
- A solver that follows a fixed algorithm
- An unintelligent solution sequence optimizer
- A decent set of test cases
- robot control
- raspberry pi camera functionality
- webpage for manipulating the cube

## Other cool things I use in this project

This is a nice optimize solver I make calls to:
https://github.com/hkociemba/RubiksCube-TwophaseSolver

```
pip3 install kociemba
```

A nice javascript cube view I found useful:
https://cubing.github.io/AnimCubeJS/animcubejs.html#introduction

This color resolver totally saved me from a ton of work generating a cube from camera images:
https://github.com/dwalton76/rubiks-color-resolver

A nice web server I use for the webpage:
https://bottlepy.org/docs/dev/index.html
sudo pip3 install bottle

## Installation

### Entry Points and Links
If you decide to put the project somewhere else, adjust accordingly.

```
mkdir ~/rubik
cd ~/rubik

git clone git@github.com:mhirst1960/rubik-note.git

edit  ~/.bashrc and add the following line somewhere:

   PATH=~/bin:$PATH

mkdir ~/bin
cd ~/bin

ln -s ~/rubik/rubik-text-solver/robot/closegrippers.py
ln -s ~/rubik/rubik-text-solver/robot/cradle.py
ln -s ~/rubik/rubik-text-solver/webpage/cubesolverhttp.py
ln -s ~/rubik/rubik-text-solver/robot/getcubestate.py
ln -s ~/rubik/rubik-text-solver/robot/moverrobot.py
ln -s ~/rubik/rubik-text-solver/robot/opengrippers.py
ln -s ~/rubik-text-solver/tmwrubik.py
```

Install the optimized cube solver:
```
pip3 install kociemba
```

### Servos
Every servo is unique.  It requires trial and error to configure the robot gripper parameters for
exactly 0, 90, and 180 degree rotation.  It would be good to read through this long blog to understand
the servos: https://forum.arduino.cc/t/rubiks-cube-robot-solver/262557

As described in the blog I created a test jig out of wood to tune my 3D-printed grippers before mounting
on the actual robot stand.

Parameters are in this file:
rubik-text-solver/robot/CubeMover.py

You will need to customize these lines of code:

```
        self.kit.servo[self.rightWrist].set_pulse_width_range(400, 2600)
        self.kit.servo[self.leftWrist].set_pulse_width_range(400, 2600)
        self.left = Gripper(self.kit, self.leftPinch,  self.leftWrist,
                                81, 93, 150, #close, cradle, open
                                18, 98, 171)  #back, up, front
        self.right= Gripper(self.kit, self.rightPinch, self.rightWrist,
                                78, 90, 150, #close, cradle, open
                                170, 93, 15)  #back, up, front
```
### Your Customized Cube

You will need to edit rubik/tmwrubik.py to match the stickers you put on your cube.  These are the values
- TMW_CUBE_LABELS
- TMW_CUBE_GROUPS
- TMW_PEOPLE

#### Rubik's clock
Note: if you want to make a clock you can use the parameters found in this file as a starting point:
     rubik-text-solver/rubik-clock.py
     
The clock works fine in the simulation but is not very practical with the robot I'm using since it can typically
take 2 to 6 minutes to solve. Under 10 seconds would be ideal and this robot is a long way from that.
(TODO: investigate faster robots for a cool clock impementation.  Investigate adapting hkociemba/RubiksCube-TwophaseSolver
to optimize for solving only the front of the cube, not the whole cube.  We don't care about sticker values on any layer except the front.)
     
## Implementation

### Piece

The cornerstone of this implementation is the Piece class. A Piece stores two
pieces of information:

1. An integer `position` vector `(x, y, z)` where each component is one of the following values: -1, 0,
1
    - `(0, 0, 0)` is the center of the cube
    - the positive x-axis points to the right face
    - the positive y-axis points to the up face
    - the positive z-axis points to the front face

2. A `stickers` vector `(sx, sy, sz)`, giving the a tuple of (color,label,group,destination) of the sticker along each
axis. Null values are placeholders whenever that Piece has less than three sides. For
example, a Piece with `colors=('Orange', None, 'Red')` is an edge piece with an
`'Orange'` sticker facing the x-direction and a `'Red'` sticker facing the
z-direction. There is no sticker in the 'Y' direction.

This same piece may optionally have three labels. ('T', None, '-').  So the 'Orange'
would also be decorated with a 'T'.  I define the character '-' with special meaning
that there is no label decoration on this sticker.  In this example, the 'Red' sticker
would not have a label on it.

To simplify the problem, each Piece has a group.  All stickers on the Piece
must be declared in the same group.  Typically multiple pieces will be in a single group but this is not a requirement.
When solved, the letter is placed on the front side and is restricted to the position defined by its
group.  When solved, only one labelled sticker in a group will show up in the group. All other stickers within the same
group must be blank (defined as '-').

Compared to 'color', a more generic description of sticker direction is its future `destination` of where it will sit once solved.
A destination can be any one of these letters: `ULFRDB` as in
`up, left, front, right, and down`.  For a normal cube every destination corresponds directly to a color:
`OGWBYR` because solving results in all `orange` on the `up` face, all `green` on the `left` face, etc.
By removing this restriction of for instance `up = orange` the cube can be considered solved when the
message string is on the front, thus disregarding the actuall colors of the cube.


A Piece provides a method `Piece.rotate(matrix)`, which accepts a (90 degree)
rotation matrix. A matrix-vector multiplication is done to update the Piece's
`position` vector. Then we update the `colors` vector, by swapping exactly two
entries in the `colors` vector:

- For example, a corner Piece has three stickers of different colors. After a
  90 degree rotation of the Piece, one sticker remains facing down the same
  axis, while the other two stickers swap axes. This corresponds to swapping the
  positions of two entries in the Piece’s `colors` vector.
- For an edge or face piece, the argument is the same as above, although we may
  swap around one or more null entries.

### Sticker

The sticker class encapsulates a piece's tuple: color,label,group,destination.
Where there are between one and three stickers for every piece in the cube.

### Cube

The Cube class is built on top of the Piece class. The Cube stores a list of
Pieces and provides nice methods for flipping slices of the cube, as well as
methods for querying the current state. (I followed standard [Rubik's Cube
notation](http://ruwix.com/the-rubiks-cube/notation/))

Because the Piece class encapsulates all of the rotation logic, implementing
rotations in the Cube class is simple - just apply the appropriate
rotation matrix to all Pieces involved in the rotation. An example: To
implement `Cube.L()` - a clockwise rotation of the left face - do the
following:

1. Construct the appropriate [rotation matrix](
http://en.wikipedia.org/wiki/Rotation_matrix) for a 90 degree rotation in the
`x = -1` plane.
2. Select all Pieces satisfying `position.x == -1`.
3. Apply the rotation matrix to each of these Pieces.

To implement `Cube.X()` - a clockwise rotation of the entire cube around the
positive x-axis - just apply a rotation matrix to all Pieces stored in the
Cube.

### Solver

The solver implements the algorithm described
[here](http://peter.stillhq.com/jasmine/rubikscubesolution.html) and
[here](http://www.chessandpoker.com/rubiks-cube-solution.html). It is a
layer-by-layer solution. First the front-face (the `z = 1` plane) is solved,
then the middle layer (`z = 0`), and finally the back layer (`z = -1`). When
the solver is done, `Solver.moves` is a list representing the solution
sequence.

In this implementation, you can pass a short string to the solver to generate a new cube configuration.  It will solve the front
layer and return the origional `unsolved` cube.  Colors are unchanged but `destinations` are reassigned
to indicate where each sticker should migrate to once solved.

You can pass this newly generated cube to any of the various cube solvers that are available (including the built-in solver).
For efficiency I used the kociemba implementation to generate the actual moves used by my robot. 

### CubeOrder State Conversion

There does not seem to be any standard established in the cubing community to describe the state of a cube.  I used several different applications
for solving and displaying the cube. The class CubeOrder is very handy utility class for translating among applications.

### robot

The robot I built is based on a design by KAS https://forum.arduino.cc/t/rubiks-cube-robot-solver/262557 .  It uses only two grippers the hold the cube in place as it moves the pieces around.  The design was ideal for my application.  I felt it was important to put the focus on the cube, not so much on the solver.  This robot presents the cube to onlookers.  Whereas many of the other robot designs available seem to engulf the cube thus making it less accessible or 'friendly' to the audience.  I also decided to 3d-print the robot all in black for the same reason: to put the focus on the cube not the robot.  The down side of this robot is that, with only two grippers, it is very slow.  It is limited to moves only on the "down" and "back" sides of the cube.  So these are the legal moves: Y, Yi, Y2, Z, Zi, Z2, D, Di, D2, B, Bi, B2.  (This site has nice explanations of cube notation: https://ruwix.com/the-rubiks-cube/notation/).  It takes about 4-5 minutes to solve the cube.

The computer inside the base of the robot is a Raspberry Pi 4b computer.  There is also a pca9685 PWM circuit board to control the servo motors that grab and rotate the cube.

The 3d print files are downloaded from here:

https://www.thingiverse.com/thing:3826740
(Which is a remix from the original: https://www.thingiverse.com/thing:2800244)

### camera
This implements functionality to use the robot to rotate the cube to present all six sides to the raspberry pi
camera.  After all sticker colors are sampled, the values are passed to a pretty robust piece of software to assign
a color to every sticker.


### webpage

There is a simple webpage to display the cube, edit the cube, and initiate various commands:
1. open robot grippers
2. cradle grippers (to allow a person to place a cube ready to be solved or remove it)
3. stop all operation.  Abort whatever is going on right now.
4. input a message to solve.
5. solve it
6. You can import a cube state
7. You can edit any sticker in case software calculated it wrong.
8. You can save the cube state

The webpage is based on bottle webserver https://bottlepy.org/

Note: if you have this connected to a live robot, this webpage might be a little dangerous to access from a remote host as there are buttons to directly control the robot grippers.  If you plan to only run the webpage on a browser on your local raspberry pi. Consider
setting up a firewall.  I used port 18080.  (You can use any port you want, the standard is typically port 8080 or port 80).  So consider running this command on you raspberry pi when you are running the webpage to block other computers from accessing the webpage, adjusting the port that you are using:

iptables -A INPUT -p tcp --dport 18080 -j DROP

## Files
### ~/bin directory
To give you an idea of the important entry points to the software these are the symbolic links I have in my bin directory:

```
tmwrubik.py -> /home/pi/rubik/rubik-text-solver/tmwrubik.py

closegrippers.py -> /home/pi/rubik/rubik-text-solver/robot/closegrippers.py
cradle.py -> /home/pi/rubik/rubik-text-solver/robot/cradle.py
moverrobot.py -> /home/pi/rubik/rubik-text-solver/robot/moverrobot.py
opengrippers.py -> /home/pi/rubik/rubik-text-solver/robot/opengrippers.py

cubesolverhttp.py -> /home/pi/rubik/rubik-text-solver/webpage/cubesolverhttp.py
getcubestate.py -> /home/pi/rubik/rubik-text-solver/robot/getcubestate.py
```

See the installation section for commands to create these important links.

#### rubik-text-solver/tmwrubik.py
A primary entrypoint to the system.  This is called from the webpage discussed below.  It accepts a wide varienty of parameters including "--help":

```
python3 ./tmwrubik.py --help
usage: tmwrubik.py [-h] [--verbose] [--person PERSON] [--inputorder {xray,unfold,kociemba,camera}] [--infile INFILE] [--input INPUT]
                   [--updatestate] [--no-updatestate] [--output {xray,unfold,kociemba,robot,moves}]
                   [--outputdatatype {destinations,colors,frontstring,moves,None}] [--movenotation {singmaster,programmer}] [--robot]
                   [--no-robot] [--camera] [--no-camera] [--simulation]

optional arguments:
  -h, --help            show this help message and exit
  --verbose, -v         show debug messages -v, -vv, -vvv for more and more debug
  --person PERSON       initials for person to solve for
  --inputorder {xray,unfold,kociemba,camera}
                        Color input from camera or color string order: back=front, onfolded paper cube, or orbital kociemba
  --infile INFILE       File contains one line list of colors: OGYWBR and order depends on --inputorder: back=front, onfolded paper cube,
                        or orbital kociemba
  --input INPUT         values for input are: "camera", "file", or list of colors: OGYWBR and order depends on --inputorder: back=front,
                        onfolded paper cube, or orbital kociemba
  --updatestate         for persistance, update input file with current state when finished (default: --updatestate)
  --no-updatestate      Do not persist the state. Do not update input file. (default: --updatestate)
  --output {xray,unfold,kociemba,robot,moves}
                        robot solve, or print planned moves, or print destination order: back=front, onfolded paper cube, or orbital
                        kociemba
  --outputdatatype {destinations,colors,frontstring,moves,None}
                        how should we print output (No output = None)
  --movenotation {singmaster,programmer}
                        primmaster uses prime like X', programmer uses i like Xi
  --robot               Allow robot to move (default: --no-robot)
  --no-robot            Do not allow robot to move (default: --no-robot)
  --camera              Use the camera (default: --no-camera)
  --no-camera           Do not use the camera (default: --no-camera)
  --simulation          do not use the camera or robot. Generate webpage and update state file when done.
```

In this file you will find several parameters that need to be customized for a cube with different labels:

- TMW_CUBE_LABELS
- TMW_CUBE_GROUPS
- TMW_PEOPLE

(TODO: I need to rename tmwrubik.py to something generic and move the data to a config file or pass as parameter.  TMW are the initials for The Mad Wrapper.)

### rubik-text-solver/rfid directory
This directory can be ignored.  My first implementation included an RFID reader to scan RFID tags attached to gifts.  The code works
fine on it's own but it is unreliable -- probably a hardware issue.  With all the electronics in the base of my robot I suspect there
is interference between the robot servos and the SPI interface to the RC522.  Also, I needed to implement a webpage interface anyway
so, in the end, I went with the webpage instead of RFID.

### rubik-text-solver/robot directory
Python files in this directory control the robot and the camera.


#### rubik-text-solver/robot/opengrippers.py
A utility application to open the grippers.  Simply call from the command line and both grippers will open and drop the cube.
Call this if your cube gets jammed.

#### rubik-text-solver/robot/closegrippers.py
A utility application to close the grippers.  Simply call from the command line and the grippers will close.

#### rubik-text-solver/robot/cradle.py
A utility application to cradle the grippers.  Simply call from the command line and the grippers will partially close
to allow the user to insert or remove the cube from the grippers.

#### rubik-text-solver/robot/CubeMover.py
Class for moving the cube pieces.  See instalation notes for changes you need to make to this file for the servos you
are using.

#### rubik-text-solver/robot/Gripper.py
Small class used by CubeMover to encapsulate paramewters for one of the grippers.  Along with a few utility functions
used my CubeMover.

#### rubik-text-solver/robot/Lighting.py
Small class to control LED GPIO lighting.

#### rubik-text-solver/robot/getcubestate.py
application to take pictures of all sides of the cube to discover the current state of all stickers on  the cube.

You may need to customize these parameters for position depending on where your camera gets mounted in relation to the cube.
You can also experiment with camera resolution by adjusting these parameters.

```
    resolution = (640, 480)
    stickerSize=65
    stickerSize2= int(stickerSize * 0.5)
    stickerSpace=90

    #Sticker centers
    stickerX1 = 190
    stickerY1 = 95   

    #areas for white balance (white sticker placed on the gripper)
    wbX1 = 120
    wbY1 = 360
    wbX2 = 530
    wbY2 = 350
    wbWidth1 = 15
    wbHeight1 = 15
```

The oupput and an HTML page are generated based on these parmaeters:

```
HOME = "/home/pi/"
OUTFILE = HOME + "cubestate.txt"
HTMLDIR = HOME + "/cubeshower/"
```

A ton of raw images are saved here for debugging:

```
/home/pi/cubeimages/
```

Also the color resolver application generates HTML here that you can view from your browser:
```
/tmp/rubiks-color-resolver.html
```

(TODO: HOME should be a variable.  There is a python command to get that.  Also, maybe parse args so users can specify the directory for all the files.)

#### rubik-text-solver/robot/moverrobot.py

move the robot with a sequence of moves

```
moverrobot.py --help
usage: moverrobot.py [-h] [--verbose] [--moves MOVES] [--cradleafter]
                     [--simulation]

optional arguments:
  -h, --help     show this help message and exit
  --verbose, -v  show debug messages -v, -vv, -vvv for more and more debug
  --moves MOVES  list of moves for the robot to execute
  --cradleafter  After all moves are complete cradle the cube so users are
                 able to easily remove the cube.
  --simulation   do not use the camera or robot. Generate webpage and update
                 state file when done.
```

Here is a simple example thst moves the back 90 degrees then 90 degrees in the opposit direction to the origional state:

```
moverrobot.py --moves "B Bi"
```

#### rubik-text-solver/robot/servo.py
Test code.  Feel free to hack this file if you make modifications and need to do some debugging.
(TODO: I should rename to servotest.py or something)

### rubik-text-solver/rubik directory
Python files in this directory are used for generating custom cubes that are solved by putting a message on the front of the cube.
This also contains an algorithm to actually solve the cube and generate a sequence of moves to feed to the robot.  This algorithm
is simple and works fine but is not optimized.  I ended up using a different "third party" application to generate the actual robot moves.
The Kociemba approach generates a robot move sequence about half as long as the method implemented in the rubik directory.

### rubik-text-solver/tests directory
Various tests to test cube solver code in the 'rubik' directory. Mostly this is the origional untouched code implemented by pglass for
solving normal non-labeled cubes.  TODO: I should probably add more tests here to test the text solver functionality.

### rubik-text-solver/webpage directory
The code here implements a simple web page server using bottle framework.


