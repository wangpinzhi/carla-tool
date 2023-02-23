import numpy as np
import torch

import sys, os

parent_path = os.path.abspath(os.path.join(__file__, *(['..'] * 2)))
sys.path.insert(0, parent_path)

from tools import c2e
import torch.nn.functional as F
import argparse
import os, re, cv2
import numpy as np
from tqdm import tqdm

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
