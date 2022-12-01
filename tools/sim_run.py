
import sys,os
import time
parent_path = os.path.abspath(os.path.join(__file__, *(['..'] * 2)))
sys.path.insert(0, parent_path)


import carla
import random,math 
from utilities import get_args, config_sensors, config_sim_scene
from queue import Queue, Empty
import logging

def main():

    args = get_args()
    logging.basicConfig(format='[%(levelname)s] %(message)s', level=logging.INFO)
    random.seed(5)
    try:
        
        hero_actor, spectator, hero_route, client, original_settings, npc_vehicle_list, npc_walker_list, npc_walker_id, npc_walker_actors = config_sim_scene(args)

        traffic_manager = client.get_trafficmanager(args.traffic_manager_port)
        world = client.get_world()
            
        # Sensor 队列
        sensor_queue = Queue(maxsize=-1)

        sensor_actors = config_sensors(world, hero_actor, sensor_queue, args)
        
        logging.info('spawned %d vehicles and %d walkers',len(npc_vehicle_list), len(npc_walker_list))

        # Example of how to use Traffic Manager parameters
        traffic_manager.global_percentage_speed_difference(30.0)

        write_strs = ['|  Frame   |   External Matrix  |']

        counter = 0
        start_time = time.time()
        
        while True:
            
            if math.sqrt((hero_actor.get_location().x-hero_route[-1].x)**2+(hero_actor.get_location().y-hero_route[-1].y)**2)<0.5 :# <0.5m
                break

            # Tick the server
            world.tick()

            # 将CARLA界面摄像头跟随ego_vehicle动
            loc = hero_actor.get_transform().location
            spectator.set_transform(carla.Transform(carla.Location(x=loc.x,y=loc.y,z=35),carla.Rotation(yaw=0,pitch=-90,roll=0)))

            # 将ego_car遇到的红灯变为绿灯
            # if hero_actor.is_at_traffic_light():
            #     traffic_light = hero_actor.get_traffic_light()
            #     if traffic_light.get_state() == carla.TrafficLightState.Red:
            #         traffic_light.set_state(carla.TrafficLightState.Green)

            # Set parameters of TM vehicle control, we don't want lane changes
            traffic_manager.update_vehicle_lights(hero_actor, True)
            traffic_manager.random_left_lanechange_percentage(hero_actor, 0)
            traffic_manager.random_right_lanechange_percentage(hero_actor, 0)
            traffic_manager.auto_lane_change(hero_actor, False)
            traffic_manager.set_path(hero_actor, hero_route) # 设置车辆行驶路线

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
                counter += 1
                logging.info('Frames:%d time_use:%f seconds', counter, end_time-start_time)

                write_strs.append(f'\n| {cur_frame} |   {str(cur_ex_matrix)}  |')

            except Empty:
                logging.warning("Some of the sensor information is missed!")
                # Tick the server     
    
    finally:

        
        world.apply_settings(original_settings)
        traffic_manager.set_synchronous_mode(False)

        hero_actor.destroy()
        logging.info("Destroy Actor: hero_actor")

        logging.info('destroying %d vehicles' % len(npc_vehicle_list))
        client.apply_batch([carla.command.DestroyActor(x) for x in npc_vehicle_list])

        for i in range(0, len(npc_walker_id), 2):
            npc_walker_actors[i].stop()
        
        logging.info('destroying %d walkers' % len(npc_walker_list))
        client.apply_batch([carla.command.DestroyActor(x) for x in npc_walker_id])
        
        logging.info('destroying %d sensors' % len(sensor_actors))
        for actor in sensor_actors:
            actor.destroy()
        
        with open(os.path.join(args.save_data_path,'external.txt'),'a') as f:
            f.writelines(write_strs)
        
        time.sleep(0.5)


if __name__ == '__main__':
    main()