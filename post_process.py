import numpy as np
from tqdm import tqdm
import cv2
from scipy.spatial.transform import Rotation as R


from torch.utils.data import DataLoader

from package_postprocessing_tools import ClassCubemapProcesser
from package_postprocessing_tools import ClassCubemapDataset

if __name__ == '__main__':
    
    cube_order = ['back_data', 'right_data', 'front_data', 'left_data' , 'up_data', 'down_data']
    batch_size = 4

    post_dataset = ClassCubemapDataset(
        parameter_cubemap_dir=r'output/huaweI_parking16/raw_data/cm_rgb9',
        parameter_cubemap_order=cube_order,
        parameter_target_type='fe',
        parameter_target_format='jpg',
    )

    post_dataloader = DataLoader(dataset=post_dataset, batch_size=4, num_workers=2)
    
    rot = R.from_euler(seq='ZYX', angles=[90, 0, 0], degrees=True)
    post_processer = ClassCubemapProcesser(
        parameter_target_type='fe',
        parameter_target_height=320,
        parameter_target_width=320,
        parameter_target_fov=190,
        parameter_rot_matrix=rot.as_matrix().astype(np.float32),
        parameter_device='cuda:0',
        parameter_batchsize=batch_size,
    )

    for item in tqdm(post_dataloader):
        # print(item['cube']['front_data'].shape)
        results = post_processer.trans(item['cube'], cube_order)
        for i in range(batch_size):
            img = results[i].cpu().numpy()
            img = img.astype(np.uint8)
            img = img.transpose(1, 2, 0)
            cv2.imwrite('test_out/'+item['save_name'][i], img)
            # img.save()
            # save_image(imgs[i], )
        # print(imgs[0].shape)


    