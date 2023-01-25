import cv2
import argparse
import re
import time
import torch.nn.functional as F
import torch
import numpy as np
from tqdm import tqdm
from scipy.spatial.transform import Rotation as R
import sys
import os
parent_path = os.path.abspath(os.path.join(__file__, *(['..'] * 2)))
sys.path.insert(0, parent_path)


class Cubemap2Fisheye:
    def __init__(self, fish_h, fish_w, fish_FoV, Rot=np.identity(3, dtype=np.float32), use_cuda=False):

        if use_cuda:
            print('Use GPU')
            self.device = torch.device('cuda')
        else:
            self.device = torch.device('cpu')

        self.radius = (fish_h) // 2
        self.FoV = fish_FoV // 2
        self.FovTh = self.FoV / 180 * np.pi
        self.fish_h, self.fish_w = fish_h, fish_w
        fish_x, fish_y = np.meshgrid(range(fish_w), range(fish_h))
        fish_x = (fish_x.astype(np.float32) - (fish_w - 1) / 2)
        # fish_y = (fish_y.astype(np.float32) - (fish_h - 1) / 2)
        # fish_x = (fish_x.astype(np.float32)) * fish_w / (fish_w - 1) - self.radius
        fish_y = (fish_y.astype(np.float32)) * \
            fish_h / (fish_h - 1) - self.radius
        fish_theta = np.sqrt(fish_x * fish_x + fish_y *
                             fish_y) / self.radius * self.FoV  # theta deg
        fish_theta = fish_theta / 180 * np.pi
        fish_phi = np.arctan2(-fish_y, -fish_x)

        self.invalidMask = (fish_theta > self.FovTh)
        # fish_theta[self.invalidMask] = 0.000001

        z = np.cos(fish_theta)
        x = np.sin(fish_theta) * np.cos(fish_phi)
        y = np.sin(fish_theta) * np.sin(fish_phi)
        coor3d = np.expand_dims(np.dstack((x, y, z)), axis=-1)
        coor3d_r = np.matmul(Rot, coor3d).squeeze(-1)
        x_3d = coor3d_r[:, :, 0:1]
        y_3d = coor3d_r[:, :, 1:2]
        z_3d = coor3d_r[:, :, 2:]
        self.masked_grid_list = []
        self.mask_list = []
        # Compute the back grid
        grid_back_raw = coor3d_r / np.abs(z_3d)
        grid_back_w = grid_back_raw[:, :, 0]
        grid_back_h = -grid_back_raw[:, :, 1]
        grid_back = np.concatenate(
            [np.expand_dims(grid_back_w, 2), np.expand_dims(grid_back_h, 2)], 2)
        mask_back = ((grid_back_w <= 1) * (grid_back_w >= -1)) * \
            ((grid_back_h <= 1) * (grid_back_h >= -1)) * \
            (grid_back_raw[:, :, 2] < 0)
        masked_grid_back = grid_back * np.float32(np.expand_dims(mask_back, 2))
        self.masked_grid_list.append(masked_grid_back)
        self.mask_list.append(mask_back)
        # Compute the left grid
        grid_left_raw = coor3d_r / np.abs(x_3d)
        grid_left_w = grid_left_raw[:, :, 2]
        grid_left_h = -grid_left_raw[:, :, 1]
        grid_left = np.concatenate(
            [np.expand_dims(grid_left_w, 2), np.expand_dims(grid_left_h, 2)], 2)
        mask_left = ((grid_left_w <= 1) * (grid_left_w >= -1)) * \
            ((grid_left_h <= 1) * (grid_left_h >= -1)) * \
            (grid_left_raw[:, :, 0] > 0)
        masked_grid_left = grid_left * np.float32(np.expand_dims(mask_left, 2))
        self.masked_grid_list.append(masked_grid_left)
        self.mask_list.append(mask_left)
        # Compute the front grid
        grid_front_raw = coor3d_r / np.abs(z_3d)
        grid_front_w = -grid_front_raw[:, :, 0]
        grid_front_h = -grid_front_raw[:, :, 1]
        grid_front = np.concatenate(
            [np.expand_dims(grid_front_w, 2), np.expand_dims(grid_front_h, 2)], 2)
        mask_front = ((grid_front_w <= 1) * (grid_front_w >= -1)) * \
            ((grid_front_h <= 1) * (grid_front_h >= -1)) * \
            (grid_front_raw[:, :, 2] > 0)
        masked_grid_front = grid_front * \
            np.float32(np.expand_dims(mask_front, 2))
        self.masked_grid_list.append(masked_grid_front)
        self.mask_list.append(mask_front)
        # Compute the right grid
        grid_right_raw = coor3d_r / np.abs(x_3d)
        grid_right_w = -grid_right_raw[:, :, 2]
        grid_right_h = -grid_right_raw[:, :, 1]
        grid_right = np.concatenate(
            [np.expand_dims(grid_right_w, 2), np.expand_dims(grid_right_h, 2)], 2)
        mask_right = ((grid_right_w <= 1) * (grid_right_w >= -1)) * \
            ((grid_right_h <= 1) * (grid_right_h >= -1)) * \
            (grid_right_raw[:, :, 0] < 0)
        masked_grid_right = grid_right * \
            np.float32(np.expand_dims(mask_right, 2))
        self.masked_grid_list.append(masked_grid_right)
        self.mask_list.append(mask_right)
        # Compute the up grid
        grid_up_raw = coor3d_r / np.abs(y_3d)
        grid_up_w = -grid_up_raw[:, :, 0]
        grid_up_h = grid_up_raw[:, :, 2]
        grid_up = np.concatenate(
            [np.expand_dims(grid_up_w, 2), np.expand_dims(grid_up_h, 2)], 2)
        mask_up = ((grid_up_w <= 1) * (grid_up_w >= -1)) * \
            ((grid_up_h <= 1) * (grid_up_h >= -1)) * (grid_up_raw[:, :, 1] > 0)
        masked_grid_up = grid_up * np.float32(np.expand_dims(mask_up, 2))
        self.masked_grid_list.append(masked_grid_up)
        self.mask_list.append(mask_up)
        # Compute the down grid
        grid_down_raw = coor3d_r / np.abs(y_3d)
        grid_down_w = -grid_down_raw[:, :, 0]
        grid_down_h = -grid_down_raw[:, :, 2]
        grid_down = np.concatenate(
            [np.expand_dims(grid_down_w, 2), np.expand_dims(grid_down_h, 2)], 2)
        mask_down = ((grid_down_w <= 1) * (grid_down_w >= -1)) * \
            ((grid_down_h <= 1) * (grid_down_h >= -1)) * \
            (grid_down_raw[:, :, 1] < 0)
        masked_grid_down = grid_down * np.float32(np.expand_dims(mask_down, 2))
        self.masked_grid_list.append(masked_grid_down)
        self.mask_list.append(mask_down)

    # cube_faces:6 x c x h x w, 6 faces of the cube map. back - left - front - right - up - down
    def trans(self, cube_faces):
        n, c, h, w = cube_faces.shape
        assert n == 6, ("cube map should have 6 faces, but the number of input faces is {}".format(n))
        out = np.zeros([c, self.fish_h, self.fish_w])
        for i in range(0, 6):
            ori = cube_faces[i, :, :, :]
            ori = torch.from_numpy(ori).unsqueeze(0)
            ori.to(self.device)
            mask_grid = torch.from_numpy(self.masked_grid_list[i]).unsqueeze(0)
            mask_grid = mask_grid.type(torch.float32)
            mask_grid.to(self.device)
            fish = F.grid_sample(ori, mask_grid, mode='bilinear', padding_mode='zeros', align_corners=False)
            fish = fish.squeeze_(0).cpu().numpy()
            mask = ~(np.repeat(np.expand_dims(self.mask_list[i], 0), c, 0))
            fish[mask] = 0.0
            out = out + fish
        out[:, self.invalidMask] = 0
        return out


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='parameters for cubemap2fisheye')

    # basic settings
    parser.add_argument('--fov', type=int, default=190,
                        help='target fisheye fov')
    parser.add_argument('--cubemap_dir', type=str,
                        default='output_raw_data/cubemap')
    parser.add_argument('--camera', type=str)
    parser.add_argument('--format', type=str, default='jpg')
    parser.add_argument('--cubeW', type=int)
    parser.add_argument('--outW', type=int)
    parser.add_argument('--external_path', type=str, default='output_raw_data/external.txt', help='path of external.txt')
    parser.add_argument('--output_dir', type=str, default='output_raw_data/output_fisheye')
    parser.add_argument('--use_cuda', action='store_true', default=False, help='use gpu to post data')
    parser.add_argument('--r_x', type=float, default=0.0, help='the angle of rotation_axis x (°)')
    parser.add_argument('--r_y', type=float, default=0.0,
                        help='the angle of rotation_axis y (°)')
    parser.add_argument('--r_z', type=float, default=0.0,
                        help='the angle of rotation_axis z (°)')

    args = parser.parse_args()
    c2f = Cubemap2Fisheye(args.outW, args.outW, args.fov, Rot=R.from_euler('zyx', [
                          args.r_z, args.r_y, args.r_x], degrees=True).as_matrix(), use_cuda=args.use_cuda)

    # get frames
    frames = []
    regex = re.compile(r'(\d)+')
    with open(args.external_path, 'r') as f:
        f.readline()
        for line in f.readlines():
            s = regex.search(line)
            frames.append(int(s.group()))

    # get cameras type
    cam = args.camera[3:]

    cube = np.zeros([6, 3, args.cubeW, args.cubeW], dtype=np.float32)

    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    pbar = tqdm(frames, desc='Cubemap2Fisheye Processing ', unit='frames')

    for frame in pbar:

        # back - left - front - right - up - down
        # step 1 readcube
        cube[0, :, :, :] = np.transpose(cv2.imread(
            f"{args.cubemap_dir}/cm_{cam}_back_{frame}.{args.format}"), (2, 0, 1))
        cube[1, :, :, :] = np.transpose(cv2.imread(
            f"{args.cubemap_dir}/cm_{cam}_left_{frame}.{args.format}"), (2, 0, 1))
        cube[2, :, :, :] = np.transpose(cv2.imread(
            f"{args.cubemap_dir}/cm_{cam}_front_{frame}.{args.format}"), (2, 0, 1))
        cube[3, :, :, :] = np.transpose(cv2.imread(
            f"{args.cubemap_dir}/cm_{cam}_right_{frame}.{args.format}"), (2, 0, 1))
        cube[4, :, :, :] = np.transpose(cv2.imread(
            f"{args.cubemap_dir}/cm_{cam}_up_{frame}.{args.format}"), (2, 0, 1))
        cube[5, :, :, :] = np.transpose(cv2.imread(
            f"{args.cubemap_dir}/cm_{cam}_down_{frame}.{args.format}"), (2, 0, 1))

        # execute trans
        start_time = time.time()
        fish = c2f.trans(cube)
        fish = fish.transpose((1, 2, 0))
        fish.astype(np.uint8)
        trans_img_time = time.time()-start_time

        start_time = time.time()
        cv2.imwrite(os.path.join(args.output_dir, f'fe_{cam}_{frame}.jpg'), fish, [
                    int(cv2.IMWRITE_JPEG_QUALITY), 97])
        save_img_time = time.time()-start_time

        pbar.set_postfix(trans_cost=trans_img_time,
                         save_cost=save_img_time,
                         use_cuda=args.use_cuda)
