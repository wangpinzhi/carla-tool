
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
            # 车后视角
            spectator.set_transform(carla.Transform((loc + carla.Location(x=0, y=-5, z=2)), carla.Rotation(yaw=rot.yaw, pitch=-10+rot.pitch, roll=rot.roll)))
            
            # spectator.set_transform(carla.Transform(carla.Location(x=loc.x,y=loc.y,z=35),carla.Rotation(yaw=0,pitch=-90,roll=0))) 

            # if hero_actor.is_at_traffic_light():
            #    traffic_light = hero_actor.get_traffic_light()
            #    traffic_light.set_state(carla.TrafficLightState.Green)

            
            
    
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