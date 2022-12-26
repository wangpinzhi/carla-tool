@echo off

@REM Variables
set ROOT_PATH=output/huawei_demo

echo [INFO]file_path:"%ROOT_PATH%"

start python tools/cubemap2fisheye.py --fov 190^
                                --external_path "%ROOT_PATH%/external.txt"^
                                --cubemap_dir "%ROOT_PATH%/cubemap"^
                                --output_dir "%ROOT_PATH%/fisheye"^
                                --camera "cm_rgb9"^
                                --use_cuda

start python tools/cubemap2fisheye.py --fov 190^
                                --external_path "%ROOT_PATH%/external.txt"^
                                --cubemap_dir "%ROOT_PATH%/cubemap"^
                                --output_dir "%ROOT_PATH%/fisheye"^
                                --camera "cm_rgb10"^
                                --use_cuda

start python tools/cubemap2fisheye.py --fov 190^
                                --external_path "%ROOT_PATH%/external.txt"^
                                --cubemap_dir "%ROOT_PATH%/cubemap"^
                                --output_dir "%ROOT_PATH%/fisheye"^
                                --camera "cm_rgb11"^
                                --use_cuda

start python tools/cubemap2fisheye.py --fov 190^
                                --external_path "%ROOT_PATH%/external.txt"^
                                --cubemap_dir "%ROOT_PATH%/cubemap"^
                                --output_dir "%ROOT_PATH%/fisheye"^
                                --camera "cm_rgb12"^
                                --use_cuda

@REM start python tools/cubemap2erp.py     --external_path "%ROOT_PATH%/external.txt"^
@REM                                 --cubemap_dir "%ROOT_PATH%/cubemap"^
@REM                                 --output_dir "%ROOT_PATH%/erp"^
@REM                                 --camera "cm_depth9"^
@REM                                 --use_cuda
