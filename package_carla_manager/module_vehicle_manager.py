import random
import carla
import numpy as np
import gc

__all__ = [
    'instance_var_vehicle_manager'
]

GLOBAL_CONSTANT_DRIVE_TYPE_STATIC = 0
GLOBAL_CONSTANT_DRIVE_TYPE_AUTOPILOT = 1
GLOBAL_CONSTANT_DRIVE_TYPE_FILE_CONTROL_STEER = 2
GLOBAL_CONSTANT_DRIVE_TYPE_FILE_CONTROL_ALL = 3


class ClassVehicleUnit(object):

    def __init__(self,
                 parameter_role_name: str,
                 parameter_actor: carla.Vehicle,
                 parameter_ctrl_type: int,
                 parameter_ctrl_array: np.ndarray = None,
                 parameter_constant_velocity: carla.Vector3D = None) -> None:
        self.__local_val_role_name = parameter_role_name
        self.__local_val_actor = parameter_actor
        self.__local_val_ctrl_type = parameter_ctrl_type
        self.__local_val_ctrl_array = parameter_ctrl_array
        self.__local_val_ctrl_counter = 0
        self.__local_val_constant_velocity = parameter_constant_velocity

    def function_get_role_name(self):
        return self.__local_val_role_name

    def function_get_actor(self):
        return self.__local_val_actor

    def _function_get_ctrl(self) -> carla.VehicleControl:
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
        constraints = [GLOBAL_CONSTANT_DRIVE_TYPE_FILE_CONTROL_STEER,
                       GLOBAL_CONSTANT_DRIVE_TYPE_FILE_CONTROL_ALL]
        if self.__local_val_ctrl_type in constraints:  # Only affect steer
            local_current_ctrl.throttle = float(self.__local_val_ctrl_array[self.__local_val_ctrl_counter][0])
            local_current_ctrl.steer = float(self.__local_val_ctrl_array[self.__local_val_ctrl_counter][1])
            local_current_ctrl.brake = float(self.__local_val_ctrl_array[self.__local_val_ctrl_counter][2])
            local_current_ctrl.hand_brake = bool(self.__local_val_ctrl_array[self.__local_val_ctrl_counter][3])
            local_current_ctrl.reverse = bool(self.__local_val_ctrl_array[self.__local_val_ctrl_counter][4])
            local_current_ctrl.manual_gear_shift = bool(self.__local_val_ctrl_array[self.__local_val_ctrl_counter][5])
            local_current_ctrl.gear = int(self.__local_val_ctrl_array[self.__local_val_ctrl_counter][6])

        # flush the counter
        self.__local_val_ctrl_counter = self.__local_val_ctrl_counter + 1

        # if file control ends, change type to static.
        if self.__local_val_ctrl_counter >= len(self.__local_val_ctrl_array):
            self.__local_val_ctrl_type = GLOBAL_CONSTANT_DRIVE_TYPE_STATIC

        return local_current_ctrl

    def function_destroy(self):
        local_val_command_batch = []
        local_val_command_destroy = carla.command.DestroyActor
        local_val_command_batch.append(local_val_command_destroy(self.__local_val_actor))
        self.__local_val_role_name = None
        self.__local_val_actor = None
        self.__local_val_ctrl_type = ''
        self.__local_val_ctrl_array = None
        self.__local_val_ctrl_counter = 0
        self.__local_val_constant_velocity = None
        return local_val_command_batch

    def function_init_state(self):
        """
        This function starts vehicles which drive type is autopilot.

        :return: carla.command batch
        """

        local_val_command_batch = []
        local_val_command_set_autopilot = carla.command.SetAutopilot

        if self.__local_val_ctrl_type == GLOBAL_CONSTANT_DRIVE_TYPE_AUTOPILOT:
            local_val_command_batch.append(local_val_command_set_autopilot(self.__local_val_actor, True))
        elif self.__local_val_ctrl_type == GLOBAL_CONSTANT_DRIVE_TYPE_FILE_CONTROL_STEER:
            self.__local_val_actor.enable_constant_velocity(self.__local_val_constant_velocity)

        return local_val_command_batch

    def function_flush_state(self):
        """
        This function flush vehicles which drive type is file control.

        :return: carla.command batch
        """
        local_val_command_batch = []
        local_val_command_apply_control = carla.command.ApplyVehicleControl
        if self.__local_val_ctrl_type == GLOBAL_CONSTANT_DRIVE_TYPE_STATIC:
            self.__local_val_actor.enable_constant_velocity(carla.Vector3D(0.0, 0.0, 0.0))
        elif self.__local_val_ctrl_type == GLOBAL_CONSTANT_DRIVE_TYPE_FILE_CONTROL_STEER:
            local_val_command_batch.append(local_val_command_apply_control(self.__local_val_actor,
                                                                           self._function_get_ctrl()))
        elif self.__local_val_ctrl_type == GLOBAL_CONSTANT_DRIVE_TYPE_FILE_CONTROL_ALL:
            local_val_command_batch.append(local_val_command_apply_control(self.__local_val_actor,
                                                                           self._function_get_ctrl()))
        return local_val_command_batch


