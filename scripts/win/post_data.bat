@echo off

@REM Variables
set MAP=Town10
set ROOT_PATH=output/%MAP%_demo_100frames

echo [INFO]file_path:"%ROOT_PATH%"

start python tools/cubemap2fisheye.py --fov 210^
                                --external_path "%ROOT_PATH%/external.txt"^
                                --cubemap_dir "%ROOT_PATH%/cubemap"^
                                --output_dir "%ROOT_PATH%/fisheye"^
                                --camera "cm_rgb1"^
                                --use_cuda

start python tools/cubemap2fisheye.py --fov 210^
                                --external_path "%ROOT_PATH%/external.txt"^
                                --cubemap_dir "%ROOT_PATH%/cubemap"^
                                --output_dir "%ROOT_PATH%/fisheye"^
                                --camera "cm_rgb2"^
                                --use_cuda

start python tools/cubemap2fisheye.py --fov 210^
                                --external_path "%ROOT_PATH%/external.txt"^
                                --cubemap_dir "%ROOT_PATH%/cubemap"^
                                --output_dir "%ROOT_PATH%/fisheye"^
                                --camera "cm_rgb3"^
                                --use_cuda

start python tools/cubemap2fisheye.py --fov 210^
                                --external_path "%ROOT_PATH%/external.txt"^
                                --cubemap_dir "%ROOT_PATH%/cubemap"^
                                --output_dir "%ROOT_PATH%/fisheye"^
                                --camera "cm_rgb4"^
                                --use_cuda

start python tools/cubemap2erp.py     --external_path "%ROOT_PATH%/external.txt"^
                                --cubemap_dir "%ROOT_PATH%/cubemap"^
                                --output_dir "%ROOT_PATH%/erp"^
                                --use_cuda
