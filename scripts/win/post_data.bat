@echo off

set root_path=output/Town04_frames_500

echo [INFO]file_path:"%root_path%"

start python tools/cubemap2fisheye.py --fov 210^
                                --external_path "%root_path%/external.txt"^
                                --cubemap_dir "%root_path%/cubemap"^
                                --output_dir "%root_path%/fisheye"^
                                --use_cuda

start python tools/cubemap2erp.py     --external_path "%root_path%/external.txt"^
                                --cubemap_dir "%root_path%/cubemap"^
                                --output_dir "%root_path%/erp"^
                                --use_cuda
