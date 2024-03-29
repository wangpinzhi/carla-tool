import time
import gc
import carla
import random
from tqdm import tqdm
import sys

# read configs from json file.
from .module_file_reader import function_get_map_json, function_get_weather_json
from .module_file_reader import function_get_vehicle_json_list, function_get_sensor_json_list
from .module_file_reader import function_get_save_json, function_get_sepctator_json

# according to the json file, set the world.
from .module_map_control import function_set_map
from .module_weather_control import function_set_weather

# import global vehicle manager to control vehicles
from .module_vehicle_manager import instance_var_vehicle_manager as global_var_vehicle_manager

# import global sensor manager to control sensors
from .module_sensor_manager import instance_var_sensor_manager as global_val_sensor_manager

# import global sensor manager to control spectator
from .module_spectator_manager import instance_var_spectator_manager as global_val_spectator_manager

from .module_signal_control import function_get_global_signal

class ClassSimulatorManager(object):

    def __init__(self,
                 parameter_host: str,
                 parameter_port: int,
                 parameter_path_scene: str,
                 parameter_path_sensor: str,
                 parameter_path_save: str = './output',
                 parameter_random_seed: int = 136,
                 parameter_client_timeout: float = 20.0):
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
        self.local_val_client = carla.Client(self.local_val_host, self.local_val_port)# get client
        self.local_val_client.set_timeout(parameter_client_timeout)  # Default 20s timeout
        self.local_val_scene_config_path = parameter_path_scene
        self.local_val_sensor_config_path = parameter_path_sensor
        global_val_spectator_manager.function_register_spectator(self.local_val_client.get_world())

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
        self.local_val_client.set_timeout(60.0)  # 20s timeout

        # set map
        local_val_map_config = function_get_map_json(self.local_val_scene_config_path)
        function_set_map(self.local_val_client, local_val_map_config)

        # set weather
        local_val_weather_config = function_get_weather_json(self.local_val_scene_config_path)
        function_set_weather(self.local_val_client.get_world(), local_val_weather_config)

        # set spectator
        local_val_spectator_config = function_get_sepctator_json(self.local_val_scene_config_path)
        global_val_spectator_manager.function_init_spectator(local_val_spectator_config)


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

            global_var_vehicle_manager.function_init_vehicles(self.local_val_client)  # init vehicles state

            # skip frames that do not need saving
            print('\033[1;35m Sikpping Unused Frames\033[0m')
            while local_val_counter < local_val_frame_start:
                global_var_vehicle_manager.function_flush_vehicles(self.local_val_client) # flush
                self.local_val_client.get_world().tick()
                local_val_counter += 1
            
            global_val_sensor_manager.function_start_sensors()
            global_val_sensor_manager.function_listen_sensors()

            with tqdm(total=local_val_frame_num, unit='frame', leave=True, colour='blue') as pbar:
                pbar.set_description(f'Processing')
                while (not function_get_global_signal()) and (local_val_frame_start <= local_val_frame_end):
                    # flush vehicle state
                    global_var_vehicle_manager.function_flush_vehicles(self.local_val_client)
                    self.local_val_client.get_world().tick()  # tick the world
                    if global_val_sensor_manager.function_sync_sensors():  # check sensor data receive ready or not
                        local_val_frame_start += 1
                        pbar.update(1)
                    else:
                        raise Exception('funciton_sync_sensors error')
        finally:
            
            #  # ctrl c capture
            # if function_get_global_signal():
            #     print('\033[1;31m[Receive Exit Signal] Reloading World, Please Wait!\033[0m')
            #     self.local_val_client.get_world().apply_settings(self.local_val_origin_world_settings)
            #     self.local_val_client.reload_world(reset_settings=False)
            #     print('\033[1;31m[Receive Exit Signal] Exit Main Process Bye!\033[0m')
            #     sys.exit()

            # destroy all sensors
            
            # self.local_val_client.get_world().tick()
            # print('\033[1;35m[Stop All Sensors]\033[0m')
            global_val_sensor_manager.function_stop_sensors()
            global_val_sensor_manager.function_destroy_sensors(self.local_val_client)
            self.local_val_client.get_world().tick()
            global_val_sensor_manager.function_clean_sensors()
            print('\033[1;35m[Destroy All Sensors]\033[0m')

            # destroy all vehicles
            global_var_vehicle_manager.function_destroy_vehicles(self.local_val_client)
            self.local_val_client.get_world().tick()
            print('\033[1;35m[Destroy All Vehicles]\033[0m')

            # recover world settings
            self.local_val_client.get_world().apply_settings(self.local_val_origin_world_settings)

            if function_get_global_signal():
                print('\033[1;31m[Receive Exit Signal] Exit Main Process Bye!\033[0m')
                sys.exit()

            

    def function_start_sim_collect(self,
                                   parameter_split_num: int = 3):
        
        local_val_sensor_configs = function_get_sensor_json_list(self.local_val_sensor_config_path)
        
        print('\033[1;32m[Total Sensors Num]:\033[0m', '    ',
              f'\033[1;33m{len(local_val_sensor_configs)}\033[0m')
        print('\033[1;32m[Split Sensors Num]:\033[0m', '    ',
              f'\033[1;33m{parameter_split_num}\033[0m')
        
        local_val_item_nums = int(len(local_val_sensor_configs) / parameter_split_num) + 1

        print('\033[1;35m------------------------------------COLLECT START------------------------------------------------\033[0m')
        for i in range(parameter_split_num):
            local_val_part = local_val_sensor_configs[
                             i * local_val_item_nums:i * local_val_item_nums + local_val_item_nums]
            if len(local_val_part) > 0:
                # get sensors
                local_val_part_sensors = [item['name_id'] for item in local_val_part]
                print(f'\033[1;32m[Part {i+1}]:\033[0m', '    ', f'\033[1;33m{str(local_val_part_sensors)}\033[0m')
                self._function_sim_one_step(local_val_part)
                gc.collect()
                time.sleep(3.0)
        print('\033[1;35m------------------------------------COLLECT END-------------------------------------------------\033[0m')



if __name__ == '__main__':
    local_val_test_client = ClassSimulatorManager(
        parameter_host='127.0.0.1',
        parameter_port=2000,
        parameter_path_scene='output/huawei_demo_parking/configs/scene_config.json',
        parameter_path_sensor='output/huawei_demo_parking/configs/sensor_config.json'
    )
    local_val_test_client.function_init_world()
    local_val_test_client.function_start_sim_collect()
