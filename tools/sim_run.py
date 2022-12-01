
import sys,os
import time
parent_path = os.path.abspath(os.path.join(__file__, *(['..'] * 2)))
sys.path.insert(0, parent_path)


import carla
import random
from utilities import get_args, config_sensors, random_generate_vehicle, random_generate_walker
from queue import Queue, Empty
import logging

def main():

    args = get_args()
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)

    # 创建client
    client = carla.Client(args.server_ip, args.server_port)
    client.set_timeout(10.0)

    # 连接world
    world = client.get_world()
    if args.reload_map:
        world = client.load_world(args.map)

    # Actotr列表
    actor_list=[]
    random.seed(5)
    try:
        
        original_settings = world.get_settings()
        settings = world.get_settings()
        settings.actor_active_distance = 2000
        settings.synchronous_mode = args.sync_mode # Enables synchronous mode
        settings.fixed_delta_seconds = args.fixed_delta_time
        if args.no_rendering:
            settings.no_rendering_mode = True
        world.apply_settings(settings)

        # 获得spectator        
        spectator = world.get_spectator() 
        
        # 获取world蓝图
        blueprint_library = world.get_blueprint_library()

        # Traffic Manager
        traffic_manager = client.get_trafficmanager(args.traffic_manager_port)
        traffic_manager.set_global_distance_to_leading_vehicle(1.0)
        traffic_manager.set_synchronous_mode(args.sync_mode)
        traffic_manager.set_random_device_seed(62)
        traffic_manager.set_hybrid_physics_mode(True)
        traffic_manager.set_hybrid_physics_radius(70.0)
        traffic_manager.set_respawn_dormant_vehicles(True)
        traffic_manager.set_boundaries_respawn_dormant_vehicles(25,700)

        # 设置ego_vehicle
        transform_ego = random.choice(world.get_map().get_spawn_points())
        ego_bp = blueprint_library.find("vehicle.audi.invisiable") # 设置audi.tt为invisiable
        ego_bp.set_attribute('role_name', 'hero')
        ego_vehicle = world.spawn_actor(ego_bp, transform_ego)
        traffic_manager.ignore_lights_percentage(ego_vehicle, 30) # ignore traffic lights percentage
        ego_vehicle.set_autopilot(True, args.traffic_manager_port)
        actor_list.append(ego_vehicle)
            
        # Sensor 队列
        sensor_queue = Queue(maxsize=-1)

        sensor_actors = config_sensors(world, ego_vehicle, sensor_queue, args)
        actor_list += sensor_actors
        
        counter = 0

        # generate npc
        
        vehicles_list = random_generate_vehicle(client,world,traffic_manager,transform_ego,args)
        walkers_list, all_id, all_actors = random_generate_walker(client,world,args)
       

        print('spawned %d vehicles and %d walkers' % (len(vehicles_list), len(walkers_list)))

        # Example of how to use Traffic Manager parameters
        traffic_manager.global_percentage_speed_difference(30.0)

        write_strs = ['|  Frame   |   External Matrix  |']

        while True and counter < args.frames:
            
            # Tick the server
            world.tick()

            start_time = time.time()

            # 将CARLA界面摄像头跟随ego_vehicle动
            loc = ego_vehicle.get_transform().location
            spectator.set_transform(carla.Transform(carla.Location(x=loc.x,y=loc.y,z=35),carla.Rotation(yaw=0,pitch=-90,roll=0)))

            # 将ego_car遇到的红灯变为绿灯
            if ego_vehicle.is_at_traffic_light():
                traffic_light = ego_vehicle.get_traffic_light()
                if traffic_light.get_state() == carla.TrafficLightState.Red:
                    traffic_light.set_state(carla.TrafficLightState.Green)

            # 处理传感器数据
            try:

                save_queue = Queue()
                cur_frame = None
                for i in range(0, len(sensor_actors)):
                    s_name, s_frame, s_data  = sensor_queue.get(block=True, timeout=1.0)
                    cur_frame = s_frame
                    cur_ex_matrix = s_data.transform.get_matrix()
                    if 'ph' in s_name:
                        save_queue.put((os.path.join(args.save_data_path,'pinhole','{}_{}_{}.png'.format(s_name, s_data.frame, s_data.timestamp)),s_data,carla.ColorConverter.Raw))
                    elif 'cm' in s_name:
                        if 'depth' in s_name:
                            save_queue.put((os.path.join(args.save_data_path,'cubemap','{}_{}_{}.png'.format(s_name,s_data.frame,s_data.timestamp)),s_data,carla.ColorConverter.Raw))
                        elif 'rgb' in s_name:
                            save_queue.put((os.path.join(args.save_data_path,'cubemap','{}_{}_{}.png'.format(s_name,s_data.frame,s_data.timestamp)),s_data,carla.ColorConverter.Raw))  

                while not save_queue.empty():
                    path, data, converter= save_queue.get(block=True, timeout=1.0)
                    data.save_to_disk(path,color_converter=converter)

                end_time = time.time()

                logging.info('[%d]/[%d] time_use:%f seconds', counter+1, args.frames, end_time-start_time)

                write_strs.append(f'\n| {cur_frame} |   {str(cur_ex_matrix)}  |')
                counter += 1

            except Empty:
                logging.warning("Some of the sensor information is missed!")
                # Tick the server     
    
    finally:
        world.apply_settings(original_settings)
        
        # destory vehicle actors
        logging.info('\ndestroying %d vehicles' % len(vehicles_list))
        client.apply_batch([carla.command.DestroyActor(x) for x in vehicles_list])

        # stop walker controllers (list is [controller, actor, controller, actor ...])
        for i in range(0, len(all_id), 2):
            all_actors[i].stop()
        
        # destory walker actors
        logging.info('\ndestroying %d walkers' % len(walkers_list))
        client.apply_batch([carla.command.DestroyActor(x) for x in all_id])

        traffic_manager.set_synchronous_mode(False)

        for actor in actor_list:
            actor.destroy()
        logging.info("\nbasic actors cleaned up!!!")
        
        with open(os.path.join(args.save_data_path,'external.txt'),'a') as f:
            f.writelines(write_strs)
        
        time.sleep(0.5)


if __name__ == '__main__':
    main()