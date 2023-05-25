import os
import numpy as np
from torch.utils.data import Dataset
import torch

from .module_cubemap_enum import EnumCamModel
from .module_cubemap_enum import EnumTargetType
from PIL import Image

class ClassCubemapDataset(Dataset):
    def __init__(self, 
                 parameter_cubemap_dir,
                 parameter_cubemap_order,
                 parameter_target_model,
                 parameter_target_type):
        self.local_val_cubemap_dir = parameter_cubemap_dir
        self.local_val_files = os.listdir(self.local_val_cubemap_dir)
        self.local_val_model = parameter_target_model
        self.local_val_type = parameter_target_type
        self.local_val_order = parameter_cubemap_order

    def __function_get_save_file(self,
                                 parameter_source_name:str):
        local_val_save_name = parameter_source_name
        # save file
        if self.local_val_model == EnumCamModel['PINHOLE']:
            local_val_save_name = local_val_save_name.replace('cm', 'ph')
        elif self.local_val_model == EnumCamModel['FISHEYE']:
            local_val_save_name = local_val_save_name.replace('cm', 'fe')
        elif self.local_val_model == EnumCamModel['ERP']:
            local_val_save_name = local_val_save_name.replace('cm', 'erp')
        
        # get save format
        if self.local_val_type == EnumTargetType['DEPTH']:
            local_val_save_name = local_val_save_name.split('.')[0] + '.npz'
        elif self.local_val_type == EnumTargetType['RGB']:
            local_val_save_name = local_val_save_name.split('.')[0] + '.jpg'

        return local_val_save_name
    
    def __getitem__(self, index):        
        
        local_val_file = self.local_val_files[index]
        local_val_save_name = self.__function_get_save_file(local_val_file)
        local_val_full_path = os.path.join(self.local_val_cubemap_dir, local_val_file)
        local_val_array = np.load(local_val_full_path)
     
        local_val_cube = {}
        for local_val_view in self.local_val_order:
            local_val_cube_view = local_val_array[local_val_view] # H*W*C
            Image.fromarray(local_val_cube_view).save('test.jpg')
            local_val_cube_view = local_val_cube_view.transpose(2, 0, 1) # 1*C*H*W
            local_val_cube_view = torch.from_numpy(local_val_cube_view)
            local_val_cube_view.requires_grad = False
            local_val_cube_view = local_val_cube_view.float() # dtype force to float32
            if self.local_val_type == EnumTargetType['DEPTH']:
                # convert bgr to depth
                normalized = (local_val_cube_view[2:3,:,:] + local_val_cube_view[1:2,:,:] * 256 + local_val_cube_view[0:1,:,:] * 256 * 256) / (256 * 256 * 256 - 1)
                in_meters = 1000 * normalized
                _, H, W = in_meters.shape
                local_val_grids_w, local_val_grids_h = torch.meshgrid(torch.arange(W),torch.arange(H),  indexing = 'xy')
                local_val_grids_h = local_val_grids_h.float()
                local_val_grids_w = local_val_grids_w.float()
                local_val_grids_center = (W - 1) / 2
                local_val_grids_h = local_val_grids_h - local_val_grids_center
                local_val_grids_w = local_val_grids_w - local_val_grids_center
                local_val_cube_f =  torch.tensor(W / 2, dtype=torch.float32) # cube must satisfy: H=W, fov=90
                local_val_grids_r = torch.sqrt(local_val_grids_h**2+local_val_grids_w**2+local_val_cube_f**2) # H*W
                local_val_factor = (local_val_grids_r/local_val_cube_f).unsqueeze(0) # 1*H*W
                local_val_cube[local_val_view] = torch.multiply(local_val_factor,in_meters) # real depth
            else:
                local_val_cube[local_val_view] = local_val_cube_view # C*H*W
        return {'save_name':local_val_save_name, 
                'cube':local_val_cube}
    
    def __len__(self):
        return len(self.local_val_files)
