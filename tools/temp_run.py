import glob
import logging
import os
import sys
parent_path = os.path.abspath(os.path.join(__file__, *(['..'] * 2)))
sys.path.insert(0, parent_path)

try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla

import random
import json
import time
import cv2

try:
    import numpy as np
except ImportError:
    raise RuntimeError('cannot import numpy, make sure numpy package is installed')

import argparse
from queue import Queue
from queue import Empty


def tutorial(args):
    # read config json
    with open(args.config_path, 'r') as f:
        config_settings = json.load(f)
    scene_settings = config_settings["scene_config"]
    sensor_settings = config_settings["sensor_config"]
    random.seed(config_settings["random_seed"])

    # get client
    client = carla.Client(args.server_ip, args.server_port)
    client.set_timeout(10.0)

    # 连接world
    world = client.get_world()

    # 获取当前map
    old_map = world.get_map().name
    if scene_settings["map"] not in old_map:
        world = client.load_world(scene_settings["map"])
        print('reload world map: {}->{}'.format(old_map, scene_settings["map"]))

    # 获取world蓝图
    blueprint_library = world.get_blueprint_library()

    # 设置traffic manager
    traffic_manager = client.get_trafficmanager(8000)
    traffic_manager.set_synchronous_mode(True)
    # traffic_manager.set_global_distance_to_leading_vehicle(1.0)

    # 设置world同步模式
    original_settings = world.get_settings()
    settings = world.get_settings()
    settings.synchronous_mode = True
    settings.fixed_delta_seconds = scene_settings["fixed_delta_time"]
    world.apply_settings(settings)

    actor_list = []
    camera_list = []

    try:
        # 获得spawn points
        spawn_points = world.get_map().get_spawn_points()

        # generate vehicle
        for vehicle_setting in scene_settings["vehicle_npc"]:
            if vehicle_setting["spawn_points_index"] == -1:
                loc_x = vehicle_setting["spawn_points"]['loc_x']
                loc_y = vehicle_setting["spawn_points"]['loc_y']
                loc_z = vehicle_setting["spawn_points"]['loc_z']
                rot_p = vehicle_setting["spawn_points"]['rot_p']
                rot_y = vehicle_setting["spawn_points"]['rot_y']
                rot_r = vehicle_setting["spawn_points"]['rot_r']
                spwan_point = carla.Transform(carla.Location(loc_x, loc_y, loc_z), carla.Rotation(rot_p, rot_y, rot_r))
            else:
                spwan_point = spawn_points[vehicle_setting["spawn_points_index"]]

            if vehicle_setting['random_bluerint']:
                vehicle_bp = random.choice(blueprint_library.filter('vehicle.*.*'))
            else:
                vehicle_bp = blueprint_library.find(vehicle_setting["blueprint"])

            vehicle = world.spawn_actor(
                blueprint=vehicle_bp,
                transform=spwan_point)
            vehicle.set_autopilot(vehicle_setting["autopilot"])
            actor_list.append(vehicle)

        # generate hero car
        hero_bp = blueprint_library.find(scene_settings["hero_actor"]["blueprint"])
        hero_bp.set_attribute('role_name', 'hero')

        if scene_settings["hero_actor"]["spawn_points_index"] == -1:
            loc_x = scene_settings["hero_actor"]["spawn_points"]['loc_x']
            loc_y = scene_settings["hero_actor"]["spawn_points"]['loc_y']
            loc_z = scene_settings["hero_actor"]["spawn_points"]['loc_z']
            rot_p = scene_settings["hero_actor"]["spawn_points"]['rot_p']
            rot_y = scene_settings["hero_actor"]["spawn_points"]['rot_y']
            rot_r = scene_settings["hero_actor"]["spawn_points"]['rot_r']
            hero_spawn_point = carla.Transform(carla.Location(loc_x, loc_y, loc_z), carla.Rotation(rot_p, rot_y, rot_r))
        else:
            hero_spawn_point = spawn_points[scene_settings["hero_actor"]["spawn_points_index"]]

        hero_actor = world.spawn_actor(
            blueprint=hero_bp,
            transform=hero_spawn_point)
        hero_actor.set_autopilot(scene_settings["hero_actor"]["autopilot"])
        actor_list.append(hero_actor)

        spectator = world.get_spectator()

        # generate sensor
        sensor_queue = []

        # set data save path
        cubemap_save_path = os.path.join(args.save_data_path, 'cubemap')
        pinhole_save_path = os.path.join(args.save_data_path, 'pinhole')
        os.makedirs(pinhole_save_path, exist_ok=True)
        os.makedirs(cubemap_save_path, exist_ok=True)
        # if not os.path.isdir(cubemap_save_path):
        #     os.mkdir(cubemap_save_path)
        # if not os.path.isdir(pinhole_save_path):
        #     os.mkdir(pinhole_save_path)

        # generate pinhole camera rgb
        for idx, cur_setting in enumerate(sensor_settings["pinhole_rgb"]):
            cam_bp = blueprint_library.find('sensor.camera.rgb')
            cam_bp.set_attribute("image_size_x", "{}".format(cur_setting["image_width"]))
            cam_bp.set_attribute("image_size_y", "{}".format(cur_setting["image_height"]))
            cam_bp.set_attribute("sensor_tick", '{}'.format(cur_setting["sensor_tick"]))
            cam_bp.set_attribute("fov", '{}'.format(cur_setting["fov"]))

            single_queue = Queue()

            actor = world.spawn_actor(cam_bp, carla.Transform(
                carla.Location(x=cur_setting['location_x'], y=cur_setting['location_y'], z=cur_setting['location_z']),
                carla.Rotation(pitch=cur_setting['rotation_pitch'], yaw=cur_setting['rotation_yaw'],
                               roll=cur_setting['rotation_roll'])), attach_to=hero_actor)
            actor.listen(lambda data, s_name=cur_setting['name']: single_queue.put((s_name, data.frame, data)))
            camera_list.append(actor)

            sensor_queue.append(single_queue)

        # generate pinhole camera depth
        for idx, cur_setting in enumerate(sensor_settings["pinhole_depth"]):
            cam_bp = blueprint_library.find('sensor.camera.depth')
            cam_bp.set_attribute("image_size_x", "{}".format(cur_setting["image_width"]))
            cam_bp.set_attribute("image_size_y", "{}".format(cur_setting["image_height"]))
            cam_bp.set_attribute("sensor_tick", '{}'.format(cur_setting["sensor_tick"]))
            cam_bp.set_attribute("fov", '{}'.format(cur_setting["fov"]))

            single_queue = Queue()

            actor = world.spawn_actor(cam_bp, carla.Transform(
                carla.Location(x=cur_setting['location_x'], y=cur_setting['location_y'],
                               z=cur_setting['location_z']),
                carla.Rotation(pitch=cur_setting['rotation_pitch'], yaw=cur_setting['rotation_yaw'],
                               roll=cur_setting['rotation_roll'])), attach_to=hero_actor)
            actor.listen(lambda data, s_name=cur_setting['name']: single_queue.put((s_name, data.frame, data)))
            camera_list.append(actor)

            sensor_queue.append(single_queue)

        # generate cubemap camera rgb
        for idx, cur_setting in enumerate(sensor_settings["cubemap_rgb"]):
            cam_bp = blueprint_library.find('sensor.camera.rgb')
            cam_bp.set_attribute("image_size_x", "{}".format(cur_setting["image_width"]))
            cam_bp.set_attribute("image_size_y", "{}".format(cur_setting["image_width"]))
            cam_bp.set_attribute("sensor_tick", '{}'.format(cur_setting["sensor_tick"]))
            cam_bp.set_attribute("fov", '{}'.format(90))

            items = [('front', 0, 0, 0), ('right', 0, 90, 0), ('back', 0, 180, 0), ('left', 0, -90, 0),
                     ('up', 90, 0, 0), ('down', -90, 0, 0)]
            for view, rotation_pitch, rotation_yaw, rotation_roll in items:
                single_queue = Queue()

                actor = world.spawn_actor(cam_bp,
                                          carla.Transform(
                                              carla.Location(x=cur_setting['location_x'], y=cur_setting['location_y'],
                                                             z=cur_setting['location_z']),
                                              carla.Rotation(pitch=rotation_pitch,
                                                             yaw=rotation_yaw + cur_setting['rotation_yaw'],
                                                             roll=rotation_roll)
                                              ),
                                          attach_to=hero_actor)

                actor.listen(
                    lambda data, s_name=cur_setting["name"], s_view=
                    view: single_queue.put((s_name+'_'+s_view, data.frame, data)))

                camera_list.append(actor)
                sensor_queue.append(single_queue)

        # generate cubemap camera depth
        for idx, cur_setting in enumerate(sensor_settings["cubemap_depth"]):
            cam_bp = blueprint_library.find('sensor.camera.depth')
            cam_bp.set_attribute("image_size_x", "{}".format(cur_setting["image_width"]))
            cam_bp.set_attribute("image_size_y", "{}".format(cur_setting["image_width"]))
            cam_bp.set_attribute("sensor_tick", '{}'.format(cur_setting["sensor_tick"]))
            cam_bp.set_attribute("fov", '{}'.format(90))

            items = [('front', 0, 0, 0), ('right', 0, 90, 0), ('back', 0, 180, 0), ('left', 0, -90, 0),
                     ('up', 90, 0, 0), ('down', -90, 0, 0)]
            for view, rotation_pitch, rotation_yaw, rotation_roll in items:
                single_queue = Queue()

                actor = world.spawn_actor(cam_bp,
                                          carla.Transform(
                                              carla.Location(x=cur_setting['location_x'],
                                                             y=cur_setting['location_y'],
                                                             z=cur_setting['location_z']),
                                              carla.Rotation(pitch=rotation_pitch,
                                                             yaw=rotation_yaw + cur_setting['rotation_yaw'],
                                                             roll=rotation_roll)
                                          ),
                                          attach_to=hero_actor)

                actor.listen(
                    lambda data, s_name=cur_setting["name"], s_view=
                    view: single_queue.put((s_name + '_' + s_view, data.frame, data)))

                camera_list.append(actor)
                sensor_queue.append(single_queue)

        print('sensors:', len(camera_list))

        write_strs = ['|  Frame   |  Timestamp | Hero Car External Matrix  |']

        for frame_counter in range(config_settings['save_frames']+config_settings['ignore_frames']):
            # Tick the server
            world.tick()
            world_frame = world.get_snapshot().frame
            total_start_time = time.time()

            # 将CARLA界面摄像头跟随ego_vehicle动
            loc = hero_actor.get_transform().location + carla.Location(x=0, y=0, z=35)
            rot = hero_actor.get_transform().rotation
            spectator.set_transform(carla.Transform(loc, carla.Rotation(roll=rot.roll, yaw=rot.yaw, pitch=-90)))

            # 处理传感器数据
            cur_ex_matrix = hero_actor.get_transform().get_matrix()

            try:
                cur_timestamp = None
                data_pre_time = 0

                for single_queue in sensor_queue:
                    s_name, s_frame, s_data = single_queue.get(block=True, timeout=None)
                    if frame_counter < config_settings['ignore_frames']:
                        continue
                    cur_timestamp = s_data.timestamp

                    start_time = time.time()
                    data_array = np.frombuffer(s_data.raw_data, dtype=np.dtype("uint8"))
                    data_array = np.reshape(data_array, (s_data.height, s_data.width, 4))
                    data_array = data_array[:, :, :3]
                    data_pre_time += (time.time()-start_time)

                    if 'ph' in s_name:
                        cv2.imwrite(os.path.join(args.save_data_path, 'pinhole', '{}_{}.png'.format(s_name, frame_counter)), data_array)
                    elif 'cm_rgb' in s_name:
                        cv2.imwrite(os.path.join(args.save_data_path, 'cubemap', '{}_{}.jpg'.format(s_name, frame_counter)), data_array, [int(cv2.IMWRITE_JPEG_QUALITY), 97])
                    elif 'cm_depth' in s_name:
                        np.savez(os.path.join(args.save_data_path, 'cubemap', '{}_{}.npz'.format(s_name, frame_counter)), data_array)

                if frame_counter >= config_settings['ignore_frames']:
                    write_strs.append(f'\n| {frame_counter} | {str(cur_timestamp)}  | {str(cur_ex_matrix)}  |')
                if len(camera_list) > 0:
                    logging.info('Processed Frames: (%d)/(%d) | Data Prepare Time_use: %fs | Total one frame time_use: %fs',frame_counter,config_settings['save_frames']+config_settings['ignore_frames'], data_pre_time/len(camera_list),time.time()-total_start_time)

            except Empty:
                logging.warning("Some of the sensor information is missed!")




    finally:
        world.apply_settings(original_settings)
        if len(actor_list) > 0:
            for actor in actor_list:
                actor.destroy()
        if len(camera_list) > 0:
            for camera in camera_list:
                camera.destroy()





