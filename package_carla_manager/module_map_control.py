import carla


def function_set_map(parameter_client: carla.Client,
                     parameter_map: str):

    # get current map name,
    local_current_map = parameter_client.get_world().get_map().name.spilt()
    
