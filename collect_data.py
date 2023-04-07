from package_carla_manager import ClassSimulatorManager

if __name__ == '__main__':
    name = 'huawei_parking15_cmp'
    local_val_simulator_manager = ClassSimulatorManager(
        parameter_host='127.0.0.1',
        parameter_port=2000,
        parameter_path_sensor=rf'output\{name}\configs\sensor_config.json',
        parameter_path_scene=rf'output\{name}\configs\scene_config.json',
        parameter_path_save=rf'output\{name}\raw_data',
    )
    local_val_simulator_manager.function_init_world()
    local_val_simulator_manager.function_start_sim_collect()
