
import carla
import random
from utilities import get_args, config_sensors
from queue import Queue, Empty
import os

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
        settings.fixed_delta_seconds = args.fixed_delta_time
        world.apply_settings(settings)

        # 获得spectator        
        spectator = world.get_spectator() 
        
        # 获取world蓝图
        blueprint_library = world.get_blueprint_library()

        # 设置ego_vehicle
        transform_vehicle = random.choice(world.get_map().get_spawn_points())
        ego_vehicle = world.spawn_actor(blueprint_library.find("vehicle.tesla.model3"), transform_vehicle)
        ego_vehicle.set_autopilot(True, args.traffic_manager_port)
        actor_list.append(ego_vehicle)
        
        # Traffic Manager
        traffic_manager = client.get_trafficmanager(args.traffic_manager_port)
        traffic_manager.set_synchronous_mode(args.sync_mode)
        traffic_manager.ignore_lights_percentage(ego_vehicle,100) # ignore traffic lights percentage
        traffic_manager.set_random_device_seed(0)
        random.seed(0)
        
        # Sensor 队列
        sensor_queue = Queue(maxsize=-1)

        sensor_actors = config_sensors(world, ego_vehicle, sensor_queue, args)
        actor_list += sensor_actors
        
        counter = 0

       

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
        traffic_manager.set_synchronous_mode(False)
        for actor in actor_list:
            actor.destroy()
        print("\nAll actors cleaned up!!!")


if __name__ == '__main__':
    main()