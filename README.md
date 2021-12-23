![PyPI](https://img.shields.io/pypi/v/rubik-cube)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/rubik-cube)

# Overview

Provide a short string and this program will find the letters and solve such that those letters end up on the front of the cube.
You can also use it to solve the full cube in the normal fashon based on the colors.

I implemented two examples:
1. a solver for the initialis of everyone in my family
2. a rubik-clock which shows the time of day on the cube as a 12-hour clock with am/pm

Everything is written using Python 3.

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

## Installation


## Implementation

### Piece

The cornerstone of this implementation is the Piece class. A Piece stores two
pieces of information:

1. An integer `position` vector `(x, y, z)` where each component is in {-1, 0,
1}:
    - `(0, 0, 0)` is the center of the cube
    - the positive x-axis points to the right face
    - the positive y-axis points to the up face
    - the positive z-axis points to the front face

2. A `stickers` vector `(sx, sy, sz)`, giving the a tuple of (color,label,group,destination) of the sticker along each
axis. Null values are place whenever that Piece has less than three sides. For
example, a Piece with `colors=('Orange', None, 'Red')` is an edge piece with an
`'Orange'` sticker facing the x-direction and a `'Red'` sticker facing the
z-direction. The Piece doesn't know or care which direction along the x-axis
the `'Orange'` sticker is facing, just that it is facing in the x-direction and
not the y- or z- directions.

This same piece may optionally have three labels. ('T', None, '-').  So the 'Orange'
would also be decorated with a 'T'.  I define the character '-' with special meaning
that there is no label decoration on this sticker.  In this example, the 'Red' sticker
would not have a label on it.

To simplify the problem, each Piece will have a group.  And all stickers on the Piece
will be defined as beingin the same group.  Typically multiple pieces will be in a single group.
When solved, the letter is placed on the front side but is restricted to the position defined by its
group.  When solved, all other sitckers within the same group will be '-' or blank.

The `destination` is a rather more generic way of describing the direction of
a sitcker in solved position.  A destination can be any one of these letters: `ULFRDB` for
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

### Cube

The Cube class is built on top of the Piece class. The Cube stores a list of
Pieces and provides nice methods for flipping slices of the cube, as well as
methods for querying the current state. (I followed standard [Rubik's Cube
notation](http://ruwix.com/the-rubiks-cube/notation/))

Because the Piece class encapsulates all of the rotation logic, implementing
rotations in the Cube class is dead simple - just apply the appropriate
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

You can pass a short string to the solver.  And it will solve the front layer only.
No need tocontinue solving the entire cube.  After the front is solved, destinations are
assigned to the resulting cube in case you want to export the cube state to be handled
byt a more capable solver that will calculate the minimum number of moves to get to
the final solved state.

### state conversion
For import/export, there is a class that handles some cube state conversions.  You can call some of these
conversions to make it easier to call external programs like a mor efficient solver, display a javascript
or html webpage, validate colors from camera input.

### robot
I am using a robot with only two grippers so moves are restricted to "down" and "back" (and related moves).
So I have some conversions to generate only those legal moves.

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