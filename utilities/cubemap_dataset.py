from torch.utils.data import Dataset, DataLoader
import torch
import numpy as np
import cv2

class CubemapDataset(Dataset):
    def __init__(self, cubeW, camera_type, frames_list, cubemap_dir, format):
        super().__init__()
        self.camera_type = camera_type
        self.frames_list = frames_list
        self.cubemap_dir = cubemap_dir
        self.format = format
        self.cube = np.zeros([6, 3, cubeW, cubeW], dtype=np.float32)
    
    def __getitem__(self, index):
        self.cube[0,:,:,:]=np.transpose(cv2.imread(f"{self.cubemap_dir}/cm_{self.camera_type}_back_{self.frames_list[index]}.{self.format}"),(2,0,1))
        self.cube[1,:,:,:]=np.transpose(cv2.imread(f"{self.cubemap_dir}/cm_{self.camera_type}_left_{self.frames_list[index]}.{self.format}"),(2,0,1))
        self.cube[2,:,:,:]=np.transpose(cv2.imread(f"{self.cubemap_dir}/cm_{self.camera_type}_front_{self.frames_list[index]}.{self.format}"),(2,0,1))
        self.cube[3,:,:,:]=np.transpose(cv2.imread(f"{self.cubemap_dir}/cm_{self.camera_type}_right_{self.frames_list[index]}.{self.format}"),(2,0,1))
        self.cube[4,:,:,:]=np.transpose(cv2.imread(f"{self.cubemap_dir}/cm_{self.camera_type}_up_{self.frames_list[index]}.{self.format}"),(2,0,1))
        self.cube[5,:,:,:]=np.transpose(cv2.imread(f"{self.cubemap_dir}/cm_{self.camera_type}_down_{self.frames_list[index]}.{self.format}"),(2,0,1))
        return self.cube

    def __len__(self):
        return len(self.frames_list)

if __name__ == '__main__':
    frames_list = [i for i in range(6, 206)]
    test_dataset = CubemapDataset(2560, 'rgb0', frames_list, 'output/nju_driving05/cubemap','jpg')
    test_loader = DataLoader(test_dataset, batch_size=4, shuffle=False, num_workers=2, pin_memory=False)
    
    for i, sample in enumerate(test_loader):
        sample = sample.transpose(0,1)
        print(sample.shape, sample.dtype)