class ClassVehicleManager(object):

    def __init__(self) -> None:
        self.__local_val_vehicles = []

    @staticmethod
    def _function_get_spawn(parameter_vehicle_config: dict,
                            parameter_blueprint_library: carla.BlueprintLibrary,
                            parameter_spawn_points: list):
        """
        This function gets the blueprint and spawn point from the config json (obtained from 'scene_config.json')

        :param parameter_blueprint_library: Obtained by 'carla.World.get_blueprint_library()'
        :param parameter_vehicle_config: json string for vehicle setting
        :param parameter_spawn_points: Obtained by 'carla.World.get_spawn_points()'
        :return: blueprint and spawn point
        """
        # get spawn point
        local_val_spawn_point = carla.Transform()
        if 'spawn_point' in parameter_vehicle_config.keys():
            local_val_spawn_point.location = carla.Location(x=parameter_vehicle_config['spawn_point'][0],
                                                            y=parameter_vehicle_config['spawn_point'][1],
                                                            z=parameter_vehicle_config['spawn_point'][2])
            local_val_spawn_point.rotation = carla.Rotation(pitch=parameter_vehicle_config['spawn_point'][3],
                                                            yaw=parameter_vehicle_config['spawn_point'][4],
                                                            roll=parameter_vehicle_config['spawn_point'][5])
        elif 'spawn_point_idx' in parameter_vehicle_config.keys():
            local_val_spawn_point = parameter_spawn_points[parameter_vehicle_config['spawn_point_idx']]
        else:
            # random chose a spawn point
            local_val_spawn_point = random.choice(parameter_spawn_points)

        # get blueprint
        local_blueprint_library = parameter_blueprint_library
        if 'blueprint' in parameter_vehicle_config.keys():
            local_blueprint_library = parameter_blueprint_library.filter(parameter_vehicle_config['blueprint'])
        local_blueprint = random.choice(local_blueprint_library)

        # set hero car, sensors will attach to it.
        if parameter_vehicle_config['role_name'] == 'hero':
            local_blueprint.set_attribute('role_name', 'hero')

        return local_blueprint, local_val_spawn_point

    def function_spawn_vehicles(self,
                                parameter_client: carla.Client,
                                parameter_vehicle_configs: list):
        """
        This function must be used when sync mode is off.

        :param parameter_client: client to spawn vehicles
        :param parameter_vehicle_configs:  vehicle configs obtained from 'scene_config.json'
        :return:
        """
        local_val_blueprint_library = parameter_client.get_world().get_blueprint_library()
        local_val_spawn_points = parameter_client.get_world().get_map().get_spawn_points()

        for local_val_vehicle_config in parameter_vehicle_configs:
            local_val_blueprint, local_val_spawn_point = self._function_get_spawn(local_val_vehicle_config,
                                                                                  local_val_blueprint_library,
                                                                                  local_val_spawn_points)
            local_val_actor = parameter_client.get_world().spawn_actor(local_val_blueprint,
                                                                       local_val_spawn_point)

            # get control array and constant velocity
            local_val_control_array = None
            local_val_constant_velocity = None
            if local_val_vehicle_config['drive_type'] == GLOBAL_CONSTANT_DRIVE_TYPE_FILE_CONTROL_STEER:
                local_val_control_array = np.load(local_val_vehicle_config['drive_file'])
                local_val_constant_velocity = carla.Vector3D(x=local_val_vehicle_config['constant_velocity'][0],
                                                             y=local_val_vehicle_config['constant_velocity'][1],
                                                             z=local_val_vehicle_config['constant_velocity'][2])
            elif local_val_vehicle_config['drive_type'] == GLOBAL_CONSTANT_DRIVE_TYPE_FILE_CONTROL_ALL:
                local_val_control_array = np.load(local_val_vehicle_config['drive_file'])

            # add to vehicle list
            self.__local_val_vehicles.append(ClassVehicleUnit(local_val_actor.attributes['role_name'],
                                                              local_val_actor,
                                                              local_val_vehicle_config['drive_type'],
                                                              local_val_control_array,
                                                              local_val_constant_velocity))
        print('\033[1;32m[Spawn Vehicles]:\033[0m', '    ',
              f'\033[1;33m{len(self.__local_val_vehicles)}/{len(parameter_vehicle_configs)}\033[0m')

    def function_destroy_vehicles(self,
                                  parameter_client: carla.Client):
        """
        This function must be used when sync mode is off.

        :param parameter_client: client to start vehicles
        :return:
        """
        local_val_command_batch = []
        for local_val_vehicle_unit in self.__local_val_vehicles:
            local_val_command_batch.extend(local_val_vehicle_unit.function_destroy())
        parameter_client.apply_batch_sync(local_val_command_batch, False)
        del self.__local_val_vehicles[:]
        gc.collect()

    def function_init_vehicles(self,
                               parameter_client: carla.Client):
        """
         This function must be used when sync mode is on.

        :param parameter_client: client to start vehicles
        :return:
        """
        local_val_command_batch = []
        for local_val_vehicle_unit in self.__local_val_vehicles:
            local_val_command_batch.extend(local_val_vehicle_unit.function_init_state())
        for local_val_response in parameter_client.apply_batch_sync(local_val_command_batch, False):
            if local_val_response.error:
                print(local_val_response.error)

    def function_flush_vehicles(self,
                                parameter_client: carla.Client):
        """

        This function must be used when sync mode is on.
        This function will tick the world automatically.

        :return:
        """
        local_val_command_batch = []
        for local_val_vehicle_unit in self.__local_val_vehicles:
            local_val_command_batch.extend(local_val_vehicle_unit.function_flush_state())
        for local_val_response in parameter_client.apply_batch_sync(local_val_command_batch, False):
            if local_val_response.error:
                print(local_val_response.error)

    def function_get_vehicle_by_role_name(self,
                                          parameter_role_name: str):
        for local_val_vehicle in self.__local_val_vehicles:
            if local_val_vehicle.function_get_role_name() == parameter_role_name:
                return local_val_vehicle.function_get_actor()
        print(f"Not Found RoleName {parameter_role_name} Actor")


instance_var_vehicle_manager = ClassVehicleManager()
