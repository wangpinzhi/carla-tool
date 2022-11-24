
import sys,os
parent_path = os.path.abspath(os.path.join(__file__, *(['..'] * 2)))
sys.path.insert(0, parent_path)


import carla
import random
from utilities import get_args, config_sensors, get_actor_blueprints
from queue import Queue, Empty

def main():

    args = get_args()

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
        synchronous_master = True
        settings.fixed_delta_seconds = args.fixed_delta_time
        world.apply_settings(settings)

        # 获得spectator        
        spectator = world.get_spectator() 
        
        # 获取world蓝图
        blueprint_library = world.get_blueprint_library()

        # Traffic Manager
        traffic_manager = client.get_trafficmanager(args.traffic_manager_port)
        traffic_manager.set_synchronous_mode(args.sync_mode)
        traffic_manager.set_random_device_seed(54)
        traffic_manager.set_hybrid_physics_mode(True)
        traffic_manager.set_hybrid_physics_radius(70.0)
        traffic_manager.set_respawn_dormant_vehicles(True)
        traffic_manager.set_boundaries_respawn_dormant_vehicles(25,700)

        # 设置ego_vehicle
        transform_vehicle = random.choice(world.get_map().get_spawn_points())
        ego_bp = blueprint_library.find("vehicle.audi.invisiable") # 设置audi.tt为invisiable
        ego_bp.set_attribute('role_name', 'hero')
        ego_vehicle = world.spawn_actor(ego_bp, transform_vehicle)
        traffic_manager.ignore_lights_percentage(ego_vehicle, 30) # ignore traffic lights percentage
        ego_vehicle.set_autopilot(True, args.traffic_manager_port)
        actor_list.append(ego_vehicle)
        
        
        
        
        # Sensor 队列
        sensor_queue = Queue(maxsize=-1)

        sensor_actors = config_sensors(world, ego_vehicle, sensor_queue, args)
        actor_list += sensor_actors
        
        counter = 0

        # --------------
        # generate npc
        # --------------
        npc_blueprints_vehicle = get_actor_blueprints(world, args.filterv, args.generationv)
        npc_blueprints_vehicle = sorted(npc_blueprints_vehicle, key=lambda bp: bp.id)
        # npc_blueprints_walker = get_actor_blueprints(world, args.filterw, args.generationw)
        
         # filter invisiable car
        npc_blueprints_vehicle = [x for x in npc_blueprints_vehicle if not x.id.endswith('invisiable')]

        npc_spawn_points = world.get_map().get_spawn_points()
        number_of_spawn_points = len(npc_spawn_points)

        if args.number_of_vehicles < number_of_spawn_points:
            random.shuffle(npc_spawn_points)
        elif args.number_of_vehicles > number_of_spawn_points:
            print('requested %d vehicles, but could only find %d spawn points'.format(args.number_of_vehicles, number_of_spawn_points))
            args.number_of_vehicles = number_of_spawn_points

        SpawnActor = carla.command.SpawnActor
        SetAutopilot = carla.command.SetAutopilot
        FutureActor = carla.command.FutureActor
        
        # --------------
        # Spawn vehicles
        # --------------
        batch = []
        vehicles_list = []
        for n, transform in enumerate(npc_spawn_points):
            if n >= args.number_of_vehicles:
                break
            blueprint = random.choice(npc_blueprints_vehicle)

            if blueprint.has_attribute('color'):
                color = random.choice(blueprint.get_attribute('color').recommended_values)
                blueprint.set_attribute('color', color)
            if blueprint.has_attribute('driver_id'):
                driver_id = random.choice(blueprint.get_attribute('driver_id').recommended_values)
                blueprint.set_attribute('driver_id', driver_id)
            blueprint.set_attribute('role_name', f'npc{n}')

            # spawn the cars and set their autopilot and light state all together
            batch.append(SpawnActor(blueprint, transform)
                .then(SetAutopilot(FutureActor, True, traffic_manager.get_port())))

        for response in client.apply_batch_sync(batch, synchronous_master):
            if response.error:
                print(response.error)
            else:
                vehicles_list.append(response.actor_id)

        
        write_strs = ['|  Frame   |   External Matrix  |']
        while True and counter < args.frames:
            
            # Tick the server
            world.tick()

            # 将CARLA界面摄像头跟随ego_vehicle动
            loc = ego_vehicle.get_transform().location
            spectator.set_transform(carla.Transform(carla.Location(x=loc.x,y=loc.y,z=35),carla.Rotation(yaw=0,pitch=-90,roll=0)))
            # 处理传感器数据
            try:

                save_queue = Queue()
                cur_frame = None
                cur_loc = None
                for i in range(0, len(sensor_actors)):
                    s_name, s_frame, s_data  = sensor_queue.get(block=True, timeout=1.0)
                    if 'ph' in s_name:
                        save_queue.put((os.path.join(args.save_data_path,'pinhole','{}_{}_{}.png'.format(s_name, s_data.frame, s_data.timestamp)),s_data,carla.ColorConverter.Raw))
                    elif 'cm' in s_name:
                        if 'depth' in s_name:
                            save_queue.put((os.path.join(args.save_data_path,'cubemap','{}_{}_{}.png'.format(s_name,s_data.frame,s_data.timestamp)),s_data,carla.ColorConverter.Raw))
                            cur_frame = s_frame
                            cur_ex_matrix = s_data.transform.get_matrix()
                        elif 'rgb' in s_name:
                            save_queue.put((os.path.join(args.save_data_path,'cubemap','{}_{}_{}.png'.format(s_name,s_data.frame,s_data.timestamp)),s_data,carla.ColorConverter.Raw))  
                    
                print(f'INFO: [{counter+1}]/[{args.frames}]')
                write_strs.append(f'\n| {cur_frame} |   {str(cur_ex_matrix)}  |')
                counter += 1

                while not save_queue.empty():
                    path, data, converter= save_queue.get(block=True, timeout=1.0)
                    data.save_to_disk(path,color_converter=converter)

            except Empty:
                print("Some of the sensor information is missed!")
                # Tick the server     
    
    finally:
        world.apply_settings(original_settings)
        
        print('\ndestroying %d vehicles' % len(vehicles_list))
        client.apply_batch([carla.command.DestroyActor(x) for x in vehicles_list])

        traffic_manager.set_synchronous_mode(False)
        for actor in actor_list:
            actor.destroy()
        print("\nbasic actors cleaned up!!!")
        
        with open(os.path.join(args.save_data_path,'external.txt'),'a') as f:
            f.writelines(write_strs)


if __name__ == '__main__':
    main()