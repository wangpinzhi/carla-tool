import time

import carla
import random
from tqdm import tqdm

# read configs from json file.
from .module_file_reader import function_get_map_json, function_get_weather_json
from .module_file_reader import function_get_vehicle_json_list, function_get_sensor_json_list
from .module_file_reader import function_get_save_json

# according to the json file, set the world.
from .module_map_control import function_set_map
from .module_weather_control import function_set_weather

# import global vehicle manager to control vehicles
from .module_vehicle_manager import instance_var_vehicle_manager as global_var_vehicle_manager

# import global sensor manager to control sensors
from .module_sensor_manager import instance_var_sensor_manager as global_val_sensor_manager


class ClassSimulatorManager(object):

    def __init__(self,
                 parameter_host: str,
                 parameter_port: int,
                 parameter_path_scene: str,
                 parameter_path_sensor: str,
                 parameter_path_save: str = './output',
                 parameter_random_seed: int = 136):
        """
        :param parameter_path_save: path to save data (Default: './output')
        :param parameter_host: client bind host. (Default: 127.0.0.0.1)
        :param parameter_port: client bind port. (Default: 2000)
        :param parameter_path_scene: path to scene_config.json
        :param parameter_path_sensor: path to sensor_config.json
        """
        self.local_val_save_path = parameter_path_save
        self.local_val_world_settings = None
        self.local_val_origin_world_settings = None
        random.seed(parameter_random_seed)
        self.local_val_host = parameter_host
        self.local_val_port = parameter_port
        self.local_val_scene_config_path = parameter_path_scene
        self.local_val_sensor_config_path = parameter_path_sensor
        print('\033[1;32m[Scene Config Path]:\033[0m', '    ',
              f'\033[1;33m{self.local_val_scene_config_path}\033[0m')
        print('\033[1;32m[Sensor Config Path]:\033[0m', '    ',
              f'\033[1;33m{self.local_val_sensor_config_path}\033[0m')
        print('\033[1;32m[Save Data Path]:\033[0m', '    ',
              f'\033[1;33m{self.local_val_save_path}\033[0m')

    def function_init_world(self) -> None:
        """
        This function set the initial state of the world.
        All actors stop.

        :return:
        """
        # get client
        self.local_val_client = carla.Client(self.local_val_host, self.local_val_port)
        self.local_val_client.set_timeout(5.0)  # 20s timeout

        # set map
        local_val_map = function_get_map_json(self.local_val_scene_config_path)
        function_set_map(self.local_val_client, local_val_map)

        # set weather
        local_val_weather = function_get_weather_json(self.local_val_scene_config_path)
        function_set_weather(self.local_val_client.get_world(), local_val_weather)

    def _function_sim_one_step(self,
                               parameter_sensor_config):
        local_val_counter = 0
        try:
            
            # get save setting
            local_val_save_config = function_get_save_json(self.local_val_sensor_config_path)
            local_val_frame_start = local_val_save_config['frame_start']
            local_val_frame_end = local_val_save_config['frame_end']
            local_val_frame_num = local_val_frame_end - local_val_frame_start + 1

            # spawn vehicles
            local_val_vehicle_configs = function_get_vehicle_json_list(self.local_val_scene_config_path)
            global_var_vehicle_manager.function_spawn_vehicles(self.local_val_client,
                                                               local_val_vehicle_configs)
            # spawn sensors
            global_val_sensor_manager.function_spawn_sensors(local_val_frame_num,
                                                             self.local_val_client,
                                                             parameter_sensor_config)
            global_val_sensor_manager.function_set_save_root_path(self.local_val_save_path)

            # get current world setting and save it
            self.local_val_origin_world_settings = self.local_val_client.get_world().get_settings()
            self.local_val_world_settings = self.local_val_client.get_world().get_settings()

            # We set CARLA syncronous mode
            self.local_val_world_settings.fixed_delta_seconds = 0.05
            self.local_val_world_settings.synchronous_mode = True
            self.local_val_client.get_world().apply_settings(self.local_val_world_settings)

            # skip frames that do not need saving
            while local_val_counter < local_val_frame_start:
                print('\033[1;35m Sikp Unused Frames:\033[0m')
                global_var_vehicle_manager.function_flush_vehicles(self.local_val_client) # flush
                self.local_val_client.get_world().tick()
                local_val_counter += 1

            global_var_vehicle_manager.function_init_vehicles(self.local_val_client)  # init vehicles state
            global_val_sensor_manager.function_start_sensors()
            global_val_sensor_manager.function_listen_sensors()

            with tqdm(total=local_val_frame_num, unit='frame', leave=True, colour='blue') as pbar:
                pbar.set_description(f'Processing')
                while True:
                    if local_val_frame_start > local_val_frame_end:
                        break
                    # flush vehicle state
                    global_var_vehicle_manager.function_flush_vehicles(self.local_val_client)
                    self.local_val_client.get_world().tick()  # tick the world
                    global_val_sensor_manager.function_sync_sensors()  # check sensor data receive ready or not
                    local_val_frame_start += 1
                    pbar.update(1)
        finally:
            # stop all sensors
            # global_val_sensor_manager.function_stop_sensors()
            # recover world settings
            self.local_val_client.get_world().apply_settings(self.local_val_origin_world_settings)
            # destroy all sensors
            global_val_sensor_manager.function_destroy_sensors(self.local_val_client)
            # destroy all vehicles
            global_var_vehicle_manager.function_destroy_vehicles(self.local_val_client)
            # time.sleep(3.0)

    def function_start_sim_collect(self,
                                   parameter_split_num: int = 3):
        
        local_val_sensor_configs = function_get_sensor_json_list(self.local_val_sensor_config_path)
        print('\033[1;32m[Total Sensors Num]:\033[0m', '    ',
              f'\033[1;33m{len(local_val_sensor_configs)}\033[0m')
        print('\033[1;32m[Split Sensors Num]:\033[0m', '    ',
              f'\033[1;33m{parameter_split_num}\033[0m')
        local_val_item_nums = int(len(local_val_sensor_configs) / parameter_split_num) + 1
        for i in range(parameter_split_num):
            print('\033[1;35m------------------------------------------------------------------------------------------------\033[0m')
            self.local_val_client = carla.Client(self.local_val_host, self.local_val_port)# get client
            local_val_part = local_val_sensor_configs[
                             i * local_val_item_nums:i * local_val_item_nums + local_val_item_nums]
            if len(local_val_part) > 0:
                # get sensors
                local_val_part_sensors = [item['name_id'] for item in local_val_part]
                print(f'\033[1;32m[Part {i+1}]:\033[0m', '    ', f'\033[1;33m{str(local_val_part_sensors)}\033[0m')
                self._function_sim_one_step(local_val_part)
                time.sleep(2.0)


if __name__ == '__main__':
    local_val_test_client = ClassSimulatorManager(
        parameter_host='127.0.0.1',
        parameter_port=2000,
        parameter_path_scene='output/huawei_demo_parking/configs/scene_config.json',
        parameter_path_sensor='output/huawei_demo_parking/configs/sensor_config.json'
    )
    local_val_test_client.function_init_world()
    local_val_test_client.function_start_sim_collect()
