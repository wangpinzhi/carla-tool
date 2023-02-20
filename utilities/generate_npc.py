import logging
import random
import carla




def get_actor_blueprints(world, filter, generation):
    bps = world.get_blueprint_library().filter(filter)

    if generation.lower() == "all":
        return bps

    # If the filter returns only one bp, we assume that this one needed
    # and therefore, we ignore the generation
    if len(bps) == 1:
        return bps

    try:
        int_generation = int(generation)
        # Check if generation is in available generations
        if int_generation in [1, 2]:
            bps = [x for x in bps if int(
                x.get_attribute('generation')) == int_generation]
            return bps
        else:
            print("   Warning! Actor Generation is not valid. No actor will be spawned.")
            return []
    except:
        print("   Warning! Actor Generation is not valid. No actor will be spawned.")
        return []


def generate_vehicle(client, gen_list, args):

    batch = []

    SpawnActor = carla.command.SpawnActor
    SetAutopilot = carla.command.SetAutopilot
    FutureActor = carla.command.FutureActor

    world = client.get_world()
    blueprint_library = world.get_blueprint_library()
    spawn_points = world.get_map().get_spawn_points()

    for vehicle_setting in gen_list:
        if vehicle_setting["spawn_points_index"] == -1:
            loc_x = vehicle_setting["spawn_points"]['loc_x']
            loc_y = vehicle_setting["spawn_points"]['loc_y']
            loc_z = vehicle_setting["spawn_points"]['loc_z']
            rot_p = vehicle_setting["spawn_points"]['rot_p']
            rot_y = vehicle_setting["spawn_points"]['rot_y']
            rot_r = vehicle_setting["spawn_points"]['rot_r']
            spwan_point = carla.Transform(carla.Location(loc_x,loc_y,loc_z),carla.Rotation(rot_p,rot_y,rot_r))
        else:
            spwan_point = spawn_points[vehicle_setting["spawn_points_index"]]

        # get blueprint 
        if vehicle_setting['random_bluerint']:
            vehicle_bp = random.choice(blueprint_library.filter('vehicle.*.*'))
        else:
            vehicle_bp = blueprint_library.find(vehicle_setting["blueprint"])
        
        batch.append(
            SpawnActor(vehicle_bp, spwan_point).then(
                SetAutopilot(FutureActor, vehicle_setting["autopilot"], vehicle_setting["tm_port"])
            )
        )
    
    return batch

def generate_walker(client, gen_list, args):

    world = client.get_world()
    SpawnActor = carla.command.SpawnActor
    walkers_list = []
    all_id = []

    percentagePedestriansRunning=0.0
    percentagePedestriansCrossing=0.0
    
    # spawn the walker object
    batch = []
    walker_speed = []

    for walker_setting in gen_list:
        if walker_setting['random_bluerint']:
            walker_bp = random.choice(world.get_blueprint_library().filter('walker.pedestrian.*'))
        else:
            walker_bp = world.get_blueprint_library().find(walker_setting["blueprint"])
        # set as not invincible
        if walker_bp.has_attribute('is_invincible'):
            walker_bp.set_attribute('is_invincible', 'false')

        # set the max speed
        if walker_bp.has_attribute('speed'):
            if (random.random() > percentagePedestriansRunning):
                # walking
                walker_speed.append(walker_bp.get_attribute('speed').recommended_values[1])
            else:
                # running
                walker_speed.append(walker_bp.get_attribute('speed').recommended_values[2])
        else:
            print("Walker has no speed")
            walker_speed.append(0.0)
        
        walker_transform = carla.Transform(
            carla.Location(x=walker_setting["spawn_points_x"],y=walker_setting["spawn_points_y"],z=walker_setting["spawn_points_z"]),
            carla.Rotation(roll=walker_setting["spawn_points_roll"],pitch=walker_setting["spawn_points_pitch"],yaw=walker_setting["spawn_points_yaw"])
        ) 
        batch.append(SpawnActor(walker_bp,walker_transform))

    results = client.apply_batch_sync(batch, True)
    walker_speed2 = []
    for i in range(len(results)):
        if results[i].error:
            logging.error(results[i].error)
        else:
            walkers_list.append({"id": results[i].actor_id})
            walker_speed2.append(walker_speed[i])
    walker_speed = walker_speed2
        
    # spawn the walker controller
    batch = []
    walker_controller_bp = world.get_blueprint_library().find('controller.ai.walker')
    for i in range(len(walkers_list)):
        batch.append(SpawnActor(walker_controller_bp, carla.Transform(
            carla.Location(x=walker_setting["spawn_points_x"],y=walker_setting["spawn_points_y"],z=walker_setting["spawn_points_z"]+100),
            carla.Rotation(0,0,0)
        ), walkers_list[i]["id"]))
    results = client.apply_batch_sync(batch, True)
    for i in range(len(results)):
        if results[i].error:
            logging.error(results[i].error)
        else:
            walkers_list[i]["con"] = results[i].actor_id
    
    # put together the walkers and controllers id to get the objects from their id
    for i in range(len(walkers_list)):
        all_id.append(walkers_list[i]["con"])
        all_id.append(walkers_list[i]["id"])
    all_actors = world.get_actors(all_id)

    # wait for a tick to ensure client receives the last transform of the walkers we have just created
    if not world.get_settings().synchronous_mode:
        world.wait_for_tick()
    else:
        world.tick()
        
    # 5. initialize each controller and set target to walk to (list is [controler, actor, controller, actor ...])
    # set how many pedestrians can cross the road
    world.set_pedestrians_cross_factor(percentagePedestriansCrossing)
    for i in range(0, len(all_id), 2):
        # start walker
        all_actors[i].start()
        # set walk to random point
        all_actors[i].go_to_location(world.get_random_location_from_navigation())
        # max speed
        all_actors[i].set_max_speed(float(walker_speed[int(i/2)]))
    
    return walkers_list, all_id, all_actors


