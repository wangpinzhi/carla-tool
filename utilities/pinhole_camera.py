
import carla
from queue import Queue

def pinhole_data_callback(sensor_data, sensor_queue:Queue, sensor_name):
    
    sensor_queue.put((sensor_name, sensor_data.frame, sensor_data))

'''
get pinhole_camera_rgb actors from dict
'''
def get_pinhole_camera_rgb(world, target_vehicle, sensor_queue, settings:list):

    blueprint_library = world.get_blueprint_library()
    actors = []
    for idx, cur_setting in enumerate(settings):
        cam_bp = blueprint_library.find('sensor.camera.rgb')
        cam_bp.set_attribute("image_size_x", "{}".format(cur_setting["image_width"]))
        cam_bp.set_attribute("image_size_y", "{}".format(cur_setting["image_height"]))
        cam_bp.set_attribute("sensor_tick", '{}'.format(cur_setting["sensor_tick"]))
        cam_bp.set_attribute("fov", '{}'.format(cur_setting["fov"]))
        
        actor=world.spawn_actor(cam_bp, carla.Transform(carla.Location(x=cur_setting['location_x'],y=cur_setting['location_y'],z=cur_setting['location_z']),carla.Rotation(pitch=cur_setting['rotation_pitch'],yaw=cur_setting['rotation_yaw'],roll=cur_setting['rotation_roll'])), attach_to=target_vehicle)
        actor.listen(lambda data, s_name=cur_setting['name']: pinhole_data_callback(data, sensor_queue, s_name))
        actors.append(actor)
    
    return actors

'''
get pinhole_camera_depth actors from dict
'''
def get_pinhole_camera_depth(world, target_vehicle, sensor_queue, settings:list):

    blueprint_library = world.get_blueprint_library()
    actors = []
    for idx, cur_setting in enumerate(settings):
        cam_bp = blueprint_library.find('sensor.camera.depth')
        cam_bp.set_attribute("image_size_x", "{}".format(cur_setting["image_width"]))
        cam_bp.set_attribute("image_size_y", "{}".format(cur_setting["image_height"]))
        cam_bp.set_attribute("sensor_tick", '{}'.format(cur_setting["sensor_tick"]))
        cam_bp.set_attribute("fov", '{}'.format(cur_setting["fov"]))
        
        actor=world.spawn_actor(cam_bp, carla.Transform(carla.Location(x=cur_setting['location_x'],y=cur_setting['location_y'],z=cur_setting['location_z']),carla.Rotation(pitch=cur_setting['rotation_pitch'],yaw=cur_setting['rotation_yaw'],roll=cur_setting['rotation_roll'])), attach_to=target_vehicle)
        actor.listen(lambda data, s_name=cur_setting['name']: pinhole_data_callback(data, sensor_queue, s_name))
        actors.append(actor)
    
    return actors
