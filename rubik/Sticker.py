from rubik.Color import Color


class Sticker:
    def __init__(self, color, label, group, destination=None):
        self.color = color
        self.label = label
        self.group = group

        if (destination == None):
            self.setDefaultDestination(color) # direction based on color
        else:
            self.destination = destination # direction this points to when solved

    # yellow on left, white on front, green on right, blue on back, orange on up, red on down side
    destinations= {'Y':'L', 'W':'F', 'G':'R', 'B':'B', 'O':'U', 'R':'D'}

    def setDefaultDestination(self, color):
            self.destination = self.destinations[color]

    colorLookup = {'W':Color.F_White, 'B':Color.F_Blue, 'Y':Color.F_Yellow, 'G':Color.F_Green, 'O':Color.F_Orange, 'R':Color.F_Red}

    def __str__(self):
        colorModify=self.colorLookup[self.color]
        #return f"{colorModify}{self.destination}{Color.F_Default}"
        return f"{colorModify}{self.label}{Color.F_Default}"
        #return f"{colorModify}({self.label}{self.group}){Color.F_Default}"
        #return f"{colorModify}({self.label}{self.destination}{self.group}){Color.F_Default}"
   