from rubik.optimize import optimize_moves
from rubik.optimize import apply_do_undo_optimization
from rubik.optimize import apply_repeat_three_optimization
from rubik.optimize import apply_2_optimization
class RobotMoves:
    
    """
    Robot only has two grippers underneath the cube.
    Unable to grab top of middle layers, we need to convert all movements to Y, Z, D, and B
    """
    
    GrippersYZLegal =[
        'Y', 'Yi', 'Y2',
        'Z', 'Zi', 'Z2',
        'B', 'Bi', 'B2',
        'D', 'Di', 'D2'
        ]
    
    GrippersYZ = {
        '':[],
        
        'Y':['Y'],
        'Yi':['Yi'],
        'Y2':['Y2'],
        'Z':['Z'],
        'Zi':['Zi'],
        'Z2':['Z2'],
        'X':['Y', 'Z', 'Yi'],
        'Xi':['Y', 'Zi', 'Yi'],
        'X2':['Y', 'Z2', 'Yi'],

        'D':['D'],
        'Di':['Di'],
        'D2':['D2'],
        'B':['B'],
        'Bi':['Bi'],
        'B2':['B2'],
        'F':['Y2', 'B', 'Y2'],
        'Fi':['Y2', 'Bi', 'Y2'],
        'F2':['Y2', 'B2', 'Y2'],
        'U':['Z2', 'D', 'Z2'],
        'Ui':['Z2', 'Di', 'Z2'],
        'U2':['Z2', 'D2', 'Z2'],
        'L':['Y', 'B', 'Yi'],
        'Li':['Y', 'Bi', 'Yi'],
        'L2':['Y', 'B2', 'Yi'],
        'R':['Yi', 'B', 'Y'],
        'Ri':['Yi', 'Bi', 'Y'],
        'R2':['Yi', 'B2', 'Y'],
        
        'M':['Y', 'Bi', 'Y2', 'B', 'Z', 'Y'],
        'Mi':['Y', 'B', 'Y2', 'Bi', 'Zi', 'Y'],
        'M2':['Y', 'B2', 'Y2', 'B2', 'Yi', 'Z2'],
        'E':['Di', 'Z2', 'D', 'Z2', 'Yi'],
        'Ei':['D', 'Z2', 'Di', 'Z2', 'Y'],
        'E2':['D2', 'Z2', 'D2', 'Y2', 'Z2'],
        'S':['B', 'Y2', 'Bi', 'Y2', 'Z'],
        'Si':['Bi', 'Y2', 'B', 'Y2', 'Zi'],
        'S2':['B2', 'Y2', 'B2', 'Y2', 'Z2']          
    }
    
    def __init__(self, gripperStyle="YZ"):
        if gripperStyle == "YZ":
            self.legalMoves = self.GrippersYZLegal
            self.converter = self.GrippersYZ
        else:
            assert False
        
    def convert(self, moves):
        """
        convert list of moves to list of moves compatible with your robot
        """
        newMoves = list()
        
        for move in moves:
            move = move.replace('3', 'i')
            move = move.replace('1', '')
            if move in self.converter:
                nm = self.converter[move]
                for newMove in nm:
                    assert any(newMove in m for m in self.legalMoves)
                newMoves += nm
            else:
                print ("ERROR unsupported move: ", move)
                newMoves.append('ERROR')
                newMoves.append(move)
                break
        
        return newMoves

    def optimize (self, moves):
        
        
        newMoves = self.convert(moves)
        
        #optMoves = optimize_moves(newMoves)
        apply_repeat_three_optimization(newMoves)
        apply_do_undo_optimization(newMoves)
        apply_2_optimization(newMoves)
        # TODO optimize for minimal robot moves
        return newMoves