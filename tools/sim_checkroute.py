
import sys,os
parent_path = os.path.abspath(os.path.join(__file__, *(['..'] * 2)))
sys.path.insert(0, parent_path)


import carla
import random,math
from utilities import get_args, config_sim_scene
import logging,time,json

def main():

    args = get_args()
    logging.basicConfig(format='%(levelname)s %(message)s', level=logging.INFO)
    with open(args.config_path,'r') as f:
        config_settings = json.load(f)
    
    random.seed(config_settings["random_seed"])

    try:
        
        hero_actor, client, original_settings, npc_vehicle_list, npc_walker_list, npc_walker_id, npc_walker_actors = config_sim_scene(args)
        world = client.get_world()
        spectator = world.get_spectator() 

        while True:
            try:
                # Tick the server
                world.tick()

                # 将CARLA界面摄像头跟随ego_vehicle动
                loc = hero_actor.get_transform().location + carla.Location(x=0,y=0,z=1.25)
                rot = hero_actor.get_transform().rotation 
                # 车后视角
                spectator.set_transform(carla.Transform(loc,carla.Rotation(roll=rot.roll,yaw=rot.yaw,pitch=-20)))
                
                # spectator.set_transform(carla.Transform(carla.Location(x=loc.x,y=loc.y,z=35),carla.Rotation(yaw=0,pitch=-90,roll=0)))           
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

        hero_actor.destroy()
        logging.info("Destroy Actor: hero_actor")

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