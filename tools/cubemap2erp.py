import sys,os
parent_path = os.path.abspath(os.path.join(__file__, *(['..'] * 2)))
sys.path.insert(0, parent_path)

import torch
from utilities import c2e
import argparse
import glob,os,re
import numpy as np
import cv2
import math


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='parameters for cubemap2panoramic')

    # basic settings
    parser.add_argument('--cubemap_dir', type=str, default='output_invisiable_data_frame100/cubemap')
    parser.add_argument('--camera_list', type=str, default='depth1')
    parser.add_argument('--external_path', type=str, default='output_invisiable_data_frame100/external.txt')
    parser.add_argument('--output_dir', type=str, default='output_invisiable_data_frame100/output_erp')
    parser.add_argument('--out_height',type=int,default=1024)

    args=parser.parse_args()
    
    cubemap2erp = c2e(cubeW=1024, outH=args.out_height, outW=args.out_height*2)
    if not os.path.exists(r'cube_help.npy'):
        cube_cos = np.zeros((1024,1024),dtype=np.float64)
        for i in range(1024):
            for j in range(1024):
                cube_cos[i][j] = math.sqrt(511.5*511.5/((i-511.5)*(i-511.5)+(j-511.5)*(j-511.5)+511.5*511.5))
        np.save(r'cube_help.npy',cube_cos)
    else:
        cube_cos = np.load(r'cube_help.npy')
    
    # get frames
    frames = []
    regex=re.compile(r'(\d)+')
    with open(args.external_path,'r') as f:
        f.readline()
        for line in f.readlines():
            s = regex.search(line)
            frames.append(int(s.group()))
    

    # get cameras
    cameras = args.camera_list.split(',')
    
    cube = np.zeros([6,1,1024,1024], dtype=np.float64)

    outputVis_dir = args.output_dir+'Vis'
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)
    if not os.path.exists(outputVis_dir):
        os.makedirs(outputVis_dir)

    step = 1
    total_steps = len(cameras)*len(frames)
    for cam in cameras:
        for frame in frames:
            #back down front left right up
            #step 1 readcube
            if 'depth' in cam:
                for idx,view in [(0,'back'),(1,'down'),(2,'front'),(3,'left'),(4,'right'),(5,'up')]:
                    raw = cv2.imread(glob.glob(f"{args.cubemap_dir}/cm_{cam}_{view}_{frame}_*.png")[0],-1)
                    raw = cv2.cvtColor(raw,cv2.COLOR_BGRA2RGB)
                    raw = raw.astype(np.float64)
                    raw = np.transpose(raw,(2,0,1))
                    normalized = (raw[0] + raw[1] * 256 + raw[2] * 256 * 256) / (256 * 256 * 256 - 1)
                    in_meters = 1000 * normalized

                    cube[idx][0] = in_meters/cube_cos
                
                cube_tensor=torch.from_numpy(cube)
                out_batch = cubemap2erp.ToEquirecTensor(cube_tensor)
                out = out_batch.cpu().numpy()
                out = np.squeeze(out,axis=0)
                out = np.squeeze(out,axis=0)

                vis = (out.max()-out)/(out.max()-out.min())*255
                vis = np.array(vis,dtype=np.uint8)

                cv2.imwrite(os.path.join(outputVis_dir, f'erpVis_{cam}_{frame}.png'),vis)
                np.save(os.path.join(args.output_dir, f'erp_{cam}_{frame}.npy'),out)
                print('\r', f'Total Frames:  {total_steps}   Processed Frames: {step}   Left Frames:   {total_steps-step}', end=' ', file=sys.stdout, flush=True)
                step = step + 1