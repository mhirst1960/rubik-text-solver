from rubik.Color import Color
from rubik.CubePrintStyles import CubePrintStyles
class Sticker:
    

    def __init__(self, color, label, group, destination=None):
        self.color = color
        self.label = label
        self.group = group

        self.printStyle = CubePrintStyles.Colored
        
        #if (destination == None):
        #    self.setDefaultDestination(color) # direction based on color
        #else:
        #    self.destination = destination # direction this points to when solved
            
        self.destination = destination
        
    # yellow on left, white on front, green on right, blue on back, orange on up, red on down side
    destinations= {'Y':'L', 'W':'F', 'G':'R', 'B':'B', 'O':'U', 'R':'D', None:'?'}

    def setPrintStyle(self, printStyle):
        assert isinstance(printStyle, CubePrintStyles)
        self.printStyle = printStyle

    def setDefaultDestination(self, color=None):
        if color == None:
            color = self.color
        self.destination = self.destinations[color]

    colorLookup = {'W':Color.B_White, 'B':Color.B_Blue, 'Y':Color.B_Yellow, 'G':Color.B_Green, 'O':Color.B_Orange, 'R':Color.B_Red}
    destinadtionColorLookup = {'F':Color.B_White, 'U':Color.B_Blue, 'L':Color.B_Yellow, 'D':Color.B_Green, 'B':Color.B_Orange, 'R':Color.B_Red,
                               '-':Color.B_DarkGray, '?':Color.B_DarkGray, None:Color.B_DarkGray}

    def colorize (self, color, dictionary=None):
        
        if dictionary == None:
            dictionary = self.colorLookup
            
        if color in dictionary:
            return dictionary[color]
        else:
            return ""
        
    def destinationStr(self):
        if self.destination == None:
            return '?'
        else:
            return self.destination
        
    def labelOrBlank(self):
        if self.label in ['?', '-']:
            return ' '
        else:
            return self.label
        
    def stringDestinationColored(self):
        colorModify=self.colorize(self.destination, self.destinadtionColorLookup) # color based on destination
        return f"{colorModify}{Color.F_Black}{self.labelOrBlank()} {Color.B_Default}{Color.F_Default}"

    def stringDestinationGroupColored(self):
        colorModify=self.colorize(self.destination, self.destinadtionColorLookup) # color based on destination
        return f"{colorModify}{Color.F_Black}{self.labelOrBlank()}{self.group}{Color.B_Default}{Color.F_Default}"

    def stringColored(self):
        colorModify=self.colorize(self.color)  # actual colors
        return f"{colorModify}{Color.F_Black}{self.labelOrBlank()} {Color.B_Default}{Color.F_Default}"

    def stringLabelColor(self):
        if self.color >= 'A' and self.color <= 'Z':
            color = self.color.lower()
        else:
            color = self.color

        return f"{self.label}{color}" # 1st character = label, second character = color

    def stringUncolored(self):
        return f"{self.label} " # no colors

    def __str__(self):
        
        if self.printStyle == CubePrintStyles.Uncolored:
            return self.stringUncolored()
        elif self.printStyle == CubePrintStyles.Colored:
            return self.stringColored()
        elif self.printStyle == CubePrintStyles.LabelColor:
            return self.stringLabelColor()
        elif self.printStyle == CubePrintStyles.DestinationColored:
            return self.stringDestinationColored()
        elif self.printStyle == CubePrintStyles.DestinationGroupColored:
            return self.stringDestinationGroupColored()
        else:
            return self.stringLabelColor()
    
        #colorModify = ""
        colorModify=self.colorize(self.color)  # actual colors
        #colorModify=self.colorize(self.destination, self.destinadtionColorLookup) # color based on destination
        #return f"{colorModify}{self.destination}{Color.F_Default}"
        #return f"{colorModify}{Color.F_Black}{self.label} {Color.B_Default}{Color.F_Default}"
        #return f"{colorModify}({self.label}{self.group}){Color.F_Default}"
        #return f"({self.label}{self.destinationStr()}{self.group})"
        #return f"{colorModify}{Color.F_Black}({self.label}{self.destinationStr()}{self.group}){Color.B_Default}{Color.F_Default}"
        return f"{colorModify}{Color.F_Black}{self.labelOrBlank()} {Color.B_Default}{Color.F_Default}"
        #return f"{self.labelOrBlank()}" # no colors
   