import numpy as np
import torch
import torch.nn.functional as F

class ClassCubemapProcesser(object):
    def __init__(self, 
                 parameter_target_type,
                 parameter_target_height, # fisheye model will discard it
                 parameter_target_width,
                 parameter_target_fov, # degree
                 parameter_rot_matrix=None, # rotation matrix
                 parameter_batchsize=1,
                 parameter_device='cpu'):
        self.local_val_rot_matrix = parameter_rot_matrix
        self.local_val_batchsize = parameter_batchsize
        self.local_val_target_height = parameter_target_height
        self.local_val_target_width  = parameter_target_width
        self.local_val_target_fov = parameter_target_fov
        self.local_val_device = parameter_device
        self.local_val_grids = None
        if parameter_target_type == 'fe':
            self.local_val_grids = self.__get_fisheye_grids()
            print(self.local_val_grids.keys())

    def __transforms(self, 
                     parameter_alpha,
                     parameter_beta):
        local_val_temp_X = np.cos(parameter_alpha)
        local_val_temp_Y = np.sin(parameter_alpha) * np.cos(parameter_beta)
        local_val_temp_Z = np.sin(parameter_alpha) * np.sin(parameter_beta)
        local_val_temp_coor3d = np.dstack((local_val_temp_X, local_val_temp_Y, local_val_temp_Z))
        local_val_temp_coor3d = np.expand_dims(local_val_temp_coor3d, axis=-1) # H*W*3*1
        
        local_val_target_coor3d = np.matmul(self.local_val_rot_matrix, local_val_temp_coor3d).squeeze(-1) # H*W*3
        local_val_target_X = local_val_target_coor3d[:,:,0] #H*W
        local_val_target_Y = local_val_target_coor3d[:,:,1]
        local_val_target_Z = local_val_target_coor3d[:,:,2]

        local_val_target_beta = np.arctan2(local_val_target_Z, local_val_target_Y)
        local_val_target_r = np.sqrt(local_val_target_X**2+local_val_target_Y**2+local_val_target_Z**2)
        local_val_target_alpha = np.arccos(local_val_target_X / local_val_target_r)

        return local_val_target_alpha, local_val_target_beta
    
    def __get_fisheye_grids(self):
        local_val_target_grids = {} 

        local_val_alpha_max =  np.deg2rad(self.local_val_target_fov) / 2
        local_val_target_focal = (self.local_val_target_width/2) / local_val_alpha_max

        # gridy, gridz
        local_val_Y, local_val_Z = np.meshgrid(range(self.local_val_target_width), range(self.local_val_target_width))
        local_val_Y = local_val_Y.astype(np.float32)
        local_val_Z = local_val_Z.astype(np.float32)
        local_val_centerY = (self.local_val_target_width - 1 ) / 2
        local_val_centerZ = (self.local_val_target_width - 1 ) / 2
        local_val_Y = local_val_Y - local_val_centerY
        local_val_Z = -(local_val_Z - local_val_centerZ)
        
        local_val_R = np.sqrt(local_val_Y*local_val_Y+local_val_Z*local_val_Z)
        local_val_alpha = local_val_R / local_val_target_focal  # rad instead of degree
        local_val_beta = np.arctan2(local_val_Z, local_val_Y)
        local_val_invalid_mask = local_val_alpha > local_val_alpha_max
        
        # transforms 
        if self.local_val_rot_matrix is not None:
            local_val_alpha, local_val_beta = self.__transforms(local_val_alpha, local_val_beta)
        
        # front gird
        local_val_front_mask = (np.cos(local_val_alpha) < 0) | local_val_invalid_mask
        local_val_front_Y = np.tan(local_val_alpha) * np.cos(local_val_beta)
        local_val_front_Z = -np.tan(local_val_alpha) * np.sin(local_val_beta)
        local_val_front_Y[local_val_front_mask] = -2.
        local_val_front_Z[local_val_front_mask] = -2.
        local_val_front_grid = np.dstack((local_val_front_Y, local_val_front_Z))
        local_val_front_grid = np.expand_dims(local_val_front_grid, axis=0).repeat(self.local_val_batchsize, axis=0)
        local_val_target_grids['front_data'] = torch.from_numpy(local_val_front_grid).to(self.local_val_device)
        local_val_target_grids['front_data'].requires_grad = False

        # left grid
        local_val_left_mask = (np.cos(local_val_beta) > 0) | local_val_invalid_mask
        local_val_left_Z = np.tan(local_val_beta)
        local_val_left_X = (-1) / (np.tan(local_val_alpha)*np.cos(local_val_beta))
        local_val_left_Z[local_val_left_mask] = -2.
        local_val_left_X[local_val_left_mask] = -2.
        local_val_left_grid = np.dstack((local_val_left_X, local_val_left_Z))
        local_val_left_grid = np.expand_dims(local_val_left_grid, axis=0).repeat(self.local_val_batchsize, axis=0)
        local_val_target_grids['left_data'] = torch.from_numpy(local_val_left_grid).to(self.local_val_device)
        local_val_target_grids['left_data'].requires_grad = False

        # back grid
        local_val_back_mask = (np.cos(local_val_alpha) > 0) |  local_val_invalid_mask # invalid mask
        local_val_back_Y = np.tan(local_val_alpha) * np.cos(local_val_beta)
        local_val_back_Z = np.tan(local_val_alpha) * np.sin(local_val_beta)
        local_val_back_Y[local_val_back_mask] = -2.
        local_val_back_Z[local_val_back_mask] = -2.
        local_val_back_grid = np.dstack((local_val_back_Y, local_val_back_Z))
        local_val_back_grid = np.expand_dims(local_val_back_grid, axis=0).repeat(self.local_val_batchsize, axis=0)
        local_val_target_grids['back_data'] = torch.from_numpy(local_val_back_grid).to(self.local_val_device)
        local_val_target_grids['back_data'].requires_grad = False

        # right grid
        local_val_right_mask = (np.cos(local_val_beta) < 0) | local_val_invalid_mask
        local_val_right_Z = -np.tan(local_val_beta)
        local_val_right_X = (-1) / (np.tan(local_val_alpha)*np.cos(local_val_beta))
        local_val_right_Z[local_val_right_mask] = -2.
        local_val_right_X[local_val_right_mask] = -2.
        local_val_right_grid = np.dstack((local_val_right_X, local_val_right_Z))
        local_val_right_grid = np.expand_dims(local_val_right_grid, axis=0).repeat(self.local_val_batchsize, axis=0)
        local_val_target_grids['right_data'] = torch.from_numpy(local_val_right_grid).to(self.local_val_device)
        local_val_target_grids['right_data'].requires_grad = False


        # up grid
        local_val_up_mask = (np.sin(local_val_beta) < 0) | local_val_invalid_mask
        local_val_up_X = 1 / (np.tan(local_val_alpha)*np.sin(local_val_beta))
        local_val_up_Y = 1 / (np.tan(local_val_beta))
        local_val_up_X[local_val_up_mask] = -2.
        local_val_up_Y[local_val_up_mask] = -2.
        local_val_up_grid =  np.dstack((local_val_up_Y, local_val_up_X))
        local_val_up_grid = np.expand_dims(local_val_up_grid, axis=0).repeat(self.local_val_batchsize, axis=0)
        local_val_target_grids['up_data'] = torch.from_numpy(local_val_up_grid).to(self.local_val_device)
        local_val_target_grids['up_data'].requires_grad = False
        
        # down grid
        local_val_down_mask = (np.sin(local_val_beta) > 0) | local_val_invalid_mask
        local_val_down_X = 1 / (np.tan(local_val_alpha)*np.sin(local_val_beta))
        local_val_down_Y = (-1) / (np.tan(local_val_beta))
        local_val_down_X[local_val_down_mask] = -2.
        local_val_down_Y[local_val_down_mask] = -2.
        local_val_down_grid = np.dstack((local_val_down_Y, local_val_down_X))
        local_val_down_grid = np.expand_dims(local_val_down_grid, axis=0).repeat(self.local_val_batchsize, axis=0)
        local_val_target_grids['down_data'] = torch.from_numpy(local_val_down_grid).to(self.local_val_device)
        local_val_target_grids['down_data'].requires_grad = False

        return local_val_target_grids
        
    def trans(self, 
              parameter_cube:dict, # N * C * H * W
              parameter_order):
        
        local_val_target = None
        for local_val_view in parameter_order:
            local_val_temp = F.grid_sample(input = parameter_cube[local_val_view].to(self.local_val_device), 
                                           grid = self.local_val_grids[local_val_view], 
                                           mode='bilinear', padding_mode='zeros', align_corners=False)
            if local_val_target is None:
                local_val_target = local_val_temp
            else:
                local_val_target += local_val_temp
                # pass
        return local_val_target
        

        