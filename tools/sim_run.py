
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

    try:
        
        original_settings = world.get_settings()
        settings = world.get_settings()
        settings.synchronous_mode = args.sync_mode # Enables synchronous mode
        synchronous_master = True
        settings.fixed_delta_seconds = args.fixed_delta_time
        world.apply_settings(settings)

        # 获得spectator        
        spectator = world.get_spectator() 
        
        # 获取world蓝图
        blueprint_library = world.get_blueprint_library()

        # 设置ego_vehicle
        transform_vehicle = random.choice(world.get_map().get_spawn_points())
        ego_bp = blueprint_library.find("vehicle.audi.tt")
        ego_vehicle = world.spawn_actor(ego_bp, transform_vehicle)
        ego_vehicle.set_autopilot(True, args.traffic_manager_port)
        actor_list.append(ego_vehicle)
        
        # Traffic Manager
        traffic_manager = client.get_trafficmanager(args.traffic_manager_port)
        traffic_manager.set_synchronous_mode(args.sync_mode)
        traffic_manager.ignore_lights_percentage(ego_vehicle, 100) # ignore traffic lights percentage
        traffic_manager.set_random_device_seed(0)
        random.seed(0)
        
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


        while True and counter < args.frames:
            
            # Tick the server
            world.tick()

            # 将CARLA界面摄像头跟随ego_vehicle动
            loc = ego_vehicle.get_transform().location
            spectator.set_transform(carla.Transform(carla.Location(x=loc.x,y=loc.y,z=35),carla.Rotation(yaw=0,pitch=-90,roll=0)))

            # 处理传感器数据
            try:
                for i in range(0, len(sensor_actors)):
                    s_name, s_frame  = sensor_queue.get(block=True, timeout=1.0)
                    print("    Frame: %d   Sensor: %s" % (s_frame, s_name))
                
            except Empty:
                print("Some of the sensor information is missed")
                # Tick the server
            counter += 1
            
            
    finally:
        world.apply_settings(original_settings)
        
        print('\ndestroying %d vehicles' % len(vehicles_list))
        client.apply_batch([carla.command.DestroyActor(x) for x in vehicles_list])

        traffic_manager.set_synchronous_mode(False)
        for actor in actor_list:
            actor.destroy()
        print("\nbasic actors cleaned up!!!")


if __name__ == '__main__':
    main()