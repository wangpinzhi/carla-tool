import argparse
import cv2
import os
import re
import sys

import numpy as np
import torch
import torch.nn.functional as F
from tqdm import tqdm

parent_path = os.path.abspath(os.path.join(__file__, *(['..'] * 2)))
sys.path.insert(0, parent_path)


class c2e:
    """
    Cube map to ERP
    Functions:
    __init__: constructor
    _ToEquirec: private transformation function
    getGrid: get grid and mask for 6 faces of cube map
    ToEquirecTensor: callable API
    input faces order: back down front left right up
    """

    def __init__(self, batch_size=1, cubeW=256, outH=256, outW=512, FOV=90, CUDA=False):
        """
        Input:
          batch_size: [int] batch size of input tensor, the default is 6 (6 faces of a cube map)
          cubeW: [int] width of each face of cube map
          outH: [int] height of output ERP image
          outW: [int] width of output ERP image
          FOV: [int] field-of-view of the virtual cameras(degree). The default is 90
          CUDA: [bool] use cuda or not
        Output: None
        """
        self.batch_size = batch_size  # NOTE: not in use at all
        self.cubeW = cubeW
        self.outH = outH
        self.outW = outW
        self.fov = FOV
        self.fov_rad = self.fov * np.pi / 180
        self.CUDA = CUDA

        # Compute the parameters for projection
        self.radius = int(0.5 * cubeW)

        # Map equirectangular pixel to longitude and latitude
        # NOTE: Make end a full length since arange have a right open bound [a, b)
        theta_start = -1 / 2 * np.pi + (np.pi / outW)
        theta_end = 3 / 2 * np.pi
        theta_step = 2 * np.pi / outW
        theta_range = torch.arange(theta_start, theta_end, theta_step)

        phi_start = -0.5 * np.pi + (0.5 * np.pi / outH)
        phi_end = 0.5 * np.pi
        phi_step = np.pi / outH
        phi_range = torch.arange(phi_start, phi_end, phi_step)

        # Stack to get the longitude latitude map
        self.theta_map = theta_range.unsqueeze(0).repeat(outH, 1)
        self.phi_map = phi_range.unsqueeze(-1).repeat(1, outW)
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
        x_3d = (self.radius * torch.cos(self.phi_map) * torch.cos(self.theta_map)).view(self.outH, self.outW, 1)
        y_3d = (self.radius * torch.cos(self.phi_map) * torch.sin(self.theta_map)).view(self.outH, self.outW, 1)
        z_3d = (self.radius * torch.sin(self.phi_map)).view(self.outH, self.outW, 1)

        self.grid_ball = torch.cat([x_3d, y_3d, z_3d], 2).view(self.outH, self.outW, 3)

        # Compute the down grid
        radius_ratio_down = torch.abs(z_3d / self.radius)
        grid_down_raw = self.grid_ball / radius_ratio_down.view(self.outH, self.outW, 1).expand(-1, -1, 3)
        grid_down_w = (-grid_down_raw[:, :, 0].clone() / self.radius).unsqueeze(-1)
        grid_down_h = (-grid_down_raw[:, :, 1].clone() / self.radius).unsqueeze(-1)
        grid_down = torch.cat([grid_down_w, grid_down_h], 2).unsqueeze(0)
        mask_down = (((grid_down_w <= 1) * (grid_down_w >= -1)) * ((grid_down_h <= 1) * (grid_down_h >= -1)) * (
                grid_down_raw[:, :, 2] == self.radius).unsqueeze(2)).float()

        # Compute the up grid
        radius_ratio_up = torch.abs(z_3d / self.radius)
        grid_up_raw = self.grid_ball / radius_ratio_up.view(self.outH, self.outW, 1).expand(-1, -1, 3)
        grid_up_w = (-grid_up_raw[:, :, 0].clone() / self.radius).unsqueeze(-1)
        grid_up_h = (grid_up_raw[:, :, 1].clone() / self.radius).unsqueeze(-1)
        grid_up = torch.cat([grid_up_w, grid_up_h], 2).unsqueeze(0)
        mask_up = (((grid_up_w <= 1) * (grid_up_w >= -1)) * ((grid_up_h <= 1) * (grid_up_h >= -1)) * (
                grid_up_raw[:, :, 2] == -self.radius).unsqueeze(2)).float()

        # Compute the front grid
        radius_ratio_front = torch.abs(y_3d / self.radius)
        grid_front_raw = self.grid_ball / radius_ratio_front.view(self.outH, self.outW, 1).expand(-1, -1, 3)
        grid_front_w = (-grid_front_raw[:, :, 0].clone() / self.radius).unsqueeze(-1)
        grid_front_h = (grid_front_raw[:, :, 2].clone() / self.radius).unsqueeze(-1)
        grid_front = torch.cat([grid_front_w, grid_front_h], 2).unsqueeze(0)
        mask_front = (((grid_front_w <= 1) * (grid_front_w >= -1)) * ((grid_front_h <= 1) * (grid_front_h >= -1)) * (
                torch.round(grid_front_raw[:, :, 1]) == self.radius).unsqueeze(2)).float()

        # Compute the back grid
        radius_ratio_back = torch.abs(y_3d / self.radius)
        grid_back_raw = self.grid_ball / radius_ratio_back.view(self.outH, self.outW, 1).expand(-1, -1, 3)
        grid_back_w = (grid_back_raw[:, :, 0].clone() / self.radius).unsqueeze(-1)
        grid_back_h = (grid_back_raw[:, :, 2].clone() / self.radius).unsqueeze(-1)
        grid_back = torch.cat([grid_back_w, grid_back_h], 2).unsqueeze(0)
        mask_back = (((grid_back_w <= 1) * (grid_back_w >= -1)) * ((grid_back_h <= 1) * (grid_back_h >= -1)) * (
                torch.round(grid_back_raw[:, :, 1]) == -self.radius).unsqueeze(2)).float()

        # Compute the right grid
        radius_ratio_right = torch.abs(x_3d / self.radius)
        grid_right_raw = self.grid_ball / radius_ratio_right.view(self.outH, self.outW, 1).expand(-1, -1, 3)
        grid_right_w = (-grid_right_raw[:, :, 1].clone() / self.radius).unsqueeze(-1)
        grid_right_h = (grid_right_raw[:, :, 2].clone() / self.radius).unsqueeze(-1)
        grid_right = torch.cat([grid_right_w, grid_right_h], 2).unsqueeze(0)
        mask_right = (((grid_right_w <= 1) * (grid_right_w >= -1)) * ((grid_right_h <= 1) * (grid_right_h >= -1)) * (
                torch.round(grid_right_raw[:, :, 0]) == -self.radius).unsqueeze(2)).float()

        # Compute the left grid
        radius_ratio_left = torch.abs(x_3d / self.radius)
        grid_left_raw = self.grid_ball / radius_ratio_left.view(self.outH, self.outW, 1).expand(-1, -1, 3)
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
            output = Variable(torch.zeros(1, ch, self.outH, self.outW), requires_grad=False).cuda()
        else:
            output = Variable(torch.zeros(1, ch, self.outH, self.outW), requires_grad=False)

        for ori in range(6):
            grid = self.grid[ori, :, :, :].unsqueeze(0)  # 1, self.output_h, self.output_w, 2
            mask = (self.orientation_mask == ori).unsqueeze(0)  # 1, self.output_h, self.output_w, 1

            if self.CUDA:
                masked_grid = Variable(
                    grid * mask.double().expand(-1, -1, -1, 2)).cuda()  # 1, self.output_h, self.output_w, 2
            else:
                masked_grid = Variable(grid * mask.double().expand(-1, -1, -1, 2))

            source_image = batch[ori].unsqueeze(0)  # 1, ch, H, W
            sampled_image = torch.nn.functional.grid_sample(source_image, masked_grid, mode=mode,
                                                            align_corners=True)  # 1, ch, self.output_h, self.output_w

            if self.CUDA:
                sampled_image_masked = sampled_image * Variable(
                    mask.float().view(1, 1, self.outH, self.outW).expand(1, ch, -1, -1)).cuda()
            else:
                sampled_image_masked = sampled_image * Variable(
                    mask.float().view(1, 1, self.outH, self.outW).expand(1, ch, -1, -1))
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

    parser = argparse.ArgumentParser(description='parameters for cubemap2fisheye')

    # basic settings
    parser.add_argument('--fov', type=int, default=90, help='target fisheye fov')
    parser.add_argument('--cubeW', type=int, default=1080)
    parser.add_argument('--outH', type=int)
    parser.add_argument('--outW', type=int)
    parser.add_argument('--format', type=str, default='jpg')
    parser.add_argument('--cubemap_dir', type=str, default='output_raw_data/cubemap')
    parser.add_argument('--camera', type=str)
    parser.add_argument('--external_path', type=str, default='output_raw_data/external.txt',
                        help='path of external.txt')
    parser.add_argument('--output_dir', type=str, default='output_raw_data/output_fisheye')
    parser.add_argument('--use_cuda', action='store_true', default=False, help='use gpu to post data')

    args = parser.parse_args()

    #  get frames
    frames = []
    regex = re.compile(r'(\d)+')
    with open(args.external_path, 'r') as f:
        f.readline()
        for line in f.readlines():
            s = regex.search(line)
            frames.append(int(s.group()))

    # get cameras type
    cam = args.camera[3:]

    # step2 trans cubemap to erp
    cube = np.zeros([6, 3, args.cubeW, args.cubeW], dtype=np.float64)
    cubemap2erp = c2e(cubeW=args.cubeW, outH=args.cubeW, outW=args.cubeW * 2, CUDA=args.use_cuda)

    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    # get grid
    xc = (args.outW - 1) / 2
    yc = (args.outH - 1) / 2

    face_x, face_y = np.meshgrid(range(args.outW), range(args.outH))
    x = face_x - xc
    y = face_y - yc
    focal = xc / np.tan(np.radians(args.fov / 2))
    z = np.ones_like(x) * focal
    x, y, z = x / z, y / z, z / z
    theta = np.arctan2(x, z).astype(np.float64)
    phi = np.arctan2(y, np.sqrt(x * x + z * z)).astype(np.float64)
    theta = theta / np.pi
    phi = phi / np.pi * 2.0

    grid = np.stack([theta, phi], axis=-1)
    grid = np.expand_dims(grid, axis=0)
    grid = torch.from_numpy(grid)
    if args.use_cuda:
        grid = grid.cuda()
    for frame in tqdm(frames, desc=f'c2p {args.camera}', unit='frames'):
        cube[0, :, :, :] = np.transpose(cv2.imread(f"{args.cubemap_dir}/cm_{cam}_back_{frame}.{args.format}"),
                                        (2, 0, 1))
        cube[1, :, :, :] = np.transpose(cv2.imread(f"{args.cubemap_dir}/cm_{cam}_down_{frame}.{args.format}"),
                                        (2, 0, 1))
        cube[2, :, :, :] = np.transpose(cv2.imread(f"{args.cubemap_dir}/cm_{cam}_front_{frame}.{args.format}"),
                                        (2, 0, 1))
        cube[3, :, :, :] = np.transpose(cv2.imread(f"{args.cubemap_dir}/cm_{cam}_left_{frame}.{args.format}"),
                                        (2, 0, 1))
        cube[4, :, :, :] = np.transpose(cv2.imread(f"{args.cubemap_dir}/cm_{cam}_right_{frame}.{args.format}"),
                                        (2, 0, 1))
        cube[5, :, :, :] = np.transpose(cv2.imread(f"{args.cubemap_dir}/cm_{cam}_up_{frame}.{args.format}"), (2, 0, 1))

        cube_tensor = torch.from_numpy(cube)
        out_erp = cubemap2erp.ToEquirecTensor(cube_tensor)
        out_pinhole = F.grid_sample(out_erp, grid, mode='bilinear', padding_mode='zeros', align_corners=True)

        out = out_pinhole.cpu().numpy()
        out = np.squeeze(out, axis=0)
        out = np.transpose(out, (1, 2, 0))
        out = out.astype(np.uint8)

        cv2.imwrite(os.path.join(args.output_dir, f'ph_{cam}_{frame}.{args.format}'), out,
                    [int(cv2.IMWRITE_JPEG_QUALITY), 97])
