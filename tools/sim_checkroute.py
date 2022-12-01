
import sys,os
parent_path = os.path.abspath(os.path.join(__file__, *(['..'] * 2)))
sys.path.insert(0, parent_path)


import carla
import random
from utilities import get_args, config_sim_scene
import logging

def main():

    args = get_args()
    logging.basicConfig(format='%(levelname)s%(message)s', level=logging.INFO)
    random.seed(5)

    try:
        
        hero_actor, spectator, client, original_settings = config_sim_scene(args)

        traffic_manager = client.get_trafficmanager(args.traffic_manager_port)
        world = client.get_world()
        
        while True:
            
            # Tick the server
            world.tick()

            # 将CARLA界面摄像头跟随ego_vehicle动
            loc = hero_actor.get_transform().location
            spectator.set_transform(carla.Transform(carla.Location(x=loc.x,y=loc.y,z=35),carla.Rotation(yaw=0,pitch=-90,roll=0)))  
    
    finally:
        
        world.apply_settings(original_settings)
        traffic_manager.set_synchronous_mode(False)

        hero_actor.destroy()
        logging.info("Destroy Actor: hero_actor")

        spectator.destroy()
        logging.info("Destroy Actor: spectator")


if __name__ == '__main__':
    main()