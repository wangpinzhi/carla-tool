import carla
import numpy as np
import os

from ActorManager import ActorUnit,ActorManager



class SensorUnit(ActorUnit):
    def __init__(self,  name_id: str, 
                        actor_id: int,
                        save_path:str) -> None:
        super().__init__(name_id, actor_id)
        self.savePath = save_path
        self.ex_matrix = None

    def save_data(self):
        pass

class CubemapCameraUnit:
    def __init__(self,  name_id: str, 
                        cube_cams: dict, 
                        save_path: str):
        self.nameId = name_id
        self.savePath = save_path
        self.revCounter = 0
        self.cube_cams = cube_cams
        self.ex_matrix = None
        self.timestamp:float = 0.0
        self.saveData:dict = {
            'front':None,
            'left':None,
            'right':None,
            'up':None,
            'down':None,
            'back':None,
        }

    def save_data(self, frame_id):
        np.savez(
            os.path.join(self.savePath,f'{self.nameId}_{frame_id}.npz'),
            front_data = self.saveData['front'],
            left_data = self.saveData['left'],
            right_data = self.saveData['right'],
            back_data = self.saveData['back'],
            up_data = self.saveData['up'],
            down_data = self.saveData['down'],
            ex_matrix = self.ex_matrix,
            timestamp = self.timestamp
        )
    # def cubemap_data_callback(  self,
    #                             cube_face:str,
    #                             s_data:carla.Image):
    #     data_array = np.frombuffer(s_data.raw_data, dtype=np.dtype("uint8"))
    #     data_array = np.reshape(data_array, (s_data.height, s_data.width, 4))
    #     data_array = data_array[:, :, :3]
    #     self.saveData[cube_face]=data_array
    #     print(self.nameId, cube_face)
    #     if cube_face == 'front':
    #         self.ex_matrix = np.array(s_data.transform.get_matrix())
    #         self.timestamp = s_data.timestamp

def cubemap_data_callback(  s_data:carla.Image,
                            unit:CubemapCameraUnit,
                            cube_face:str):
    data_array = np.frombuffer(s_data.raw_data, dtype=np.dtype("uint8"))
    data_array = np.reshape(data_array, (s_data.height, s_data.width, 4))
    data_array = data_array[:, :, :3]
    unit.saveData[cube_face]=data_array
    if cube_face == 'front':
        unit.ex_matrix = np.array(s_data.transform.get_matrix())
        unit.timestamp = s_data.timestamp

class SensorManager(ActorManager):

    def __init__(self, world: carla.World) -> None:
        super().__init__(world)
        self._CubemapCameraUnit_list:list[CubemapCameraUnit] = []
        self.__sensors = []

    def add_sensor_actor(self,  nameId:str,
                                blueprint:carla.ActorBlueprint,
                                type:str,
                                transform:carla.Transform, 
                                attach_actor,
                                save_path:str):
        
        os.makedirs(save_path,exist_ok=True)
        
        if type in ['CubemapRGB','CubemapDepth']:
            cube_cams = {}

            front_transform = transform
            actor = self._world.spawn_actor(blueprint, front_transform, attach_actor)
            cube_cams['front'] = actor.id

            left_transform = transform
            left_transform.rotation.yaw -= 90
            actor = self._world.spawn_actor(blueprint, left_transform, attach_actor)
            cube_cams['left'] = actor.id

            right_transform = transform
            right_transform.rotation.yaw += 90
            actor = self._world.spawn_actor(blueprint, right_transform, attach_actor)
            cube_cams['right'] = actor.id

            back_transform = transform
            back_transform.rotation.yaw += 180
            actor = self._world.spawn_actor(blueprint, back_transform, attach_actor)
            cube_cams['back'] = actor.id

            up_transform = transform
            up_transform.rotation.pitch += 90
            actor =  self._world.spawn_actor(blueprint, up_transform, attach_actor)
            cube_cams['up'] = actor.id

            down_transform = transform
            down_transform.rotation.pitch -= 90
            actor = self._world.spawn_actor(blueprint, down_transform, attach_actor)
            cube_cams['down'] = actor.id

            cm_cam_unit = CubemapCameraUnit(nameId,cube_cams,save_path)
            self._CubemapCameraUnit_list.append(cm_cam_unit)

    def set_sensors_listen(self):
        for cubesensor_unit in self._CubemapCameraUnit_list:
            for cube_face in ['front','left','right','back','up','down']:
                sensor = self._world.get_actor(cubesensor_unit.cube_cams[cube_face])
                # sensor.listen(lambda data, cube_face=cube_face:cubesensor_unit.cubemap_data_callback(cube_face, data))
                sensor.listen(lambda data, unit=cubesensor_unit, cube_face=cube_face:cubemap_data_callback(unit, cube_face, data))
                self.__sensors.append(sensor)

    def save_sensors_data(self, frameId:int):
        for cubesensor_unit in self._CubemapCameraUnit_list:
            cubesensor_unit.save_data(frameId)

    def get_sensor_nums(self) -> int:
        return len(self._CubemapCameraUnit_list)

    def destroy_all_actors(self) -> int:
        destroy_nums = 0
        # destroy cubeactor
        for cubesensor_unit in self._CubemapCameraUnit_list:
            for cube_face in ['front','left','right','back','up','down']:
                actor = self._world.get_actor(cubesensor_unit.cube_cams[cube_face])
                actor.stop()
                print(actor.destroy())
            destroy_nums += 1
        return destroy_nums