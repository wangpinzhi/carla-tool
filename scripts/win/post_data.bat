@echo off

@REM Variables
set ROOT_PATH=output/nju_scene1

echo [INFO]file_path:"%ROOT_PATH%"

@REM start python tools/cubemap2pinhole.py   --fov 60^
@REM                                         --cubeW 2560^
@REM                                         --outH 720^
@REM                                         --outW 1280^
@REM                                         --external_path "%ROOT_PATH%/external.txt"^
@REM                                         --cubemap_dir "%ROOT_PATH%/cubemap"^
@REM                                         --output_dir "%ROOT_PATH%/pinhole_720p_60"^
@REM                                         --camera "cm_rgb0"^
@REM                                         --use_cuda

start python tools/cubemap2fisheye.py   --fov 190^
                                        --cubeW 2560^
                                        --outW 2560^
                                        --r_x 0^
                                        --external_path "%ROOT_PATH%/external.txt"^
                                        --cubemap_dir "%ROOT_PATH%/cubemap"^
                                        --output_dir "%ROOT_PATH%/fisheye_p0"^
                                        --camera "cm_rgb0"^
                                        --use_cuda

@REM start python tools/cubemap2erp.py       --external_path "%ROOT_PATH%/external.txt"^
@REM                                         --cubeW 2560^
@REM                                         --cubemap_dir "%ROOT_PATH%/cubemap"^
@REM                                         --output_dir "%ROOT_PATH%/erp"^
@REM                                         --camera "cm_rgb0"^
@REM                                         --use_cuda
