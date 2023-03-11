import carla

GLOBAL_CONSTANT_SPECTATOR_CTRL_TYPE_STATIC = 0
GLOBAL_CONSTANT_SPECTATOR_CTRL_TYPE_CONSTANT_VELOCITY = 1

class ClassSpectatorManager(object):
    def __init__(self) -> None:
        super(ClassSpectatorManager,self).__init__()
        self.__local_val_spectator = None
        self.__local_val_constant_velocity = None
        self.__local_val_ctrl_type = 0

    def function_register_spectator(self,
                                    parameter_world: carla.World):
        self.__local_val_spectator = parameter_world.get_spectator()

    def function_init_spectator(self,
                               parameter_config: dict):
        self.__local_val_ctrl_type = parameter_config['control_type']
        if 'transform' in parameter_config.keys():
            local_val_transform = carla.Transform(carla.Location(parameter_config['transform'][0],
                                                                parameter_config['transform'][1],
                                                                parameter_config['transform'][2]),
                                                carla.Rotation(parameter_config['transform'][3],
                                                                parameter_config['transform'][4],
                                                                parameter_config['transform'][5]))
            self.__local_val_spectator.set_transform(local_val_transform)
        if 'constant_velocity' in parameter_config.keys():
            self.__local_val_constant_velocity = carla.Vector3D(parameter_config['constant_velocity'][0],
                                                                parameter_config['constant_velocity'][1],
                                                                parameter_config['constant_velocity'][2])

    def function_get_spectator(self):
        return self.__local_val_spectator

instance_var_spectator_manager = ClassSpectatorManager()