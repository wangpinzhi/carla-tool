from queue import Queue
import os
import carla

'''
callback function for put data in queue
'''
def pinhole_data_callback(sensor_data, sensor_queue:Queue, sensor_name, save_data_path):

    sensor_data.save_to_disk(os.path.join(save_data_path,'{}_{}_{}.jpg'.format(sensor_name, sensor_data.frame, sensor_data.timestamp)))
    
    sensor_queue.put((sensor_name, sensor_data.frame))


def cubemap_data_callback(sensor_data, sensor_queue:Queue, sensor_name:str, view:str, save_data_path):

    if 'depth' in sensor_name:
        if sensor_name == 'cm_depth1': # record extrins
            with open(os.path.join(save_data_path,'external.txt'),'a') as f:
                f.write('\n|  {}  |   {}  |'.format(sensor_data.frame,str(sensor_data.transform.get_matrix())))
                 
        sensor_data.save_to_disk(os.path.join(save_data_path,'{}_{}_{}_{}.png'.format(sensor_name,view,sensor_data.frame,sensor_data.timestamp)),color_converter=carla.ColorConverter.Depth)
    elif 'rgb' in sensor_name:
        sensor_data.save_to_disk(os.path.join(save_data_path,'{}_{}_{}_{}.jpg'.format(sensor_name,view,sensor_data.frame,sensor_data.timestamp)))  

    sensor_queue.put((sensor_name+'_'+view, sensor_data.frame))