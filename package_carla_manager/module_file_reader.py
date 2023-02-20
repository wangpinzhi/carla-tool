import json


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
    :return: list of vehicle json.
    """

    with open(parameter_file_path) as f:
        local_val_vehicles = json.load(f)['vehicles']

    return local_val_vehicles
