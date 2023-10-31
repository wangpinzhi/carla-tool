from .module_cubemap_loader import ClassCubemapDataset
from .module_cubemap_processor import ClassCubemapProcesser
import cv2
from PIL import Image

def vis_depth(depth, max_depth=5, min_depth=0):
    # invalid_mask = (depth<min_depth)|(depth>max_depth)
    # print(depth.min())
    scale_depth = 255 - cv2.convertScaleAbs(depth, alpha=255/20.0)
    vis_color = cv2.cvtColor(cv2.applyColorMap(scale_depth, cv2.COLORMAP_INFERNO),cv2.COLOR_BGR2RGB)
    # vis_color[:,:,0][invalid_mask] = 0 
    # vis_color[:,:,1][invalid_mask] = 0 
    # vis_color[:,:,2][invalid_mask] = 0
    vis_color = Image.fromarray(vis_color)
    return vis_color

def vis_invdepth(invdepth, max_invdepth=1/1.65, min_invdepth=1/100):
    invalid_mask = (invdepth<min_invdepth)|(invdepth>max_invdepth)
    scale_depth = cv2.convertScaleAbs(invdepth, alpha=255/(max_invdepth-min_invdepth), beta=min_invdepth)
    vis_color = cv2.applyColorMap(scale_depth, cv2.COLORMAP_JET)
    vis_color[:,:,0][invalid_mask] = 0 
    vis_color[:,:,1][invalid_mask] = 0 
    vis_color[:,:,2][invalid_mask] = 0
    vis_color = Image.fromarray(vis_color)
    return vis_color