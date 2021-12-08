class CubeOrder:
    
    """""
    There does not seem to be one single standard for cube representation among various solvers.
    Different programs will receive an input string expecting a different order.
    This class allows us to convert from one order to another order allowing stitching among solvers.
    
    The names of the facelet positions of the cube
                  |************|
                  |*U1**U2**U3*|
                  |************|
                  |*U4**U5**U6*|
                  |************|
                  |*U7**U8**U9*|
                  |************|
     |************|************|************|************|
     |*L1**L2**L3*|*F1**F2**F3*|*R1**R2**R3*|*B1**B2**B3*|
     |************|************|************|************|
     |*L4**L5**L6*|*F4**F5**F6*|*R4**R5**R6*|*B4**B5**B6*|
     |************|************|************|************|
     |*L7**L8**L9*|*F7**F8**F9*|*R7**R8**R9*|*B7**B8**B9*|
     |************|************|************|************|
                  |************|
                  |*D1**D2**D3*|
                  |************|
                  |*D4**D5**D6*|
                  |************|
                  |*D7**D8**D9*|
                  |************|
    
    Note that the bottom (B1-B9) is considered viewed from the bottom.
    So B1 is adjacent to R3.  And B3 is adjacent to L1. Etc.
    
    """
    
    U1 = "U1"
    U2 = "U2"
    U3 = "U3"
    U4 = "U4"
    U5 = "U5"
    U6 = "U6"
    U7 = "U7"
    U8 = "U8"
    U9 = "U9"
    
    L1 = "L1"
    L2 = "L2"
    L3 = "L3"
    L4 = "L4"
    L5 = "L5"
    L6 = "L6"
    L7 = "L7"
    L8 = "L8"
    L9 = "L9"
    
    F1 = "F1"
    F2 = "F2"
    F3 = "F3"
    F4 = "F4"
    F5 = "F5"
    F6 = "F6"
    F7 = "F7"
    F8 = "F8"
    F9 = "F9"

    R1 = "R1"
    R2 = "R2"
    R3 = "R3"
    R4 = "R4"
    R5 = "R5"
    R6 = "R6"
    R7 = "R7"
    R8 = "R8"
    R9 = "R9"

    B1 = "B1"
    B2 = "B2"
    B3 = "B3"
    B4 = "B4"
    B5 = "B5"
    B6 = "B6"
    B7 = "B7"
    B8 = "B8"
    B9 = "B9"
    
    D1 = "D1"
    D2 = "D2"
    D3 = "D3"
    D4 = "D4"
    D5 = "D5"
    D6 = "D6"
    D7 = "D7"
    D8 = "D8"
    D9 = "D9"

    # kociemba defines INPUT/OUPUT for his cube in an order that keeps the stickers of every face together
    # U1-U9, R1-R9, F1-F9, D1-D9, L1-L9, B1-B9
    # Note: B7 is adjacent to R9
    STICKER_GROUPS_URFDLB = [
    U1, U2, U3,
    U4, U5, U6,
    U7, U8, U9,
    
    R1, R2, R3,
    R4, R5, R6,
    R7, R8, R9,
    
    F1, F2, F3,
    F4, F5, F6,
    F7, F8, F9,
    
    D1, D2, D3,
    D4, D5, D6,
    D7, D8, D9,
    
    L1, L2, L3,
    L4, L5, L6,
    L7, L8, L9,
    
    B1, B2, B3,
    B4, B5, B6,
    B7, B8, B9
    ]

    KOCIEMBA_ORDER = STICKER_GROUPS_URFDLB
    
    # Other solvers represent INPUT/OUTPUT by unfolding the cube then simply reading order:
    # in top to bottom rows read left to right 
    
    # Unfold back means we think of the Back as if viewed from below, looking up
    # as if unfolding a paper box and laying it down flat
    # The Back pieces retain their order as we rotate the entire cube around Z
    # Note: B7 is adjacent to R9
    SLICE_UNFOLD_BACK = [
                     U1, U2, U3,
                     U4, U5, U6,
                     U7, U8, U9,
        L1, L2, L3,  F1, F2, F3,  R1, R2, R3,  B1, B2, B3,
        L4, L5, L6,  F4, F5, F6,  R4, R5, R6,  B4, B5, B6,
        L7, L8, L9,  F7, F8, F9,  R7, R8, R9,  B7, B8, B9,
                     D1, D2, D3,
                     D4, D5, D6,
                     D7, D8, D9
    ]

    # Xray slices means we think of the Back as if viewed through the front
    # Note: B7 is adjacent to R9
    SLICE_XRAYBACK = [
                     U1, U2, U3,
                     U4, U5, U6,
                     U7, U8, U9,
        L1, L2, L3,  F1, F2, F3,  R1, R2, R3,  B3, B2, B1,
        L4, L5, L6,  F4, F5, F6,  R4, R5, R6,  B6, B5, B4,
        L7, L8, L9,  F7, F8, F9,  R7, R8, R9,  B9, B8, B7,
                     D1, D2, D3,
                     D4, D5, D6,
                     D7, D8, D9
    ]

    def convert (self, cubeString, fromType, toType):
        convertedList = [None]*54
        
        for i, cubeChar in enumerate(cubeString):
            sticker = fromType[i]
            j = toType.index(sticker)
            convertedList[j] = cubeChar

        assert None not in convertedList
        
        convertString = "".join(convertedList)
        
        return convertString
    