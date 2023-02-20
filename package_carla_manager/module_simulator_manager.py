import carla

from module_file_reader import function_get_map_json, function_get_weather_json
from module_map_control import function_set_map
from module_weather_control import function_set_weather


class ClassSimulatorManager(object):

    def __init__(self,
                 parameter_host: str,
                 parameter_port: int,
                 parameter_path_scene: str,
                 parameter_path_sensor: str):
        """

        :param parameter_host: client bind host. (Default: 127.0.0.0.1)
        :param parameter_port: client bind port. (Default: 2000)
        :param parameter_path_scene: path to scene_config.json
        :param parameter_path_sensor: path to sensor_config.json
        """

        self.local_val_client = carla.Client(parameter_host, parameter_port)
        self.local_val_client.set_timeout(20.0)  # 20s timeout
        self.local_val_scene_config_path = parameter_path_scene
        self.local_val_sensor_config_path = parameter_path_sensor

    def function_init_world(self) -> None:
        """
        This function set the initial state of the world.
        All actors stop.

        :return:
        """

        # set map
        local_val_map = function_get_map_json(self.local_val_scene_config_path)
        function_set_map(self.local_val_client, local_val_map)

        # set weather
        local_val_weather = function_get_weather_json(self.local_val_scene_config_path)
        function_set_weather(self.local_val_client.get_world(), local_val_weather)

        # spawn vehicles



if __name__ == '__main__':
    local_val_test_client = ClassSimulatorManager(
        parameter_host='127.0.0.1',
        parameter_port=2000,
        parameter_path_scene='output/huawei_demo_parking/configs/scene_config.json',
        parameter_path_sensor='output/huawei_demo_parking/configs/sensor_config.json'
    )

    local_val_test_client.function_init_world()
