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
from omnicv import fisheyeImgConv
from PIL import Image


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='parameters for cubemap2panoramic')

    # basic settings
    parser.add_argument('--cubemap_dir', type=str, default='output_invisiable_data_frame100/cubemap')
    parser.add_argument('--camera', type=str, default='depth1')
    parser.add_argument('--external_path', type=str, default='output_invisiable_data_frame100/external.txt')
    parser.add_argument('--output_dir', type=str, default='output_invisiable_data_frame100/output_erp')
    parser.add_argument('--cubeW',type=int, default=1080)
    parser.add_argument('--out_height',type=int,default=1440)
    parser.add_argument('--use_cuda',action='store_true',default=False, help='use gpu to post data')

    args=parser.parse_args()
    
    cubemap2erp = c2e(cubeW=args.cubeW, outH=args.out_height, outW=args.out_height*2,CUDA=args.use_cuda)
    if not os.path.exists(r'cube_help.npy'):
        cube_cos = np.zeros((args.cubeW,args.cubeW),dtype=np.float64)
        D = (args.cubeW-1)/2
        for i in range(args.cubeW):
            for j in range(args.cubeW):
                cube_cos[i][j] = math.sqrt(D*D/((i-D)*(i-D)+(j-D)*(j-D)+D*D))
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
    

    # get cameras type
    cam  = args.camera[3:]
    

    outputVis_dir = args.output_dir+'Vis'
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)
    if not os.path.exists(outputVis_dir):
        os.makedirs(outputVis_dir)

    step = 1
    total_steps = len(frames)

    for frame in frames:
        #back down front left right up
        #step 1 readcube
        if 'depth' in args.camera:
            cube = np.zeros([6,1,args.cubeW,args.cubeW], dtype=np.float64)
            for idx,view in [(0,'back'),(1,'down'),(2,'front'),(3,'left'),(4,'right'),(5,'up')]:
                raw = cv2.imread(glob.glob(f"{args.cubemap_dir}/{args.camera}_{view}_{frame}.png")[0],-1)
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

            vis_color=cv2.applyColorMap(cv2.convertScaleAbs(out,alpha=255/50),cv2.COLORMAP_JET)
            im=Image.fromarray(vis_color)
                
            im.save(os.path.join(outputVis_dir, f'erpVis_{cam}_{frame}.png'))
            np.save(os.path.join(args.output_dir, f'erp_{cam}_{frame}.npy'),out)
            print('\r', f'Total Frames:  {total_steps}   Processed Frames: {step}   Left Frames:   {total_steps-step}', end=' ', file=sys.stdout, flush=True)
            step = step + 1
        
        else:

            cube = np.zeros([6,3,args.cubeW,args.cubeW], dtype=np.float64)
            mapper = fisheyeImgConv()

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

            persp = mapper.eqruirect2persp(out, 100, 180, 0, 1560, 2880)

            cv2.imwrite(os.path.join(args.output_dir, f'erp_{cam}_{frame}.png'), persp)

            

            print('\r', f'Total Frames:  {total_steps}   Processed Frames: {step}   Left Frames:   {total_steps-step}', end=' ', file=sys.stdout, flush=True)
            step = step + 1

    print('',end='\n')
    os.system('PAUSE')