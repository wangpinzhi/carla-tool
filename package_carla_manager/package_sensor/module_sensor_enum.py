from enum import IntEnum, unique

@unique
class ENumSensorType(IntEnum):
    CUBE = 0
    NORMAL = 1

@unique
class ENumAttachType(IntEnum):
     SPECTATOR = 0
     VEHICLE = 1
     WALKER = 2