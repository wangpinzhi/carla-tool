from utilities.pinhole_camera import get_pinhole_camera_rgb
from utilities.cubemap_camera import get_cubemap_camera_rgb, get_cubemap_camera_depth
import json
import argparse
import os


def get_args():
    parser = argparse.ArgumentParser(description='parameters for collecting data')

    # basic settings
    parser.add_argument('--server_ip', type=str, default='127.0.0.1', help='the host ip of carla server')
    parser.add_argument('--server_port', type=int, default=2000, help='the port of carla server listen')
    parser.add_argument('--reload_map', action='store_true', default=False, help='decide whether reload map')
    parser.add_argument('--map', type=str, default='Town01', choices=['Town01', 'Town02', 'Town03', 'Town04', 'Town05', 'Town06', 'Town07', 'Town08', 'Town09', 'Town10'])
    parser.add_argument('--sync_mode', action='store_true', default=True, help='decide whether use sync mode')
    parser.add_argument('--fixed_delta_time', type=float ,default=0.05, help='fixed_delta_time of the server')
    parser.add_argument('--traffic_manager_port', type= int, default=8000, help='the port number of the traffic manager')

    parser.add_argument('--frames', type=int, default=5000, help='the frames of collect data')
    parser.add_argument('--sensor_config_path', type=str, default='configs\sensor_config.json', help='the path of config file')
    parser.add_argument('--save_data_path', type=str, default='output_data', help='the path for saving data')

    return parser.parse_args()




def config_sensors(world, target_vehicle, sensor_queue, args):

    # read config json (sensor_config.json)
    with open(args.sensor_config_path,'r') as f:
        sensor_settings = json.load(f)

    # set data save path
    cubemap_save_path = os.path.join(args.save_data_path, 'cubemap')
    pinhole_save_path = os.path.join(args.save_data_path, 'pinhole')
    os.makedirs(pinhole_save_path,exist_ok=True)
    os.makedirs(cubemap_save_path,exist_ok=True)

    # config_pinhole_camera_rgb
    pinhole_camera_rgb_list = get_pinhole_camera_rgb(world,target_vehicle, sensor_queue, sensor_settings["pinhole_rgb"], pinhole_save_path)

    # config_cubemap_camera_rgb
    cubemap_camera_rgb_list = get_cubemap_camera_rgb(world,target_vehicle, sensor_queue, sensor_settings["cubemap_rgb"], cubemap_save_path)

    # config_cubemap_camera_depth
    cubemap_camera_depth_list = get_cubemap_camera_depth(world,target_vehicle, sensor_queue, sensor_settings["cubemap_depth"], cubemap_save_path)

    sensor_actors = pinhole_camera_rgb_list + cubemap_camera_rgb_list + cubemap_camera_depth_list
    print('sensors:', len(sensor_actors))

    return sensor_actors