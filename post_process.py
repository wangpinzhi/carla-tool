import numpy as np
import cv2
import os
import argparse

from tqdm import tqdm

from scipy.spatial.transform import Rotation as R
import torch
from torch.utils.data import DataLoader

from package_postprocessing_tools import ClassCubemapProcesser
from package_postprocessing_tools import ClassCubemapDataset
from package_carla_manager import function_get_sensor_json_list

def get_args():
    parser = argparse.ArgumentParser(description='scripts for post-processing raw data')
    parser.add_argument('--num_workers', type=int, default=2,
                        help='threads for dataloader.')
    parser.add_argument('--gpu', type=int, default=None,
                        help='Specify the gpu to use, otherwise use the cpu.')
    parser.add_argument('--batch_size', type=int, default=1,
                        help='Specify the number of gpu parallel processing.')
    parser.add_argument('--sensor_config_json', type=str,
                        help='Specify post-processing scenarios.')
    parser.add_argument('--raw_data_dir', type=str, 
                        help='path of the scenario raw data.')
    parser.add_argument('--save_dir', type=str)
    return parser.parse_args()

def main(args):

    cube_order = ['back_data', 'right_data', 'front_data', 'left_data' , 'up_data', 'down_data']
    sensors = function_get_sensor_json_list(args.sensor_config_json)
    print(len(sensors))
    for sensor in sensors:
        if 'post_process' not in sensor.keys():
            continue
        name_id = sensor['name_id']
        cam_model = sensor['post_process']['cam_model']
        target_fov = sensor['post_process']['fov']
        target_width = sensor['post_process']['width']
        target_height = sensor['post_process']['height']
        target_format = sensor['post_process']['format']
        target_rot = None
        print('[Process {}] CamModel:{}, ImageH: {}, ImageW:{}, ImageFov:{}, ImageFormat:{}'.format(name_id,
                                                                                                    cam_model,
                                                                                                    target_height,
                                                                                                    target_width,
                                                                                                    target_fov,
                                                                                                    target_format))
        if cam_model == 'erp':
            continue

        if 'rotation' in sensor.keys():
            rot = sensor['post_process']['rotation']
            target_rot = R.from_euler(seq=rot['seq'], angles=rot['angles'], degrees=rot['degrees'])
            target_rot = target_rot.as_matrix().astype(np.float32)

        post_dataset = ClassCubemapDataset(
            parameter_cubemap_dir=os.path.join(args.raw_data_dir,f'{name_id}'),
            parameter_cubemap_order=cube_order,
            parameter_target_model=cam_model,
            parameter_target_format=target_format,
        )
        post_dataloader = DataLoader(dataset=post_dataset, batch_size=args.batch_size, num_workers=args.num_workers)
        
        device = 'cpu'
        if args.gpu is not None:
            torch.cuda.empty_cache()
            device = torch.device('cuda:{}'.format(args.gpu))

        post_processer = ClassCubemapProcesser(
            parameter_target_type=cam_model,
            parameter_target_height=target_height,
            parameter_target_width=target_width,
            parameter_target_fov=target_fov,
            parameter_rot_matrix=target_rot,
            parameter_device=device,
            parameter_batchsize=args.batch_size,
        )

        save_dir = os.path.join(args.save_dir, f'{name_id}')
        os.makedirs(save_dir, exist_ok=True)
        
        for item in tqdm(post_dataloader):
            results = post_processer.trans(item['cube'], cube_order)
            for i in range(args.batch_size):
                img = results[i].cpu().numpy()
                img = img.astype(np.uint8)
                img = img.transpose(1, 2, 0)
                cv2.imwrite(os.path.join(save_dir,item['save_name'][i]), img)

if __name__ == '__main__':
    args = get_args()
    main(args)



    