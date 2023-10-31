from package_carla_manager import ClassSimulatorManager
import random
import numpy
random.seed(111)
numpy.random.seed(111)

if __name__ == '__main__':
    
    name = 'random_objects_8'
    local_val_simulator_manager = ClassSimulatorManager(
        parameter_host='127.0.0.1',
        parameter_port=2000,
        parameter_path_sensor=rf'output\{name}\configs\sensor_config.json',
        parameter_path_scene=rf'output\{name}\configs\scene_config.json',
        parameter_path_save=rf'H:RandomObjects\raw_data\{name}',
    )
    split_num = 4

    # name = 'shipyard'
    # local_val_simulator_manager = ClassSimulatorManager(
    #     parameter_host='127.0.0.1',
    #     parameter_port=2000,
    #     parameter_path_sensor=rf'output\{name}\configs\sensor_config.json',
    #     parameter_path_scene=rf'output\{name}\configs\scene_config.json',
    #     parameter_path_save=rf'H:RandomObjects\raw_data\{name}',
    # )
    # split_num = 1
    
    local_val_simulator_manager.function_init_world()
    local_val_simulator_manager.function_start_sim_collect(parameter_split_num=split_num)
