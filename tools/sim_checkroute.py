
import sys,os
parent_path = os.path.abspath(os.path.join(__file__, *(['..'] * 2)))
sys.path.insert(0, parent_path)


import carla
import random,math
from utilities import get_args, config_sim_scene
import logging,time

def main():

    args = get_args()
    logging.basicConfig(format='%(levelname)s %(message)s', level=logging.INFO)
    random.seed(5)

    try:
        
        hero_actor, spectator, hero_route, client, original_settings, npc_vehicle_list, npc_walker_list, npc_walker_id, npc_walker_actors = config_sim_scene(args)

        traffic_manager = client.get_trafficmanager(args.traffic_manager_port)
        world = client.get_world()

        while True:
            
            if math.sqrt((hero_actor.get_location().x-hero_route[-1].x)**2+(hero_actor.get_location().y-hero_route[-1].y)**2)<0.5 :# <0.5m
                break

            # Tick the server
            world.tick()

            # 将CARLA界面摄像头跟随ego_vehicle动
            loc = hero_actor.get_transform().location
            rot = hero_actor.get_transform().rotation
            spectator.set_transform(carla.Transform(carla.Location(x=loc.x,y=loc.y,z=35),carla.Rotation(yaw=0,pitch=-90,roll=0)))

            # Set parameters of TM vehicle control, we don't want lane changes
            traffic_manager.update_vehicle_lights(hero_actor, True)
            traffic_manager.random_left_lanechange_percentage(hero_actor, 0)
            traffic_manager.random_right_lanechange_percentage(hero_actor, 0)
            traffic_manager.auto_lane_change(hero_actor, False)
            traffic_manager.set_path(hero_actor, hero_route) # 设置车辆行驶路线
            
    
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

        time.sleep(1)


if __name__ == '__main__':
    main()