from utilities.pinhole_camera import get_pinhole_camera_rgb, get_pinhole_camera_depth
from utilities.cubemap_camera import get_cubemap_camera_rgb, get_cubemap_camera_depth
from utilities.generate_npc import generate_vehicle, generate_walker
from utilities.erpCubemap import c2e
import carla
import json,re
import os



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
    pinhole_camera_rgb_list = get_pinhole_camera_rgb(world,target_vehicle, sensor_queue, sensor_settings["pinhole_rgb"])

    # config_pinhole_camera_depth
    pinhole_camera_depth_list = get_pinhole_camera_depth(world,target_vehicle, sensor_queue, sensor_settings["pinhole_depth"])

    # config_cubemap_camera_rgb
    cubemap_camera_rgb_list = get_cubemap_camera_rgb(world,target_vehicle, sensor_queue, sensor_settings["cubemap_rgb"])

    # config_cubemap_camera_depth
    cubemap_camera_depth_list = get_cubemap_camera_depth(world,target_vehicle, sensor_queue, sensor_settings["cubemap_depth"])

    sensor_actors = pinhole_camera_rgb_list + cubemap_camera_rgb_list + cubemap_camera_depth_list+pinhole_camera_depth_list
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
    old_map = world.get_map().name
    if scene_settings["map"] not in old_map :
        world = client.load_world(scene_settings["map"])
        print('reload world map: {}->{}'.format(old_map, scene_settings["map"]))
    
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
    print('get hero_bp success')
    hero_bp = blueprint_library.find(scene_settings["hero_actor"]["blueprint"])
    hero_bp.set_attribute('role_name', 'hero')
      
    if scene_settings["hero_actor"]["spawn_points_index"] == -1:
        loc_x = scene_settings["hero_actor"]["spawn_points"]['loc_x']
        loc_y = scene_settings["hero_actor"]["spawn_points"]['loc_y']
        loc_z = scene_settings["hero_actor"]["spawn_points"]['loc_z']
        rot_p = scene_settings["hero_actor"]["spawn_points"]['rot_p']
        rot_y = scene_settings["hero_actor"]["spawn_points"]['rot_y']
        rot_r = scene_settings["hero_actor"]["spawn_points"]['rot_r']
        hero_spawn_point = carla.Transform(carla.Location(loc_x,loc_y,loc_z),carla.Rotation(rot_p,rot_y,rot_r))
    else:
        hero_spawn_point = spawn_points[scene_settings["hero_actor"]["spawn_points_index"]]
           
    hero_actor = world.spawn_actor(hero_bp, hero_spawn_point)
    print('Spawn hero actor success')
    hero_actor.set_autopilot(scene_settings["hero_actor"]["autopilot"], scene_settings["hero_actor"]["tm_port"])
    print('Set autopilot success')
    if scene_settings["hero_actor"]["autopilot"]:
        route = [spawn_points[ind].location for ind in scene_settings["hero_actor"]["route_indices"]]
        if len(route) == 0:
            route = [
                carla.Location(item["loc_x"],item["loc_y"],item["loc_z"]) for item in scene_settings["hero_actor"]["route_points"]
            ]
            # route = scene_settings["hero_actor"]["route_points"]
        print(len(route))
        tm = client.get_trafficmanager(scene_settings["hero_actor"]["tm_port"])
        # Set parameters of TM hero actor control
        tm.ignore_lights_percentage(hero_actor, scene_settings["hero_actor"]["ignore_lights_percentage"])
        tm.random_left_lanechange_percentage(hero_actor, scene_settings["hero_actor"]["random_left_lanechange_percentage"])
        tm.random_right_lanechange_percentage(hero_actor, scene_settings["hero_actor"]["random_right_lanechange_percentage"])
        tm.auto_lane_change(hero_actor, scene_settings["hero_actor"]["auto_lane_change"])
        tm.set_desired_speed(hero_actor, scene_settings["hero_actor"]["desired_speed"])
        tm.ignore_signs_percentage(hero_actor, 0)
        tm.set_path(hero_actor, route) # 设置车辆行驶路线
    else:
        print("hero actor not autopilot!")

    # gen vehicle npc
    npc_vehicle_list = generate_vehicle(client,scene_settings["vehicle_npc"],args)
    npc_walker_list, npc_walker_id, npc_walker_actors = generate_walker(client,scene_settings["walker_npc"],args)
    
    return hero_actor, client, original_settings, npc_vehicle_list, npc_walker_list, npc_walker_id, npc_walker_actors

   
