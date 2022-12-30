@echo off

@REM Variables
set ROOT_PATH=output/huawei_demo

echo [INFO]file_path:"%ROOT_PATH%"

@REM start python tools/cubemap2fisheye.py --fov 190^
@REM                                 --external_path "%ROOT_PATH%/external.txt"^
@REM                                 --cubemap_dir "%ROOT_PATH%/cubemap"^
@REM                                 --output_dir "%ROOT_PATH%/fisheye"^
@REM                                 --camera "cm_rgb9"^
@REM                                 --use_cuda

@REM start python tools/cubemap2fisheye.py --fov 190^
@REM                                 --external_path "%ROOT_PATH%/external.txt"^
@REM                                 --cubemap_dir "%ROOT_PATH%/cubemap"^
@REM                                 --output_dir "%ROOT_PATH%/fisheye"^
@REM                                 --camera "cm_rgb10"^
@REM                                 --use_cuda

@REM start python tools/cubemap2fisheye.py --fov 190^
@REM                                 --external_path "%ROOT_PATH%/external.txt"^
@REM                                 --cubemap_dir "%ROOT_PATH%/cubemap"^
@REM                                 --output_dir "%ROOT_PATH%/fisheye"^
@REM                                 --camera "cm_rgb11"^
@REM                                 --use_cuda

@REM start python tools/cubemap2fisheye.py --fov 190^
@REM                                 --external_path "%ROOT_PATH%/external.txt"^
@REM                                 --cubemap_dir "%ROOT_PATH%/cubemap"^
@REM                                 --output_dir "%ROOT_PATH%/fisheye"^
@REM                                 --camera "cm_rgb12"^
@REM                                 --use_cuda

python tools/cubemap2erp.py     --external_path "%ROOT_PATH%/external.txt"^
                                --cubeW 1080^
                                --cubemap_dir "%ROOT_PATH%/cubemap"^
                                --output_dir "%ROOT_PATH%/erp"^
                                --camera "cm_rgb9"^
                                --use_cuda
