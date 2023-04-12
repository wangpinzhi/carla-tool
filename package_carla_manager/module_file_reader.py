import json
import os


def function_get_map_json(parameter_file_path: str) -> dict:
    """
    This function gets map_json which is needed by 'function_set_map()' from 'scene_config.json'.

    :param parameter_file_path: path to scene_configs.json
    :return: map_json
    """

    with open(parameter_file_path) as f:
        local_val_map = json.load(f)['map']

    return local_val_map


def function_get_weather_json(parameter_file_path: str) -> dict:
    """
    This function gets map_json which is needed by 'function_set_weather()' from 'scene_config.json'.

    :param parameter_file_path: path to scene_configs.json
    :return: weather_json
    """

    with open(parameter_file_path) as f:
        local_val_weather = json.load(f)['weather']

    return local_val_weather


def function_get_vehicle_json_list(parameter_file_path: str) -> list:
    """
    This function gets list of vehicle setting json from 'scene_config.json'.
    ClassVehicleManager uses these jsons to spawn vehicles and set their state.

    :param parameter_file_path: path to scene_configs.json
    :return: list of vehicle dict.
    """
    with open(parameter_file_path) as f:
        local_val_vehicles = json.load(f)['vehicles']
        # convert rel path to abs path
        for local_val_vehicle in local_val_vehicles:
            if 'drive_file' in local_val_vehicle.keys():
                local_val_vehicle['drive_file'] = os.path.join(os.path.dirname(parameter_file_path),
                                                               local_val_vehicle['drive_file'])
    return local_val_vehicles

def function_get_sepctator_json(parameter_file_path: str) -> dict:
    """
    This function get spectator config json from 'scene_config.json'.

    :param parameter_file_path: path to scene_configs.json
    :return: spectator config dict.
    """
    with open(parameter_file_path) as f:
        local_val_spectator_config = json.load(f)['spectator']
    return local_val_spectator_config

def function_get_sensor_json_list(parameter_file_path: str) -> list:
    """
    This function gets list of sensor setting json from 'sensor_config.json'.
    ClassVehicleManager uses these jsons to spawn sensors and set their state.

    :param parameter_file_path: path to sensor_config.json
    :return: list of sensor dict.
    """
    with open(parameter_file_path) as f:
        local_val_sensor = json.load(f)['sensors']
    return local_val_sensor


def function_get_save_json(parameter_file_path: str) -> dict:
    """
    This function gets the save setting(format: dict).

    :param parameter_file_path: path to 'sensor_config.json'
    :return: save setting dict.
    """
    with open(parameter_file_path) as f:
        local_val_save_setting = json.load(f)['save_setting']
    return local_val_save_setting

