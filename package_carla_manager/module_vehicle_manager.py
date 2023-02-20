import carla
import numpy as np

GLOBAL_CONSTANT_DRIVE_TYPE_STATIC = 0
GLOBAL_CONSTANT_DRIVE_TYPE_AUTOPILOT = 1
GLOBAL_CONSTANT_DRIVE_TYPE_FILE_CONTROL_STEER = 2
GLOBAL_CONSTANT_DRIVE_TYPE_FILE_CONTROL_ALL = 3


class ClassVehicleUnit(object):

    def __init__(self,
                 parameter_name_id: str,
                 parameter_actor: carla.Vehicle,
                 parameter_ctrl_type: int,
                 parameter_ctrl_array: np.ndarray) -> None:
        self.__local_val_name_id = parameter_name_id
        self.__local_val_actor = parameter_actor
        self.__local_val_ctrl_type = parameter_ctrl_type
        self.__local_val_ctrl_array = parameter_ctrl_array
        self.__local_val_ctrl_counter = 0

    def function_next_state(self):
        """
        According to the drive type, update the state of the vehicle.

        :return:
        """
        if self.__local_val_ctrl_type == GLOBAL_CONSTANT_DRIVE_TYPE_STATIC:
            pass
        elif self.__local_val_ctrl_type == GLOBAL_CONSTANT_DRIVE_TYPE_AUTOPILOT:
            pass
        elif self.__local_val_ctrl_type == GLOBAL_CONSTANT_DRIVE_TYPE_FILE_CONTROL_STEER:

