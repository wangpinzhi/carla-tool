from package_carla_manager import ClassSimulatorManager
import random
import numpy
random.seed(111)
numpy.random.seed(111)

if __name__ == '__main__':
    
    name = 'omnitest'
    local_val_simulator_manager = ClassSimulatorManager(
        parameter_host='127.0.0.1',
        parameter_port=2000,
        parameter_path_sensor=rf'output\{name}\configs\sensor_config.json',
        parameter_path_scene=rf'output\{name}\configs\scene_config.json',
        parameter_path_save=rf'output\{name}\raw_data',
    )
    split_num = 2

    # name = 'rail_test'
    # number = '35'
    # local_val_simulator_manager = ClassSimulatorManager(
    #     parameter_host='127.0.0.1',
    #     parameter_port=2000,
    #     parameter_path_sensor=rf'output\{name}\configs\sensor_config.json',
    #     parameter_path_scene=rf'output\{name}\configs\scene_config.json',
    #     parameter_path_save=rf'output\{name}\raw_data\{number}',
    # )
    # split_num = 5

    # 帅江海
    # name = 'indoor_room'
    # local_val_simulator_manager = ClassSimulatorManager(
    #     parameter_host='127.0.0.1',
    #     parameter_port=2000,
    #     parameter_path_sensor=rf'output\{name}\configs\sensor_mono_config.json',
    #     parameter_path_scene=rf'output\{name}\configs\scene_config.json',
    #     parameter_path_save=rf'output\{name}\raw_data\indoor_room_6',
    # )

    # name = 'indoor_4fisheye_gym'
    # local_val_simulator_manager = ClassSimulatorManager(
    #     parameter_host='127.0.0.1',
    #     parameter_port=2000,
    #     parameter_path_sensor=rf'output\{name}\configs\sensor_config.json',
    #     parameter_path_scene=rf'output\{name}\configs\scene_config.json',
    #     parameter_path_save=rf'output\{name}\raw_data\parking180',
    # )
    split_num = 1
    
    local_val_simulator_manager.function_init_world()
    local_val_simulator_manager.function_start_sim_collect(parameter_split_num=split_num)
