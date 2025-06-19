import cv2
import numpy as np
import cv2
import os
from tqdm.auto import tqdm

path = './raw_data/random_objects' # 场景根目录
frames = 3500 # 场景帧数

def depth2disp(depth, baseline, fov, width):
    focal = width / (2*np.tan(fov/2)) # fov 单位rad
    disp = focal*baseline/depth
    return disp

# for i, frame in enumerate(tqdm(range(frames))):
#     left_path = os.path.join(path, 'ph_rgb0', f'ph_rgb0_{frame}.npz')
#     right_path = os.path.join(path, 'ph_rgb1', f'ph_rgb1_{frame}.npz')
#     gt_path = os.path.join(path, 'ph_depth0', f'ph_depth0_{frame}.npz')

#     left_array = np.load(left_path)['data'] # (H, W, 3) BGR
#     cv2.imwrite(f'RandomOBJs/scene3/left/left_frame_{i:0>4d}.jpg', left_array.astype(np.uint8))
#     right_array = np.load(right_path)['data'] # (H, W, 3) BGR
#     cv2.imwrite(f'RandomOBJs/scene3/right/right_frame_{i:0>4d}.jpg', right_array.astype(np.uint8))
    
#     gt_array = np.load(gt_path)['data'] # (H, W, 3) BGR
#     # 从编码还原深度
#     gt_array = gt_array.astype(np.float32)
#     normalized = (gt_array[:,:,2] + gt_array[:,:,1] * 256 + gt_array[:,:,0] * 256 * 256) / (256 * 256 * 256 - 1) # (H, W)
#     in_meters = 1000 * normalized # 以米为单位的 平面深度
#     np.save(f'./RandomOBJs/scene3/depth_gt/depth_frame_{i:0>4d}.npy', in_meters)

#     disp = depth2disp(in_meters, 0.09, np.deg2rad(120), 640).astype(np.float32)
#     print(disp.shape)
#     gridX, gridY = np.meshgrid(
#         np.linspace(0, 639, 640, dtype=np.float32),
#         np.linspace(0, 359, 360, dtype=np.float32),
#     )
#     warp_img = cv2.remap(right_array.astype(np.float32), gridX-disp, gridY, cv2.INTER_LINEAR)
#     warp_img = warp_img.astype(np.uint8)
#     cv2.imshow('warp_img', warp_img)
#     cv2.waitKey(-1)
#     print(warp_img)

#     print(disp.max())
#     exit(0)
    # vis_disp = 255 - cv2.convertScaleAbs(in_meters, alpha=255/64.0)
    # vis_disp = cv2.applyColorMap(vis_disp, cv2.COLORMAP_JET)

    # vis_depth = 255 - cv2.convertScaleAbs(in_meters, alpha=25.5, beta=0.3)
    # vis_depth = cv2.applyColorMap(vis_depth, cv2.COLORMAP_JET)

    # save_img = np.concatenate([left_array, vis_depth], axis=1) # (H, 2*W, 3)

    # cv2.imwrite(f'temp/{i}.png', save_img)
    # cv2.waitKey(50)

if __name__ =='__main__':
    
    raw_data = np.load(r'D:\heterogenenous-data-carla-main\output\timeclip\raw_data\timeclip\ph_depth0\ph_depth0_0.npz')['data'] # BGR
    
    raw_data = raw_data.astype(np.float32)

    normalized = (raw_data[:,:,2] + raw_data[:,:,1] * 256 + raw_data[:,:,0] * 256 * 256) / (256 * 256 * 256 - 1) # (H, W)
    
    in_meters = 1000 * normalized # 以米为单位的 平面深度
    
    vis_depth = (1-in_meters / 10.0) * 255

    cv2.imwrite('img.png', vis_depth.astype(np.uint8))