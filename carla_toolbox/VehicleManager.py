import carla
import numpy as np

class VehicleUnit:
    def __init__(self,  name_id:str,
                        actor_id:int,
                        control_type:str='Static', 
                        control_file_path:str=None) -> None:
        self.nameId = name_id
        self.actorId = actor_id
        self.ctrlCounter = 0
        self.ctrlType = control_type
        if self.ctrlType == 'File':
            self.control_matrix = np.load(control_file_path)
            self.maxCounter = len(self.control_matrix) - 1
    
    def get_VehicleControl(self, auto_flush=True) -> carla.VehicleControl:
        control = carla.VehicleControl(
            float(self.control_matrix[self.ctrlCounter][0]),
            float(self.control_matrix[self.ctrlCounter][1]),
            float(self.control_matrix[self.ctrlCounter][2]),
            bool(self.control_matrix[self.ctrlCounter][3]),
            bool(self.control_matrix[self.ctrlCounter][4]),
            bool(self.control_matrix[self.ctrlCounter][5]),
            int(self.control_matrix[self.ctrlCounter][6]),
        )
        if auto_flush:
            self.ctrlCounter += 1
        return control


        


class VehicleManager:
    def __init__(self, world:carla.World) -> None:
        self._world = world
        self._vehicleUnit_list : list[VehicleUnit] = []
    
    def add_vehicle_actor(self, nameId:str,
                                blueprint:carla.ActorBlueprint, 
                                transform:carla.Transform, 
                                ctrl_type:str='Static', 
                                ctrl_file:str=None):

        vehicle_actor = self._world.spawn_actor(blueprint, transform)
        vehicle_unit = VehicleUnit(nameId, vehicle_actor.id, ctrl_type, ctrl_file)
        self._vehicleUnit_list.append(vehicle_unit)
    
    def get_actor_by_actorId(self, actorId:int):
        for vehicle_unit in self._vehicleUnit_list:
            if actorId == vehicle_unit.actorId:
                return self._world.get_actor(vehicle_unit.actorId)
        print(f'Not found actorID:{actorId} actor')

    def get_actor_by_nameId(self, nameId:str):
        for vehicle_unit in self._vehicleUnit_list:
            if nameId == vehicle_unit.nameId:
                return self.get_actor_by_actorId(vehicle_unit.actorId)
        print(f'Not found nameID:{nameId} actor')

    def enable_autopilot(self):
        for vehicle_unit in self._vehicleUnit_list:
            if vehicle_unit.ctrlType=='Autopilot':
                vehicle_actor = self._world.get_actor(vehicle_unit.actorId)
                vehicle_actor.set_autopilot(True)

    def flush_all_vehicle(self):
        for vehicle_unit in self._vehicleUnit_list:
            if vehicle_unit.ctrlType=='File' and vehicle_unit.ctrlCounter <= vehicle_unit.maxCounter:
                vehicle_ctrl = vehicle_unit.get_VehicleControl()
                vehicle_actor = self._world.get_actor(vehicle_unit.actorId)
                vehicle_actor.apply_control(vehicle_ctrl)
            
    def get_vehicle_nums(self) -> int:
        return len(self._vehicleUnit_list)

    def destroy_all_actors(self) -> int:
        destroy_nums = 0
        for vehicle_unit in self._vehicleUnit_list:
            vehicle_actor = self._world.get_actor(vehicle_unit.actorId)
            if vehicle_actor.destroy():
                destroy_nums += 1
        return destroy_nums

