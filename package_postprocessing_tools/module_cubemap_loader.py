import os
import numpy as np
from torch.utils.data import Dataset
import torch

class ClassCubemapDataset(Dataset):
    def __init__(self, 
                 parameter_cubemap_dir,
                 parameter_cubemap_order,
                 parameter_target_model,
                 parameter_target_format,
                 parameter_target_type):
        self.local_val_cubemap_dir = parameter_cubemap_dir
        self.local_val_files = os.listdir(self.local_val_cubemap_dir)
        self.local_val_format = parameter_target_format
        self.local_val_model = parameter_target_model
        self.local_val_order = parameter_cubemap_order
        self.local_val_type = parameter_target_type

    def __getitem__(self, index):        
        
        local_val_file = self.local_val_files[index]
        local_val_save_name = local_val_file.replace('cm', self.local_val_model)
        local_val_save_name = local_val_save_name.split('.')[0] + '.' + self.local_val_format
        local_val_full_path = os.path.join(self.local_val_cubemap_dir, local_val_file)
        local_val_array = np.load(local_val_full_path)

        local_val_cube = {}
        for local_val_view in self.local_val_order:
            local_val_cube_view = local_val_array[local_val_view] # H*W*C
            local_val_cube_view = local_val_cube_view.transpose(2, 0, 1) # 1*C*H*W
            local_val_cube_view = torch.from_numpy(local_val_cube_view)
            local_val_cube_view.requires_grad = False
            local_val_cube_view = local_val_cube_view.float() # dtype force to float32
            local_val_cube[local_val_view] = local_val_cube_view 
        
        return {'save_name':local_val_save_name, 
                'cube':local_val_cube}
    
    def __len__(self):
        return len(self.local_val_files)
