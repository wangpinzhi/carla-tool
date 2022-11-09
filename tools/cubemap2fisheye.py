from utilities import Cubemap2Fisheye
import argparse
import glob,os
import numpy as np
import cv2

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='parameters for cubemap2fisheye')

    # basic settings
    parser.add_argument('--fov', type=int, default=190, help='target fisheye fov')
    parser.add_argument('--cubemap_dir', type=str, default='output_data/cubemap')
    parser.add_argument('--camera_list', type=str, default='rgb1,rgb2,rgb3,rgb4')
    parser.add_argument('--output_dir', type=str, default='output_fisheye')


    args=parser.parse_args()
    
    c2f = Cubemap2Fisheye(1024, 1024, 1024, 1024, args.fov)
    
    # get frames
    frames = [13438,13440,13441,13442,13444,13445]

    # get cameras
    cameras = args.camera_list.split(',')
    
    cube = np.zeros([6,3,1024,1024], dtype=np.float32)

    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    for cam in cameras:
        for frame in frames:
            #back - left - front - right - up - down 
            #step 1 readcube
            cube[0,:,:,:]=np.transpose(cv2.imread(glob.glob(f"{args.cubemap_dir}/cm_{cam}_down_{frame}_*.jpg")[0]),(2,0,1))
            cube[1,:,:,:]=np.transpose(cv2.imread(glob.glob(f"{args.cubemap_dir}/cm_{cam}_left_{frame}_*.jpg")[0]),(2,0,1))
            cube[2,:,:,:]=np.transpose(cv2.imread(glob.glob(f"{args.cubemap_dir}/cm_{cam}_front_{frame}_*.jpg")[0]),(2,0,1))
            cube[3,:,:,:]=np.transpose(cv2.imread(glob.glob(f"{args.cubemap_dir}/cm_{cam}_right_{frame}_*.jpg")[0]),(2,0,1))
            cube[4,:,:,:]=np.transpose(cv2.imread(glob.glob(f"{args.cubemap_dir}/cm_{cam}_up_{frame}_*.jpg")[0]),(2,0,1))
            cube[5,:,:,:]=np.transpose(cv2.imread(glob.glob(f"{args.cubemap_dir}/cm_{cam}_down_{frame}_*.jpg")[0]),(2,0,1))

            # execute trans
            cube.astype(np.float32)
            fish = c2f.trans(cube)
            fish = fish.transpose((1, 2, 0))
            fish.astype(np.uint8)
            cv2.imwrite(os.path.join(args.output_dir,f'fe_{cam}_{frame}.jpg'), fish)