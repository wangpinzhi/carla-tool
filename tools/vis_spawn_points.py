import sys,os
parent_path = os.path.abspath(os.path.join(__file__, *(['..'] * 2)))
sys.path.insert(0, parent_path)

from utilities import get_args

import carla,logging,cv2

if __name__ == '__main__':

    args = get_args()
    logging.basicConfig(format='[%(levelname)s]: %(message)s', level=logging.INFO)

    # 创建client
    client = carla.Client(args.server_ip, args.server_port)
    client.set_timeout(10.0)

    # 获取world
    world = client.get_world()

    # 获取所有 spawn points
    spawn_points = world.get_map().get_spawn_points()

    logging.info('Found %d recommanded spawn points',len(spawn_points))

    for i, spawn_point in enumerate(spawn_points):
        world.debug.draw_string(spawn_point.location, str(i), life_time=10)