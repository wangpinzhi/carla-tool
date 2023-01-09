@echo off

@REM Variables
set ROOT_PATH=output/huawei/huawei_parking02

echo [INFO]file_path:"%ROOT_PATH%"

@REM start python tools/cubemap2pinhole.py   --fov 60^
@REM                                         --cubeW 2560^
@REM                                         --outH 1080^
@REM                                         --outW 1920^
@REM                                         --external_path "%ROOT_PATH%/external.txt"^
@REM                                         --cubemap_dir "%ROOT_PATH%/cubemap"^
@REM                                         --output_dir "%ROOT_PATH%/pinhole_1080p_60"^
@REM                                         --camera "cm_rgb8"^
@REM                                         --use_cuda

@REM start python tools/cubemap2fisheye.py   --fov 190^
@REM                                         --cubeW 2560^
@REM                                         --outW 2560^
@REM                                         --r_x 0^
@REM                                         --external_path "%ROOT_PATH%/external.txt"^
@REM                                         --cubemap_dir "%ROOT_PATH%/cubemap"^
@REM                                         --output_dir "%ROOT_PATH%/fisheye190"^
@REM                                         --camera "cm_rgb13"^
@REM                                         --use_cuda

@REM start python tools/cubemap2erp.py       --external_path "%ROOT_PATH%/external.txt"^
@REM                                         --cubeW 2560^
@REM                                         --format "npz"^
@REM                                         --cubemap_dir "%ROOT_PATH%/cubemap"^
@REM                                         --output_dir "%ROOT_PATH%/erp"^
@REM                                         --camera "cm_depth0"^
@REM                                         --use_cuda
