from PIL import Image
import torch
import torch.nn.functional as F
from torchvision import transforms
import numpy as np

baseline = 1.0
cam_w = 640
cam_fov = np.deg2rad(190)
cam_K = cam_w / cam_fov
cam1_proj_mat = np.array([[ 1., 0., 0., 0.],
                          [ 0., 1., 0., 0.],
                          [ 0., 0., 1.,-baseline],
                          [ 0., 0., 0., 1. ]])

# generate warp grid
def get_warp_grids(hypo_depth:np.array, proj_mat, erp_h:int=320):
    
    erp_w = erp_h*2
    grid_w, grid_h = np.meshgrid(range(erp_w), range(erp_h))
    grid_lat = np.pi*(grid_h/erp_h-0.5)
    grid_lon = 2*np.pi*(grid_w/erp_w-0.5)
    grids = []
    for depth in hypo_depth:
        coordY = np.sin(grid_lat)*depth
        coordX = np.cos(grid_lat)*np.sin(grid_lon)*depth
        coordZ = np.cos(grid_lat)*np.cos(grid_lon)*depth
        coordXYZ_1 = np.concatenate([coordX[...,None], coordY[...,None], coordZ[...,None], np.ones_like(coordX[...,None])], axis=-1)
        coordXYZ_1 = np.matmul(proj_mat, coordXYZ_1[...,None]).squeeze(-1)
        coordXYZ = coordXYZ_1[..., 0:3]
        cam_theta = np.arccos(coordXYZ[..., 2]/np.sqrt(coordXYZ[..., 0]**2+coordXYZ[..., 1]**2+coordXYZ[..., 2]**2+1e-8))
        invalid_mask = cam_theta > (cam_fov/2)
        cam_rho = cam_K * cam_theta
        camX = cam_rho * coordXYZ[...,0] / np.sqrt(coordXYZ[..., 0]**2+coordXYZ[..., 1]**2+1e-8) * 2 / cam_w
        camY = cam_rho * coordXYZ[...,1] / np.sqrt(coordXYZ[..., 0]**2+coordXYZ[..., 1]**2+1e-8) * 2 / cam_w
        grid = np.concatenate([camX[...,None], camY[...,None]], axis=-1)
        grid[invalid_mask]=-2.0
        grids.append(grid)

    return np.array(grids)

def main():
    hypo_depth = np.array(range(32)) + 1
    hypo_depth = hypo_depth*baseline
    warp_grids = get_warp_grids(hypo_depth, cam1_proj_mat)
    warp_grid_z = np.zeros_like(warp_grids)[..., 0:1]
    warp_grids = np.concatenate([warp_grids, warp_grid_z], axis=-1)
    warp_grids = torch.from_numpy(warp_grids).float()

    fe_img = Image.open(r'output\omnitest\post_data\fisheye190\fe_rgb1_0.png')
    fe_tensor = transforms.ToTensor()(fe_img)
    
    warp_erp_tensor = F.grid_sample(fe_tensor.unsqueeze(0).unsqueeze(2), warp_grids.unsqueeze(0), mode='bilinear', align_corners=True)
    warp_erp_array = (warp_erp_tensor.numpy()*255)
    warp_erp_array = warp_erp_array.astype(np.uint8)
    for i, depth in enumerate(hypo_depth):
        warp_img = warp_erp_array[0, :, i]
        warp_img = warp_img.transpose((1,2,0))
        Image.fromarray(warp_img).save(rf'temp\baseline1.0_depth1.0\{i}.png')


if __name__ == '__main__':
    main()

