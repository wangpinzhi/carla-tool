
import sys,os
import time
parent_path = os.path.abspath(os.path.join(__file__, *(['..'] * 2)))
sys.path.insert(0, parent_path)

import carla
import random, cv2
from utilities import config_sensors, config_sim_scene
from queue import Queue, Empty
from multiprocessing import JoinableQueue,Process, TimeoutError, ProcessError
import logging,json,argparse
import numpy as np




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

    # multi processer setting
    parser.add_argument('--num_workers', type=int, default=1)

    return parser.parse_args()



def producer(transQ:JoinableQueue, args):

    with open(args.config_path,'r') as f:
        config_settings = json.load(f)
    
    random.seed(config_settings["random_seed"])

    # 设置日志输出
    logger = logging.getLogger("Producer")
    logger.setLevel(logging.INFO)
    log_format = logging.Formatter('[%(name)s] [%(levelname)s] [%(message)s]')
    log_stream = logging.StreamHandler()
    log_stream.setLevel(logging.INFO)
    log_stream.setFormatter(log_format)
    logger.addHandler(log_stream)

    try:
        
        hero_actor_id, client, original_settings, npc_vehicle_list, npc_walker_list, npc_walker_id, npc_walker_actors = config_sim_scene(args)

        world = client.get_world()   

        hero_actor = world.get_actor(hero_actor_id)  
        spectator = world.get_spectator() 
        
            
        # Sensor 队列
        sensor_queue = Queue(maxsize=-1)

        sensor_actors = config_sensors(world, hero_actor, sensor_queue, args)
        
        logger.info('spawned %d vehicles and %d walkers',len(npc_vehicle_list), len(npc_walker_list))   

        write_strs = ['|  Frame   |  Timestamp | Hero Car External Matrix  |']
        
        frame_counter = 0
        cur_frame = 1
        while frame_counter < (config_settings['save_frames']+config_settings['ignore_frames']):

            # Tick the server
            world.tick()

            # 将CARLA界面摄像头跟随ego_vehicle动
            loc = hero_actor.get_transform().location + carla.Location(x=0,y=0,z=35)
            rot = hero_actor.get_transform().rotation 
            spectator.set_transform(carla.Transform(loc,carla.Rotation(roll=rot.roll,yaw=rot.yaw,pitch=-90)))         
            
            # 处理传感器数据
            cur_ex_matrix = hero_actor.get_transform().get_matrix()
            try:
                # save_queue = Queue()   
                cur_timestamp = None
                data_pre_time = 0
                total_start_time = time.time()

                for i in range(0, len(sensor_actors)):
                    s_name, s_frame, s_data  = sensor_queue.get(block=True, timeout=None)
                    if frame_counter < config_settings['ignore_frames']:
                        continue
                    cur_timestamp = s_data.timestamp

                    start_time  = time.time()
                    data_array = np.frombuffer(s_data.raw_data, dtype=np.dtype("uint8"))
                    data_array = np.reshape(data_array, (s_data.height, s_data.width, 4))
                    data_array = data_array[:, :, :3]
                    data_pre_time += (time.time()-start_time)

                    if 'ph_rgb' in s_name:
                        transQ.put((os.path.join(args.save_data_path,'pinhole','{}_{}.jpg'.format(s_name, cur_frame)), data_array))
                    elif 'ph_depth' in s_name:
                        transQ.put((os.path.join(args.save_data_path,'pinhole','{}_{}.npz'.format(s_name, cur_frame)), data_array))
                    elif 'cm_rgb' in s_name:
                        transQ.put((os.path.join(args.save_data_path,'cubemap','{}_{}.jpg'.format(s_name, cur_frame)), data_array))
                    elif 'cm_depth' in s_name:
                        transQ.put((os.path.join(args.save_data_path,'cubemap','{}_{}.npz'.format(s_name, cur_frame)), data_array))
                transQ.join()

                if frame_counter >= config_settings['ignore_frames']:
                    write_strs.append(f'\n| {cur_frame} | {str(cur_timestamp)}  | {str(cur_ex_matrix)}  |')   
                cur_frame += 1
                frame_counter += 1
                logger.info('Processed Frames: (%d)/(%d) | Data Prepare Time_use: %fs | Total one frame time_use: %fs',frame_counter,config_settings['save_frames']+config_settings['ignore_frames'], data_pre_time/len(sensor_actors),time.time()-total_start_time)

            except Empty:
                logger.warning("Some of the sensor information is missed!")

    finally:
        
        world.apply_settings(original_settings)
        tm_setting_list = config_settings['scene_config']["traffic_mananger_setting"]
        for tm_setting in tm_setting_list:
            tm = client.get_trafficmanager(tm_setting["port"])
            tm.set_synchronous_mode(False)
        
        logger.info('Destroying %d sensors' % len(sensor_actors))
        for sensor in sensor_actors:
            sensor.destroy()

        logger.info('destroying %d vehicles' % len(npc_vehicle_list))
        client.apply_batch([carla.command.DestroyActor(x) for x in npc_vehicle_list])

        for i in range(0, len(npc_walker_id), 2):
            npc_walker_actors[i].stop()
        
        logger.info('destroying %d walkers' % len(npc_walker_list))
        client.apply_batch([carla.command.DestroyActor(x) for x in npc_walker_id])

        with open(os.path.join(args.save_data_path,'external.txt'),'w') as f:
            f.writelines(write_strs)
        time.sleep(0.5)
        
        

def consumuer(transQ:JoinableQueue):
    while True :
        path, data= transQ.get()
        if 'cm_rgb' in path:
            cv2.imwrite(path,data, [int(cv2.IMWRITE_JPEG_QUALITY),97])
        elif 'cm_depth' in path:
            np.savez(path,data)
        elif 'ph_depth' in path:
            np.savez(path,data)
        else:
            cv2.imwrite(path,data)
        transQ.task_done()
    


if __name__ == '__main__':

    args = get_args()
    try:
        transQ = JoinableQueue()

        prod = Process(target=producer,args=(transQ, args))
        con_list = []
        for i in range(min(args.num_workers,16)):
            con = Process(target=consumuer,args=(transQ,))
            con.daemon = True
            con_list.append(con)

        prod.start()
        for con in con_list:
            con.start() 
        
        prod.join()  # 等待生产和消费完成，主线程结束
    
    except ProcessError as e:
        print('Process Error:',str(e))
    
    finally:
        print('Exit Main Process')
    