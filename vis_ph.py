import cv2
import numpy as np
import os

root_left_path = r'output\pole\raw_data\ph_rgb0'
root_right_path = r'output\pole\raw_data\ph_rgb1'

if __name__ == '__main__':
    for i in range(100):
        left_data = np.load(os.path.join(root_left_path,f'ph_rgb0_{i}.npz'))['data']
        right_data = np.load(os.path.join(root_right_path,f'ph_rgb1_{i}.npz'))['data']
        cv2.imshow('imgL', left_data)
        cv2.imshow('imgR', right_data)
        cv2.waitKey(100)