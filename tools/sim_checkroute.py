
import sys,os
parent_path = os.path.abspath(os.path.join(__file__, *(['..'] * 2)))
sys.path.insert(0, parent_path)


import carla
import random,argparse
from utilities import config_sim_scene
import logging,time,json

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

def main():

    args = get_args()
    logging.basicConfig(format='%(levelname)s %(message)s', level=logging.INFO)
    with open(args.config_path,'r') as f:
        config_settings = json.load(f)
    
    random.seed(config_settings["random_seed"])

    try:
        
        hero_actor_id, client, original_settings, npc_vehicle_list, npc_walker_list, npc_walker_id, npc_walker_actors = config_sim_scene(args)
        world = client.get_world()
        hero_actor = world.get_actor(hero_actor_id)
        spectator = world.get_spectator()
        frames = 1 
        hero_actor.set_autopilot(True, 8000)
        while True:
            try:
                print(f'frames:{frames}',end='\r',flush=True)
                # Tick the server
                world.tick()
                
                # 将CARLA界面摄像头跟随ego_vehicle动
                loc = hero_actor.get_transform().location + carla.Location(x=0,y=0,z=35) 
                # 车后视角
                spectator.set_transform(carla.Transform(loc,carla.Rotation(pitch=-90)))
                
                # spectator.set_transform(carla.Transform(carla.Location(x=loc.x,y=loc.y,z=35),carla.Rotation(yaw=0,pitch=-90,roll=0)))           
                frames += 1
            except Exception as e:
                print(str(e))
     
    except Exception as e:
                print(str(e))  
    finally:
        
        world.apply_settings(original_settings)
        tm_setting_list = config_settings['scene_config']["traffic_mananger_setting"]
        for tm_setting in tm_setting_list:
            tm = client.get_trafficmanager(tm_setting["port"])
            tm.set_synchronous_mode(False)

        logging.info('destroying %d vehicles' % len(npc_vehicle_list))
        client.apply_batch([carla.command.DestroyActor(x) for x in npc_vehicle_list])

        for i in range(0, len(npc_walker_id), 2):
            npc_walker_actors[i].stop()
        
        logging.info('destroying %d walkers' % len(npc_walker_list))
        client.apply_batch([carla.command.DestroyActor(x) for x in npc_walker_id])

        time.sleep(1)


if __name__ == '__main__':
    main()
    os.system("PAUSE")