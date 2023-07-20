import carla
import numpy as np
import random

GLOBAL_CONSTANT_SPECTATOR_CTRL_TYPE_STATIC = 0
GLOBAL_CONSTANT_SPECTATOR_CTRL_TYPE_RANDOM = 1
GLOBAL_CONSTANT_SPECTATOR_CTRL_TYPE_ORDER = 2

class ClassSpectatorManager(object):
    def __init__(self) -> None:
        super(ClassSpectatorManager,self).__init__()
        self.__local_val_spectator = None
        self.__local_val_constant_velocity = None
        self.__local_val_ctrl_type = 0
        self.local_val_counter = 0

    def function_register_spectator(self,
                                    parameter_world: carla.World):
        self.__local_val_spectator = parameter_world.get_spectator()

    def function_init_spectator(self,
                               parameter_config: dict):
        self.__local_val_ctrl_type = parameter_config['control_type']
        if self.__local_val_ctrl_type == GLOBAL_CONSTANT_SPECTATOR_CTRL_TYPE_RANDOM:
            self.local_raw_data = np.load(parameter_config['random_path'])
            self.local_val_random_idx = self.local_raw_data['random_idx']
            self.local_val_random_rot = self.local_raw_data['random_rot']
            self.local_val_random_pos = self.local_raw_data['random_pos']
            self.local_val_data = self.local_raw_data['data']
            self.local_val_total_idx_num = self.local_raw_data['random_idx'].size(0)

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
    def function_flush_state(self):
        if self.__local_val_ctrl_type == GLOBAL_CONSTANT_SPECTATOR_CTRL_TYPE_RANDOM:
            local_val_random_idx = int(self.local_val_random_idx[self.local_val_counter][0])
            local_val_random_loc = carla.Location(x=float(self.local_val_data[local_val_random_idx][0]/100)+float(self.local_val_random_pos[self.local_val_counter][0]),
                                                  y=float(self.local_val_data[local_val_random_idx][1]/100)+float(self.local_val_random_pos[self.local_val_counter][1]),
                                                  z=float(self.local_val_data[local_val_random_idx][2]/100)+float(self.local_val_random_pos[self.local_val_counter][2]))
            local_val_random_rot = carla.Rotation(pitch=float(self.local_val_data[local_val_random_idx][3])+float(self.local_val_random_rot[self.local_val_counter][0]),
                                                  yaw=float(self.local_val_data[local_val_random_idx][4])+float(self.local_val_random_rot[self.local_val_counter][1]),
                                                  roll=float(self.local_val_data[local_val_random_idx][5])+float(self.local_val_random_rot[self.local_val_counter][2]))

            self.__local_val_spectator.set_transform(carla.Transform(local_val_random_loc, local_val_random_rot))
            self.local_val_counter = (self.local_val_counter+1)%(self.local_val_total_idx_num)

    def function_get_spectator(self):
        return self.__local_val_spectator
    
    def function_reset_counter(self):
        self.local_val_counter = 0

instance_var_spectator_manager = ClassSpectatorManager()