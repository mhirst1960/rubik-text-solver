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

pip3 install kociemba


A nice javascript cube view I found useful:
https://cubing.github.io/AnimCubeJS/animcubejs.html#introduction

This color resolver totally saved me from a ton of work generating a cube from camera images:
https://github.com/dwalton76/rubiks-color-resolver

A nice web server I use for the webpage:
https://bottlepy.org/docs/dev/index.html
sudo pip3 install bottle

## Installation


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
camera.  After all sticker colors are sampled, the values are provided to a pretty robust piece of software to assign
a stick color to every sticker.


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
