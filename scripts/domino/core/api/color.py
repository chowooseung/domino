# maya
from pymel import core as pm

dt = pm.datatypes


# maya color index
MAYA_OVERRIDE_COLOR = {
    0: [48, 48, 48],
    1: [0, 0, 0],
    2: [13, 13, 13],
    3: [81, 81, 81],
    4: [84, 0, 5],
    5: [0, 0, 30],
    6: [0, 0, 255],
    7: [0, 16, 2],
    8: [5, 0, 14],
    9: [147, 0, 147],
    10: [65, 17, 8],
    11: [13, 4, 3],
    12: [81, 5, 0],
    13: [255, 0, 0],
    14: [0, 255, 0],
    15: [0, 13, 81],
    16: [255, 255, 255],
    17: [255, 255, 0],
    18: [32, 183, 255],
    19: [14, 255, 93],
    20: [255, 111, 111],
    21: [198, 105, 49],
    22: [255, 255, 32],
    23: [0, 81, 23],
    24: [91, 37, 8],
    25: [87, 91, 8],
    26: [35, 91, 8],
    27: [8, 91, 28],
    28: [8, 91, 91],
    29: [8, 35, 91],
    30: [41, 8, 91],
    31: [91, 8, 37]
}

RED = dt.Color.red
GREEN = dt.Color.green
BLUE = dt.Color.blue