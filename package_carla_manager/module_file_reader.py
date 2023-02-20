import json


def function_get_map_json(parameter_file_path: str) -> dict:
    """
    This function gets map_json which is needed by 'function_set_map()' from 'scene_configs.json'.

    :param parameter_file_path: path to scene_configs.json
    :return: map_json
    """

    with open(parameter_file_path) as f:
        local_val_map_json = json.load(f)['map']

    return local_val_map_json


def function_get_weather_json(parameter_file_path: str) -> dict:
    """
    This function gets map_json which is needed by 'function_set_weather()' from 'scene_configs.json'.

    :param parameter_file_path: path to scene_configs.json
    :return: weather_json
    """

    with open(parameter_file_path) as f:
        local_val_weather_json = json.load(f)['weather']

    return local_val_weather_json
