import carla


def function_set_weather(parameter_world: carla.World,
                         parameter_weather_configs: dict) -> None:
    """
    This function is used to set world weather according to the configs which
    are obtained from the file.

    :param parameter_world: world for set weather
    :param parameter_weather_configs: Include weather parameters
    :return:
    """

    local_val_weather = parameter_world.get_weather()

    if 'cloudiness' in parameter_weather_configs.keys():
        local_val_weather.cloudiness = parameter_weather_configs['cloudiness']
    if 'precipitation' in parameter_weather_configs.keys():
        local_val_weather.precipitation = parameter_weather_configs['precipitation']
    if 'precipitation_deposits' in parameter_weather_configs.keys():
        local_val_weather.precipitation_deposits = parameter_weather_configs['precipitation_deposits']
    if 'wind_intensity' in parameter_weather_configs.keys():
        local_val_weather.wind_intensity = parameter_weather_configs['wind_intensity']
    if 'sun_azimuth_angle' in parameter_weather_configs.keys():
        local_val_weather.sun_azimuth_angle = parameter_weather_configs['sun_azimuth_angle']
    if 'sun_altitude_angle' in parameter_weather_configs.keys():
        local_val_weather.sun_altitude_angle = parameter_weather_configs['sun_altitude_angle']
    if 'fog_density' in parameter_weather_configs.keys():
        local_val_weather.fog_density = parameter_weather_configs['fog_density']
    if 'fog_distance' in parameter_weather_configs.keys():
        local_val_weather.fog_distance = parameter_weather_configs['fog_distance']
    if 'fog_falloff' in parameter_weather_configs.keys():
        local_val_weather.fog_falloff = parameter_weather_configs['fog_falloff']
    if 'wetness' in parameter_weather_configs.keys():
        local_val_weather.wetness = parameter_weather_configs['wetness']
    if 'scattering_intensity' in parameter_weather_configs.keys():
        local_val_weather.scattering_intensity = parameter_weather_configs['scattering_intensity']
    if 'mie_scattering_scale' in parameter_weather_configs.keys():
        local_val_weather.mie_scattering_scale = parameter_weather_configs['mie_scattering_scale']
    if 'rayleigh_scattering_scale' in parameter_weather_configs.keys():
        local_val_weather.rayleigh_scattering_scale = parameter_weather_configs['rayleigh_scattering_scale']
    if 'dust_storm' in parameter_weather_configs.keys():
        local_val_weather.dust_storm = parameter_weather_configs['dust_storm']

    parameter_world.set_weather(local_val_weather)
    