@echo off

@REM Variables
set ROOT_PATH=%1

echo "process cm_rgb6 cm_rgb5 cm_rgb4"

start python tools/cubemap2fisheye.py   --fov 180^
                                        --cubeW 2560^
                                        --outW 2560^
                                        --r_x 0^
                                        --external_path "%ROOT_PATH%/external.txt"^
                                        --cubemap_dir "%ROOT_PATH%/cubemap"^
                                        --output_dir "%ROOT_PATH%/fisheye180"^
                                        --camera "cm_rgb6"^
                                        --use_cuda

start python tools/cubemap2fisheye.py   --fov 180^
                                        --cubeW 2560^
                                        --outW 2560^
                                        --r_x 0^
                                        --external_path "%ROOT_PATH%/external.txt"^
                                        --cubemap_dir "%ROOT_PATH%/cubemap"^
                                        --output_dir "%ROOT_PATH%/fisheye180"^
                                        --camera "cm_rgb5"^
                                        --use_cuda

start /WAIT python tools/cubemap2fisheye.py   --fov 180^
                                        --cubeW 2560^
                                        --outW 2560^
                                        --r_x 0^
                                        --external_path "%ROOT_PATH%/external.txt"^
                                        --cubemap_dir "%ROOT_PATH%/cubemap"^
                                        --output_dir "%ROOT_PATH%/fisheye180"^
                                        --camera "cm_rgb4"^
                                        --use_cuda

