@echo off

@REM Variables
set WORLD_MAP=Town10
set FRAMES=50
set ROOT_PATH=output/%WORLD_MAP%_frames_%FRAMES%

echo [INFO]file_path:"%ROOT_PATH%"

start python tools/cubemap2fisheye.py --fov 210^
                                --external_path "%ROOT_PATH%/external.txt"^
                                --cubemap_dir "%ROOT_PATH%/cubemap"^
                                --output_dir "%ROOT_PATH%/fisheye"^
                                --use_cuda

start python tools/cubemap2erp.py     --external_path "%ROOT_PATH%/external.txt"^
                                --cubemap_dir "%ROOT_PATH%/cubemap"^
                                --output_dir "%ROOT_PATH%/erp"^
                                --use_cuda
