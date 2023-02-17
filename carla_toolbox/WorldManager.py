import carla
import json
import os, random, time

from VehicleManager import VehicleManager
from SensorManager import SensorManager

class WorldManager:

    def __init__(self, host:str, ip:int, root_path:str):
        
        self._client = carla.Client(host,ip)
        self._root_path = root_path
        self._config_path = os.path.join(self._root_path, 'configs')

        # load scene_config.json
        with open(os.path.join(self._config_path,'scene_config.json'),'r') as f:
            self._dict_sceneConfig = json.load(f)
        
        # load sensor_config.json
        with open(os.path.join(self._config_path,'sensor_config.json'),'r') as f:
            self._dict_sensorConfig = json.load(f)

        # set seed
        random.seed(self._dict_sceneConfig['RandomSeed'])

        self._world = self._client.get_world()

        # get world original setting
        self._origin_setting = self._world.get_settings()

        # get blueprints_library
        self._bps_library = self._world.get_blueprint_library()

        # get spawnable points
        self._spawn_points = self._world.get_map().get_spawn_points()
        print(f'Found {len(self._spawn_points)} recommanded spawn points')

        # world map setting
        target_map = self._dict_sceneConfig['Map']
        current_map = (self._world.get_map().name).split('/')[-1]
        if target_map != current_map:
            self._client.load_world(target_map)
            print(f'[load_world] from {current_map} to {target_map}')

        # world weather setting
        dict_weatherParameters = self._dict_sceneConfig['WeatherParameters']
        self._weather = self._world.get_weather()
        self._load_weatherParameters(dict_weatherParameters)

        # vehicle_manager
        self._vm = VehicleManager(self._world)

        # sensor_manager
        self._sm = SensorManager(self._world)
        
    def _spawn_vehicles(self):

        dict_vehicles = self._dict_sceneConfig['Vehicles']

        for dict_vehicle in dict_vehicles:
            
            # set blueprint
            dict_bp = (dict_vehicle['blueprint'])
            vehicle_bp = random.choice(self._bps_library.filter(dict_bp['filter']))
            
            # set transform
            spawn_point = self._spawn_points[dict_vehicle['spawn_point_index']]

            # spawn actor
            ctrl_path = os.path.join(self._config_path,'vehicle_controls',dict_vehicle['ctrl_file']) if dict_vehicle['mode'] == 'File' else None
            self._vm.add_vehicle_actor(dict_vehicle['name_id'],vehicle_bp,spawn_point,dict_vehicle['mode'],ctrl_path)
        
        print(f'Spawn {self._vm.get_vehicle_nums()} / {len(dict_vehicles)} vehicles')
    
    def _spawn_sensors(self, dict_list:list):
        for dict_sensor in dict_list:
            
            # set blueprint
            if dict_sensor['type'] == 'CubemapRGB':
                sensor_bp = self._bps_library.find("sensor.camera.rgb")
                sensor_bp.set_attribute("image_size_x", "{}".format(dict_sensor["width"]))
                sensor_bp.set_attribute("image_size_y", "{}".format(dict_sensor["width"]))
                sensor_bp.set_attribute("sensor_tick", '{}'.format(dict_sensor["sensor_tick"]))
                sensor_bp.set_attribute("fov", '{}'.format(90))
                save_type = 'cubemap'
            elif dict_sensor['type'] == 'CubemapDepth':
                sensor_bp = self._bps_library.find("sensor.camera.depth")
                sensor_bp.set_attribute("image_size_x", "{}".format(dict_sensor["width"]))
                sensor_bp.set_attribute("image_size_y", "{}".format(dict_sensor["width"]))
                sensor_bp.set_attribute("sensor_tick", '{}'.format(dict_sensor["sensor_tick"]))
                sensor_bp.set_attribute("fov", '{}'.format(90))
                save_type = 'cubemap'

            # set transform
            loc_x, loc_y, loc_z = dict_sensor['attach_to']['loc_xyz']
            rot_r, rot_p, rot_y = dict_sensor['attach_to']['rot_rpy']
            sensor_transform = carla.Transform(
                carla.Location(x=loc_x,y=loc_y,z=loc_z),
                carla.Rotation(pitch=rot_p,yaw=rot_y,roll=rot_r)
            )

            # set attacth actor
            attach_actor = self._vm.get_actor_by_nameId(dict_sensor['attach_to']['vehicle_name_id'])
            self._sm.add_sensor_actor(
                dict_sensor['name'],
                sensor_bp,
                dict_sensor['type'],
                sensor_transform,
                attach_actor,
                os.path.join(self._root_path, save_type)
            )

        print(f'Spawn {self._sm.get_sensor_nums()} / {len(dict_list)} sensors')

    def _destroy_all_vehicles(self):
        print(f'Destroy {self._vm.destroy_all_actors()} / {self._vm.get_vehicle_nums()} vehicles')
    
    def _destroy_all_sensors(self):
        print(f'Destroy {self._sm.destroy_all_actors()} / {self._sm.get_sensor_nums()} sensors')
    
    def _load_weatherParameters(self, params:dict):
        if "cloudiness" in params.keys():
            self._weather.cloudiness = params['cloudiness']
        if "precipitation" in params.keys():
            self._weather.precipitation = params['precipitation']
        if "precipitation_deposits" in params.keys():
            self._weather.precipitation_deposits = params['precipitation_deposits']
        if "wind_intensity" in params.keys():
            self._weather.wind_intensity = params['wind_intensity']
        if "sun_azimuth_angle" in params.keys():
            self._weather.sun_azimuth_angle = params['sun_azimuth_angle']
        if "sun_altitude_angle" in params.keys():
            self._weather.sun_altitude_angle = params['sun_altitude_angle']
        if "fog_density" in params.keys():
            self._weather.fog_density = params['fog_density']
        if "fog_distance" in params.keys():
            self._weather.fog_distance = params['fog_distance']
        if "wetness" in params.keys():
            self._weather.wetness = params['wetness']
        if "fog_falloff" in params.keys():
            self._weather.fog_falloff = params['fog_falloff']
        if "scattering_intensity" in params.keys():
            self._weather.scattering_intensity = params['scattering_intensity']
        if "mie_scattering_scale" in params.keys():
            self._weather.mie_scattering_scale = params['mie_scattering_scale']
        if "rayleigh_scattering_scale" in params.keys():
            self._weather.rayleigh_scattering_scale = params['rayleigh_scattering_scale']
        if "dust_storm" in params.keys():
            self._weather.dust_storm = params['dust_storm']
        self._world.set_weather(self._weather)

    def run_collect_data(self):
        
        for dict_part in self._dict_sensorConfig['parts']:

            print(f'|*******Run', dict_part['name'], '*******|')
            self._spawn_vehicles() # spawn vehicles
            self._spawn_sensors(dict_part['sensors']) # spawn sensors

            # set sync mode
            settings = self._world.get_settings()
            settings.synchronous_mode = True
            settings.fixed_delta_seconds = 0.05
            self._world.apply_settings(settings)
        
            # enable vehicle autopilot
            self._vm.enable_autopilot()

            # enable sensor listen
            self._sm.set_sensors_listen()

            frameCounter = 0
            total_save_frames = self._dict_sensorConfig['save_frames']
            try:
                while frameCounter < total_save_frames:
                    start_time = time.time()
                    
                    self._world.tick()
                    self._vm.flush_all_vehicle()
                    self._sm.save_sensors_data(frameCounter)
                    frameCounter += 1

                    use_time = time.time() - start_time

                    print(f'Processed Frames: {frameCounter}/{total_save_frames} | time_use: {use_time}s |')
            except KeyboardInterrupt:
                print('manual stop signal catch')
            finally:
                self._world.apply_settings(self._origin_setting)
                self._destroy_all_sensors()
                self._destroy_all_vehicles()
        
    
        



if __name__ == '__main__':

    wm = WorldManager('127.0.0.1', 2000, r'output\huawei_driving11')
    wm.run_collect_data()
    
    


