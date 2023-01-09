import sys,os
parent_path = os.path.abspath(os.path.join(__file__, *(['..'] * 2)))
sys.path.insert(0, parent_path)

from utilities import Cubemap2Fisheye
import concurrent.futures
from scipy.spatial.transform import Rotation as R
from tqdm import tqdm
import os,re,argparse,cv2,glob
import numpy as np

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='parameters for cubemap2fisheye')

    # basic settings
    parser.add_argument('--fov', type=int, default=190, help='target fisheye fov')
    parser.add_argument('--cubemap_dir', type=str, default='output_raw_data/cubemap')
    parser.add_argument('--camera', type=str)
    parser.add_argument('--format', type=str, default='jpg')
    parser.add_argument('--cubeW',type=int)
    parser.add_argument('--outW',type=int)
    parser.add_argument('--external_path', type=str, default='output_raw_data/external.txt', help='path of external.txt')
    parser.add_argument('--output_dir', type=str, default='output_raw_data/output_fisheye')
    parser.add_argument('--use_cuda',action='store_true',default=False, help='use gpu to post data')
    parser.add_argument('--r_x',type=float,default=0.0,help='the angle of rotation_axis x (°)')
    parser.add_argument('--r_y',type=float,default=0.0,help='the angle of rotation_axis y (°)')
    parser.add_argument('--r_z',type=float,default=0.0,help='the angle of rotation_axis z (°)')

    args=parser.parse_args()
    c2f = Cubemap2Fisheye(args.cubeW, args.cubeW, args.outW, args.outW, args.fov, Rot= R.from_euler('zyx', [args.r_z,args.r_y,args.r_x], degrees=True).as_matrix(),use_cuda=args.use_cuda)
    
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
    
    cube = np.zeros([6,3,args.cubeW,args.cubeW], dtype=np.float64)

    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    for frame in tqdm(frames, desc='Cubemap2Fisheye Processing ', unit='frames'):
        
        #back - left - front - right - up - down 
        #step 1 readcube
        cube[0,:,:,:]=np.transpose(cv2.imread(f"{args.cubemap_dir}/cm_{cam}_back_{frame}.{args.format}"),(2,0,1))
        cube[1,:,:,:]=np.transpose(cv2.imread(f"{args.cubemap_dir}/cm_{cam}_left_{frame}.{args.format}"),(2,0,1))
        cube[2,:,:,:]=np.transpose(cv2.imread(f"{args.cubemap_dir}/cm_{cam}_front_{frame}.{args.format}"),(2,0,1))
        cube[3,:,:,:]=np.transpose(cv2.imread(f"{args.cubemap_dir}/cm_{cam}_right_{frame}.{args.format}"),(2,0,1))
        cube[4,:,:,:]=np.transpose(cv2.imread(f"{args.cubemap_dir}/cm_{cam}_up_{frame}.{args.format}"),(2,0,1))
        cube[5,:,:,:]=np.transpose(cv2.imread(f"{args.cubemap_dir}/cm_{cam}_down_{frame}.{args.format}"),(2,0,1))

        # execute trans
        fish = c2f.trans(cube)
        fish = fish.transpose((1, 2, 0))
        fish.astype(np.uint8)

        cv2.imwrite(os.path.join(args.output_dir,f'fe_{cam}_{frame}.jpg'), fish, [int(cv2.IMWRITE_JPEG_QUALITY), 97])


    os.system('PAUSE')
