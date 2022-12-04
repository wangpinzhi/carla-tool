
import sys,os
import time
parent_path = os.path.abspath(os.path.join(__file__, *(['..'] * 2)))
sys.path.insert(0, parent_path)



import carla
import random,math,cv2 
from utilities import get_args, config_sensors, config_sim_scene
from queue import Queue, Empty
from multiprocessing import JoinableQueue,Process,Value
import logging
import numpy as np

def producer(transQ:JoinableQueue, total_images:Value):

    args = get_args()
    random.seed(5)

    # 设置日志输出
    logger = logging.getLogger("Producer")
    logger.setLevel(logging.INFO)
    log_format = logging.Formatter('[%(name)s] [%(levelname)s] [%(message)s]')
    log_stream = logging.StreamHandler()
    log_stream.setLevel(logging.INFO)
    log_stream.setFormatter(log_format)
    logger.addHandler(log_stream)

    try:
        
        hero_actor, spectator, hero_route, client, original_settings, npc_vehicle_list, npc_walker_list, npc_walker_id, npc_walker_actors = config_sim_scene(args)

        traffic_manager = client.get_trafficmanager(args.traffic_manager_port)
        world = client.get_world()
            
        # Sensor 队列
        sensor_queue = Queue(maxsize=-1)

        sensor_actors = config_sensors(world, hero_actor, sensor_queue, args)
        
        logger.info('spawned %d vehicles and %d walkers',len(npc_vehicle_list), len(npc_walker_list))   

        write_strs = ['|  Frame   |  Timestamp |External Matrix  |']
        
        while True:
        
            if math.sqrt((hero_actor.get_location().x-hero_route[-1].x)**2+(hero_actor.get_location().y-hero_route[-1].y)**2)<0.5 :# <0.5m
                break

            # Tick the server
            world.tick()

            # 将CARLA界面摄像头跟随ego_vehicle动
            loc = hero_actor.get_transform().location
            rot = hero_actor.get_transform().rotation
            spectator.set_transform(carla.Transform((loc + carla.Location(x=0, y=-5, z=2)), carla.Rotation(yaw=rot.yaw, pitch=-10+rot.pitch, roll=rot.roll)))         

            # 处理传感器数据
            try:
                save_queue = Queue()   
                cur_frame = None
                cur_timestamp = None
                for i in range(0, len(sensor_actors)):
                    s_name, s_frame, s_data  = sensor_queue.get(block=True, timeout=1.0)
                    cur_frame = s_frame
                    cur_timestamp = s_data.timestamp
                    cur_ex_matrix = s_data.transform.get_matrix()
                    if 'ph' in s_name:
                        data_array = np.frombuffer(s_data.raw_data, dtype=np.dtype("uint8"))
                        data_array = np.reshape(data_array, (s_data.height, s_data.width, 4))
                        data_array = data_array[:, :, :3]
                        save_queue.put((os.path.join(args.save_data_path,'pinhole','{}_{}.png'.format(s_name, s_data.frame)),data_array))
                    elif 'cm' in s_name:
                        data_array = np.frombuffer(s_data.raw_data, dtype=np.dtype("uint8"))
                        data_array = np.reshape(data_array, (s_data.height, s_data.width, 4))
                        data_array = data_array[:, :, :3]
                        save_queue.put((os.path.join(args.save_data_path,'cubemap','{}_{}.png'.format(s_name,s_data.frame)),data_array))


                while not save_queue.empty():
                    with total_images.get_lock():

                        total_images.value += 1
                        path, data= save_queue.get()
                        transQ.put((path,data))
                
                write_strs.append(f'\n| {cur_frame} | {str(cur_timestamp)}  |{str(cur_ex_matrix)}  |')
                transQ.join()
            
            except Empty:
                logger.warning("Some of the sensor information is missed!")
        
        
    
    finally:
        
        world.apply_settings(original_settings)
        traffic_manager.set_synchronous_mode(False)
        
        logger.info('Destroying %d sensors' % len(sensor_actors))
        for sensor in sensor_actors:
            sensor.destroy()

        logger.info('Destroying hero vehicles')
        hero_actor.destroy()

        logger.info('destroying %d vehicles' % len(npc_vehicle_list))
        client.apply_batch([carla.command.DestroyActor(x) for x in npc_vehicle_list])

        for i in range(0, len(npc_walker_id), 2):
            npc_walker_actors[i].stop()
        
        logger.info('destroying %d walkers' % len(npc_walker_list))
        client.apply_batch([carla.command.DestroyActor(x) for x in npc_walker_id])

        with open(os.path.join(args.save_data_path,'external.txt'),'a') as f:
            f.writelines(write_strs)
        time.sleep(0.5)
        
        

def consumuer(transQ:JoinableQueue, total_images, consume_images, start_time):

    # 设置日志输出
    logger = logging.getLogger(f"Consumer")
    logger.setLevel(logging.INFO)
    log_format = logging.Formatter('[%(name)s][%(levelname)s][%(message)s]')
    log_stream = logging.StreamHandler()
    log_stream.setLevel(logging.INFO)
    log_stream.setFormatter(log_format)
    logger.addHandler(log_stream)

    while True :
        if not transQ.qsize() == 0:
            with consume_images.get_lock():
                path, data= transQ.get()
                cv2.imwrite(path,data)
                consume_images.value += 1
                logger.info('Images:(%d)/(%d) time_use: %fs',consume_images.value, total_images.value,time.time()-start_time)
                transQ.task_done()
    


if __name__ == '__main__':

    transQ = JoinableQueue()
    total_images = Value('Q', 0)
    consume_images = Value('Q', 0)
    start_time = time.time()

    prod = Process(target=producer,args=(transQ,total_images))
    con1 = Process(target=consumuer,args=(transQ,total_images, consume_images, start_time))
    con2 = Process(target=consumuer,args=(transQ,total_images, consume_images, start_time))
    con3 = Process(target=consumuer,args=(transQ,total_images, consume_images, start_time))
    con4 = Process(target=consumuer,args=(transQ,total_images, consume_images, start_time))

    con1.daemon=True
    con2.daemon=True
    con3.daemon=True
    con4.daemon=True

    prod.start()

    con1.start()
    con2.start()
    con3.start()
    con4.start()
    
    prod.join()  # 等待生产和消费完成，主线程结束

    print('Exit Main Process')