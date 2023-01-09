import sys,os
parent_path = os.path.abspath(os.path.join(__file__, *(['..'] * 2)))
sys.path.insert(0, parent_path)

import carla,logging,re,argparse

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


if __name__ == '__main__':

    args = get_args()
    logging.basicConfig(format='[%(levelname)s]: %(message)s', level=logging.INFO)

    # 创建client
    client = carla.Client(args.server_ip, args.server_port)
    client.set_timeout(10.0)

    # 获取world
    world = client.get_world()

    # 获取当前map
    # reg = re.compile('Town\d\d')
    # old_map = re.findall(reg,world.get_map().name)
    logging.info('world map: %s', world.get_map().name)

    # 获取所有 spawn points
    spawn_points = world.get_map().get_spawn_points()
    walker_spawn_location = carla.Location(x=-36,y=36,z=0.6)

    logging.info('Found %d recommanded spawn points',len(spawn_points))

    for i, spawn_point in enumerate(spawn_points):
        world.debug.draw_string(spawn_point.location, str(f'i:{i}, x:{spawn_point.location.x}, y:{spawn_point.location.y}'), life_time=10)
    world.debug.draw_string(walker_spawn_location, 'walker', color=carla.Color(0,255,0,255),life_time=20)