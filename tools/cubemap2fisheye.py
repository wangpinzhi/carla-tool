import sys,os
parent_path = os.path.abspath(os.path.join(__file__, *(['..'] * 2)))
sys.path.insert(0, parent_path)

from utilities import Cubemap2Fisheye
import argparse
import glob,os,re
import numpy as np
import cv2

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='parameters for cubemap2fisheye')

    # basic settings
    parser.add_argument('--fov', type=int, default=210, help='target fisheye fov')
    parser.add_argument('--cubemap_dir', type=str, default='output_raw_data/cubemap')
    parser.add_argument('--camera', type=str)
    parser.add_argument('--external_path', type=str, default='output_raw_data/external.txt', help='path of external.txt')
    parser.add_argument('--output_dir', type=str, default='output_raw_data/output_fisheye')
    parser.add_argument('--use_cuda',action='store_true',default=False, help='use gpu to post data')

    args=parser.parse_args()
    
    c2f = Cubemap2Fisheye(1024, 1024, 1024, 1024, args.fov, use_cuda=args.use_cuda)
    
    # get frames
    frames = []
    regex=re.compile(r'(\d)+')
    with open(args.external_path,'r') as f:
        f.readline()
        for line in f.readlines():
            s = regex.search(line)
            frames.append(int(s.group()))
    

    # get cameras
    
    cube = np.zeros([6,3,1024,1024], dtype=np.float32)

    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    step = 1
    total_steps = len(frames)
    for frame in frames:
            
        #back - left - front - right - up - down 
        #step 1 readcube
        cube[0,:,:,:]=np.transpose(cv2.imread(glob.glob(f"{args.cubemap_dir}/{args.camera}_back_{frame}.png")[0]),(2,0,1))
        cube[1,:,:,:]=np.transpose(cv2.imread(glob.glob(f"{args.cubemap_dir}/{args.camera}_left_{frame}.png")[0]),(2,0,1))
        cube[2,:,:,:]=np.transpose(cv2.imread(glob.glob(f"{args.cubemap_dir}/{args.camera}_front_{frame}.png")[0]),(2,0,1))
        cube[3,:,:,:]=np.transpose(cv2.imread(glob.glob(f"{args.cubemap_dir}/{args.camera}_right_{frame}.png")[0]),(2,0,1))
        cube[4,:,:,:]=np.transpose(cv2.imread(glob.glob(f"{args.cubemap_dir}/{args.camera}_up_{frame}.png")[0]),(2,0,1))
        cube[5,:,:,:]=np.transpose(cv2.imread(glob.glob(f"{args.cubemap_dir}/{args.camera}_down_{frame}.png")[0]),(2,0,1))

            # execute trans
        cube.astype(np.float32)
        fish = c2f.trans(cube)
        fish = fish.transpose((1, 2, 0))
        fish.astype(np.uint8)
        new_camera = str(args.camera)
        new_camera = new_camera.replace("cm","fe")
        cv2.imwrite(os.path.join(args.output_dir,f'{new_camera}_{frame}.png'), fish)
        print('\r', f'Total Frames:  {total_steps}   Processed Frames: {step}   Left Frames:   {total_steps-step}', end=' ', file=sys.stdout, flush=True)
        step = step + 1
    print('',end='\n')
    os.system('PAUSE')
