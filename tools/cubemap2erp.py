import os
import argparse
import torch
import numpy as np
import cv2
import math
from torch.autograd import Variable
from PIL import Image
from tqdm import tqdm

class ClassCubemap2ERP:

    def __init__(self, 
                 parameter_batch_size: int=1, 
                 parameter_cube_width: int=2560,
                 parameter_out_width: int=5120,
                 parameter_use_cuda: bool=False):
        
        self.local_val_out_height = parameter_out_width // 2
        self.local_val_out_width = parameter_out_width
        # Compute the parameters for projection
        self.radius = int(0.5 * parameter_cube_width)
        self.CUDA = parameter_use_cuda

        # Map equirectangular pixel to longitude and latitude
        # NOTE: Make end a full length since arange have a right open bound [a, b)
        theta_start = -1 / 2 * np.pi + (np.pi / parameter_out_width)
        theta_end = 3 / 2 * np.pi
        theta_step = 2 * np.pi / parameter_out_width
        theta_range = torch.arange(theta_start, theta_end, theta_step, dtype=torch.float32)

        phi_start = -0.5 * np.pi + (0.5 * np.pi / self.local_val_out_height)
        phi_end = 0.5 * np.pi
        phi_step = np.pi / self.local_val_out_height
        phi_range = torch.arange(phi_start, phi_end, phi_step)

        # Stack to get the longitude latitude map
        self.theta_map = theta_range.unsqueeze(0).repeat(self.local_val_out_height, 1)
        self.phi_map = phi_range.unsqueeze(-1).repeat(1, parameter_out_width)
        self.lonlat_map = torch.stack([self.theta_map, self.phi_map], dim=-1)

        # Get mapping relation (h, w, face)
        # [back, down, front, left, right, up] => [0, 1, 2, 3, 4, 5]
        # self.orientation_mask = self.get_orientation_mask()

        # Project each face to 3D cube and convert to pixel coordinates
        self.grid, self.orientation_mask = self.getGrid()

        if self.CUDA:
            self.grid.cuda()
            self.orientation_mask.cuda()

    def getGrid(self):
        """
        Input:
          None
        Output:
          grids and masks of 6 faces
        """
        # Get the point of equirectangular on 3D ball
        x_3d = (self.radius * torch.cos(self.phi_map) * torch.cos(self.theta_map)).view(self.local_val_out_height, self.local_val_out_width, 1)
        y_3d = (self.radius * torch.cos(self.phi_map) * torch.sin(self.theta_map)).view(self.local_val_out_height, self.local_val_out_width, 1)
        z_3d = (self.radius * torch.sin(self.phi_map)).view(self.local_val_out_height, self.local_val_out_width, 1)

        self.grid_ball = torch.cat([x_3d, y_3d, z_3d], 2).view(self.local_val_out_height, self.local_val_out_width, 3)

        # Compute the down grid
        radius_ratio_down = torch.abs(z_3d / self.radius)
        grid_down_raw = self.grid_ball / radius_ratio_down.view(self.local_val_out_height, self.local_val_out_width, 1).expand(-1, -1, 3)
        grid_down_w = (-grid_down_raw[:, :, 0].clone() / self.radius).unsqueeze(-1)
        grid_down_h = (-grid_down_raw[:, :, 1].clone() / self.radius).unsqueeze(-1)
        grid_down = torch.cat([grid_down_w, grid_down_h], 2).unsqueeze(0)
        mask_down = (((grid_down_w <= 1) * (grid_down_w >= -1)) * ((grid_down_h <= 1) * (grid_down_h >= -1)) * (
                grid_down_raw[:, :, 2] == self.radius).unsqueeze(2)).float()

        # Compute the up grid
        radius_ratio_up = torch.abs(z_3d / self.radius)
        grid_up_raw = self.grid_ball / radius_ratio_up.view(self.local_val_out_height, self.local_val_out_width, 1).expand(-1, -1, 3)
        grid_up_w = (-grid_up_raw[:, :, 0].clone() / self.radius).unsqueeze(-1)
        grid_up_h = (grid_up_raw[:, :, 1].clone() / self.radius).unsqueeze(-1)
        grid_up = torch.cat([grid_up_w, grid_up_h], 2).unsqueeze(0)
        mask_up = (((grid_up_w <= 1) * (grid_up_w >= -1)) * ((grid_up_h <= 1) * (grid_up_h >= -1)) * (
                grid_up_raw[:, :, 2] == -self.radius).unsqueeze(2)).float()

        # Compute the front grid
        radius_ratio_front = torch.abs(y_3d / self.radius)
        grid_front_raw = self.grid_ball / radius_ratio_front.view(self.local_val_out_height, self.local_val_out_width, 1).expand(-1, -1, 3)
        grid_front_w = (-grid_front_raw[:, :, 0].clone() / self.radius).unsqueeze(-1)
        grid_front_h = (grid_front_raw[:, :, 2].clone() / self.radius).unsqueeze(-1)
        grid_front = torch.cat([grid_front_w, grid_front_h], 2).unsqueeze(0)
        mask_front = (((grid_front_w <= 1) * (grid_front_w >= -1)) * ((grid_front_h <= 1) * (grid_front_h >= -1)) * (
                torch.round(grid_front_raw[:, :, 1]) == self.radius).unsqueeze(2)).float()

        # Compute the back grid
        radius_ratio_back = torch.abs(y_3d / self.radius)
        grid_back_raw = self.grid_ball / radius_ratio_back.view(self.local_val_out_height, self.local_val_out_width, 1).expand(-1, -1, 3)
        grid_back_w = (grid_back_raw[:, :, 0].clone() / self.radius).unsqueeze(-1)
        grid_back_h = (grid_back_raw[:, :, 2].clone() / self.radius).unsqueeze(-1)
        grid_back = torch.cat([grid_back_w, grid_back_h], 2).unsqueeze(0)
        mask_back = (((grid_back_w <= 1) * (grid_back_w >= -1)) * ((grid_back_h <= 1) * (grid_back_h >= -1)) * (
                torch.round(grid_back_raw[:, :, 1]) == -self.radius).unsqueeze(2)).float()

        # Compute the right grid
        radius_ratio_right = torch.abs(x_3d / self.radius)
        grid_right_raw = self.grid_ball / radius_ratio_right.view(self.local_val_out_height, self.local_val_out_width, 1).expand(-1, -1, 3)
        grid_right_w = (-grid_right_raw[:, :, 1].clone() / self.radius).unsqueeze(-1)
        grid_right_h = (grid_right_raw[:, :, 2].clone() / self.radius).unsqueeze(-1)
        grid_right = torch.cat([grid_right_w, grid_right_h], 2).unsqueeze(0)
        mask_right = (((grid_right_w <= 1) * (grid_right_w >= -1)) * ((grid_right_h <= 1) * (grid_right_h >= -1)) * (
                torch.round(grid_right_raw[:, :, 0]) == -self.radius).unsqueeze(2)).float()

        # Compute the left grid
        radius_ratio_left = torch.abs(x_3d / self.radius)
        grid_left_raw = self.grid_ball / radius_ratio_left.view(self.local_val_out_height, self.local_val_out_width, 1).expand(-1, -1, 3)
        grid_left_w = (grid_left_raw[:, :, 1].clone() / self.radius).unsqueeze(-1)
        grid_left_h = (grid_left_raw[:, :, 2].clone() / self.radius).unsqueeze(-1)
        grid_left = torch.cat([grid_left_w, grid_left_h], 2).unsqueeze(0)
        mask_left = (((grid_left_w <= 1) * (grid_left_w >= -1)) * ((grid_left_h <= 1) * (grid_left_h >= -1)) * (
                torch.round(grid_left_raw[:, :, 0]) == self.radius).unsqueeze(2)).float()

        # Face map contains numbers correspond to that face
        orientation_mask = mask_back * 0 + mask_down * 1 + mask_front * 2 + mask_left * 3 + mask_right * 4 + mask_up * 5

        return torch.cat([grid_back, grid_down, grid_front, grid_left, grid_right, grid_up], 0), orientation_mask

    def _ToEquirec(self, batch, mode):
        """
        Input:
          batch: cube map data [back down front left right up]
          mode: interpolate mode
        Output:
          ERP image
        """
        batch_size, ch, H, W = batch.shape
        if batch_size != 6:
            raise ValueError("Batch size mismatch!!")

        if self.CUDA:
            output = Variable(torch.zeros(1, ch, self.local_val_out_height, self.local_val_out_width), requires_grad=False).cuda()
        else:
            output = Variable(torch.zeros(1, ch, self.local_val_out_height, self.local_val_out_width), requires_grad=False)

        for ori in range(6):
            grid = self.grid[ori, :, :, :].unsqueeze(0)  # 1, self.output_h, self.output_w, 2
            mask = (self.orientation_mask == ori).unsqueeze(0)  # 1, self.output_h, self.output_w, 1

            if self.CUDA:
                masked_grid = Variable(
                    grid * mask.float().expand(-1, -1, -1, 2)).cuda()  # 1, self.output_h, self.output_w, 2
            else:
                masked_grid = Variable(grid * mask.float().expand(-1, -1, -1, 2))

            source_image = batch[ori].unsqueeze(0)  # 1, ch, H, W
            sampled_image = torch.nn.functional.grid_sample(source_image, masked_grid, mode=mode,
                                                            align_corners=True)  # 1, ch, self.output_h, self.output_w

            if self.CUDA:
                sampled_image_masked = sampled_image * Variable(
                    mask.float().view(1, 1, self.local_val_out_height, self.local_val_out_width).expand(1, ch, -1, -1)).cuda()
            else:
                sampled_image_masked = sampled_image * Variable(
                    mask.float().view(1, 1, self.local_val_out_height, self.local_val_out_width).expand(1, ch, -1, -1))
            output = output + sampled_image_masked  # 1, ch, self.output_h, self.output_w

        return output

    def ToEquirecTensor(self, batch, mode='bilinear'):
        """
        Input:
          batch: cube map data [back down front left right up]
          mode: interpolate mode
        Output:
          ERP image
        """
        # Check whether batch size is 6x
        assert mode in ['nearest', 'bilinear']
        batch_size = batch.size()[0]
        if batch_size % 6 != 0:
            raise ValueError("Batch size should be 6x")
        processed = []
        if self.CUDA:
            batch = Variable(batch, requires_grad=False).cuda()
        for idx in range(int(batch_size / 6)):
            target = batch[idx * 6:(idx + 1) * 6, :, :, :]
            target_processed = self._ToEquirec(target, mode)
            processed.append(target_processed)

        output = torch.cat(processed, 0)
        return output


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='parameters for cubemap2panoramic')

    # basic settings
    parser.add_argument('--cubemap_dir', type=str, default=r'output\huawei_demo_parking\raw_data')
    parser.add_argument('--camera', type=str, default='depth1')
    parser.add_argument('--output_dir', type=str, default=r'output\huawei_demo_parking\post_data')
    parser.add_argument('--cubeW', type=int, default=2560)
    parser.add_argument('--out_height', type=int, default=2560)
    parser.add_argument('--frames', type=int, default=200)
    parser.add_argument('--use_cuda', action='store_true', default=False, help='use gpu to post data')


    args = parser.parse_args()

    cubemap2erp = ClassCubemap2ERP(1, args.cubeW, args.out_height * 2, args.use_cuda)

    cube_cos = np.zeros((args.cubeW, args.cubeW), dtype=np.float32)
    D = (args.cubeW - 1) / 2
    for i in range(args.cubeW):
        for j in range(args.cubeW):
            cube_cos[i][j] = math.sqrt(D * D / ((i - D) * (i - D) + (j - D) * (j - D) + D * D))

    # get frames
    frames = [i for i in range(args.frames)]

    # get cameras type
    cam = args.camera

    args.output_vis_dir = os.path.join(args.output_dir, f'erp_vis')
    if not os.path.exists(args.output_vis_dir):
        os.makedirs(args.output_vis_dir)

    args.output_dir = os.path.join(args.output_dir, f'erp')
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)
    
    for frame in tqdm(frames, desc='Cubemap2ERP Processing ', unit='frames'):
        # back down front left right up
        # step 1 readcube
        if 'depth' in args.camera:
            raw_data = np.load(os.path.join(args.cubemap_dir, f'cm_{cam}', f'cm_{cam}_{frame}.npz'), allow_pickle=True)
            cube = np.zeros([6, 1, args.cubeW, args.cubeW], dtype=np.float32)

            for idx, key in enumerate(['back_data', 'down_data', 'front_data', 'left_data', 'right_data', 'up_data']):
                raw = np.transpose(raw_data[key], (2, 0, 1))
                raw = raw.astype(np.float32)
                normalized = (raw[2] + raw[1] * 256 + raw[0] * 256 * 256) / (256 * 256 * 256 - 1)
                in_meters = 1000 * normalized
                cube[idx][0] = in_meters / cube_cos

            cube_tensor = torch.from_numpy(cube)
            out_batch = cubemap2erp.ToEquirecTensor(cube_tensor)
            out = out_batch.cpu().numpy()
            out = np.squeeze(out, axis=0)
            out = np.squeeze(out, axis=0)
            vis_color = cv2.applyColorMap(cv2.convertScaleAbs(out, alpha=255/50), cv2.COLORMAP_JET)
            # im=Image.fromarray(vis_color)
                
            # im.save(os.path.join(args.output_vis_dir, f'erp_vis_{cam}_{frame}.jpg'))
            cv2.imwrite(os.path.join(args.output_vis_dir, f'erp_vis_{cam}_{frame}.jpg'), vis_color, [int(cv2.IMWRITE_JPEG_QUALITY), 97])
            np.save(os.path.join(args.output_dir, f'erp_{cam}_{frame}.npy'), out)


        else:

            cube = np.zeros([6, 3, args.cubeW, args.cubeW], dtype=np.float64)

            cube[0, :, :, :] = np.transpose(cv2.imread(f"{args.cubemap_dir}/cm_{cam}_back_{frame}.png"), (2, 0, 1))
            cube[1, :, :, :] = np.transpose(cv2.imread(f"{args.cubemap_dir}/cm_{cam}_down_{frame}.png"), (2, 0, 1))
            cube[2, :, :, :] = np.transpose(cv2.imread(f"{args.cubemap_dir}/cm_{cam}_front_{frame}.png"), (2, 0, 1))
            cube[3, :, :, :] = np.transpose(cv2.imread(f"{args.cubemap_dir}/cm_{cam}_left_{frame}.png"), (2, 0, 1))
            cube[4, :, :, :] = np.transpose(cv2.imread(f"{args.cubemap_dir}/cm_{cam}_right_{frame}.png"), (2, 0, 1))
            cube[5, :, :, :] = np.transpose(cv2.imread(f"{args.cubemap_dir}/cm_{cam}_up_{frame}.png"), (2, 0, 1))

            cube_tensor = torch.from_numpy(cube)
            out_batch = cubemap2erp.ToEquirecTensor(cube_tensor)
            out = out_batch.cpu().numpy()

            out = np.squeeze(out, axis=0)
            out = np.transpose(out, (1, 2, 0))
            out = out.astype(np.uint8)

            cv2.imwrite(os.path.join(args.output_dir, f'erp_{cam}_{frame}.jpg'), out,
                        [int(cv2.IMWRITE_JPEG_QUALITY), 97])
