@echo off

@REM Variables
set ROOT_PATH=output/erp2ph_demo

echo [INFO]file_path:"%ROOT_PATH%"

start python tools/cubemap2pinhole.py   --fov 30^
                                        --cubeW 2560^
                                        --outH 1560^
                                        --outW 2880^
                                        --external_path "%ROOT_PATH%/external.txt"^
                                        --cubemap_dir "%ROOT_PATH%/cubemap"^
                                        --output_dir "%ROOT_PATH%/pinhole_2880_1560_30"^
                                        --camera "cm_rgb1"^
                                        --use_cuda

start python tools/cubemap2pinhole.py   --fov 100^
                                        --cubeW 2560^
                                        --outH 1560^
                                        --outW 2880^
                                        --external_path "%ROOT_PATH%/external.txt"^
                                        --cubemap_dir "%ROOT_PATH%/cubemap"^
                                        --output_dir "%ROOT_PATH%/pinhole_2880_1560_100"^
                                        --camera "cm_rgb1"^
                                        --use_cuda

start python tools/cubemap2pinhole.py   --fov 30^
                                        --cubeW 2560^
                                        --outH 1080^
                                        --outW 1920^
                                        --external_path "%ROOT_PATH%/external.txt"^
                                        --cubemap_dir "%ROOT_PATH%/cubemap"^
                                        --output_dir "%ROOT_PATH%/pinhole_1920_1080_30"^
                                        --camera "cm_rgb1"^
                                        --use_cuda

start python tools/cubemap2pinhole.py   --fov 100^
                                        --cubeW 2560^
                                        --outH 1080^
                                        --outW 1920^
                                        --external_path "%ROOT_PATH%/external.txt"^
                                        --cubemap_dir "%ROOT_PATH%/cubemap"^
                                        --output_dir "%ROOT_PATH%/pinhole_1920_1080_100"^
                                        --camera "cm_rgb1"^
                                        --use_cuda


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

@REM python tools/cubemap2erp.py     --external_path "%ROOT_PATH%/external.txt"^
@REM                                 --cubeW 1080^
@REM                                 --cubemap_dir "%ROOT_PATH%/cubemap"^
@REM                                 --output_dir "%ROOT_PATH%/erp"^
@REM                                 --camera "cm_rgb9"^
@REM                                 --use_cuda