def main():
    argparser = argparse.ArgumentParser(
        description='parameters for collecting data')

    # basic settings
    argparser.add_argument(
        '--server_ip',
        type=str,
        default='127.0.0.1',
        help='the host ip of carla server')
    argparser.add_argument(
        '--server_port',
        type=int, default=2000,
        help='the port of carla server listen')

    # collect settings
    argparser.add_argument(
        '--config_path',
        type=str,
        default='configs/demo_config.json',
        help='the path of config file')
    argparser.add_argument(
        '--save_data_path',
        type=str,
        default='output_data_maskcar',
        help='the path for saving data')

    # npc setttings
    argparser.add_argument(
        '-n',
        '--number-of-vehicles',
        metavar='N',
        default=30,
        type=int,
        help='Number of vehicles (default: 30)')
    argparser.add_argument(
        '-w',
        '--number-of-walkers',
        metavar='W',
        default=10,
        type=int,
        help='Number of walkers (default: 10)')
    argparser.add_argument(
        '--safe',
        action='store_true',
        help='Avoid spawning vehicles prone to accidents')
    argparser.add_argument(
        '--filterv',
        metavar='PATTERN',
        default='vehicle.*',
        help='Filter vehicle model (default: "vehicle.*")')
    argparser.add_argument(
        '--generationv',
        metavar='G',
        default='All',
        help='restrict to certain vehicle generation (values: "1","2","All" - default: "All")')
    argparser.add_argument(
        '--filterw',
        metavar='PATTERN',
        default='walker.pedestrian.*',
        help='Filter pedestrian type (default: "walker.pedestrian.*")')
    argparser.add_argument(
        '--generationw',
        metavar='G',
        default='2',
        help='restrict to certain pedestrian generation (values: "1","2","All" - default: "2")')
    argparser.add_argument(
        '--seedw',
        metavar='S',
        default=0,
        type=int,
        help='Set the seed for pedestrians module')

    # multi processer setting
    argparser.add_argument(
        '--num_workers',
        type=int,
        default=1)

    args = argparser.parse_args()

    try:
        tutorial(args)

    except KeyboardInterrupt:
        print('\nCancelled by user. Bye!')


if __name__ == '__main__':
    main()
