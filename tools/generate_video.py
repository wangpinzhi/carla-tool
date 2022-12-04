import sys,os
parent_path = os.path.abspath(os.path.join(__file__, *(['..'] * 2)))
sys.path.insert(0, parent_path)

import argparse
import cv2,re

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='parameters for generate video')

    # basic settings
    parser.add_argument('--input_dir', type=str)
    parser.add_argument('--output_dir', type=str)
    parser.add_argument('--camera', type=str, default='erpVis_depth1')
    parser.add_argument('--output_width', type=int)
    parser.add_argument('--output_height', type=int)
    parser.add_argument('--external_path', type=str)

    # video settings
    parser.add_argument('--fps', type=int , default=20)

    args=parser.parse_args()

    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')

    # get frames
    frames = []
    regex=re.compile(r'(\d)+')
    with open(args.external_path,'r') as f:
        f.readline()
        for line in f.readlines():
            s = regex.search(line)
            frames.append(int(s.group()))

    
    output_path = os.path.join(args.output_dir,f'{args.camera}.mp4')
    size = (args.output_width,args.output_height) # W x H
    video = cv2.VideoWriter(output_path, fourcc, args.fps, size)
    
    print('start generate video {}'.format(output_path))
    
    for frame in frames:
        img = cv2.imread(os.path.join(args.input_dir,f'{args.camera}_{frame}.png'))
        video.write(img)  # 把图片写进视频
    video.release()

    print('video generate finished')
        

        
        

