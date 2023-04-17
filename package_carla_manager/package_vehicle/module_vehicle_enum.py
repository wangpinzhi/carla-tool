from enum import IntEnum
from enum import unique

@unique
class ENumDriveType(IntEnum):
    STATIC = 0
    AUTOPILOT = 1
    FILE_CONTROL_STEER  = 2
    FILE_CONTROL_ALL = 3
    FILE_CONTROL_TRANSFORM = 4
    