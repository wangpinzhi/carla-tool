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
                 parameter_ctrl_array: np.ndarray = None) -> None:
        self.__local_val_name_id = parameter_name_id
        self.__local_val_actor = parameter_actor
        self.__local_val_ctrl_type = parameter_ctrl_type
        self.__local_val_ctrl_array = parameter_ctrl_array
        self.__local_val_ctrl_counter = 0

    def function_get_state(self) -> carla.VehicleControl:
        """
        When drive type is file_control, this function returns the carla.VehicleControl needed to be applied.
        And auto flush the counter.

        :return: VehicleControl needed to be applied by client.
        """

        # check drive type, it must be FILE_CONTROL_STEER or FILE_CONTROL_ALL.
        assert self.__local_val_ctrl_type in [GLOBAL_CONSTANT_DRIVE_TYPE_FILE_CONTROL_STEER,
                                              GLOBAL_CONSTANT_DRIVE_TYPE_FILE_CONTROL_ALL]

        # check ctrl array
        assert self.__local_val_ctrl_counter < len(self.__local_val_ctrl_array)

        # flush the control
        local_current_ctrl = self.__local_val_actor.get_control()
        if self.__local_val_ctrl_type == GLOBAL_CONSTANT_DRIVE_TYPE_FILE_CONTROL_STEER:  # Only affect steer
            local_current_ctrl.steer = float(self.__local_val_ctrl_array[self.__local_val_ctrl_counter][1])
        elif self.__local_val_ctrl_type == GLOBAL_CONSTANT_DRIVE_TYPE_FILE_CONTROL_ALL:  # Affect all control
            local_current_ctrl.throttle = float(self.__local_val_ctrl_array[self.__local_val_ctrl_counter][0])
            local_current_ctrl.steer = float(self.__local_val_ctrl_array[self.__local_val_ctrl_counter][1])
            local_current_ctrl.brake = float(self.__local_val_ctrl_array[self.__local_val_ctrl_counter][2])
            local_current_ctrl.hand_brake = bool(self.__local_val_ctrl_array[self.__local_val_ctrl_counter][3])
            local_current_ctrl.reverse = bool(self.__local_val_ctrl_array[self.__local_val_ctrl_counter][4])
            local_current_ctrl.manual_gear_shift = bool(self.__local_val_ctrl_array[self.__local_val_ctrl_counter][5])
            local_current_ctrl.gear = int(self.__local_val_ctrl_array[self.__local_val_ctrl_counter][6])

        # flush the counter
        self.__local_val_ctrl_counter = self.__local_val_ctrl_counter + 1

        # check counter is ended. If true, change drive type to static.
        if self.__local_val_ctrl_counter >= len(self.__local_val_ctrl_array):
            self.__local_val_ctrl_type = GLOBAL_CONSTANT_DRIVE_TYPE_STATIC

        return local_current_ctrl

class ClassVehicleManager(object):

    def __init__(self) -> None:
        self.__local_val_vehicles = []

    def _function_get_spawn_point
    def function_spawn_vehicles(self,
                                parameter_client: carla.Client,
                                parameter_vehicle_configs: list):
        for local_val_vehicle_config in parameter_vehicle_configs:

