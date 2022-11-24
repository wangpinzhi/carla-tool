from queue import Queue

'''
callback function for put data in queue
'''
def pinhole_data_callback(sensor_data, sensor_queue:Queue, sensor_name, save_data_path):
    
    sensor_queue.put((sensor_name, sensor_data.frame, sensor_data))


def cubemap_data_callback(sensor_data, sensor_queue:Queue, sensor_name:str, view:str, save_data_path):

    sensor_queue.put((sensor_name+'_'+view, sensor_data.frame, sensor_data))