@echo off

@REM Variables
set ROOT_PATH=%1

echo "process cm_rgb9 cm_rgb10 cm_rgb12"

start python tools/cubemap2fisheye.py   --fov 190^
                                        --cubeW 2560^
                                        --outW 2560^
                                        --r_x 15^
                                        --external_path "%ROOT_PATH%/external.txt"^
                                        --cubemap_dir "%ROOT_PATH%/cubemap"^
                                        --output_dir "%ROOT_PATH%/fisheye190_new"^
                                        --camera "cm_rgb9"^
                                        --use_cuda
                                        

start python tools/cubemap2fisheye.py   --fov 190^
                                        --cubeW 2560^
                                        --outW 2560^
                                        --r_x 15^
                                        --external_path "%ROOT_PATH%/external.txt"^
                                        --cubemap_dir "%ROOT_PATH%/cubemap"^
                                        --output_dir "%ROOT_PATH%/fisheye190_new"^
                                        --camera "cm_rgb10"^
                                        --use_cuda
                                        

start /WAIT python tools/cubemap2fisheye.py   --fov 190^
                                        --cubeW 2560^
                                        --outW 2560^
                                        --r_x 15^
                                        --external_path "%ROOT_PATH%/external.txt"^
                                        --cubemap_dir "%ROOT_PATH%/cubemap"^
                                        --output_dir "%ROOT_PATH%/fisheye190_new"^
                                        --camera "cm_rgb12"^
                                        --use_cuda
                                        

