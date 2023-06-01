from enum import IntEnum, unique

@unique
class EnumCamModel(IntEnum):
    PINHOLE = 0
    FISHEYE = 1
    ERP = 2
    OCAM = 3

@unique
class EnumTargetType(IntEnum):
     DEPTH = 0
     RGB = 1 
