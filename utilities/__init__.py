from utilities.pinhole_camera import get_pinhole_camera_rgb
from utilities.cubemap_camera import get_cubemap_camera_rgb, get_cubemap_camera_depth
from utilities.fisheyeCubemap import Cubemap2Fisheye
from utilities.erpCubemap import c2e
from utilities.generate_npc import random_generate_vehicle, random_generate_walker
from utilities.generate_npc import generate_vehicle, generate_walker
import carla
import json,re
import argparse,logging
import os



def get_args():
    parser = argparse.ArgumentParser(description='parameters for collecting data')

    # basic settings
    parser.add_argument('--server_ip', type=str, default='127.0.0.1', help='the host ip of carla server')
    parser.add_argument('--server_port', type=int, default=2000, help='the port of carla server listen')

    # collect settings
    parser.add_argument('--config_path', type=str, default='configs/demo_config.json', help='the path of config file')
    parser.add_argument('--save_data_path', type=str, default='output_data_maskcar', help='the path for saving data')

    # npc setttings
    parser.add_argument('-n', '--number-of-vehicles', metavar='N', default=30, type=int, help='Number of vehicles (default: 30)')
    parser.add_argument('-w', '--number-of-walkers', metavar='W', default=10, type=int, help='Number of walkers (default: 10)')
    parser.add_argument('--safe', action='store_true', help='Avoid spawning vehicles prone to accidents')
    parser.add_argument('--filterv',metavar='PATTERN',default='vehicle.*',help='Filter vehicle model (default: "vehicle.*")')
    parser.add_argument('--generationv',metavar='G',default='All',help='restrict to certain vehicle generation (values: "1","2","All" - default: "All")')
    parser.add_argument('--filterw',metavar='PATTERN',default='walker.pedestrian.*',help='Filter pedestrian type (default: "walker.pedestrian.*")')
    parser.add_argument('--generationw',metavar='G',default='2',help='restrict to certain pedestrian generation (values: "1","2","All" - default: "2")')
    parser.add_argument('--seedw',metavar='S', default=0, type=int, help='Set the seed for pedestrians module')


    return parser.parse_args()




def config_sensors(world, target_vehicle, sensor_queue, args):

    # read config json (sensor_config.json)
    with open(args.config_path,'r') as f:
        sensor_settings = json.load(f)["sensor_config"]

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

def config_sim_scene(args):

    # read config json
    with open(args.config_path,'r') as f:
        scene_settings = json.load(f)["scene_config"]
    
    # get client
    client = carla.Client(args.server_ip, args.server_port)
    client.set_timeout(10.0)

    # 连接world
    world = client.get_world()

    # 获取当前map
    reg = re.compile('Town\d\d')
    old_map = re.findall(reg,world.get_map().name)[0]
    if old_map != scene_settings["map"]:
        world = client.load_world(scene_settings["map"])
        print('reload world map: {}->%{}'.format(old_map[0],scene_settings["map"]))
    
    # 应用设置
    original_settings = world.get_settings()
    settings = world.get_settings()
    settings.actor_active_distance = 2000
    settings.synchronous_mode = scene_settings['sync_mode'] # Enables synchronous mode
    if settings.synchronous_mode:
        settings.fixed_delta_seconds = scene_settings['fixed_delta_time']
    world.apply_settings(settings)

    # 获取world蓝图
    blueprint_library = world.get_blueprint_library()
    
    # Traffic Manager
    tm_setting_list = scene_settings["traffic_mananger_setting"]
    for tm_setting in tm_setting_list:
        tm = client.get_trafficmanager(tm_setting["port"])
        tm.set_random_device_seed(tm_setting["random_device_seed"])
        tm.set_global_distance_to_leading_vehicle(tm_setting["global_distance_to_leading_vehicle"])
        tm.set_synchronous_mode(scene_settings["sync_mode"])
        tm.set_hybrid_physics_mode(True)
        tm.set_hybrid_physics_radius(70.0)
        tm.set_respawn_dormant_vehicles(True)
        tm.set_boundaries_respawn_dormant_vehicles(25,700)
    
    
    # 获得spawn points
    spawn_points = world.get_map().get_spawn_points()

    # 设置hero car
    hero_bp = blueprint_library.find(scene_settings["hero_actor"]["blueprint"])
    hero_bp.set_attribute('role_name', 'hero')
    hero_actor = world.spawn_actor(hero_bp,spawn_points[scene_settings["hero_actor"]["spawn_points_index"]])
    hero_actor.set_autopilot(scene_settings["hero_actor"]["autopilot"], scene_settings["hero_actor"]["tm_port"])
    if scene_settings["hero_actor"]["autopilot"]:
        route = [spawn_points[ind].location for ind in scene_settings["hero_actor"]["route_indices"]]
        tm = client.get_trafficmanager(scene_settings["hero_actor"]["tm_port"])
        # Set parameters of TM hero actor control
        tm.ignore_lights_percentage(hero_actor, scene_settings["hero_actor"]["ignore_lights_percentage"])
        tm.random_left_lanechange_percentage(hero_actor, scene_settings["hero_actor"]["random_left_lanechange_percentage"])
        tm.random_right_lanechange_percentage(hero_actor, scene_settings["hero_actor"]["random_right_lanechange_percentage"])
        tm.auto_lane_change(hero_actor, scene_settings["hero_actor"]["auto_lane_change"])
        tm.set_path(hero_actor, route) # 设置车辆行驶路线
    else:
        print("hero actor not autopilot!")

    # gen vehicle npc
    npc_vehicle_list = generate_vehicle(client,scene_settings["vehicle_npc"],args)
    npc_walker_list, npc_walker_id, npc_walker_actors = generate_walker(client,scene_settings["walker_npc"],args)

    return hero_actor, client, original_settings, npc_vehicle_list, npc_walker_list, npc_walker_id, npc_walker_actors

    

    