def random_generate_vehicle(client, world, traffic_manager, transform_ego, args):

    # 获取所有车辆蓝图
    npc_blueprints_vehicle = get_actor_blueprints(
        world, args.filterv, args.generationv)
    npc_blueprints_vehicle = sorted(
        npc_blueprints_vehicle, key=lambda bp: bp.id)

    # filter invisiable car
    npc_blueprints_vehicle = [
        x for x in npc_blueprints_vehicle if not x.id.endswith('invisiable')]

    # get available spawn points
    npc_spawn_points = world.get_map().get_spawn_points()
    number_of_spawn_points = len(npc_spawn_points)

    # 检查生成目标车辆npc数目是否过多
    if args.number_of_vehicles < number_of_spawn_points:
        random.shuffle(npc_spawn_points)
    elif args.number_of_vehicles > number_of_spawn_points:
        msg = 'requested %d vehicles, but could only find %d spawn points'
        logging.warning(msg, args.number_of_vehicles, number_of_spawn_points)
        args.number_of_vehicles = number_of_spawn_points

    SpawnActor = carla.command.SpawnActor
    SetAutopilot = carla.command.SetAutopilot
    FutureActor = carla.command.FutureActor

    # --------------
    # Spawn vehicles
    # --------------
    batch = []
    vehicles_list = []
    for n, transform in enumerate(npc_spawn_points):
        if n >= args.number_of_vehicles:
            break
        blueprint = random.choice(npc_blueprints_vehicle)

        if blueprint.has_attribute('color'):
            color = random.choice(blueprint.get_attribute('color').recommended_values)
            blueprint.set_attribute('color', color)
        if blueprint.has_attribute('driver_id'):
            driver_id = random.choice(blueprint.get_attribute('driver_id').recommended_values)
            blueprint.set_attribute('driver_id', driver_id)
        blueprint.set_attribute('role_name', f'npc{n}')

        # spawn the cars and set their autopilot and light state all together
        if transform != transform_ego:
            batch.append(SpawnActor(blueprint, transform)
                .then(SetAutopilot(FutureActor, True, traffic_manager.get_port())))

    for response in client.apply_batch_sync(batch, args.sync_mode):
        if response.error:
            logging.error(response.error)
        else:
            vehicles_list.append(response.actor_id)

    return vehicles_list

def random_generate_walker(client, world,  args):
    
    SpawnActor = carla.command.SpawnActor
    npc_blueprints_walker = get_actor_blueprints(world, args.filterw, args.generationw)
    percentagePedestriansRunning = 0.0      # how many pedestrians will run
    percentagePedestriansCrossing = 0.0     # how many pedestrians will walk through the road
    all_id = []
    walkers_list = []

    if args.seedw:
        world.set_pedestrians_seed(args.seedw)
        random.seed(args.seedw)
    
    
    # 1. take all the random locations to spawn
    spawn_points = []
    for i in range(args.number_of_walkers):
        spawn_point = carla.Transform()
        loc = world.get_random_location_from_navigation()
        if (loc != None):
            spawn_point.location = loc
            spawn_points.append(spawn_point)
    
    # 2. we spawn the walker object
    batch = []
    walker_speed = []
    for spawn_point in spawn_points:
        walker_bp = random.choice(npc_blueprints_walker)
        # set as not invincible
        if walker_bp.has_attribute('is_invincible'):
            walker_bp.set_attribute('is_invincible', 'false')
        # set the max speed
        if walker_bp.has_attribute('speed'):
            if (random.random() > percentagePedestriansRunning):
                # walking
                walker_speed.append(walker_bp.get_attribute('speed').recommended_values[1])
            else:
                # running
                walker_speed.append(walker_bp.get_attribute('speed').recommended_values[2])
        else:
            print("Walker has no speed")
            walker_speed.append(0.0)
        batch.append(SpawnActor(walker_bp, spawn_point))

    results = client.apply_batch_sync(batch, True)
    walker_speed2 = []
    for i in range(len(results)):
        if results[i].error:
            logging.error(results[i].error)
        else:
            walkers_list.append({"id": results[i].actor_id})
            walker_speed2.append(walker_speed[i])
    walker_speed = walker_speed2
        
    # 3. we spawn the walker controller
    batch = []
    walker_controller_bp = world.get_blueprint_library().find('controller.ai.walker')
    for i in range(len(walkers_list)):
        batch.append(SpawnActor(walker_controller_bp, carla.Transform(), walkers_list[i]["id"]))
    results = client.apply_batch_sync(batch, True)
    for i in range(len(results)):
        if results[i].error:
            logging.error(results[i].error)
        else:
            walkers_list[i]["con"] = results[i].actor_id
    
    # 4. we put together the walkers and controllers id to get the objects from their id
    for i in range(len(walkers_list)):
        all_id.append(walkers_list[i]["con"])
        all_id.append(walkers_list[i]["id"])
    all_actors = world.get_actors(all_id)

    # wait for a tick to ensure client receives the last transform of the walkers we have just created
    if not args.sync_mode:
        world.wait_for_tick()
    else:
        world.tick()
        
    # 5. initialize each controller and set target to walk to (list is [controler, actor, controller, actor ...])
    # set how many pedestrians can cross the road
    world.set_pedestrians_cross_factor(percentagePedestriansCrossing)
    for i in range(0, len(all_id), 2):
        # start walker
        all_actors[i].start()
        # set walk to random point
        all_actors[i].go_to_location(world.get_random_location_from_navigation())
        # max speed
        all_actors[i].set_max_speed(float(walker_speed[int(i/2)]))
    
    return walkers_list, all_id, all_actors