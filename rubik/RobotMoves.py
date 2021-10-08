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
        'D':['D'],
        'Di':['Di'],
        'D2':['D2'],
        'B':['B'],
        'Bi':['Bi'],
        'B2':['B2'],
        'F':['Z2', 'B', 'Z2'],
        'Fi':['Z2', 'Bi', 'Z2'],
        'F2':['Z2', 'B2', 'Z2'],
        'U':['Z2', 'D', 'Z2'],
        'Ui':['Z2', 'Di', 'Z2'],
        'U2':['Z2', 'D2', 'Z2'],
        'L':['Z', 'D', 'Zi'],
        'Li':['Z', 'Di', 'Zi'],
        'L2':['Z', 'D2', 'Zi'],
        'R':['Zi', 'B', 'Z'],
        'Ri':['Zi', 'Bi', 'Z'],
        'R2':['Zi', 'B2', 'Z'],
        
        'M':['Bi', 'Y2', 'B', 'Z', 'Y'],
        'Mi':['B', 'Y2', 'Bi', 'Zi', 'Y'],
        'M2':['B2', 'Y2', 'B2', 'Yi', 'Z2'],
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
        
        # TODO optimize for minimal robot moves
        return newMoves