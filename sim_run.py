from package_carla_manager import ClassSimulatorManager

if __name__ == '__main__':
    # local_val_simulator_manager = ClassSimulatorManager(
    #     parameter_host='127.0.0.1',
    #     parameter_port=2000,
    #     parameter_path_sensor=r'output\huawei_demo_parking\configs\sensor_config.json',
    #     parameter_path_scene=r'output\huawei_demo_parking\configs\scene_config.json',
    #     parameter_path_save=r'output\huawei_demo_parking\raw_data',
    # )
    local_val_simulator_manager = ClassSimulatorManager(
        parameter_host='127.0.0.1',
        parameter_port=2000,
        parameter_path_sensor=r'output\huawei_fake\configs\sensor_config.json',
        parameter_path_scene=r'output\huawei_fake\configs\scene_config.json',
        parameter_path_save=r'output\huawei_fake\raw_data',
    )
    local_val_simulator_manager.function_init_world()
    local_val_simulator_manager.function_start_sim_collect(parameter_split_num=4)
