import numpy as np
import torch
from omnicv import fisheyeImgConv

import sys,os
parent_path = os.path.abspath(os.path.join(__file__, *(['..'] * 2)))
sys.path.insert(0, parent_path)

from utilities import c2e
import argparse
import os,re,cv2
import numpy as np


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='parameters for cubemap2fisheye')

    # basic settings
    parser.add_argument('--fov', type=int, default=90, help='target fisheye fov')
    parser.add_argument('--cubeW',type=int, default=1080)
    parser.add_argument('--outH',type=int)
    parser.add_argument('--outW',type=int)

    parser.add_argument('--cubemap_dir', type=str, default='output_raw_data/cubemap')
    parser.add_argument('--camera', type=str)
    parser.add_argument('--external_path', type=str, default='output_raw_data/external.txt', help='path of external.txt')
    parser.add_argument('--output_dir', type=str, default='output_raw_data/output_fisheye')
    parser.add_argument('--use_cuda',action='store_true',default=False, help='use gpu to post data')

    args=parser.parse_args()
                 

    #  get frames
    frames = []
    regex=re.compile(r'(\d)+')
    with open(args.external_path,'r') as f:
        f.readline()
        for line in f.readlines():
            s = regex.search(line)
            frames.append(int(s.group()))

    # get cameras type
    cam  = args.camera[3:]
    
    # step2 trans cubemap to erp
    cube = np.zeros([6,3,args.cubeW,args.cubeW], dtype=np.float64)
    cubemap2erp = c2e(cubeW=args.cubeW, outH=args.cubeW, outW=args.cubeW*2,CUDA=args.use_cuda)
    mapper = fisheyeImgConv()

    step = 1
    total_steps = len(frames)

    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    for frame in frames:
        for idx,view in [(0,'back'),(1,'down'),(2,'front'),(3,'left'),(4,'right'),(5,'up')]:
            raw = cv2.imread(f"{args.cubemap_dir}/{args.camera}_{view}_{frame}.png")
            raw = raw.astype(np.float64)
            raw = np.transpose(raw,(2,0,1))
            cube[idx] = raw
            
            cube_tensor=torch.from_numpy(cube)
            out_batch = cubemap2erp.ToEquirecTensor(cube_tensor)
            out = out_batch.cpu().numpy()

            out = np.squeeze(out,axis=0)
            out = np.transpose(out,(1,2,0))
            out = out.astype(np.uint8)

            persp = mapper.eqruirect2persp(out, args.fov, 0, 0, args.outH, args.outW)

            cv2.imwrite(os.path.join(args.output_dir, f'erp_{cam}_{frame}.png'), persp)

            
            print('\r', f'Total Frames:  {total_steps}   Processed Frames: {step}   Left Frames:   {total_steps-step}', end=' ', file=sys.stdout, flush=True)
            step = step + 1
        